from enum import Enum, auto
from typing import Annotated

from pydantic import BaseModel, Field, RootModel, SecretStr

EmployeeID = Annotated[str, Field(pattern=r"^E\d{4}$")]
EmployeePW = SecretStr

ShortStr = Annotated[str, Field(max_length=50)]
LongStr = Annotated[str, Field(max_length=500)]


# Storage Models
class Employee(BaseModel):
    eid: EmployeeID
    name: ShortStr
    password_hash: EmployeePW


class EmployeeDict(BaseModel):
    employees: list[Employee]


class OffenceType(Enum):
    PESTS = auto()
    MISHANDLING = auto()
    HYGIENE = auto()
    OTHERS = auto()


class Offence(BaseModel):
    type: OffenceType
    description: LongStr


class Check(BaseModel):
    license_no: Annotated[str, Field(pattern=r"^[A-Z]{3}\d{3}$")]
    eatery_name: ShortStr
    owner_name: ShortStr
    owner_contact_no: Annotated[str, Field(pattern=r"^\d{4} \d{4}$")]
    last_check_date: Annotated[
        str,
        Field(pattern=r"^\d{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4}$"),
    ]
    last_check_by_eid: EmployeeID
    last_check_by_name: ShortStr
    last_check_notes: LongStr
    last_check_offences: list[Offence]
    last_check_photo: str


ChecksDict = RootModel[dict[EmployeeID, list[Check]]]


# Network Models
class LoginRequest(BaseModel):
    username: EmployeeID
    password: EmployeePW


class Token(BaseModel):
    access_token: str
    token_type: str
