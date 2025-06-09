from datetime import datetime
from app import db
from app.models.payment import Payment
from sqlalchemy import CheckConstraint

class Customer(db.Model):
    """مدل برای ذخیره اطلاعات مشتریان"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_vip = db.Column(db.Boolean, default=False, nullable=False)  # مشتری VIP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chat_id = db.Column(db.String(32))  # chat_id تلگرام
    
    # روابط
    orders = db.relationship('Order', back_populates='customer')
    payments = db.relationship('Payment', back_populates='customer', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def balance(self):
        total_orders = sum((order.total_amount or 0) for order in self.orders)
        total_payments = sum((payment.amount or 0) for payment in self.payments)
        total_prepayments = sum((order.payment or 0) for order in self.orders)
        return total_orders - total_payments - total_prepayments
    
    def __repr__(self):
        return f'<Customer {self.full_name}>' 