# Ray Solar Solutions Backend

Backend API for the Ray Solar Solutions e-commerce platform. Built with Node.js, Express, and MongoDB.

## Project Structure

```
Ray-Solar-Solutions-Backend/
├── models/              # Database models (User, Product, Order, etc.)
├── routes/              # API route handlers
├── middleware/          # Custom middleware (auth, validation, etc.)
├── controllers/         # Business logic controllers
├── config/              # Configuration files
├── server.js            # Main application entry point
├── package.json         # Dependencies and scripts
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Features

- **Role-based Access Control** — Customer, Provider, Admin roles
- **JWT Authentication** — Secure token-based auth
- **Product Management** — CRUD operations for solar products
- **Order Management** — Handle customer orders
- **User Management** — Admin control over users and providers

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ferranbruno/Ray-Solar-Solutions-Backend.git
   cd Ray-Solar-Solutions-Backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your configuration (MongoDB URI, JWT secret, etc.)

### Running the Server

**Development mode** (with auto-reload):
```bash
npm run dev
```

**Production mode**:
```bash
npm start
```

The server will start on `http://localhost:3000` (or your configured PORT).

## API Endpoints

### Authentication
- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Login user and get JWT token
- `GET /api/auth/me` — Get current user info

### Products
- `GET /api/products` — List all products
- `GET /api/products/:id` — Get product details
- `POST /api/products` — Create new product (provider)
- `PUT /api/products/:id` — Update product (provider)
- `DELETE /api/products/:id` — Delete product (provider)

### Orders
- `GET /api/orders` — List user's orders
- `POST /api/orders` — Create new order
- `GET /api/orders/:id` — Get order details

### Admin
- `GET /api/admin/users` — List all users (admin)
- `GET /api/admin/providers` — List all providers (admin)
- `GET /api/admin/products` — List all products (admin)

## Environment Variables

See `.env.example` for all available variables:

- `PORT` — Server port (default: 3000)
- `NODE_ENV` — Environment (development/production)
- `MONGODB_URI` — MongoDB connection string
- `JWT_SECRET` — Secret key for JWT signing
- `JWT_EXPIRY` — Token expiration time (default: 7d)
- `FRONTEND_URL` — Frontend URL for CORS (default: http://localhost:5174)

## Testing

Run tests with:
```bash
npm test
```

## Development

Install the included nodemon for automatic server restart on file changes:
```bash
npm run dev
```

## Next Steps

1. Set up MongoDB database (local or Atlas)
2. Implement authentication controllers
3. Create database models and schemas
4. Implement API endpoints
5. Add comprehensive error handling
6. Write unit and integration tests
7. Deploy to production (Heroku, AWS, etc.)

## License

ISC

## Author

Ferran Bruno
