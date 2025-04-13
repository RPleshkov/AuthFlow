import bcrypt

"""Функции хэширования и валидации пароля"""


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password=password.encode(),
        salt=salt,
    )


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
