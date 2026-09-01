// Product routes placeholder
// Will handle product listing, search, and management endpoints

export const productRoutes = {
  get: {
    '/': 'List all products',
    '/:id': 'Get product details',
  },
  post: {
    '/': 'Create new product (provider only)',
  },
  put: {
    '/:id': 'Update product (provider only)',
  },
  delete: {
    '/:id': 'Delete product (provider only)',
  },
};

export default {};
