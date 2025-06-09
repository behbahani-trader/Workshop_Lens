from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.partner import Partner, PartnerTransaction
from app import db
from datetime import datetime

bp = Blueprint('partners', __name__)

@bp.route('/partners')
@login_required
def index():
    """لیست شرکا"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Partner.query
    if search:
        query = query.filter(Partner.name.ilike(f'%{search}%'))
    
    partners = query.order_by(Partner.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('partners/index.html', partners=partners, search=search)

@bp.route('/partners/new', methods=['GET', 'POST'])
@login_required
def new():
    """ثبت شریک جدید"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # اعتبارسنجی
        if not name:
            flash('نام شریک اجباری است.', 'error')
            return render_template('partners/new.html')
        
        # بررسی تکراری نبودن نام
        if Partner.query.filter_by(name=name).first():
            flash('این نام قبلاً ثبت شده است.', 'error')
            return render_template('partners/new.html')
        
        try:
            partner = Partner(
                name=name,
                phone=phone if phone else None,
                email=email if email else None,
                notes=notes if notes else None
            )
            
            db.session.add(partner)
            db.session.commit()
            
            flash('شریک جدید با موفقیت ثبت شد.', 'success')
            return redirect(url_for('partners.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('خطا در ثبت شریک. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('partners/new.html')
    
    return render_template('partners/new.html')

@bp.route('/partners/<int:id>')
@login_required
def show(id):
    """نمایش جزئیات شریک"""
    partner = Partner.query.get_or_404(id)
    transactions = PartnerTransaction.query.filter_by(partner_id=id)\
        .order_by(PartnerTransaction.transaction_date.desc()).all()
    
    # محاسبه آمار
    total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
    total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
    balance = total_deposits - total_withdrawals
    
    return render_template('partners/show.html', 
                         partner=partner, 
                         transactions=transactions,
                         total_deposits=total_deposits,
                         total_withdrawals=total_withdrawals,
                         balance=balance)

@bp.route('/partners/<int:id>/transaction', methods=['GET', 'POST'])
@login_required
def add_transaction(id):
    """افزودن تراکنش برای شریک"""
    partner = Partner.query.get_or_404(id)
    
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        transaction_date = request.form.get('transaction_date', '')
        
        # اعتبارسنجی
        if transaction_type not in ['deposit', 'withdrawal']:
            flash('نوع تراکنش نامعتبر است.', 'error')
            return render_template('partners/add_transaction.html', partner=partner)
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('مبلغ باید بیشتر از صفر باشد.', 'error')
                return render_template('partners/add_transaction.html', partner=partner)
        except (ValueError, TypeError):
            flash('مبلغ نامعتبر است.', 'error')
            return render_template('partners/add_transaction.html', partner=partner)
        
        try:
            if transaction_date:
                transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d')
            else:
                transaction_date = datetime.now()
        except ValueError:
            flash('تاریخ نامعتبر است.', 'error')
            return render_template('partners/add_transaction.html', partner=partner)
        
        try:
            transaction = PartnerTransaction(
                partner_id=partner.id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                transaction_date=transaction_date
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            transaction_type_fa = 'واریز' if transaction_type == 'deposit' else 'برداشت'
            flash(f'{transaction_type_fa} با موفقیت ثبت شد.', 'success')
            return redirect(url_for('partners.show', id=partner.id))
            
        except Exception as e:
            db.session.rollback()
            flash('خطا در ثبت تراکنش. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('partners/add_transaction.html', partner=partner)
    
    return render_template('partners/add_transaction.html', partner=partner)

@bp.route('/partners/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """ویرایش شریک"""
    partner = Partner.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # اعتبارسنجی
        if not name:
            flash('نام شریک اجباری است.', 'error')
            return render_template('partners/edit.html', partner=partner)
        
        # بررسی تکراری نبودن نام (غیر از خود شریک)
        existing_partner = Partner.query.filter_by(name=name).first()
        if existing_partner and existing_partner.id != partner.id:
            flash('این نام قبلاً ثبت شده است.', 'error')
            return render_template('partners/edit.html', partner=partner)
        
        try:
            partner.name = name
            partner.phone = phone if phone else None
            partner.email = email if email else None
            partner.notes = notes if notes else None
            partner.updated_at = datetime.now()
            
            db.session.commit()
            
            flash('اطلاعات شریک با موفقیت بروزرسانی شد.', 'success')
            return redirect(url_for('partners.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('خطا در بروزرسانی شریک. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('partners/edit.html', partner=partner)
    
    return render_template('partners/edit.html', partner=partner)

@bp.route('/partners/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف شریک"""
    partner = Partner.query.get_or_404(id)
    
    # بررسی وجود تراکنش
    if PartnerTransaction.query.filter_by(partner_id=id).first():
        flash('این شریک دارای تراکنش است و نمی‌توان آن را حذف کرد.', 'error')
        return redirect(url_for('partners.show', id=id))
    
    try:
        db.session.delete(partner)
        db.session.commit()
        
        flash('شریک با موفقیت حذف شد.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('خطا در حذف شریک. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('partners.index'))

@bp.route('/partners/report')
@login_required
def report():
    """گزارش شرکا"""
    partners = Partner.query.order_by(Partner.name).all()
    
    # محاسبه آمار کلی
    total_partners = len(partners)
    total_balance = sum(partner.balance for partner in partners)
    positive_balance_partners = len([p for p in partners if p.balance > 0])
    negative_balance_partners = len([p for p in partners if p.balance < 0])
    
    return render_template('partners/report.html',
                         partners=partners,
                         total_partners=total_partners,
                         total_balance=total_balance,
                         positive_balance_partners=positive_balance_partners,
                         negative_balance_partners=negative_balance_partners)

@bp.route('/partners/<int:partner_id>/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(partner_id, transaction_id):
    """ویرایش تراکنش شریک"""
    partner = Partner.query.get_or_404(partner_id)
    transaction = PartnerTransaction.query.filter_by(
        id=transaction_id,
        partner_id=partner_id
    ).first_or_404()

    if request.method == 'POST':
        try:
            # دریافت داده‌های فرم
            old_amount = transaction.amount
            old_type = transaction.transaction_type

            new_amount = float(request.form.get('amount', 0))
            new_type = request.form.get('transaction_type')
            new_description = request.form.get('description', '').strip()

            if new_amount <= 0:
                flash('مبلغ باید بیشتر از صفر باشد.', 'error')
                return render_template('partners/edit_transaction.html',
                                     partner=partner, transaction=transaction)

            if new_type not in ['deposit', 'withdrawal']:
                flash('نوع تراکنش نامعتبر است.', 'error')
                return render_template('partners/edit_transaction.html',
                                     partner=partner, transaction=transaction)

            # محاسبه تأثیر تغییرات بر موجودی
            # ابتدا تأثیر تراکنش قبلی را برمی‌گردانیم
            if old_type == 'deposit':
                partner.balance -= old_amount
            else:  # withdrawal
                partner.balance += old_amount

            # سپس تأثیر تراکنش جدید را اعمال می‌کنیم
            if new_type == 'deposit':
                partner.balance += new_amount
            else:  # withdrawal
                partner.balance -= new_amount

            # بروزرسانی تراکنش
            transaction.amount = new_amount
            transaction.transaction_type = new_type
            transaction.description = new_description
            transaction.updated_at = datetime.now()

            db.session.commit()
            flash('تراکنش با موفقیت ویرایش شد.', 'success')
            return redirect(url_for('partners.show', id=partner_id))

        except ValueError:
            flash('مبلغ وارد شده نامعتبر است.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('خطا در ویرایش تراکنش.', 'error')

    return render_template('partners/edit_transaction.html',
                         partner=partner, transaction=transaction)

@bp.route('/partners/<int:partner_id>/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(partner_id, transaction_id):
    """حذف تراکنش شریک"""
    partner = Partner.query.get_or_404(partner_id)
    transaction = PartnerTransaction.query.filter_by(
        id=transaction_id,
        partner_id=partner_id
    ).first_or_404()

    try:
        # برگرداندن تأثیر تراکنش بر موجودی
        if transaction.transaction_type == 'deposit':
            partner.balance -= transaction.amount
        else:  # withdrawal
            partner.balance += transaction.amount

        # حذف تراکنش
        db.session.delete(transaction)
        db.session.commit()

        flash('تراکنش با موفقیت حذف شد.', 'success')

    except Exception as e:
        db.session.rollback()
        flash('خطا در حذف تراکنش.', 'error')

    return redirect(url_for('partners.show', id=partner_id))
