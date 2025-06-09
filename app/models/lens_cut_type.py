from app import db
from datetime import datetime

class LensCutType(db.Model):
    __tablename__ = 'lens_cut_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    default_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # رابطه با OrderLens
    order_lenses = db.relationship('OrderLens', back_populates='lens_cut_type')
    
    def __repr__(self):
        return f'<LensCutType {self.name}>' 