"""
ERP Application Views using Class-Based Views (OOP)
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Product, Supplier, ProcurementOrder, StockTransaction,
    Notification, StockParity, Category, SupplierEvaluation
)
from .forms import SupplierEvaluationForm
from .services import (
    StockMonitoringService, SupplierEvaluationService,
    ProcurementReportService, NotificationService, ReportExportService
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main Dashboard View"""
    template_name = 'erp_app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stock Statistics
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(
            current_stock__lte=F('reorder_level')
        ).count()
        out_of_stock = Product.objects.filter(current_stock=0).count()
        total_stock_value = sum(p.get_total_value() for p in Product.objects.all())
        
        # Procurement Statistics
        pending_orders = ProcurementOrder.objects.filter(status='PENDING').count()
        overdue_orders = sum(1 for order in ProcurementOrder.objects.exclude(
            status__in=['RECEIVED', 'CANCELLED']
        ) if order.is_overdue())
        total_orders = ProcurementOrder.objects.count()
        
        # Supplier Statistics
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        top_suppliers = Supplier.objects.filter(is_active=True).order_by('-rating')[:5]
        
        # Recent Notifications
        recent_notifications = Notification.objects.filter(
            is_read=False
        ).order_by('-created_at')[:10]
        
        # Recent Stock Transactions
        recent_transactions = StockTransaction.objects.select_related('product').order_by('-created_at')[:10]
        
        # Stock Parity Issues
        unresolved_parities = StockParity.objects.filter(resolved=False).count()
        
        context.update({
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock': out_of_stock,
            'total_stock_value': total_stock_value,
            'pending_orders': pending_orders,
            'overdue_orders': overdue_orders,
            'total_orders': total_orders,
            'total_suppliers': total_suppliers,
            'top_suppliers': top_suppliers,
            'recent_notifications': recent_notifications,
            'recent_transactions': recent_transactions,
            'unresolved_parities': unresolved_parities,
        })
        return context


class StockListView(LoginRequiredMixin, ListView):
    """Stock Monitoring List View"""
    model = Product
    template_name = 'erp_app/stock_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        
        if status == 'low':
            queryset = queryset.filter(current_stock__lte=F('reorder_level'))
        elif status == 'out':
            queryset = queryset.filter(current_stock=0)
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        return context


class StockDetailView(LoginRequiredMixin, DetailView):
    """Stock Detail View with Transactions"""
    model = Product
    template_name = 'erp_app/stock_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.all()[:20]
        context['parities'] = self.object.parities.filter(resolved=False)
        return context


class StockParityListView(LoginRequiredMixin, ListView):
    """Stock Parity Issues List View"""
    model = StockParity
    template_name = 'erp_app/stock_parity_list.html'
    context_object_name = 'parities'
    paginate_by = 20

    def get_queryset(self):
        resolved = self.request.GET.get('resolved', 'false')
        if resolved == 'true':
            return StockParity.objects.filter(resolved=True).select_related('product')
        return StockParity.objects.filter(resolved=False).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resolved'] = self.request.GET.get('resolved', 'false')
        return context


class SupplierListView(LoginRequiredMixin, ListView):
    """Supplier List View"""
    model = Supplier
    template_name = 'erp_app/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Supplier.objects.all()
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset.order_by('-rating', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SupplierDetailView(LoginRequiredMixin, DetailView):
    """Supplier Detail View with Evaluation"""
    model = Supplier
    template_name = 'erp_app/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.object.orders.all()[:20]
        context['performance_score'] = self.object.calculate_performance_score()
        context['performance_status'] = self.object.get_performance_status()
        return context


class ProcurementOrderListView(LoginRequiredMixin, ListView):
    """Procurement Orders List View"""
    model = ProcurementOrder
    template_name = 'erp_app/procurement_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = ProcurementOrder.objects.select_related('supplier', 'created_by').all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) | Q(supplier__name__icontains=search)
            )
        
        return queryset.order_by('-order_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class ProcurementOrderDetailView(LoginRequiredMixin, DetailView):
    """Procurement Order Detail View"""
    model = ProcurementOrder
    template_name = 'erp_app/procurement_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product').all()
        context['is_overdue'] = self.object.is_overdue()
        return context


