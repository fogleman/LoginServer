from auth import app
from itsdangerous import URLSafeSerializer

def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.secret_key
    return URLSafeSerializer(secret_key)
