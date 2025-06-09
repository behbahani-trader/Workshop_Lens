from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.customer import Customer
from app.models.order import Order
from app import db
from datetime import datetime

bp = Blueprint('customers', __name__)

@bp.route('/customers')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'date_desc')

    query = Customer.query
    if search:
        query = query.filter(
            (Customer.first_name.ilike(f'%{search}%')) |
            (Customer.last_name.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%')) |
            (Customer.email.ilike(f'%{search}%'))
        )

    # مرتب‌سازی
    if sort == 'name':
        query = query.order_by(Customer.first_name, Customer.last_name)
    elif sort == 'date_asc':
        query = query.order_by(Customer.created_at.asc())
    else:  # date_desc (پیش‌فرض)
        query = query.order_by(Customer.created_at.desc())

    customers = query.paginate(
        page=page, per_page=20, error_out=False
    )

    # محاسبه آمار امروز
    from sqlalchemy import func
    today = datetime.now().date()
    today_customers = Customer.query.filter(
        func.date(Customer.created_at) == today
    ).count()

    return render_template('customers/index.html',
                         customers=customers,
                         search=search,
                         sort=sort,
                         today_customers=today_customers)

@bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        # دریافت و پاک‌سازی داده‌ها
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        chat_id = request.form.get('chat_id', '').strip()
        is_vip = request.form.get('is_vip') == 'on'

        # تبدیل string های خالی به None
        phone = phone if phone else None
        email = email if email else None
        address = address if address else None
        chat_id = chat_id if chat_id else None

        # بررسی اجباری بودن فیلدها
        if not first_name or not last_name:
            flash('نام و نام خانوادگی اجباری است.', 'error')
            return render_template('customers/new.html')

        # بررسی تکراری نبودن ایمیل
        if email and Customer.query.filter_by(email=email).first():
            flash('این ایمیل قبلاً ثبت شده است.', 'error')
            return render_template('customers/new.html')

        # بررسی تکراری نبودن تلفن
        if phone and Customer.query.filter_by(phone=phone).first():
            flash('این شماره تلفن قبلاً ثبت شده است.', 'error')
            return render_template('customers/new.html')

        try:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                address=address,
                chat_id=chat_id,
                is_vip=is_vip
            )

            db.session.add(customer)
            db.session.commit()

            flash('مشتری جدید با موفقیت ثبت شد.', 'success')
            return redirect(url_for('customers.index'))

        except Exception as e:
            db.session.rollback()
            flash('خطا در ثبت مشتری. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('customers/new.html')

    return render_template('customers/new.html')

@bp.route('/customers/<int:id>')
@login_required
def show(id):
    customer = Customer.query.get_or_404(id)
    orders = Order.query.filter_by(customer_id=id).order_by(Order.created_at.desc()).all()
    return render_template('customers/show.html', customer=customer, orders=orders)

@bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)

    if request.method == 'POST':
        # دریافت و پاک‌سازی داده‌ها
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        chat_id = request.form.get('chat_id', '').strip()
        is_vip = request.form.get('is_vip') == 'on'

        # تبدیل string های خالی به None
        phone = phone if phone else None
        email = email if email else None
        address = address if address else None
        chat_id = chat_id if chat_id else None

        # بررسی اجباری بودن فیلدها
        if not first_name or not last_name:
            flash('نام و نام خانوادگی اجباری است.', 'error')
            return render_template('customers/edit.html', customer=customer)

        # بررسی تکراری نبودن ایمیل (غیر از خود مشتری)
        if email:
            existing_customer = Customer.query.filter_by(email=email).first()
            if existing_customer and existing_customer.id != customer.id:
                flash('این ایمیل قبلاً ثبت شده است.', 'error')
                return render_template('customers/edit.html', customer=customer)

        # بررسی تکراری نبودن تلفن (غیر از خود مشتری)
        if phone:
            existing_customer = Customer.query.filter_by(phone=phone).first()
            if existing_customer and existing_customer.id != customer.id:
                flash('این شماره تلفن قبلاً ثبت شده است.', 'error')
                return render_template('customers/edit.html', customer=customer)

        try:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.phone = phone
            customer.email = email
            customer.address = address
            customer.updated_at = datetime.now()
            customer.chat_id = chat_id
            customer.is_vip = is_vip

            db.session.commit()

            flash('اطلاعات مشتری با موفقیت بروزرسانی شد.', 'success')
            return redirect(url_for('customers.index'))

        except Exception:
            db.session.rollback()
            flash('خطا در بروزرسانی مشتری. لطفاً دوباره تلاش کنید.', 'error')
            return render_template('customers/edit.html', customer=customer)

    return render_template('customers/edit.html', customer=customer)

@bp.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    
    if Order.query.filter_by(customer_id=id).first():
        flash('این مشتری دارای سفارش است و نمی‌توان آن را حذف کرد.', 'error')
        return redirect(url_for('customers.show', id=id))
    
    db.session.delete(customer)
    db.session.commit()
    
    flash('مشتری با موفقیت حذف شد.', 'success')
    return redirect(url_for('customers.index'))

@bp.route('/customers/<int:id>/ledger')
@login_required
def ledger(id):
    customer = Customer.query.get_or_404(id)
    orders = Order.query.filter_by(customer_id=id).order_by(Order.created_at).all()
    # محاسبه مانده حساب و جمع پرداخت‌ها
    total_amount = sum(order.total_amount for order in orders)
    total_payment = sum(order.payment for order in orders)
    balance = total_amount - total_payment
    status = 'تسویه شده' if balance <= 0 else 'بدهکار'
    return render_template('customers/ledger.html', customer=customer, orders=orders, total_amount=total_amount, total_payment=total_payment, balance=balance, status=status)

@bp.route('/customers/ledger/select')
@login_required
def ledger_select():
    search = request.args.get('search', '')
    query = Customer.query
    if search:
        query = query.filter(
            (Customer.first_name.ilike(f'%{search}%')) |
            (Customer.last_name.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    customers = query.order_by(Customer.first_name).all()
    return render_template('customers/ledger_select.html', customers=customers, search=search) 