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
    
    # Supplier Management
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    # Procurement
    path('procurement/', views.ProcurementOrderListView.as_view(), name='procurement_list'),
    path('procurement/<int:pk>/', views.ProcurementOrderDetailView.as_view(), name='procurement_detail'),
    path('procurement/reports/', views.ProcurementReportView.as_view(), name='procurement_reports'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Reports
    path('reports/', views.ReportsDashboardView.as_view(), name='reports_dashboard'),
]

