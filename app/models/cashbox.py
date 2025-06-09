from datetime import datetime
from app import db

class CashBox(db.Model):
    """مدل برای صندوق مالی A و B"""
    __tablename__ = 'cashboxes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 'A' یا 'B'
    balance = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    transactions = db.relationship('CashBoxTransaction', back_populates='cashbox', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CashBox {self.name}: {self.balance}>'

class CashBoxTransaction(db.Model):
    """مدل برای تراکنش‌های صندوق مالی"""
    __tablename__ = 'cashbox_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    cashbox_id = db.Column(db.Integer, db.ForeignKey('cashboxes.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income', 'expense', 'transfer'
    description = db.Column(db.Text)
    reference_type = db.Column(db.String(50))  # 'order', 'expense', 'partner_transaction'
    reference_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # روابط
    cashbox = db.relationship('CashBox', back_populates='transactions')
    
    def __repr__(self):
        return f'<CashBoxTransaction {self.id}: {self.amount}>'
