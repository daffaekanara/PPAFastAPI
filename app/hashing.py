from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def bcrypt(pwd: str):
    return pwd_ctx.hash(pwd)

def verify_bcrypt(hashed: str, plain: str):
    return pwd_ctx.verify(plain, hashed)