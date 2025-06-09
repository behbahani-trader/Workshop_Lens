from datetime import datetime
from app import db

class Payment(db.Model):
    """مدل برای ذخیره پرداختی‌های مشتری"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # روابط
    customer = db.relationship('Customer', back_populates='payments')
    
    def __repr__(self):
        return f'<Payment {self.id}>'