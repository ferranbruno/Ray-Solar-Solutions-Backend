from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.product import Product
from models.user import User, UserRole

product_bp = Blueprint('products', __name__)

@product_bp.route('', methods=['GET'])
def get_products():
    """Get all active products"""
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

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    product = Product.query.get(product_id)
    
    if not product or not product.is_active:
        return {'error': 'Product not found'}, 404
    
    return {'product': product.to_dict()}, 200

@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create new product (provider only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != UserRole.PROVIDER:
        return {'error': 'Only providers can create products'}, 403
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price'):
        return {'error': 'Name and price are required'}, 400
    
    try:
        product = Product(
            name=data['name'],
            category=data.get('category', ''),
            description=data.get('description', ''),
            price=data['price'],
            wattage=data.get('wattage', ''),
            stock=data.get('stock', 0),
            image_url=data.get('image_url', ''),
            features=data.get('features', []),
            provider_id=user_id
        )
        
        db.session.add(product)
        db.session.commit()
        
        return {'message': 'Product created', 'product': product.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product (provider only)"""
    user_id = get_jwt_identity()
    product = Product.query.get(product_id)
    
    if not product:
        return {'error': 'Product not found'}, 404
    
    if product.provider_id != user_id:
        return {'error': 'You can only update your own products'}, 403
    
    data = request.get_json()
    
    try:
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.stock = data.get('stock', product.stock)
        product.description = data.get('description', product.description)
        product.image_url = data.get('image_url', product.image_url)
        product.features = data.get('features', product.features)
        
        db.session.commit()
        
        return {'message': 'Product updated', 'product': product.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete product (provider only)"""
    user_id = get_jwt_identity()
    product = Product.query.get(product_id)
    
    if not product:
        return {'error': 'Product not found'}, 404
    
    if product.provider_id != user_id:
        return {'error': 'You can only delete your own products'}, 403
    
    try:
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted'}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500