class ProcurementReportView(LoginRequiredMixin, TemplateView):
    """Procurement Reports View"""
    template_name = 'erp_app/procurement_reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range filter
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Orders by status
        orders_by_status = ProcurementOrder.objects.filter(
            order_date__gte=start_date
        ).values('status').annotate(count=Count('id'))
        
        # Total procurement value
        total_value = ProcurementOrder.objects.filter(
            order_date__gte=start_date
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Top suppliers by order value
        top_suppliers = Supplier.objects.annotate(
            total_order_value=Sum('orders__total_amount'),
            order_count=Count('orders')
        ).filter(
            orders__order_date__gte=start_date
        ).order_by('-total_order_value')[:10]
        
        # Orders over time
        orders_over_time = ProcurementOrder.objects.filter(
            order_date__gte=start_date
        ).extra(
            select={'day': 'date(order_date)'}
        ).values('day').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('day')
        
        context.update({
            'days': days,
            'orders_by_status': orders_by_status,
            'total_value': total_value,
            'top_suppliers': top_suppliers,
            'orders_over_time': list(orders_over_time),
        })
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    """Notifications List View"""
    model = Notification
    template_name = 'erp_app/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        read = self.request.GET.get('read', 'false')
        if read == 'true':
            return Notification.objects.filter(is_read=True)
        return Notification.objects.filter(is_read=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['read'] = self.request.GET.get('read', 'false')
        context['unread_count'] = Notification.objects.filter(is_read=False).count()
        return context


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    """Reports & Analytics Dashboard"""
    template_name = 'erp_app/reports_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stock Analytics
        stock_by_category = Product.objects.values(
            'category__name'
        ).annotate(
            total_items=Count('id'),
            total_value=Sum(F('current_stock') * F('unit_price'))
        )
        
        # Supplier Performance
        supplier_performance = Supplier.objects.annotate(
            avg_order_value=Avg('orders__total_amount'),
            order_count=Count('orders')
        ).filter(is_active=True).order_by('-rating')[:10]
        
        # Low Stock Items
        low_stock_items = Product.objects.filter(
            current_stock__lte=F('reorder_level')
        ).order_by('current_stock')[:20]
        
        # Recent Activity
        recent_orders = ProcurementOrder.objects.select_related('supplier').order_by('-order_date')[:10]
        
        context.update({
            'stock_by_category': stock_by_category,
            'supplier_performance': supplier_performance,
            'low_stock_items': low_stock_items,
            'recent_orders': recent_orders,
        })
        return context


# Helper views for actions
def mark_notification_read(request, pk):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=pk)
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')


def resolve_parity(request, pk):
    """Resolve stock parity issue"""
    parity = get_object_or_404(StockParity, pk=pk)
    if request.method == 'POST':
        parity.resolve(request.user)
        messages.success(request, 'Stock parity issue resolved.')
        return redirect('stock_parity_list')
    return render(request, 'erp_app/resolve_parity.html', {'parity': parity})


# Authentication Views
class CustomLoginView(LoginView):
    """Custom Login View"""
    template_name = 'erp_app/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom Logout View"""
    pass


class RegisterView(CreateView):
    """User Registration View"""
    form_class = UserCreationForm
    template_name = 'erp_app/register.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Account created successfully! Welcome, {self.object.username}!')
        return response


# Stock Monitoring Dashboard (On-demand)
class LowStockDashboardView(LoginRequiredMixin, TemplateView):
    """Low Stock Dashboard View (On-demand)"""
    template_name = 'erp_app/low_stock_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['low_stock_products'] = StockMonitoringService.get_low_stock_products()
        context['low_stock_suggestions'] = StockMonitoringService.get_low_stock_suggestions()
        context['out_of_stock_products'] = StockMonitoringService.get_out_of_stock_products()
        return context


# Supplier Evaluation Views
class SupplierEvaluationCreateView(LoginRequiredMixin, CreateView):
    """Create Supplier Evaluation View"""
    model = SupplierEvaluation
    form_class = SupplierEvaluationForm
    template_name = 'erp_app/supplier_evaluation_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.supplier = get_object_or_404(Supplier, pk=kwargs['supplier_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        evaluation = form.save(commit=False)
        evaluation.supplier = self.supplier
        evaluation.evaluated_by = self.request.user
        evaluation.save()
        
        # Use service to update supplier rating
        SupplierEvaluationService.update_supplier_rating(self.supplier)
        
        messages.success(self.request, f'Evaluation added for {self.supplier.name}')
        return redirect('supplier_evaluations', pk=self.supplier.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier'] = self.supplier
        return context


class SupplierEvaluationsView(LoginRequiredMixin, DetailView):
    """View Supplier Evaluations"""
    model = Supplier
    template_name = 'erp_app/supplier_evaluations.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluations'] = SupplierEvaluationService.get_supplier_evaluations(self.object)
        context['performance_data'] = SupplierEvaluationService.get_supplier_performance_data(self.object)
        return context


# Export Views (JSON endpoints for jsPDF)
class ExportLowStockView(LoginRequiredMixin, TemplateView):
    """Export Low Stock Data as JSON for PDF generation"""
    template_name = 'erp_app/export_low_stock.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_data'] = ReportExportService.prepare_low_stock_data()
        return context


class ExportSupplierPerformanceView(LoginRequiredMixin, TemplateView):
    """Export Supplier Performance Data as JSON for PDF generation"""
    template_name = 'erp_app/export_supplier_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier_id = self.request.GET.get('supplier_id')
        supplier = None
        if supplier_id:
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
            except Supplier.DoesNotExist:
                pass
        context['export_data'] = ReportExportService.prepare_supplier_performance_data(supplier)
        return context


class ExportProcurementReportView(LoginRequiredMixin, TemplateView):
    """Export Procurement Report Data as JSON for PDF generation"""
    template_name = 'erp_app/export_procurement_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = int(self.request.GET.get('days', 30))
        context['export_data'] = ReportExportService.prepare_procurement_report_data(days)
        return context


class ExportDashboardView(LoginRequiredMixin, TemplateView):
    """Export Dashboard Data as JSON for PDF generation"""
    template_name = 'erp_app/export_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_data'] = ReportExportService.prepare_dashboard_data()
        return context

