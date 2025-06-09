from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.lens_cut_type import LensCutType
from app import db

bp = Blueprint('lens_cut_types', __name__)

@bp.route('/lens-cut-types')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = LensCutType.query
    if search:
        query = query.filter(LensCutType.name.ilike(f'%{search}%'))
    
    lens_cut_types = query.order_by(LensCutType.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('lens_cut_types/index.html', lens_cut_types=lens_cut_types, search=search)

@bp.route('/lens-cut-types/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        lens_cut_type = LensCutType(
            name=request.form.get('name'),
            description=request.form.get('description'),
            default_price=request.form.get('default_price')
        )
        
        db.session.add(lens_cut_type)
        db.session.commit()
        
        flash('نوع تراش جدید با موفقیت ثبت شد.', 'success')
        return redirect(url_for('lens_cut_types.index'))
    
    return render_template('lens_cut_types/new.html')

@bp.route('/lens-cut-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    lens_cut_type = LensCutType.query.get_or_404(id)
    
    if request.method == 'POST':
        lens_cut_type.name = request.form.get('name')
        lens_cut_type.description = request.form.get('description')
        lens_cut_type.default_price = request.form.get('default_price')
        
        db.session.commit()
        
        flash('اطلاعات نوع تراش با موفقیت بروزرسانی شد.', 'success')
        return redirect(url_for('lens_cut_types.index'))
    
    return render_template('lens_cut_types/edit.html', lens_cut_type=lens_cut_type)

@bp.route('/lens-cut-types/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    lens_cut_type = LensCutType.query.get_or_404(id)
    
    # بررسی اینکه آیا این نوع تراش در سفارشی استفاده شده است
    if lens_cut_type.orders.count() > 0:
        flash('این نوع تراش در سفارش‌ها استفاده شده و قابل حذف نیست.', 'error')
        return redirect(url_for('lens_cut_types.index'))
    
    db.session.delete(lens_cut_type)
    db.session.commit()
    
    flash('نوع تراش با موفقیت حذف شد.', 'success')
    return redirect(url_for('lens_cut_types.index')) 