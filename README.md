# Ray Solar Solutions Backend

A Flask-based REST API backend for the Ray Solar Solutions e-commerce platform. This backend handles user authentication, product management, orders, and administrative functions with PostgreSQL as the database.

## Project Structure

```
Ray-Solar-Solutions-Backend/
├── models/              # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py         # User model with roles
│   ├── product.py      # Product model
│   └── order.py        # Order and OrderItem models
├── routes/             # Flask blueprints (API endpoints)
│   ├── __init__.py
│   ├── auth_routes.py  # Authentication endpoints
│   ├── product_routes.py # Product management endpoints
│   └── admin_routes.py # Admin-only endpoints
├── config.py           # Configuration for Flask app
├── app.py              # Flask application factory
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Features

### Authentication & Authorization
- User registration and login with JWT tokens
- Role-based access control (Customer, Provider, Admin)
- Password hashing with bcrypt
- Token refresh mechanism

### Customer Features
- Browse and search solar lighting products
- Filter products by category
- View product details
- Track orders

### Provider Features
- Register as a solar lighting provider
- Add, update, and delete products
- Manage inventory
- View product performance

### Administrator Features
- Manage all users and roles
- Approve/deactivate provider accounts
- Moderate product listings
- View platform analytics

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **API Testing**: pytest

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**:
   ```bash
   cd Ray-Solar-Solutions-Backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and update:
   - `DATABASE_URL`: PostgreSQL connection string
   - `JWT_SECRET_KEY`: Generate a secure random key
   - `FRONTEND_URL`: URL of your React frontend

5. **Initialize the database**:
   ```bash
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Run the development server**:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT tokens
- `GET /api/auth/me` - Get current authenticated user
- `POST /api/auth/refresh` - Refresh access token

### Products
- `GET /api/products` - List all products (paginated, filterable)
- `GET /api/products/<id>` - Get product details
- `POST /api/products` - Create new product (provider only)
- `PUT /api/products/<id>` - Update product (provider only)
- `DELETE /api/products/<id>` - Delete product (provider only)

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/<id>` - Update user role/status
- `GET /api/admin/providers` - List all providers
- `GET /api/admin/products` - List all products for moderation
- `PUT /api/admin/products/<id>` - Approve/deactivate products
- `GET /api/admin/analytics` - Get platform analytics

### Health Check
- `GET /api/health` - Check backend status

## Environment Variables

```
FLASK_ENV=development                              # Environment mode
FLASK_DEBUG=True                                   # Debug mode
SECRET_KEY=your_secret_key_here                    # Flask secret key
JWT_SECRET_KEY=your_jwt_secret_key_here           # JWT signing key
DATABASE_URL=postgresql://user:pass@localhost:5432/ray_solar
FRONTEND_URL=http://localhost:5174                # React frontend URL
JWT_ACCESS_TOKEN_EXPIRES=3600                     # Token expiry in seconds
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Running with Docker (Optional)

Build and run with Docker:
```bash
docker build -t ray-solar-backend .
docker run -p 5000:5000 ray-solar-backend
```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests to ensure everything works:
   ```bash
   pytest
   ```

4. Commit with descriptive messages:
   ```bash
   git commit -m "Add: Description of changes"
   ```

5. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Database Models

### User
- Stores user information with roles (customer, provider, admin)
- Password stored as hashed values
- Tracks creation and update timestamps

### Product
- Solar lighting products with details (wattage, price, stock)
- Associated with provider (User)
- Includes features and image URL
- Can be activated/deactivated for moderation

### Order
- Customer orders with items and status tracking
- Linked to customer and order items
- Tracks total amount and shipping address

### OrderItem
- Individual items within an order
- Tracks quantity and unit price

## Next Steps

1. Set up PostgreSQL database locally
2. Implement payment integration
3. Add email notifications
4. Create admin dashboard features
5. Add comprehensive logging
6. Deploy to production (Heroku, AWS, etc.)

## License

ISC

## Author

Ferran Bruno

## Support

For issues and feature requests, please check the GitHub repository.
