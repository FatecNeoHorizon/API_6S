import hashlib

from src.config.settings import Settings


class EmailHasher:

    @staticmethod
    def hash(email: str) -> str:
        settings = Settings()
        normalized = email.strip().lower()
        payload = f"{normalized}:{settings.email_hash_salt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def verify(email: str, stored_hash: str) -> bool:
        return EmailHasher.hash(email) == stored_hash