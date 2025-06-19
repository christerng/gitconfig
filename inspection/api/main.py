import contextlib
import json
from pathlib import Path
from typing import Annotated

import fastapi
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

import lib.authentication
import lib.files
import lib.store
from lib.models import Check, ChecksDict, EmployeeID, Token
from lib.store import Store


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    store = lib.store.get_store()
    store.read(Path.cwd() / "api" / "fixtures")
    yield
    store.write(Path.cwd() / "api" / "fixtures")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token", status_code=fastapi.status.HTTP_200_OK)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    store: Annotated[Store, Depends(lib.store.get_store)],
) -> Token:
    is_authenticated = False

    # Prevent early returns to prevent timing attacks
    for employee in store.employee_dict.employees:
        if form.username == employee.eid and lib.authentication.password_context.verify(
            form.password, employee.password_hash.get_secret_value()
        ):
            is_authenticated = True

    if not is_authenticated:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=lib.authentication.create_access_token({"sub": form.username}),
        token_type="bearer",
    )


@app.get("/checks", status_code=fastapi.status.HTTP_200_OK)
def get_checks(
    employee_id: Annotated[EmployeeID, Depends(lib.authentication.get_current_employee_id)],
    store: Annotated[Store, Depends(lib.store.get_store)],
) -> list[Check]:
    return store.checks_dict.model_dump().get(employee_id)


@app.post("/checks", status_code=fastapi.status.HTTP_201_CREATED)
def create_check(
    employee_id: Annotated[EmployeeID, Depends(lib.authentication.get_current_employee_id)],
    store: Annotated[Store, Depends(lib.store.get_store)],
    check: Annotated[str, Form()],
    photo: Annotated[UploadFile, File()],
) -> None:
    # Add photo to check
    check_obj = json.loads(check)
    check_obj["last_check_photo"] = lib.files.serialize_photo(photo)

    # Modify store
    checks_dict_obj = store.checks_dict.model_dump()
    checks_dict_obj[employee_id].append(check_obj)

    store.checks_dict = ChecksDict.model_validate(checks_dict_obj)

    # Flush store into file
    store.write(Path.cwd() / "api" / "fixtures")
