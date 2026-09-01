// User model placeholder
// Will define user schema and model for authentication and user management

export const userSchema = {
  name: String,
  email: String,
  role: 'customer' | 'provider' | 'admin',
  password: String,
  createdAt: Date,
};

export default {};
