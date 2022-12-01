import bcrypt


class PasswordHash:

    @classmethod
    def hash_password(cls, password: str) -> str:
        bts = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(bts, salt)

        return str(hash_password).strip("b'")

    @classmethod
    def validate_password(cls, str_password: str, hash_password: str) -> bool:
        str_password_bytes = str_password.encode('utf-8')
        hash_password_bytes = bytes(hash_password.encode())

        return bcrypt.checkpw(str_password_bytes, hash_password_bytes)
