from django.contrib import admin
from .models import (
    Supplier, Category, Product, StockTransaction,
    ProcurementOrder, ProcurementOrderItem, Notification, StockParity
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'rating', 'total_orders', 'is_active']
    list_filter = ['is_active', 'rating']
    search_fields = ['name', 'email', 'contact_person']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'current_stock', 'reorder_level', 'unit_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'created_at', 'user']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name', 'reference_number']


class ProcurementOrderItemInline(admin.TabularInline):
    model = ProcurementOrderItem
    extra = 1


@admin.register(ProcurementOrder)
class ProcurementOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'status', 'order_date', 'total_amount']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'supplier__name']
    inlines = [ProcurementOrderItemInline]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message']


@admin.register(StockParity)
class StockParityAdmin(admin.ModelAdmin):
    list_display = ['product', 'expected_quantity', 'actual_quantity', 'discrepancy', 'resolved', 'created_at']
    list_filter = ['resolved', 'created_at']
    search_fields = ['product__name']

