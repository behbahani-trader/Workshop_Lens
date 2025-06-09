from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'لطفاً برای دسترسی به این صفحه وارد شوید.'

    # Import models
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.order import Order
    from app.models.lens_type import LensType
    from app.models.lens_cut_type import LensCutType
    from app.models.cashbox import CashBox, CashBoxTransaction
    from app.models.expense import Expense
    from app.models.partner import Partner, PartnerTransaction

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.customers import bp as customers_bp
    from app.routes.orders import bp as orders_bp
    from app.routes.lens_types import bp as lens_types_bp
    from app.routes.lens_cut_types import bp as lens_cut_types_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.docs import bp as docs_bp
    from app.routes.cashbox import bp as cashbox_bp
    from app.routes.expenses import bp as expenses_bp
    from app.routes.partners import bp as partners_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(lens_types_bp)
    app.register_blueprint(lens_cut_types_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(cashbox_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(partners_bp)

    # with app.app_context():
    #     from app.routes.orders import update_cancelled_orders
    #     update_cancelled_orders()

    return app 