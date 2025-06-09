from datetime import datetime
from app import db

class Partner(db.Model):
    """مدل برای شرکا"""
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    transactions = db.relationship('PartnerTransaction', back_populates='partner', cascade='all, delete-orphan')
    
    @property
    def balance(self):
        """محاسبه مانده حساب شریک"""
        total_deposits = sum(t.amount for t in self.transactions if t.transaction_type == 'deposit')
        total_withdrawals = sum(t.amount for t in self.transactions if t.transaction_type == 'withdrawal')
        return total_deposits - total_withdrawals
    
    def __repr__(self):
        return f'<Partner {self.name}>'

class PartnerTransaction(db.Model):
    """مدل برای تراکنش‌های شرکا"""
    __tablename__ = 'partner_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdrawal'
    description = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # روابط
    partner = db.relationship('Partner', back_populates='transactions')
    
    def __repr__(self):
        return f'<PartnerTransaction {self.id}: {self.amount}>'
