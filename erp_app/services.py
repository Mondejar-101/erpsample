"""
Business Logic Services - OOP approach
Business rules should not be in Controllers/Views/API
"""
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Product, Supplier, ProcurementOrder, StockTransaction,
    Notification, StockParity, Category, SupplierEvaluation
)


class StockMonitoringService:
    """Service for stock monitoring business logic"""
    
    @staticmethod
    def get_low_stock_products():
        """Get all products with low stock"""
        return Product.objects.filter(
            current_stock__lte=F('reorder_level')
        ).select_related('category').order_by('current_stock')
    
    @staticmethod
    def get_out_of_stock_products():
        """Get all out of stock products"""
        return Product.objects.filter(current_stock=0).select_related('category')
    
    @staticmethod
    def get_low_stock_suggestions():
        """Get low stock suggestions with reorder recommendations"""
        low_stock = StockMonitoringService.get_low_stock_products()
        suggestions = []
        for product in low_stock:
            suggestions.append({
                'product': product,
                'current_stock': product.current_stock,
                'reorder_level': product.reorder_level,
                'suggested_quantity': product.reorder_quantity,
                'status': 'Out of Stock' if product.current_stock == 0 else 'Low Stock'
            })
        return suggestions
    
    @staticmethod
    def get_stock_parity_issues():
        """Get unresolved stock parity issues"""
        return StockParity.objects.filter(resolved=False).select_related('product')


class SupplierEvaluationService:
    """Service for supplier evaluation business logic"""
    
    @staticmethod
    def add_evaluation(supplier, rating, notes=None, evaluated_by=None):
        """Add a supplier evaluation"""
        evaluation = SupplierEvaluation.objects.create(
            supplier=supplier,
            rating=rating,
            notes=notes or '',
            evaluated_by=evaluated_by
        )
        # Update supplier rating based on all evaluations
        SupplierEvaluationService.update_supplier_rating(supplier)
        return evaluation
    
    @staticmethod
    def update_supplier_rating(supplier):
        """Update supplier's average rating from all evaluations"""
        evaluations = SupplierEvaluation.objects.filter(supplier=supplier)
        if evaluations.exists():
            avg_rating = evaluations.aggregate(avg=Avg('rating'))['avg']
            supplier.rating = Decimal(str(round(avg_rating, 2)))
            supplier.save()
    
    @staticmethod
    def get_supplier_evaluations(supplier):
        """Get all evaluations for a supplier"""
        return SupplierEvaluation.objects.filter(
            supplier=supplier
        ).select_related('evaluated_by').order_by('-created_at')
    
    @staticmethod
    def get_supplier_performance_data(supplier):
        """Get comprehensive performance data for a supplier"""
        evaluations = SupplierEvaluationService.get_supplier_evaluations(supplier)
        orders = ProcurementOrder.objects.filter(supplier=supplier)
        
        total_orders = orders.count()
        completed_orders = orders.filter(status='RECEIVED').count()
        on_time_orders = orders.filter(
            status='RECEIVED',
            actual_delivery_date__lte=F('expected_delivery_date')
        ).count()
        
        on_time_rate = (on_time_orders / completed_orders * 100) if completed_orders > 0 else 0
        
        return {
            'supplier': supplier,
            'evaluations': evaluations,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'on_time_rate': round(on_time_rate, 2),
            'average_rating': supplier.rating,
            'performance_status': supplier.get_performance_status()
        }


class ProcurementReportService:
    """Service for procurement report business logic"""
    
    @staticmethod
    def get_procurement_summary(days=30):
        """Get procurement summary for a date range"""
        start_date = timezone.now() - timedelta(days=days)
        
        orders = ProcurementOrder.objects.filter(order_date__gte=start_date)
        
        total_value = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        orders_by_status = orders.values('status').annotate(count=Count('id'))
        
        return {
            'total_value': total_value,
            'total_orders': orders.count(),
            'orders_by_status': list(orders_by_status),
            'start_date': start_date,
            'end_date': timezone.now(),
            'days': days
        }
    
    @staticmethod
    def get_top_suppliers_by_value(days=30, limit=10):
        """Get top suppliers by order value"""
        start_date = timezone.now() - timedelta(days=days)
        
        return Supplier.objects.annotate(
            total_order_value=Sum('orders__total_amount'),
            order_count=Count('orders')
        ).filter(
            orders__order_date__gte=start_date
        ).order_by('-total_order_value')[:limit]


