import os
import requests


def _get_config():
    return {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
    }


def init_cloudinary():
    """Validate Cloudinary env vars are set"""
    cfg = _get_config()
    if not all(cfg.values()):
        print('[CLOUDINARY] Warning: missing env vars, uploads will fail')


def upload_image(file, folder='ray-solar'):
    """Upload an image to Cloudinary via REST API"""
    cfg = _get_config()
    if not all(cfg.values()):
        raise ValueError('Cloudinary not configured')

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    if ext not in ('png', 'jpg', 'jpeg', 'webp'):
        raise ValueError('Only PNG, JPG, JPEG, and WEBP images are allowed')

    import time, hashlib
    timestamp = str(int(time.time()))
    public_id = f"{folder}/{hashlib.md5(f'{timestamp}{file.filename}'.encode()).hexdigest()}"

    params = {
        'folder': folder,
        'public_id': public_id,
        'overwrite': 'true',
        'timestamp': timestamp,
    }
    to_sign = '&'.join(f'{k}={v}' for k, v in sorted(params.items())) + cfg['api_secret']
    signature = hashlib.sha1(to_sign.encode()).hexdigest()

    params['api_key'] = cfg['api_key']
    params['signature'] = signature

    result = requests.post(
        f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/image/upload",
        data=params,
        files={'file': (file.filename, file.stream, file.content_type)},
        timeout=30,
    )
    result.raise_for_status()
    return result.json()['secure_url']


def delete_image(url):
    """Delete an image from Cloudinary via REST API"""
    cfg = _get_config()
    if not url or not url.startswith('http') or not all(cfg.values()):
        return False
    try:
        parts = url.split('/')
        idx = next(i for i, p in enumerate(parts) if p == 'upload')
        public_id_with_ext = '/'.join(parts[idx + 1:])
        public_id = public_id_with_ext.rsplit('.', 1)[0]

        import hashlib
        timestamp = str(int(__import__('time').time()))
        signature = hashlib.sha1(f"public_id={public_id}&timestamp={timestamp}{cfg['api_secret']}".encode()).hexdigest()

        result = requests.post(
            f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/image/destroy",
            data={
                'public_id': public_id,
                'api_key': cfg['api_key'],
                'timestamp': timestamp,
                'signature': signature,
            },
            timeout=15,
        )
        return result.json().get('result') == 'ok'
    except Exception:
        return False
