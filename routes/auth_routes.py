from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models.user import User, UserRole
from datetime import timedelta
import os

auth_bp = Blueprint('auth', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'profiles')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return {'error': 'Email and password are required'}, 400

    if User.query.filter_by(email=data['email']).first():
        return {'error': 'User already exists'}, 409

    try:
        requested_role = data.get('role', 'CUSTOMER').upper()
        if requested_role not in {UserRole.CUSTOMER.name, UserRole.PROVIDER.name}:
            return {'error': 'Public registration is limited to customer or provider accounts'}, 400

        user = User(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            role=UserRole[requested_role]
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully', 'user': user.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login and token generation"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return {'error': 'Email and password are required'}, 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid email or password'}, 401

    if not user.is_active:
        return {'error': 'User account is inactive'}, 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    return {'user': user.to_dict()}, 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user's profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'first_name' in request.form:
                user.first_name = request.form['first_name']
            if 'last_name' in request.form:
                user.last_name = request.form['last_name']
            if 'phone' in request.form:
                user.phone = request.form['phone']

            profile_file = request.files.get('profile_image')
            if profile_file and profile_file.filename:
                from werkzeug.utils import secure_filename
                import uuid
                ext = profile_file.filename.rsplit('.', 1)[1].lower() if '.' in profile_file.filename else 'jpg'
                filename = f"{uuid.uuid4().hex}.{ext}"
                profile_file.save(os.path.join(UPLOAD_FOLDER, filename))
                user.profile_image = f"uploads/profiles/{filename}"
        else:
            data = request.get_json() or {}
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']

        db.session.commit()
        return {'message': 'Profile updated', 'user': user.to_dict()}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(user_id))
    return {'access_token': access_token}, 200
