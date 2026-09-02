import os
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, UserRole
from models.product import Product

product_bp = Blueprint('products', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'products')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def save_uploaded_image(file):
    if file is None or file.filename == '':
        return None

    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError('Only PNG, JPG, JPEG, and WEBP images are allowed')

    filename = secure_filename(file.filename)
    unique_name = f"{os.urandom(8).hex()}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(file_path)
    return os.path.join('uploads', 'products', unique_name)


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
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != UserRole.PROVIDER:
        return {'error': 'Only providers can create products'}, 403

    name = request.form.get('name')
    price = request.form.get('price')
    if not name or not price:
        return {'error': 'Name and price are required'}, 400

    image_file = request.files.get('image')

    try:
        image_path = save_uploaded_image(image_file)
        product = Product(
            name=name,
            category=request.form.get('category', ''),
            description=request.form.get('description', ''),
            price=float(price),
            wattage=request.form.get('wattage', ''),
            stock=int(request.form.get('stock', 0)),
            image_path=image_path,
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
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product (provider only)"""
    user_id = int(get_jwt_identity())
    product = Product.query.get(product_id)

    if not product:
        return {'error': 'Product not found'}, 404

    if product.provider_id != user_id:
        return {'error': 'You can only update your own products'}, 403

    try:
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
            product.image_path = save_uploaded_image(image_file)

        db.session.commit()

        return {'message': 'Product updated', 'product': product.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete product (provider only)"""
    user_id = int(get_jwt_identity())
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
