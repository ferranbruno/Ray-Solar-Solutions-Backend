// Product model placeholder
// Will define product schema for solar products inventory

export const productSchema = {
  id: Number,
  name: String,
  category: String,
  price: Number,
  rating: Number,
  wattage: String,
  stock: Number,
  image: String,
  description: String,
  features: [String],
  providerId: String,
  createdAt: Date,
};

export default {};
