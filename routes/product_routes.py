from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, UserRole
from models.product import Product
from models.order import Order, OrderItem
from services.cloudinary_service import upload_image, delete_image
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
product_bp = Blueprint('products', __name__)


@product_bp.route('', methods=['GET'])
def get_products():
    """Get all active products"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', None, type=str)

        query = Product.query.filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)

        products = query.paginate(page=page, per_page=per_page)

        return {
            'products': [p.to_dict() for p in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        }, 200
    except Exception as e:
        logger.exception('get_products failed')
        return {'error': 'Failed to load products'}, 500

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        product = Product.query.get(product_id)

        if not product or not product.is_active:
            return {'error': 'Product not found'}, 404

        return {'product': product.to_dict()}, 200
    except Exception as e:
        logger.exception('get_product failed')
        return {'error': 'Failed to load product'}, 500

@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create new product (provider only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or user.role not in (UserRole.PROVIDER, UserRole.ADMIN):
            return {'error': 'Only providers and admins can create products'}, 403

        name = request.form.get('name')
        price = request.form.get('price')
        if not name or not price:
            return {'error': 'Name and price are required'}, 400

        image_file = request.files.get('image')

        image_url = upload_image(image_file, folder='ray-solar/products')
        product = Product(
            name=name,
            category=request.form.get('category', ''),
            description=request.form.get('description', ''),
            price=float(price),
            wattage=request.form.get('wattage', ''),
            stock=int(request.form.get('stock', 0)),
            image_path=image_url,
            features=request.form.get('features', '[]'),
            provider_id=user_id
        )

        if isinstance(product.features, str):
            import json
            try:
                product.features = json.loads(product.features)
            except ValueError:
                product.features = []

        db.session.add(product)
        db.session.commit()

        return {'message': 'Product created', 'product': product.to_dict()}, 201
    except Exception as e:
        logger.exception('create_product failed')
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product (provider only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        product = Product.query.get(product_id)

        if not product:
            return {'error': 'Product not found'}, 404

        if product.provider_id != user_id and (not user or user.role != UserRole.ADMIN):
            return {'error': 'You can only update your own products'}, 403

        if request.form.get('name'):
            product.name = request.form['name']
        if request.form.get('price'):
            product.price = float(request.form['price'])
        if request.form.get('stock'):
            product.stock = int(request.form['stock'])
        if request.form.get('description'):
            product.description = request.form['description']
        if request.form.get('category'):
            product.category = request.form['category']
        if request.form.get('wattage'):
            product.wattage = request.form['wattage']
        if request.form.get('features'):
            import json
            try:
                product.features = json.loads(request.form['features'])
            except ValueError:
                product.features = []

        image_file = request.files.get('image')
        if image_file and image_file.filename:
            if product.image_path:
                delete_image(product.image_path)
            product.image_path = upload_image(image_file, folder='ray-solar/products')

        db.session.commit()

        return {'message': 'Product updated', 'product': product.to_dict()}, 200
    except Exception as e:
        logger.exception('update_product failed')
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete product (provider only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        product = Product.query.get(product_id)

        if not product:
            return {'error': 'Product not found'}, 404

        if product.provider_id != user_id and (not user or user.role != UserRole.ADMIN):
            return {'error': 'You can only delete your own products'}, 403

        if product.image_path:
            delete_image(product.image_path)
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted'}, 200
    except Exception as e:
        logger.exception('delete_product failed')
        db.session.rollback()
        return {'error': str(e)}, 500


@product_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_provider_analytics():
    """Get analytics for the current provider"""
    try:
        user_id = int(get_jwt_identity())

        products = Product.query.filter_by(provider_id=user_id).all()
        product_ids = [p.id for p in products]
        total_stock = sum(p.stock for p in products)
        total_value = sum(p.price * p.stock for p in products)

        today = datetime.utcnow().date()
        daily_data = []
        day_labels = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            order_count = db.session.query(Order).join(OrderItem).filter(
                OrderItem.product_id.in_(product_ids),
                Order.created_at >= day_start,
                Order.created_at <= day_end
            ).distinct().count()

            revenue = db.session.query(
                db.func.coalesce(db.func.sum(OrderItem.unit_price * OrderItem.quantity), 0)
            ).join(Order).filter(
                OrderItem.product_id.in_(product_ids),
                Order.created_at >= day_start,
                Order.created_at <= day_end,
                Order.status.in_(['confirmed', 'shipped', 'delivered'])
            ).scalar()

            day_labels.append(day.strftime('%a'))
            daily_data.append({'orders': order_count, 'revenue': float(revenue)})

        stock_rate = min(100, round((total_stock / (len(products) * 50)) * 100)) if products else 0

        return {
            'total_products': len(products),
            'total_stock': total_stock,
            'total_value': total_value,
            'stock_rate': stock_rate,
            'daily_data': daily_data,
            'day_labels': day_labels,
        }, 200
    except Exception as e:
        logger.exception('get_provider_analytics failed')
        return {'error': 'Failed to load analytics'}, 500
