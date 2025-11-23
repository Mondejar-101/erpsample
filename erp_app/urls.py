from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Stock Management
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stock/parity/', views.StockParityListView.as_view(), name='stock_parity_list'),
    path('stock/parity/<int:pk>/resolve/', views.resolve_parity, name='resolve_parity'),
    path('stock/low-stock-dashboard/', views.LowStockDashboardView.as_view(), name='low_stock_dashboard'),
    
    # Supplier Management
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:supplier_id>/evaluate/', views.SupplierEvaluationCreateView.as_view(), name='supplier_evaluate'),
    path('suppliers/<int:pk>/evaluations/', views.SupplierEvaluationsView.as_view(), name='supplier_evaluations'),
    
    # Procurement
    path('procurement/', views.ProcurementOrderListView.as_view(), name='procurement_list'),
    path('procurement/<int:pk>/', views.ProcurementOrderDetailView.as_view(), name='procurement_detail'),
    path('procurement/reports/', views.ProcurementReportView.as_view(), name='procurement_reports'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Reports
    path('reports/', views.ReportsDashboardView.as_view(), name='reports_dashboard'),
    
    # Export Views (for PDF generation)
    path('export/low-stock/', views.ExportLowStockView.as_view(), name='export_low_stock'),
    path('export/supplier-performance/', views.ExportSupplierPerformanceView.as_view(), name='export_supplier_performance'),
    path('export/procurement-report/', views.ExportProcurementReportView.as_view(), name='export_procurement_report'),
    path('export/dashboard/', views.ExportDashboardView.as_view(), name='export_dashboard'),
]

