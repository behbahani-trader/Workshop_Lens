from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from app.models.order import Order
from app.models.customer import Customer
from app.models.lens_type import LensType
from app.models.lens_cut_type import LensCutType
from app.models.order_lens import OrderLens
from app import db
from datetime import datetime, timedelta
import os
import json
from sqlalchemy import inspect

bp = Blueprint('reports', __name__)

# Create necessary directories
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'exports')
BACKUPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'backups')

# Ensure directories exist
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

@bp.route('/reports')
@login_required
def index():
    from sqlalchemy import func

    # آمار کلی
    total_orders = Order.query.count()
    total_customers = Customer.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0

    # آمار امروز
    today = datetime.now().date()
    today_orders = Order.query.filter(
        func.date(Order.created_at) == today
    ).count()

    # داده‌های نمودار سفارشات روزانه (7 روز اخیر)
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    daily_labels = [d.strftime('%m/%d') for d in days]
    daily_data = []

    for day in days:
        count = Order.query.filter(
            func.date(Order.created_at) == day
        ).count()
        daily_data.append(count)

    # داده‌های نمودار درآمد ماهانه (6 ماه اخیر)
    monthly_labels = []
    monthly_revenue = []

    for i in range(5, -1, -1):
        month_start = datetime.now().replace(day=1) - timedelta(days=i*30)
        month_start = month_start.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= month_start,
            Order.created_at <= month_end
        ).scalar() or 0

        monthly_labels.append(month_start.strftime('%Y/%m'))
        monthly_revenue.append(int(revenue))

    # داده‌های نمودار وضعیت سفارشات
    status_labels = ['در حال انجام', 'تکمیل شده', 'در انتظار', 'لغو شده']
    status_data = []
    status_mapping = {
        'in_progress': 'در حال انجام',
        'completed': 'تکمیل شده',
        'pending': 'در انتظار',
        'cancelled': 'لغو شده'
    }

    for status in ['in_progress', 'completed', 'pending', 'cancelled']:
        count = Order.query.filter_by(status=status).count()
        status_data.append(count)

    # داده‌های نمودار محبوب‌ترین عدسی‌ها
    lens_stats = db.session.query(
        LensType.name,
        func.count(OrderLens.id).label('count')
    ).join(OrderLens).group_by(LensType.id).order_by(func.count(OrderLens.id).desc()).limit(5).all()

    lens_labels = [stat[0] for stat in lens_stats]
    lens_data = [stat[1] for stat in lens_stats]

    return render_template('reports/index.html',
                         total_orders=total_orders,
                         total_customers=total_customers,
                         total_revenue=int(total_revenue),
                         today_orders=today_orders,
                         daily_labels=daily_labels,
                         daily_data=daily_data,
                         monthly_labels=monthly_labels,
                         monthly_revenue=monthly_revenue,
                         status_labels=status_labels,
                         status_data=status_data,
                         lens_labels=lens_labels,
                         lens_data=lens_data)

