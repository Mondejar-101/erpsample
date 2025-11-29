# ERP System - Minimum Viable Product (MVP)

A comprehensive Django-based ERP system with stock monitoring, supplier evaluation, procurement management, notifications, and reporting features.

## Features

### 1. Stock Monitoring Dashboard & Parity (On-demand)
- ✅ View Low Stock Dashboard (on-demand) - `/stock/low-stock-dashboard/`
- ✅ View low stock suggestions (informational)
- ✅ Export Low Stock to PDF
- Real-time stock monitoring with low stock alerts
- Stock parity tracking to identify discrepancies
- Product details with transaction history
- Stock status indicators (In Stock, Low Stock, Out of Stock)

### 2. Supplier Evaluation
- ✅ Add rating (0.0 - 5.0)
- ✅ Add evaluation notes (optional)
- ✅ View Supplier Evaluations/Scores
- ✅ Export Supplier Performance to PDF
- Supplier performance metrics (rating, on-time delivery, quality score)
- Supplier detail pages with order history
- Performance status indicators (Excellent, Good, Average, Poor)
- Supplier ranking and comparison

### 3. Procurement Reports
- ✅ View basic procurement report summaries
- ✅ Export Report to PDF
- Procurement order management
- Order status tracking (Pending, Approved, Ordered, Received, Cancelled)
- Procurement analytics and reports
- Top suppliers by order value
- Orders by status breakdown

### 4. Notifications (In-app only)
- ✅ View in-app notifications
- ✅ Mark notification read/dismiss
- ✅ Receive PR/PO/Invoice alerts
- System-wide notification system
- Priority-based notifications (Low, Medium, High, Urgent)
- Notification types: Low Stock, Order Due, Order Overdue, Stock Parity, Supplier Rating, PR/PO/Invoice Alerts
- Read/Unread notification management

### 5. Reports & Dashboards
- ✅ View Dashboards (Pending Requests, Low Stock, Spend by Supplier, Flagged Requests)
- ✅ Export Dashboard Data to PDF
- Comprehensive analytics dashboard
- Stock by category reports
- Supplier performance reports
- Low stock item alerts
- Recent activity tracking

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (configured, see setup instructions)
- **Frontend**: HTML, CSS, JavaScript (custom, no Bootstrap)
- **PDF Export**: jsPDF (client-side, offline-capable)
- **Architecture**: OOP with Service Layer pattern

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

4. **Configure PostgreSQL Database**
   - Install PostgreSQL if not already installed
   - Create database: `CREATE DATABASE erp_db;`
   - Set environment variables (optional):
     ```bash
     # Windows PowerShell
     $env:DB_NAME="erp_db"
     $env:DB_USER="postgres"
     $env:DB_PASSWORD="your_password"
     $env:DB_HOST="localhost"
     $env:DB_PORT="5432"
     
     # Linux/Mac
     export DB_NAME=erp_db
     export DB_USER=postgres
     export DB_PASSWORD=your_password
     export DB_HOST=localhost
     export DB_PORT=5432
     ```
   - Or update `erp_project/settings.py` directly with database credentials

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
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
│   ├── services.py      # Business logic services (OOP)
│   ├── forms.py         # Django forms
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
3. **Encapsulation**: Business logic is encapsulated in Service Layer (not in views/controllers)
4. **Polymorphism**: Class-based views demonstrate polymorphic behavior
5. **Composition**: Models use relationships to compose complex data structures

### Key OOP Features:

- **Abstract Models**: `TimestampMixin` and `BaseEntity` are abstract base classes
- **Service Layer**: All business logic is in `erp_app/services.py` (separated from views)
- **Method Overriding**: Models override `save()` methods to add custom logic
- **Class Methods**: Models include business logic methods (e.g., `calculate_performance_score()`, `is_low_stock()`)
- **Class-Based Views**: All views use Django's class-based view system

### Service Layer Architecture:

Business rules are NOT in Controllers/Views/API. All business logic is in:
- `StockMonitoringService` - Stock monitoring logic
- `SupplierEvaluationService` - Supplier evaluation logic
- `ProcurementReportService` - Procurement report logic
- `NotificationService` - Notification logic
- `ReportExportService` - Report export logic

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

- **Database**: PostgreSQL is configured (see setup instructions)
- **PDF Export**: Uses jsPDF library (client-side, offline-capable)
  - Currently uses CDN, can be downloaded for full offline use
  - See `MVP_FEATURES.md` for instructions
- **Business Logic**: All business rules are in Service Layer (`erp_app/services.py`)
- **Frontend**: Custom HTML/CSS/JS (no Bootstrap dependency)
- Authentication is required for all views (LoginRequiredMixin)
- The admin panel provides full CRUD operations for all models
- All HTML templates extend `base.html` which loads `custom.css` - all templates use CSS properly

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



