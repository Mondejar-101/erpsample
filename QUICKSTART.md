# Quick Start Guide

## Initial Setup (First Time Only)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create database and apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser account:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the application:**
   - Main Dashboard: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Adding Sample Data

1. Log in to the admin panel: http://127.0.0.1:8000/admin/
2. Use your superuser credentials
3. Add data in this order:
   - **Categories**: Create product categories
   - **Suppliers**: Add supplier information
   - **Products**: Add products with categories
   - **Procurement Orders**: Create purchase orders
   - **Stock Transactions**: Record stock movements

## Key Features to Test

1. **Dashboard**: View overview statistics
2. **Stock Monitoring**: Browse products, check stock levels
3. **Stock Parity**: View and resolve stock discrepancies
4. **Suppliers**: Review supplier performance and ratings
5. **Procurement**: View orders and reports
6. **Notifications**: Check system notifications
7. **Reports**: View analytics and reports

## Default Login

After creating a superuser, you can:
- Access the admin panel with your superuser credentials
- All views require login (use your superuser account)

## Troubleshooting

- **Migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`
- **Static files not loading**: Run `python manage.py collectstatic` (for production)
- **Database errors**: Delete `db.sqlite3` and run migrations again

