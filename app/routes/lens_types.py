from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.lens_type import LensType
from app.forms.lens_type import LensTypeForm
from app import db

bp = Blueprint('lens_types', __name__)

@bp.route('/lens-types')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = LensType.query
    if search:
        query = query.filter(LensType.name.ilike(f'%{search}%'))
    
    lens_types = query.order_by(LensType.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('lens_types/index.html', lens_types=lens_types, search=search)

@bp.route('/lens-types/new', methods=['GET', 'POST'])
@login_required
def new():
    form = LensTypeForm()
    if form.validate_on_submit():
        lens_type = LensType(
            name=form.name.data,
            description=form.description.data,
            default_price=form.default_price.data
        )
        db.session.add(lens_type)
        db.session.commit()
        flash('نوع عدسی با موفقیت ثبت شد.', 'success')
        return redirect(url_for('lens_types.index'))
    return render_template('lens_types/form.html', form=form)

@bp.route('/lens-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    lens_type = LensType.query.get_or_404(id)
    form = LensTypeForm(obj=lens_type)
    if form.validate_on_submit():
        lens_type.name = form.name.data
        lens_type.description = form.description.data
        lens_type.default_price = form.default_price.data
        db.session.commit()
        flash('نوع عدسی با موفقیت به‌روزرسانی شد.', 'success')
        return redirect(url_for('lens_types.index'))
    return render_template('lens_types/form.html', form=form, lens_type=lens_type)

@bp.route('/lens-types/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    lens_type = LensType.query.get_or_404(id)
    db.session.delete(lens_type)
    db.session.commit()
    flash('نوع عدسی با موفقیت حذف شد.', 'success')
    return redirect(url_for('lens_types.index')) 