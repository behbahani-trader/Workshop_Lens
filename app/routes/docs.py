from flask import Blueprint, render_template

bp = Blueprint('docs', __name__)

@bp.route('/docs')
def docs():
    return render_template('docs.html') 