class NotificationService:
    """Service for notification business logic"""
    
    @staticmethod
    def create_notification(title, message, notification_type, priority='MEDIUM', user=None, related_object=None):
        """Create a notification"""
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            user=user
        )
        
        if related_object:
            notification.related_object_id = related_object.pk
            notification.related_object_type = related_object.__class__.__name__
            notification.save()
        
        return notification
    
    @staticmethod
    def create_procurement_alert(order, alert_type='PR'):
        """Create procurement-related alert (PR/PO/Invoice)"""
        if alert_type == 'PR':
            title = f"Purchase Request Created: {order.order_number}"
            message = f"A new purchase request has been created for {order.supplier.name} with total amount ${order.total_amount}"
            notification_type = 'PR_ALERT'
        elif alert_type == 'PO':
            title = f"Purchase Order Status Update: {order.order_number}"
            message = f"Purchase order {order.order_number} status changed to {order.get_status_display()}"
            notification_type = 'PO_ALERT'
        else:  # Invoice
            title = f"Invoice Received: {order.order_number}"
            message = f"Invoice received for order {order.order_number} from {order.supplier.name}. Amount: ${order.total_amount}"
            notification_type = 'INVOICE_ALERT'
        
        return NotificationService.create_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority='HIGH' if order.status == 'PENDING' else 'MEDIUM',
            related_object=order
        )
    
    @staticmethod
    def check_and_create_low_stock_alerts():
        """Check for low stock and create alerts"""
        low_stock_products = StockMonitoringService.get_low_stock_products()
        
        for product in low_stock_products:
            NotificationService.create_notification(
                title=f"Low Stock Alert: {product.name}",
                message=f"{product.name} (SKU: {product.sku}) is below reorder level. Current stock: {product.current_stock}",
                notification_type='LOW_STOCK',
                priority='HIGH' if product.current_stock == 0 else 'MEDIUM',
                related_object=product
            )


class ReportExportService:
    """Service for report export business logic"""
    
    @staticmethod
    def prepare_low_stock_data():
        """Prepare low stock data for export"""
        suggestions = StockMonitoringService.get_low_stock_suggestions()
        return {
            'title': 'Low Stock Report',
            'generated_at': timezone.now(),
            'items': suggestions
        }
    
    @staticmethod
    def prepare_supplier_performance_data(supplier=None):
        """Prepare supplier performance data for export"""
        if supplier:
            suppliers = [supplier]
        else:
            suppliers = Supplier.objects.filter(is_active=True).order_by('-rating')
        
        data = []
        for s in suppliers:
            performance = SupplierEvaluationService.get_supplier_performance_data(s)
            data.append({
                'supplier': s,
                'rating': s.rating,
                'total_orders': performance['total_orders'],
                'on_time_rate': performance['on_time_rate'],
                'quality_score': s.quality_score,
                'performance_status': performance['performance_status']
            })
        
        return {
            'title': 'Supplier Performance Report',
            'generated_at': timezone.now(),
            'suppliers': data
        }
    
    @staticmethod
    def prepare_procurement_report_data(days=30):
        """Prepare procurement report data for export"""
        summary = ProcurementReportService.get_procurement_summary(days)
        top_suppliers = ProcurementReportService.get_top_suppliers_by_value(days)
        
        return {
            'title': 'Procurement Report',
            'generated_at': timezone.now(),
            'period_days': days,
            'summary': summary,
            'top_suppliers': list(top_suppliers)
        }
    
    @staticmethod
    def prepare_dashboard_data():
        """Prepare dashboard data for export"""
        low_stock = StockMonitoringService.get_low_stock_products()
        pending_orders = ProcurementOrder.objects.filter(status='PENDING')
        overdue_orders = [o for o in ProcurementOrder.objects.exclude(
            status__in=['RECEIVED', 'CANCELLED']
        ) if o.is_overdue()]
        
        return {
            'title': 'Dashboard Report',
            'generated_at': timezone.now(),
            'low_stock_count': low_stock.count(),
            'pending_requests': pending_orders.count(),
            'overdue_orders': len(overdue_orders),
            'low_stock_items': list(low_stock[:20]),
            'pending_orders': list(pending_orders[:20])
        }

