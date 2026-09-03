import os


def init_cloudinary():
    """Initialize Cloudinary with env vars"""
    import cloudinary
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True,
    )


def upload_image(file, folder='ray-solar'):
    """Upload an image file to Cloudinary and return the URL"""
    import cloudinary.uploader

    if not file or file.filename == '':
        return None

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    if ext not in ('png', 'jpg', 'jpeg', 'webp'):
        raise ValueError('Only PNG, JPG, JPEG, and WEBP images are allowed')

    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type='image',
        format=ext,
    )
    return result['secure_url']


def delete_image(url):
    """Delete an image from Cloudinary by URL"""
    import cloudinary.uploader

    if not url or not url.startswith('http'):
        return False
    try:
        parts = url.split('/')
        idx = next(i for i, p in enumerate(parts) if p == 'upload')
        public_id_with_ext = '/'.join(parts[idx + 1:])
        public_id = public_id_with_ext.rsplit('.', 1)[0]
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception:
        return False
