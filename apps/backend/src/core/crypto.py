import os
import hashlib
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv(dotenv_path='envs/.env.backend')

try:
    key = os.getenv("EMAIL_ENCRYPTION_KEY")
    salt = os.getenv("EMAIL_HASH_SALT")
    if not key:
        raise ValueError("A variável de ambiente EMAIL_ENCRYPTION_KEY não foi definida.")
    if not salt:
        raise ValueError("A variável de ambiente EMAIL_HASH_SALT não foi definida.")
    fernet = Fernet(key.encode())
    email_hash_salt = salt.encode('utf-8')
except (ValueError, TypeError) as e:
    print(f"Erro ao inicializar o módulo de criptografia: {e}")
    fernet = None
    email_hash_salt = None


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_email(email: str) -> str:
    if not email_hash_salt:
        raise RuntimeError("O salt de hashing de e-mail não foi inicializado.")
    return hashlib.sha256(email_hash_salt + email.encode('utf-8')).hexdigest()


def encrypt_email(email: str) -> str:
    if not fernet:
        raise RuntimeError("O sistema de criptografia Fernet não foi inicializado.")
    return fernet.encrypt(email.encode('utf-8')).decode('utf-8')


def decrypt_email(encrypted_email: str) -> str:
    if not fernet:
        raise RuntimeError("O sistema de criptografia Fernet não foi inicializado.")
    return fernet.decrypt(encrypted_email.encode('utf-8')).decode('utf-8')