from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from models.user import User, UserRole
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return {'error': 'Email and password are required'}, 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return {'error': 'User already exists'}, 409
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            role=UserRole[data.get('role', 'CUSTOMER').upper()]
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
    
    # Create tokens
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

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(user_id))
    return {'access_token': access_token}, 200
