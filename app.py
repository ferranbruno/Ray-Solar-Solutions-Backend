from flask import Flask
from flask_cors import CORS
from config import config
from extensions import db, jwt
import os


def get_allowed_frontend_origins():
    env_value = os.getenv('FRONTEND_URLS', '')
    if env_value:
        return [origin.strip() for origin in env_value.split(',') if origin.strip()]

    return [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
        'http://0.0.0.0:5173',
        'http://0.0.0.0:5174',
    ]


# Initialize extensions
def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    try:
        from services.cloudinary_service import init_cloudinary
        init_cloudinary()
    except ImportError:
        pass

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": get_allowed_frontend_origins(),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.product_routes import product_bp
    from routes.admin_routes import admin_bp
    from routes.order_routes import order_bp
    from routes.support_routes import support_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(support_bp, url_prefix='/api/support')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'Backend is running', 'version': '1.0.0'}, 200

    if os.getenv('FLASK_ENV') != 'production':
        with app.app_context():
            try:
                db.create_all()
            except Exception:
                pass
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

# For gunicorn
app = create_app(os.getenv('FLASK_ENV', 'development'))
