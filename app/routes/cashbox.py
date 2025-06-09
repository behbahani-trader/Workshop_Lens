from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.models.cashbox import CashBox, CashBoxTransaction
from app.models.order import Order
from app.models.customer import Customer
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc

bp = Blueprint('cashbox', __name__)

@bp.route('/cashbox')
@login_required
def index():
    """صفحه اصلی صندوق مالی"""
    # دریافت یا ایجاد صندوق‌ها
    cashbox_main = CashBox.query.filter_by(name='اصلی').first()
    if not cashbox_main:
        cashbox_main = CashBox(name='اصلی', balance=0.0)
        db.session.add(cashbox_main)

    cashbox_a = CashBox.query.filter_by(name='A').first()
    if not cashbox_a:
        cashbox_a = CashBox(name='A', balance=0.0)
        db.session.add(cashbox_a)

    cashbox_b = CashBox.query.filter_by(name='B').first()
    if not cashbox_b:
        cashbox_b = CashBox(name='B', balance=0.0)
        db.session.add(cashbox_b)
    
    db.session.commit()
    
    # آمار امروز
    today = datetime.now().date()
    today_income_main = db.session.query(func.sum(CashBoxTransaction.amount))\
        .filter(CashBoxTransaction.cashbox_id == cashbox_main.id,
                CashBoxTransaction.transaction_type == 'income',
                func.date(CashBoxTransaction.created_at) == today)\
        .scalar() or 0

    today_income_a = db.session.query(func.sum(CashBoxTransaction.amount))\
        .filter(CashBoxTransaction.cashbox_id == cashbox_a.id,
                CashBoxTransaction.transaction_type == 'income',
                func.date(CashBoxTransaction.created_at) == today)\
        .scalar() or 0

    today_income_b = db.session.query(func.sum(CashBoxTransaction.amount))\
        .filter(CashBoxTransaction.cashbox_id == cashbox_b.id,
                CashBoxTransaction.transaction_type == 'income',
                func.date(CashBoxTransaction.created_at) == today)\
        .scalar() or 0
    
    # آخرین تراکنش‌ها
    recent_transactions_main = CashBoxTransaction.query\
        .filter_by(cashbox_id=cashbox_main.id)\
        .order_by(desc(CashBoxTransaction.created_at))\
        .limit(10).all()

    recent_transactions_a = CashBoxTransaction.query\
        .filter_by(cashbox_id=cashbox_a.id)\
        .order_by(desc(CashBoxTransaction.created_at))\
        .limit(10).all()

    recent_transactions_b = CashBoxTransaction.query\
        .filter_by(cashbox_id=cashbox_b.id)\
        .order_by(desc(CashBoxTransaction.created_at))\
        .limit(10).all()
    
    return render_template('cashbox/index.html',
                         cashbox_main=cashbox_main,
                         cashbox_a=cashbox_a,
                         cashbox_b=cashbox_b,
                         today_income_main=today_income_main,
                         today_income_a=today_income_a,
                         today_income_b=today_income_b,
                         recent_transactions_main=recent_transactions_main,
                         recent_transactions_a=recent_transactions_a,
                         recent_transactions_b=recent_transactions_b)

@bp.route('/cashbox/<cashbox_name>')
@login_required
def detail(cashbox_name):
    """جزئیات صندوق مالی"""
    if cashbox_name not in ['اصلی', 'A', 'B']:
        flash('صندوق مالی نامعتبر است.', 'error')
        return redirect(url_for('cashbox.index'))
    
    cashbox = CashBox.query.filter_by(name=cashbox_name).first_or_404()
    
    # فیلتر تاریخ
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = CashBoxTransaction.query.filter_by(cashbox_id=cashbox.id)
    
    if date_from:
        query = query.filter(CashBoxTransaction.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(CashBoxTransaction.created_at <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    transactions = query.order_by(desc(CashBoxTransaction.created_at)).all()
    
    # محاسبه آمار
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    return render_template('cashbox/detail.html',
                         cashbox=cashbox,
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         date_from=date_from,
                         date_to=date_to)

@bp.route('/cashbox/invoice/<cashbox_name>')
@login_required
def invoice(cashbox_name):
    """فاکتور صندوق مالی"""
    if cashbox_name not in ['اصلی', 'A', 'B']:
        flash('صندوق مالی نامعتبر است.', 'error')
        return redirect(url_for('cashbox.index'))
    
    cashbox = CashBox.query.filter_by(name=cashbox_name).first_or_404()
    
    # فیلتر تاریخ
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        flash('لطفاً بازه تاریخی را انتخاب کنید.', 'error')
        return redirect(url_for('cashbox.detail', cashbox_name=cashbox_name))
    
    query = CashBoxTransaction.query.filter_by(cashbox_id=cashbox.id)
    query = query.filter(CashBoxTransaction.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    query = query.filter(CashBoxTransaction.created_at <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    transactions = query.order_by(CashBoxTransaction.created_at).all()
    
    # محاسبه آمار
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_amount = total_income - total_expense
    
    return render_template('cashbox/invoice.html',
                         cashbox=cashbox,
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         net_amount=net_amount,
                         date_from=date_from,
                         date_to=date_to)
