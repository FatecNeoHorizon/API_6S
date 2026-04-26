import structlog
from src.config.email_hasher import EmailHasher

log = structlog.get_logger()


def test_hash_is_deterministic():
    h1 = EmailHasher.hash("user@example.com")
    h2 = EmailHasher.hash("user@example.com")
    log.info("test_hash_is_deterministic", hash_1=h1, hash_2=h2, equal=h1 == h2)
    assert h1 == h2


def test_different_emails_generate_different_hashes():
    h1 = EmailHasher.hash("user@example.com")
    h2 = EmailHasher.hash("other@example.com")
    log.info("test_different_emails", hash_user=h1, hash_other=h2, equal=h1 == h2)
    assert h1 != h2


def test_verify_returns_true_for_correct_email():
    stored = EmailHasher.hash("user@example.com")
    result = EmailHasher.verify("user@example.com", stored)
    log.info("test_verify_correct", stored_hash=stored, result=result)
    assert result is True


def test_verify_returns_false_for_incorrect_email():
    stored = EmailHasher.hash("user@example.com")
    result = EmailHasher.verify("wrong@example.com", stored)
    log.info("test_verify_incorrect", stored_hash=stored, result=result)
    assert result is False


def test_hash_normalizes_email():
    h1 = EmailHasher.hash("User@Example.COM")
    h2 = EmailHasher.hash("user@example.com")
    log.info("test_hash_normalizes", hash_upper=h1, hash_lower=h2, equal=h1 == h2)
    assert h1 == h2