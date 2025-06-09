from app import db

class LensType(db.Model):
    __tablename__ = 'lens_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    default_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    order_lenses = db.relationship('OrderLens', back_populates='lens_type')
    
    def __repr__(self):
        return f'<LensType {self.name}>' 