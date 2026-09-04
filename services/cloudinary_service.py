import os
import time
import hashlib
import requests
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'products')


def _get_config():
    return {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
    }


def _is_cloudinary_configured():
    cfg = _get_config()
    return all(cfg.values())


def init_cloudinary():
    cfg = _get_config()
    if not _is_cloudinary_configured():
        print('[CLOUDINARY] Warning: missing env vars, using local storage for uploads')
    else:
        print(f'[CLOUDINARY] Configured: cloud={cfg["cloud_name"]}, key={cfg["api_key"][:6]}...')


def _sign(params, api_secret):
    to_sign = '&'.join(f'{k}={params[k]}' for k in sorted(params.keys()))
    return hashlib.sha1((to_sign + api_secret).encode()).hexdigest()


def _validate_file(file):
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError('Only PNG, JPG, JPEG, and WEBP images are allowed')
    return ext


def _save_local(file, folder='ray-solar'):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = str(int(time.time()))
    public_id = hashlib.md5(f'{timestamp}{file.filename}'.encode()).hexdigest()
    ext = _validate_file(file)
    filename = f'{public_id}_{secure_filename(file.filename.rsplit(".", 1)[0])}.{ext}'
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    print(f'[LOCAL] Saved to {filepath}')
    return f'uploads/products/{filename}'


def _delete_local(path):
    if not path or path.startswith('http'):
        return False
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def upload_image(file, folder='ray-solar'):
    if not file or not file.filename:
        raise ValueError('No file provided')

    if _is_cloudinary_configured():
        try:
            return _upload_cloudinary(file, folder)
        except Exception as e:
            print(f'[CLOUDINARY] Upload failed, falling back to local storage: {e}')
            file.stream.seek(0)
            return _save_local(file, folder)
    return _save_local(file, folder)


def _upload_cloudinary(file, folder='ray-solar'):
    cfg = _get_config()
    _validate_file(file)

    timestamp = str(int(time.time()))
    public_id = hashlib.md5(f'{timestamp}{file.filename}'.encode()).hexdigest()

    params = {
        'folder': folder,
        'public_id': public_id,
        'timestamp': timestamp,
    }
    params['api_key'] = cfg['api_key']
    params['signature'] = _sign(params, cfg['api_secret'])

    print(f'[CLOUDINARY] Uploading to folder={folder}, public_id={public_id}')

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
    if not url:
        return False
    if url.startswith('http') and _is_cloudinary_configured():
        return _delete_cloudinary(url)
    return _delete_local(url)


def _delete_cloudinary(url):
    cfg = _get_config()
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
