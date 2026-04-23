import hashlib
import bcrypt
from cryptography.fernet import Fernet
from src.config.settings import Settings


def _get_fernet() -> Fernet:
    settings = Settings()
    if not settings.email_encryption_key:
        raise RuntimeError("EMAIL_ENCRYPTION_KEY is not configured.")

    try:
        return Fernet(settings.email_encryption_key.encode("utf-8"))
    except Exception as exc:
        raise RuntimeError("EMAIL_ENCRYPTION_KEY is invalid for Fernet.") from exc


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_email(email: str) -> str:
    # TODO(5.3): replace unsalted hash with salted/peppered strategy.
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def encrypt_email(email: str) -> str:
    fernet = _get_fernet()
    return fernet.encrypt(email.encode("utf-8")).decode("utf-8")


def decrypt_email(enc: str) -> str:
    fernet = _get_fernet()
    return fernet.decrypt(enc.encode("utf-8")).decode("utf-8")