from extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    wattage = db.Column(db.String(20), nullable=True)
    stock = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(500), nullable=True)
    features = db.Column(db.JSON, default=list)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'wattage': self.wattage,
            'stock': self.stock,
            'rating': self.rating,
            'image_path': self.image_path,
            'features': self.features,
            'provider_id': self.provider_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }
