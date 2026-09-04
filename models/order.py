from extensions import db
from datetime import datetime
from enum import Enum
from models.product import Product

class OrderStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

# class Order(db.Model):
#     __tablename__ = 'orders'
    
#     id = db.Column(db.Integer, primary_key=True)
#     order_number = db.Column(db.String(50), unique=True, nullable=False)
#     customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
#     total_amount = db.Column(db.Float, nullable=False)
#     shipping_address = db.Column(db.Text, nullable=True)
#     notes = db.Column(db.Text, nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'status': self.status.value,
            'total_amount': self.total_amount,
            'items': [item.to_dict() for item in self.order_items],
            'created_at': self.created_at.isoformat(),
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        """Convert order item to dictionary"""
        product = Product.query.get(self.product_id) if self.product_id else None
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': product.name if product else '',
            'product_image': product.image_path if product else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
        }
