import base64
import json
from pathlib import Path
from typing import Annotated

from fastapi import File, UploadFile

from lib.models import ChecksDict, EmployeeDict


def read_employees(filepath: Path) -> EmployeeDict:
    return EmployeeDict.model_validate(json.loads(filepath.read_text()))


def read_checks(filepath: Path) -> ChecksDict:
    return ChecksDict.model_validate(json.loads(filepath.read_text()))


def write_checks(filepath: Path, checks_dict: ChecksDict) -> None:
    filepath.write_text(json.dumps(checks_dict.model_dump(), indent=2))


def serialize_photo(photo: Annotated[UploadFile, File()]) -> str:
    lines = [base64.b64encode(line).decode() for line in photo.file.readlines()]
    return json.dumps(lines)
