import os
import time
import hashlib
import requests


def _get_config():
    return {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
    }


def init_cloudinary():
    cfg = _get_config()
    if not all(cfg.values()):
        print('[CLOUDINARY] Warning: missing env vars, uploads will fail')


def _sign(params, api_secret):
    to_sign = '&'.join(f'{k}={params[k]}' for k in sorted(params.keys()))
    return hashlib.sha1((to_sign + api_secret).encode()).hexdigest()


def upload_image(file, folder='ray-solar'):
    cfg = _get_config()
    if not all(cfg.values()):
        raise ValueError('Cloudinary not configured')

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    if ext not in ('png', 'jpg', 'jpeg', 'webp'):
        raise ValueError('Only PNG, JPG, JPEG, and WEBP images are allowed')

    timestamp = str(int(time.time()))
    public_id = hashlib.md5(f'{timestamp}{file.filename}'.encode()).hexdigest()

    params = {
        'folder': folder,
        'public_id': public_id,
        'timestamp': timestamp,
    }
    params['api_key'] = cfg['api_key']
    params['signature'] = _sign(params, cfg['api_secret'])

    result = requests.post(
        f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/image/upload",
        data=params,
        files={'file': (file.filename, file.stream, file.content_type)},
        timeout=30,
    )
    if not result.ok:
        print(f'[CLOUDINARY ERROR] {result.status_code} {result.text}')
        result.raise_for_status()
    return result.json()['secure_url']


def delete_image(url):
    cfg = _get_config()
    if not url or not url.startswith('http') or not all(cfg.values()):
        return False
    try:
        parts = url.split('/')
        idx = next(i for i, p in enumerate(parts) if p == 'upload')
        path = '/'.join(parts[idx + 1:])
        public_id = path.rsplit('.', 1)[0]

        timestamp = str(int(time.time()))
        params = {
            'public_id': public_id,
            'timestamp': timestamp,
        }
        params['api_key'] = cfg['api_key']
        params['signature'] = _sign(params, cfg['api_secret'])

        result = requests.post(
            f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/image/destroy",
            data=params,
            timeout=15,
        )
        return result.json().get('result') == 'ok'
    except Exception:
        return False
