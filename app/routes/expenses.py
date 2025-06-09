from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.expense import Expense
from app.models.cashbox import CashBox, CashBoxTransaction
from app import db
from datetime import datetime

bp = Blueprint('expenses', __name__)

@bp.route('/expenses')
@login_required
def index():
    """لیست هزینه‌ها"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Expense.query
    if search:
        query = query.filter(Expense.title.ilike(f'%{search}%'))
    
    expenses = query.order_by(Expense.expense_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # محاسبه مجموع هزینه‌ها
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    return render_template('expenses/index.html', 
                         expenses=expenses, 
                         search=search,
                         total_expenses=total_expenses)

@bp.route('/expenses/new', methods=['GET', 'POST'])
@login_required
def new():
    """ثبت هزینه جدید"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        expense_date = request.form.get('expense_date', '')
        
        # اعتبارسنجی
        if not title:
            flash('عنوان هزینه اجباری است.', 'error')
            return render_template('expenses/new.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('مبلغ هزینه باید بیشتر از صفر باشد.', 'error')
                return render_template('expenses/new.html')
        except (ValueError, TypeError):
            flash('مبلغ هزینه نامعتبر است.', 'error')
            return render_template('expenses/new.html')
        
        try:
            if expense_date:
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d')
            else:
                expense_date = datetime.now()
        except ValueError:
            flash('تاریخ نامعتبر است.', 'error')
            return render_template('expenses/new.html')
        
        try:
            # ثبت هزینه
            expense = Expense(
                title=title,
                amount=amount,
                description=description,
                expense_date=expense_date
            )
            db.session.add(expense)
            db.session.flush()  # برای دریافت ID
            
            # کسر از صندوق اصلی
            cashbox_main = CashBox.query.filter_by(name='اصلی').first()
            if not cashbox_main:
                cashbox_main = CashBox(name='اصلی', balance=0.0)
                db.session.add(cashbox_main)
                db.session.flush()

            # بروزرسانی موجودی صندوق اصلی
            cashbox_main.balance -= amount

            # ثبت تراکنش در صندوق اصلی
            transaction = CashBoxTransaction(
                cashbox_id=cashbox_main.id,
                amount=amount,
                transaction_type='expense',
                description=f'هزینه: {title}',
                reference_type='expense',
                reference_id=expense.id
            )
            db.session.add(transaction)
            
            db.session.commit()
            
            flash('هزینه با موفقیت ثبت شد و از صندوق اصلی کسر گردید.', 'success')
            return redirect(url_for('expenses.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('خطا در ثبت هزینه. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('expenses/new.html')
    
    return render_template('expenses/new.html')

@bp.route('/expenses/<int:id>')
@login_required
def show(id):
    """نمایش جزئیات هزینه"""
    expense = Expense.query.get_or_404(id)
    return render_template('expenses/show.html', expense=expense)

@bp.route('/expenses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """ویرایش هزینه"""
    expense = Expense.query.get_or_404(id)
    old_amount = expense.amount
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        expense_date = request.form.get('expense_date', '')
        
        # اعتبارسنجی
        if not title:
            flash('عنوان هزینه اجباری است.', 'error')
            return render_template('expenses/edit.html', expense=expense)
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('مبلغ هزینه باید بیشتر از صفر باشد.', 'error')
                return render_template('expenses/edit.html', expense=expense)
        except (ValueError, TypeError):
            flash('مبلغ هزینه نامعتبر است.', 'error')
            return render_template('expenses/edit.html', expense=expense)
        
        try:
            if expense_date:
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d')
            else:
                expense_date = expense.expense_date
        except ValueError:
            flash('تاریخ نامعتبر است.', 'error')
            return render_template('expenses/edit.html', expense=expense)
        
        try:
            # بروزرسانی هزینه
            expense.title = title
            expense.amount = amount
            expense.description = description
            expense.expense_date = expense_date
            expense.updated_at = datetime.now()
            
            # تصحیح موجودی صندوق اصلی
            cashbox_main = CashBox.query.filter_by(name='اصلی').first()
            if cashbox_main:
                # برگرداندن مبلغ قبلی و کسر مبلغ جدید
                cashbox_main.balance += old_amount - amount

                # ثبت تراکنش تصحیح
                if old_amount != amount:
                    transaction = CashBoxTransaction(
                        cashbox_id=cashbox_main.id,
                        amount=abs(old_amount - amount),
                        transaction_type='income' if old_amount > amount else 'expense',
                        description=f'تصحیح هزینه: {title}',
                        reference_type='expense',
                        reference_id=expense.id
                    )
                    db.session.add(transaction)
            
            db.session.commit()
            
            flash('هزینه با موفقیت بروزرسانی شد.', 'success')
            return redirect(url_for('expenses.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('خطا در بروزرسانی هزینه. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('expenses/edit.html', expense=expense)
    
    return render_template('expenses/edit.html', expense=expense)

@bp.route('/expenses/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف هزینه"""
    expense = Expense.query.get_or_404(id)
    
    try:
        # برگرداندن مبلغ به صندوق اصلی
        cashbox_main = CashBox.query.filter_by(name='اصلی').first()
        if cashbox_main:
            cashbox_main.balance += expense.amount

            # ثبت تراکنش برگشت
            transaction = CashBoxTransaction(
                cashbox_id=cashbox_main.id,
                amount=expense.amount,
                transaction_type='income',
                description=f'حذف هزینه: {expense.title}',
                reference_type='expense',
                reference_id=expense.id
            )
            db.session.add(transaction)
        
        # حذف تراکنش‌های مرتبط
        CashBoxTransaction.query.filter_by(
            reference_type='expense',
            reference_id=expense.id
        ).delete()
        
        db.session.delete(expense)
        db.session.commit()
        
        flash('هزینه با موفقیت حذف شد و مبلغ به صندوق اصلی برگردانده شد.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('خطا در حذف هزینه. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('expenses.index'))
