import datetime
from typing import Annotated, Final, Literal

import fastapi
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from lib.models import EmployeeID

TOKEN_KEY: Final[str] = "dfed0a2bc8ff8945b9791ee2095a4256a70fc43f9ebc27e110603b1d814af4ee"
TOKEN_ALGORITHM: Final[str] = "HS256"
TOKEN_EXPIRE: Final[datetime.timedelta] = datetime.timedelta(minutes=30)

security_scheme = OAuth2PasswordBearer(tokenUrl="token")

password_context = CryptContext(schemes=["bcrypt"])


def get_current_employee_id(token: Annotated[str, Depends(security_scheme)]) -> EmployeeID:
    try:
        payload = jwt.decode(token, key=TOKEN_KEY, algorithms=[TOKEN_ALGORITHM])  # type: ignore
        assert "sub" in payload
    except (InvalidTokenError, AssertionError):
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]


def create_access_token(
    data: dict[Literal["sub"], str], expires_delta: datetime.timedelta = TOKEN_EXPIRE
) -> str:
    return jwt.encode(  # type: ignore
        payload={**data, "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta},
        key=TOKEN_KEY,
        algorithm=TOKEN_ALGORITHM,
    )
