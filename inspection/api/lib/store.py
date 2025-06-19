from pathlib import Path

import lib.files
from lib.models import ChecksDict, EmployeeDict


class Store:
    def __init__(self) -> None:
        self._employee_dict: EmployeeDict | None = None
        self._checks_dict: ChecksDict | None = None

    @property
    def employee_dict(self) -> EmployeeDict:
        if self._employee_dict is None:
            raise RuntimeError("Store not initialized")
        return self._employee_dict

    @property
    def checks_dict(self) -> ChecksDict:
        if self._checks_dict is None:
            raise RuntimeError("Store not initialized")
        return self._checks_dict

    @checks_dict.setter
    def checks_dict(self, checks_dict: ChecksDict) -> None:
        self._checks_dict = checks_dict

    def read(self, fixtures_path: Path) -> None:
        self._employee_dict = lib.files.read_employees(fixtures_path / "employees.json")
        self._checks_dict = lib.files.read_checks(fixtures_path / "checks.json")

    def write(self, fixtures_path: Path) -> None:
        if self._checks_dict is not None:
            lib.files.write_checks(fixtures_path / "checks.json", self._checks_dict)


_store = Store()


def get_store() -> Store:
    return _store
