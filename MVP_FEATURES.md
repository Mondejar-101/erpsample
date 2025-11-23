# MVP Features Implementation

This document outlines all the MVP features that have been implemented in the ERP system.

## ✅ Completed Features

### 1. Stock Monitoring Dashboard & Parity (On-demand)

**Features:**
- ✅ View Low Stock Dashboard (on-demand) - `/stock/low-stock-dashboard/`
- ✅ View low stock suggestions (informational)
- ✅ Export Low Stock to PDF using jsPDF

**Implementation:**
- `LowStockDashboardView` - Displays low stock products with suggestions
- `StockMonitoringService` - Business logic for stock monitoring
- PDF export functionality using jsPDF library

### 2. Supplier Evaluation

**Features:**
- ✅ Add rating (0.0 - 5.0)
- ✅ Add evaluation notes (optional)
- ✅ View Supplier Evaluations/Scores
- ✅ Export Supplier Performance to PDF

**Implementation:**
- `SupplierEvaluation` model - Stores evaluations
- `SupplierEvaluationService` - Business logic for evaluations
- `SupplierEvaluationCreateView` - Form to add evaluations
- `SupplierEvaluationsView` - View all evaluations for a supplier
- Automatic rating calculation based on all evaluations

### 3. Procurement Reports

**Features:**
- ✅ View basic procurement report summaries
- ✅ Export Report to PDF

**Implementation:**
- `ProcurementReportService` - Business logic for reports
- Enhanced `ProcurementReportView` with export functionality
- PDF export with order summaries and top suppliers

### 4. Notifications (In-app only)

**Features:**
- ✅ View in-app notifications
- ✅ Mark notification read/dismiss
- ✅ Receive PR/PO/Invoice alerts

**Implementation:**
- `NotificationService` - Business logic for notifications
- Automatic PR alerts when purchase requests are created
- Automatic PO alerts when order status changes
- Automatic Invoice alerts when orders are received
- Notification list view with read/unread filtering

### 5. Reports & Dashboards

**Features:**
- ✅ View Dashboards (Pending Requests, Low Stock, Spend by Supplier, Flagged Requests)
- ✅ Export Dashboard Data to PDF

**Implementation:**
- `ReportsDashboardView` - Comprehensive dashboard
- `ReportExportService` - Business logic for report exports
- PDF export functionality for all dashboard data

## Architecture

### OOP Approach
- **Service Layer**: All business logic is in `erp_app/services.py` (not in views/controllers)
- **Models**: Use inheritance and mixins (TimestampMixin, BaseEntity)
- **Views**: Class-based views following OOP principles

### Database
- **PostgreSQL** configured (requires environment variables or settings update)
- Environment variables:
  - `DB_NAME` (default: 'erp_db')
  - `DB_USER` (default: 'postgres')
  - `DB_PASSWORD` (default: '')
  - `DB_HOST` (default: 'localhost')
  - `DB_PORT` (default: '5432')

### PDF Export
- Uses **jsPDF** library (currently via CDN)
- All exports are client-side (offline-capable)
- To make fully offline, download jsPDF and serve locally:
  ```bash
  # Download jsPDF
  curl -o static/jspdf.umd.min.js https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js
  ```
  Then update templates to use: `{% static 'jspdf.umd.min.js' %}`

## New URLs

- `/stock/low-stock-dashboard/` - Low Stock Dashboard
- `/suppliers/<id>/evaluate/` - Add Supplier Evaluation
- `/suppliers/<id>/evaluations/` - View Supplier Evaluations
- `/export/low-stock/` - Export Low Stock Data
- `/export/supplier-performance/` - Export Supplier Performance
- `/export/procurement-report/` - Export Procurement Report
- `/export/dashboard/` - Export Dashboard Data

## New Models

- `SupplierEvaluation` - Stores supplier ratings and evaluation notes

## New Services

- `StockMonitoringService` - Stock monitoring business logic
- `SupplierEvaluationService` - Supplier evaluation business logic
- `ProcurementReportService` - Procurement report business logic
- `NotificationService` - Notification business logic
- `ReportExportService` - Report export business logic

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure PostgreSQL:**
   - Install PostgreSQL
   - Create database: `CREATE DATABASE erp_db;`
   - Update environment variables or `settings.py` with database credentials

3. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## Notes

- All HTML templates extend `base.html` which loads `custom.css` - all templates use CSS properly
- Business rules are in services, not in views/controllers
- PDF exports use jsPDF (client-side, offline-capable)
- Notifications are created automatically for PR/PO/Invoice events

