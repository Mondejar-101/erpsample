# ERP System - Minimum Viable Product (MVP)

A comprehensive Django-based ERP system with stock monitoring, supplier evaluation, procurement management, notifications, and reporting features.

## Features

### 1. Stock Monitoring Dashboard & Parity
- Real-time stock monitoring with low stock alerts
- Stock parity tracking to identify discrepancies
- Product details with transaction history
- Stock status indicators (In Stock, Low Stock, Out of Stock)

### 2. Supplier Evaluation
- Supplier performance metrics (rating, on-time delivery, quality score)
- Supplier detail pages with order history
- Performance status indicators (Excellent, Good, Average, Poor)
- Supplier ranking and comparison

### 3. Procurement Reports
- Procurement order management
- Order status tracking (Pending, Approved, Ordered, Received, Cancelled)
- Procurement analytics and reports
- Top suppliers by order value
- Orders by status breakdown

### 4. Notifications
- System-wide notification system
- Priority-based notifications (Low, Medium, High, Urgent)
- Notification types: Low Stock, Order Due, Order Overdue, Stock Parity, Supplier Rating
- Read/Unread notification management

### 5. Reports & Dashboards
- Comprehensive analytics dashboard
- Stock by category reports
- Supplier performance reports
- Low stock item alerts
- Recent activity tracking

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd erp
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
erp/
├── erp_project/          # Main project settings
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── erp_app/             # Main application
│   ├── models.py        # Database models (OOP-based)
│   ├── views.py         # Class-based views
│   ├── urls.py          # App URL configuration
│   └── admin.py         # Admin configuration
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   └── erp_app/         # App-specific templates
├── static/              # Static files (CSS, JS, images)
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## OOP Design Principles

The project follows Object-Oriented Programming principles:

1. **Abstract Base Classes**: `TimestampMixin` and `BaseEntity` provide reusable functionality
2. **Inheritance**: Models inherit from base classes to share common fields and methods
3. **Encapsulation**: Business logic is encapsulated within model methods
4. **Polymorphism**: Class-based views demonstrate polymorphic behavior
5. **Composition**: Models use relationships to compose complex data structures

### Key OOP Features:

- **Abstract Models**: `TimestampMixin` and `BaseEntity` are abstract base classes
- **Method Overriding**: Models override `save()` methods to add custom logic
- **Class Methods**: Models include business logic methods (e.g., `calculate_performance_score()`, `is_low_stock()`)
- **Class-Based Views**: All views use Django's class-based view system

## Usage

### Adding Sample Data

1. Access the admin panel at http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials
3. Add sample data:
   - Categories
   - Products
   - Suppliers
   - Procurement Orders
   - Stock Transactions

### Key Workflows

1. **Stock Management**: Monitor stock levels, view product details, track transactions
2. **Supplier Evaluation**: Review supplier performance, ratings, and order history
3. **Procurement**: Create and track purchase orders, view procurement reports
4. **Notifications**: View and manage system notifications
5. **Reports**: Access analytics and reports dashboard

## Features in Detail

### Stock Monitoring
- View all products with current stock levels
- Filter by stock status (All, Low Stock, Out of Stock)
- Search products by name or SKU
- View detailed product information with transaction history
- Track stock parity issues

### Supplier Evaluation
- View supplier list with performance metrics
- Detailed supplier pages with ratings and statistics
- Performance score calculation
- Order history per supplier

### Procurement Management
- Create and manage procurement orders
- Track order status and delivery dates
- View order details with line items
- Generate procurement reports

### Notifications
- System-generated notifications for important events
- Priority-based notification system
- Mark notifications as read/unread
- Filter by notification type

### Reports & Analytics
- Dashboard with key metrics
- Stock analytics by category
- Supplier performance reports
- Low stock alerts
- Recent activity tracking

## Development Notes

- The system uses SQLite by default for easy setup
- For production, consider switching to PostgreSQL or MySQL
- Authentication is required for all views (LoginRequiredMixin)
- The admin panel provides full CRUD operations for all models

## Future Enhancements

- User authentication and authorization
- Advanced reporting with charts and graphs
- Email notifications
- API endpoints for mobile apps
- Inventory forecasting
- Automated reorder suggestions
- Multi-warehouse support

## License

This is an MVP project for educational purposes.

## Support

For issues or questions, please refer to the Django documentation or create an issue in the project repository.