@bp.route('/reports/export/<type>')
@login_required
def export(type):
    try:
        import pandas as pd
    except ImportError:
        flash('برای خروجی اکسل، کتابخانه pandas نیاز است.', 'error')
        return redirect(url_for('reports.index'))

    if type == 'orders':
        data = Order.query.all()
        df = pd.DataFrame([{
            'شماره سفارش': order.order_number,
            'مشتری': order.customer.full_name if order.customer else 'نامشخص',
            'تاریخ ثبت': order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
            'وضعیت': order.status_display,
            'مبلغ کل': order.total_amount,
            'پیش پرداخت': order.payment,
            'باقی مانده': order.total_amount - (order.payment or 0),
            'تعداد عدسی': len(order.lenses),
            'توضیحات': order.notes or ''
        } for order in data])

    elif type == 'customers':
        data = Customer.query.all()
        df = pd.DataFrame([{
            'نام': customer.first_name,
            'نام خانوادگی': customer.last_name,
            'نام کامل': customer.full_name,
            'تلفن': customer.phone or '',
            'ایمیل': customer.email or '',
            'آدرس': customer.address or '',
            'Chat ID تلگرام': customer.chat_id or '',
            'تاریخ ثبت': customer.created_at.strftime('%Y-%m-%d') if customer.created_at else '',
            'تعداد سفارشات': len(customer.orders),
            'مجموع خرید': sum(order.total_amount for order in customer.orders)
        } for customer in data])

    elif type == 'financial':
        data = Order.query.all()
        df = pd.DataFrame([{
            'شماره سفارش': order.order_number,
            'مشتری': order.customer.full_name if order.customer else 'نامشخص',
            'تاریخ': order.created_at.strftime('%Y-%m-%d') if order.created_at else '',
            'مبلغ کل': order.total_amount,
            'پیش پرداخت': order.payment or 0,
            'باقی مانده': order.total_amount - (order.payment or 0),
            'وضعیت پرداخت': 'تسویه شده' if (order.total_amount - (order.payment or 0)) <= 0 else 'بدهکار',
            'وضعیت سفارش': order.status_display
        } for order in data])

    elif type == 'lens_types':
        data = LensType.query.all()
        df = pd.DataFrame([{
            'نام': lens_type.name,
            'قیمت پیش‌فرض': lens_type.default_price,
            'توضیحات': lens_type.description or '',
            'تعداد استفاده': len(lens_type.order_lenses),
            'درآمد کل': sum(ol.quantity * ol.price for ol in lens_type.order_lenses)
        } for lens_type in data])

    elif type == 'lens_cut_types':
        data = LensCutType.query.all()
        df = pd.DataFrame([{
            'نام': cut_type.name,
            'قیمت پیش‌فرض': cut_type.default_price,
            'توضیحات': cut_type.description or '',
            'تعداد استفاده': len(cut_type.order_lenses),
            'درآمد کل': sum(ol.quantity * ol.price for ol in cut_type.order_lenses)
        } for cut_type in data])

    elif type == 'performance':
        # گزارش عملکرد ماهانه
        from sqlalchemy import func
        monthly_stats = []

        for i in range(12, 0, -1):
            month_start = datetime.now().replace(day=1) - timedelta(days=i*30)
            month_start = month_start.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            orders_count = Order.query.filter(
                Order.created_at >= month_start,
                Order.created_at <= month_end
            ).count()

            revenue = db.session.query(func.sum(Order.total_amount)).filter(
                Order.created_at >= month_start,
                Order.created_at <= month_end
            ).scalar() or 0

            new_customers = Customer.query.filter(
                Customer.created_at >= month_start,
                Customer.created_at <= month_end
            ).count()

            monthly_stats.append({
                'ماه': month_start.strftime('%Y-%m'),
                'تعداد سفارشات': orders_count,
                'درآمد': int(revenue),
                'مشتریان جدید': new_customers,
                'میانگین سفارش': int(revenue / orders_count) if orders_count > 0 else 0
            })

        df = pd.DataFrame(monthly_stats)

    else:
        flash('نوع گزارش نامعتبر است.', 'error')
        return redirect(url_for('reports.index'))

    format = request.args.get('format', 'excel')
    if format == 'excel':
        filename = f'{type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = os.path.join(EXPORTS_DIR, filename)
        df.to_excel(filepath, index=False)
        return send_file(filepath, as_attachment=True)
    elif format == 'pdf':
        flash('خروجی PDF در حال توسعه است.', 'info')
        return redirect(url_for('reports.index'))
    else:
        flash('فرمت خروجی نامعتبر است.', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/reports/backup')
@login_required
def backup():
    try:
        # Get all models
        models = [Order, Customer, LensType, LensCutType, OrderLens]
        
        # Create backup data
        backup_data = {}
        for model in models:
            data = model.query.all()
            backup_data[model.__name__] = [{
                column.key: getattr(item, column.key)
                for column in inspect(model).columns
            } for item in data]

        # Save backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUPS_DIR, f'backup_{timestamp}.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=datetime_handler)

        flash('پشتیبان با موفقیت ایجاد شد.', 'success')
        return send_file(backup_file, as_attachment=True)
    except Exception as e:
        flash(f'خطا در ایجاد پشتیبان: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/reports/restore', methods=['POST'])
@login_required
def restore():
    if 'backup_file' not in request.files:
        flash('فایل پشتیبان انتخاب نشده است.', 'error')
        return redirect(url_for('reports.index'))

    file = request.files['backup_file']
    if file.filename == '':
        flash('فایل پشتیبان انتخاب نشده است.', 'error')
        return redirect(url_for('reports.index'))

    try:
        # Read backup data
        backup_data = json.load(file)

        # Restore data for each model
        models = {
            'Order': Order,
            'Customer': Customer,
            'LensType': LensType,
            'LensCutType': LensCutType,
            'OrderLens': OrderLens
        }

        # ترتیب بازیابی داده‌ها برای حفظ یکپارچگی
        restore_order = ['Customer', 'LensType', 'LensCutType', 'Order', 'OrderLens']

        for model_name in restore_order:
            if model_name in backup_data and model_name in models:
                model = models[model_name]
                # Clear existing data
                model.query.delete()
                
                # Insert backup data
                for item_data in backup_data[model_name]:
                    # Convert ISO format dates back to datetime
                    for key, value in item_data.items():
                        if isinstance(value, str) and key.endswith('_at'):
                            try:
                                item_data[key] = datetime.fromisoformat(value)
                            except ValueError:
                                pass
                    item = model(**item_data)
                    db.session.add(item)

        db.session.commit()
        flash('بازیابی پشتیبان با موفقیت انجام شد.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در بازیابی پشتیبان: {str(e)}', 'error')

    return redirect(url_for('reports.index'))

@bp.route('/reports/daily-orders')
@login_required
def daily_orders_chart():
    # محاسبه تعداد سفارشات هر روز در 7 روز اخیر
    today = datetime.today().date()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    days_str = [d.strftime('%Y-%m-%d') for d in days]
    orders_per_day = {d: 0 for d in days_str}
    orders = Order.query.filter(Order.created_at >= days[0]).all()
    for order in orders:
        day = order.created_at.strftime('%Y-%m-%d')
        if day in orders_per_day:
            orders_per_day[day] += 1
    return render_template('reports/daily_orders_chart.html', days=list(orders_per_day.keys()), counts=list(orders_per_day.values())) 