from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.order import Order
from app.models.customer import Customer
from app.models.lens_type import LensType
from app.models.lens_cut_type import LensCutType
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.models.order_lens import OrderLens
from app import db
import os
from app.utils.date_utils import format_jalali
from collections import defaultdict
import calendar

bp = Blueprint('main', __name__)

TELEGRAM_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../utils/telegram_config.txt')

def save_telegram_config(token, message):
    with open(TELEGRAM_CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(token.strip() + '\n' + message.strip())

def load_telegram_config():
    if not os.path.exists(TELEGRAM_CONFIG_PATH):
        return '', 'سفارش شما آماده تحویل است.'
    with open(TELEGRAM_CONFIG_PATH, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        if len(lines) >= 2:
            return lines[0], '\n'.join(lines[1:])
        elif len(lines) == 1:
            return lines[0], 'سفارش شما آماده تحویل است.'
        return '', 'سفارش شما آماده تحویل است.'

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # آمار کلی
    # تعداد کل سفارشات = مجموع تعداد عدسی‌های تولید شده (هر عدسی = یک سفارش)
    total_orders = db.session.query(func.sum(OrderLens.quantity)).scalar() or 0
    total_customers = Customer.query.count()

    # سفارشات امروز = مجموع عدسی‌های تولید شده امروز
    today = datetime.now().date()
    today_orders = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(func.date(Order.created_at) == today)\
        .scalar() or 0

    # درآمد امروز
    today_revenue = Order.query.filter(
        func.date(Order.created_at) == today
    ).with_entities(func.sum(Order.total_amount)).scalar() or 0

    # سفارشات در انتظار (تعداد عدسی)
    pending_lenses = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(Order.status == 'pending')\
        .scalar() or 0

    # سفارشات در حال انجام
    in_progress_orders = Order.query.filter_by(status='in_progress').count()

    # آخرین سفارشات (بر اساس شماره سفارش - آخرین سفارش بالاتر)
    recent_orders = Order.query.order_by(Order.id.desc()).limit(8).all()

    # آمار هفته اخیر
    week_ago = datetime.now() - timedelta(days=7)
    week_orders = Order.query.filter(Order.created_at >= week_ago).count()
    week_revenue = Order.query.filter(Order.created_at >= week_ago)\
        .with_entities(func.sum(Order.total_amount)).scalar() or 0

    # مشتریان جدید این هفته
    new_customers_week = Customer.query.filter(Customer.created_at >= week_ago).count()

    return render_template('main/index.html',
                         total_orders=total_orders,
                         total_customers=total_customers,
                         today_orders=today_orders,
                         today_revenue=today_revenue,
                         pending_lenses=pending_lenses,
                         in_progress_orders=in_progress_orders,
                         recent_orders=recent_orders,
                         week_orders=week_orders,
                         week_revenue=week_revenue,
                         new_customers_week=new_customers_week)

@bp.route('/dashboard')
@login_required
def dashboard():
    # دریافت فیلتر زمانی از پارامترها
    period = request.args.get('period', '30')  # پیش‌فرض 30 روز

    # محاسبه بازه زمانی
    if period == '7':
        start_date = datetime.now() - timedelta(days=7)
        period_name = 'هفته اخیر'
    elif period == '30':
        start_date = datetime.now() - timedelta(days=30)
        period_name = 'ماه اخیر'
    elif period == '90':
        start_date = datetime.now() - timedelta(days=90)
        period_name = '3 ماه اخیر'
    elif period == '365':
        start_date = datetime.now() - timedelta(days=365)
        period_name = 'سال اخیر'
    else:
        start_date = datetime.now() - timedelta(days=30)
        period_name = 'ماه اخیر'

    # آمار کلی
    # تعداد کل سفارشات = مجموع تعداد عدسی‌های تولید شده (هر عدسی = یک سفارش)
    total_orders = db.session.query(func.sum(OrderLens.quantity)).scalar() or 0
    total_customers = Customer.query.count()

    # آمار دوره انتخابی
    # تعداد سفارشات دوره = مجموع عدسی‌های تولید شده در دوره
    period_orders = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(Order.created_at >= start_date)\
        .scalar() or 0
    period_revenue = Order.query.filter(Order.created_at >= start_date)\
        .with_entities(func.sum(Order.total_amount)).scalar() or 0

    # مشتریان جدید در دوره
    new_customers = Customer.query.filter(Customer.created_at >= start_date).count()

    # آمار امروز
    today = datetime.now().date()
    # سفارشات امروز = مجموع عدسی‌های تولید شده امروز
    today_orders = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(func.date(Order.created_at) == today)\
        .scalar() or 0
    today_revenue = Order.query.filter(func.date(Order.created_at) == today)\
        .with_entities(func.sum(Order.total_amount)).scalar() or 0

    # وضعیت سفارشات
    status_map = {
        'pending': {'name': 'در انتظار', 'color': 'warning'},
        'in_progress': {'name': 'در حال انجام', 'color': 'info'},
        'completed': {'name': 'تکمیل شده', 'color': 'success'},
        'cancelled': {'name': 'لغو شده', 'color': 'error'},
    }

    status_counts = Order.query.with_entities(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()

    total_orders_for_status = sum([row[1] for row in status_counts]) or 1
    order_status = []
    for row in status_counts:
        status = row[0]
        count = row[1]
        info = status_map.get(status, {'name': status, 'color': 'neutral'})
        percentage = (count / total_orders_for_status) * 100
        order_status.append({
            'name': info['name'],
            'color': info['color'],
            'count': count,
            'percentage': percentage
        })

    # آمار عدسی‌ها
    pending_lenses = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(Order.status == 'pending')\
        .scalar() or 0

    delivered_lenses = db.session.query(func.sum(OrderLens.quantity))\
        .join(OrderLens.order)\
        .filter(Order.status == 'completed')\
        .scalar() or 0

    # آخرین سفارشات (بر اساس شماره سفارش - آخرین سفارش بالاتر)
    recent_orders = Order.query.order_by(Order.id.desc()).limit(10).all()

    return render_template('main/dashboard.html',
                         total_orders=total_orders,
                         total_customers=total_customers,
                         period_orders=period_orders,
                         period_revenue=period_revenue,
                         new_customers=new_customers,
                         today_orders=today_orders,
                         today_revenue=today_revenue,
                         order_status=order_status,
                         pending_lenses=pending_lenses,
                         delivered_lenses=delivered_lenses,
                         recent_orders=recent_orders,
                         period=period,
                         period_name=period_name)

@bp.route('/whatsapp-settings', methods=['GET'])
@login_required
def whatsapp_settings():
    return render_template('main/whatsapp_settings.html')

@bp.route('/telegram-settings', methods=['GET', 'POST'])
@login_required
def telegram_settings():
    token, message = load_telegram_config()
    if request.method == 'POST':
        new_token = request.form.get('token', '').strip()
        new_message = request.form.get('message', '').strip()
        save_telegram_config(new_token, new_message)
        flash('تنظیمات تلگرام با موفقیت ذخیره شد.', 'success')
        return redirect(url_for('main.telegram_settings'))
    return render_template('main/telegram_settings.html', token=token, message=message)

# API endpoints برای نمودارها
@bp.route('/api/dashboard/daily-orders')
@login_required
def api_daily_orders():
    """API برای نمودار سفارشات روزانه"""
    days = int(request.args.get('days', 7))

    # محاسبه روزهای مورد نظر
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)

    # تولید لیست روزها
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    # دریافت تعداد سفارشات هر روز
    orders_data = {}
    revenue_data = {}

    for date in date_list:
        # تعداد سفارشات = مجموع عدسی‌های تولید شده در آن روز
        orders_count = db.session.query(func.sum(OrderLens.quantity))\
            .join(OrderLens.order)\
            .filter(func.date(Order.created_at) == date)\
            .scalar() or 0
        revenue = Order.query.filter(func.date(Order.created_at) == date)\
            .with_entities(func.sum(Order.total_amount)).scalar() or 0

        date_str = date.strftime('%Y-%m-%d')
        orders_data[date_str] = int(orders_count)
        revenue_data[date_str] = float(revenue)

    return jsonify({
        'labels': [date.strftime('%m/%d') for date in date_list],
        'orders': list(orders_data.values()),
        'revenue': list(revenue_data.values())
    })

@bp.route('/api/dashboard/status-chart')
@login_required
def api_status_chart():
    """API برای نمودار دایره‌ای وضعیت سفارشات"""
    status_map = {
        'pending': 'در انتظار',
        'in_progress': 'در حال انجام',
        'completed': 'تکمیل شده',
        'cancelled': 'لغو شده'
    }

    status_counts = Order.query.with_entities(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()

    labels = []
    data = []
    colors = []
    color_map = {
        'pending': '#f59e0b',
        'in_progress': '#3b82f6',
        'completed': '#10b981',
        'cancelled': '#ef4444'
    }

    for status, count in status_counts:
        labels.append(status_map.get(status, status))
        data.append(count)
        colors.append(color_map.get(status, '#6b7280'))

    return jsonify({
        'labels': labels,
        'data': data,
        'colors': colors
    })

@bp.route('/api/dashboard/popular-lenses')
@login_required
def api_popular_lenses():
    """API برای نمودار محبوب‌ترین عدسی‌ها"""
    # دریافت محبوب‌ترین عدسی‌ها بر اساس تعداد فروش
    popular_lenses = db.session.query(
        LensType.name,
        func.sum(OrderLens.quantity).label('total_quantity')
    ).join(OrderLens.lens_type)\
     .group_by(LensType.id, LensType.name)\
     .order_by(func.sum(OrderLens.quantity).desc())\
     .limit(10).all()

    labels = [lens.name for lens in popular_lenses]
    data = [int(lens.total_quantity) for lens in popular_lenses]

    return jsonify({
        'labels': labels,
        'data': data
    })

@bp.route('/api/dashboard/monthly-stats')
@login_required
def api_monthly_stats():
    """API برای آمار ماهانه"""
    months = int(request.args.get('months', 6))

    # محاسبه ماه‌های مورد نظر
    current_date = datetime.now()
    monthly_data = []

    for i in range(months):
        # محاسبه ماه
        month_date = current_date - timedelta(days=30*i)
        start_of_month = month_date.replace(day=1)

        if i == 0:
            end_of_month = current_date
        else:
            next_month = start_of_month.replace(month=start_of_month.month + 1) if start_of_month.month < 12 else start_of_month.replace(year=start_of_month.year + 1, month=1)
            end_of_month = next_month - timedelta(days=1)

        # آمار ماه
        # تعداد سفارشات = مجموع عدسی‌های تولید شده در ماه
        orders_count = db.session.query(func.sum(OrderLens.quantity))\
            .join(OrderLens.order)\
            .filter(
                Order.created_at >= start_of_month,
                Order.created_at <= end_of_month
            ).scalar() or 0

        revenue = Order.query.filter(
            Order.created_at >= start_of_month,
            Order.created_at <= end_of_month
        ).with_entities(func.sum(Order.total_amount)).scalar() or 0

        monthly_data.append({
            'month': month_date.strftime('%Y/%m'),
            'orders': orders_count,
            'revenue': float(revenue)
        })

    # معکوس کردن لیست تا ماه‌های قدیمی‌تر اول باشند
    monthly_data.reverse()

    return jsonify({
        'labels': [item['month'] for item in monthly_data],
        'orders': [item['orders'] for item in monthly_data],
        'revenue': [item['revenue'] for item in monthly_data]
    })

@bp.route('/api/dashboard/delivered-items')
@login_required
def api_delivered_items():
    """API برای نمودار ایتم‌های تحویل داده شده"""
    days = int(request.args.get('days', 7))

    # محاسبه روزهای مورد نظر
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)

    # تولید لیست روزها
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    # دریافت تعداد ایتم‌های تحویل شده هر روز
    delivered_data = {}
    pending_data = {}

    for date in date_list:
        # ایتم‌های تحویل شده (سفارشات completed)
        delivered_items = db.session.query(func.sum(OrderLens.quantity))\
            .join(OrderLens.order)\
            .filter(
                func.date(Order.created_at) == date,
                Order.status == 'completed'
            ).scalar() or 0

        # ایتم‌های در انتظار (سفارشات pending)
        pending_items = db.session.query(func.sum(OrderLens.quantity))\
            .join(OrderLens.order)\
            .filter(
                func.date(Order.created_at) == date,
                Order.status == 'pending'
            ).scalar() or 0

        date_str = date.strftime('%Y-%m-%d')
        delivered_data[date_str] = int(delivered_items)
        pending_data[date_str] = int(pending_items)

    return jsonify({
        'labels': [date.strftime('%m/%d') for date in date_list],
        'delivered': list(delivered_data.values()),
        'pending': list(pending_data.values())
    })

