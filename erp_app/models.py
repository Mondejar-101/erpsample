"""
ERP Application Models using OOP principles
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class TimestampMixin(models.Model):
    """Abstract base class for timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseEntity(TimestampMixin):
    """Abstract base class for entities with common fields"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Supplier(BaseEntity):
    """Supplier model with evaluation metrics"""
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    total_orders = models.IntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    quality_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )

    class Meta:
        ordering = ['-rating', 'name']

    def calculate_performance_score(self):
        """Calculate overall performance score"""
        return (
            self.rating * 20 + 
            self.on_time_delivery_rate * 0.3 + 
            self.quality_score * 0.3
        ) / 2

    def get_performance_status(self):
        """Get performance status based on score"""
        score = self.calculate_performance_score()
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        else:
            return "Poor"


class Category(BaseEntity):
    """Product category model"""
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )

    class Meta:
        verbose_name_plural = "Categories"


class Product(BaseEntity):
    """Product/Stock item model"""
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reorder_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    reorder_quantity = models.IntegerField(default=50, validators=[MinValueValidator(1)])
    current_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    unit_of_measure = models.CharField(max_length=20, default='units')
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.current_stock <= self.reorder_level

    def get_stock_status(self):
        """Get stock status"""
        if self.current_stock == 0:
            return "Out of Stock"
        elif self.is_low_stock():
            return "Low Stock"
        else:
            return "In Stock"

    def get_total_value(self):
        """Calculate total stock value"""
        return self.current_stock * self.unit_price


class StockTransaction(TimestampMixin):
    """Stock transaction model for tracking stock movements"""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
        ('RET', 'Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Override save to update product stock"""
        super().save(*args, **kwargs)
        if self.transaction_type == 'IN' or self.transaction_type == 'RET':
            self.product.current_stock += self.quantity
        elif self.transaction_type == 'OUT':
            self.product.current_stock -= self.quantity
        self.product.save()


class ProcurementOrder(TimestampMixin):
    """Procurement/Purchase Order model"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(default=timezone.now)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_orders')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-order_date']

    def calculate_total(self):
        """Calculate total order amount"""
        return sum(item.subtotal() for item in self.items.all())

    def save(self, *args, **kwargs):
        """Override save to update total and create notifications"""
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_instance = ProcurementOrder.objects.get(pk=self.pk)
                old_status = old_instance.status
            except ProcurementOrder.DoesNotExist:
                pass
        
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)
        
        # Create notifications using service
        from .services import NotificationService
        
        if is_new:
            # New order created - PR alert
            NotificationService.create_procurement_alert(self, alert_type='PR')
        elif old_status and old_status != self.status:
            # Status changed - PO alert
            NotificationService.create_procurement_alert(self, alert_type='PO')
            # If received, create invoice alert
            if self.status == 'RECEIVED':
                NotificationService.create_procurement_alert(self, alert_type='Invoice')

    def is_overdue(self):
        """Check if order is overdue"""
        if self.expected_delivery_date and self.status not in ['RECEIVED', 'CANCELLED']:
            return timezone.now() > self.expected_delivery_date
        return False


class ProcurementOrderItem(models.Model):
    """Procurement Order Line Items"""
    order = models.ForeignKey(ProcurementOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ['order', 'product']

    def subtotal(self):
        """Calculate line item subtotal"""
        return self.quantity * self.unit_price

    def is_fully_received(self):
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity


class Notification(TimestampMixin):
    """Notification model for system alerts"""
    NOTIFICATION_TYPES = [
        ('LOW_STOCK', 'Low Stock Alert'),
        ('ORDER_DUE', 'Order Due'),
        ('ORDER_OVERDUE', 'Order Overdue'),
        ('STOCK_PARITY', 'Stock Parity Issue'),
        ('SUPPLIER_RATING', 'Supplier Rating Update'),
        ('PR_ALERT', 'Purchase Request Alert'),
        ('PO_ALERT', 'Purchase Order Alert'),
        ('INVOICE_ALERT', 'Invoice Alert'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at', '-priority']

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


class StockParity(TimestampMixin):
    """Stock Parity model for tracking discrepancies"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parities')
    expected_quantity = models.IntegerField()
    actual_quantity = models.IntegerField()
    discrepancy = models.IntegerField()
    reason = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stock Parities"

    def save(self, *args, **kwargs):
        """Calculate discrepancy on save"""
        self.discrepancy = self.actual_quantity - self.expected_quantity
        super().save(*args, **kwargs)

    def resolve(self, user):
        """Resolve parity issue"""
        self.resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()


class SupplierEvaluation(TimestampMixin):
    """Supplier Evaluation model for tracking ratings and notes"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='evaluations')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    notes = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Supplier Evaluations"

    def __str__(self):
        return f"{self.supplier.name} - {self.rating}/5.0 - {self.created_at.strftime('%Y-%m-%d')}"

