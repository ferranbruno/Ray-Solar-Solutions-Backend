from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User, UserRole
from models.product import Product

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != UserRole.ADMIN:
            return {'error': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page)
    
    return {
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages
    }, 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user role or status (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    data = request.get_json()
    
    try:
        if 'role' in data:
            user.role = UserRole[data['role'].upper()]
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        return {'message': 'User updated', 'user': user.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@admin_bp.route('/providers', methods=['GET'])
@admin_required
def get_providers():
    """Get all providers (admin only)"""
    providers = User.query.filter_by(role=UserRole.PROVIDER).all()
    return {'providers': [p.to_dict() for p in providers]}, 200

@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_all_products():
    """Get all products for moderation (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    products = Product.query.paginate(page=page, per_page=per_page)
    
    return {
        'products': [p.to_dict() for p in products.items],
        'total': products.total,
        'pages': products.pages
    }, 200

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def moderate_product(product_id):
    """Approve or deactivate products (admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return {'error': 'Product not found'}, 404
    
    data = request.get_json()
    
    try:
        if 'is_active' in data:
            product.is_active = data['is_active']
        
        db.session.commit()
        return {'message': 'Product status updated', 'product': product.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get platform-wide analytics (admin only)"""
    total_users = User.query.count()
    total_customers = User.query.filter_by(role=UserRole.CUSTOMER).count()
    total_providers = User.query.filter_by(role=UserRole.PROVIDER).count()
    total_products = Product.query.count()
    
    return {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_providers': total_providers,
        'total_products': total_products
    }, 200
