import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from .config import settings


ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(subject: str) -> str:
    """Crée un token JWT avec expiration selon les bonnes pratiques."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return sub
    except JWTError:
        raise credentials_exception


async def verify_hmac(
    request: Request,
    x_signature: str = Header(default=None),
    x_timestamp: str = Header(default=None),
) -> None:
    if not x_signature or not x_timestamp:
        raise HTTPException(status_code=403, detail="Missing HMAC headers")

    try:
        ts = int(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid timestamp")

    if abs(time.time() - ts) > 300:
        raise HTTPException(status_code=403, detail="Signature expired")

    body = await request.body()
    message = f"{request.method}{request.url.path}{x_timestamp}".encode() + body
    expected = hmac.new(
        settings.hmac_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=403, detail="Invalid HMAC signature")


async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> str:
    if (
        form_data.username == settings.admin_username
        and form_data.password == settings.admin_password
    ):
        return form_data.username
    raise HTTPException(status_code=400, detail="Incorrect username or password")

