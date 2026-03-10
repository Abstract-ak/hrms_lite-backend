import datetime as dt
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"


class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Employee ID")
    date: dt.date = Field(..., description="Attendance date")
    status: AttendanceStatus = Field(..., description="Present or Absent")


class AttendanceResponse(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    date: dt.date
    status: AttendanceStatus
    created_at: dt.datetime


class AttendanceListResponse(BaseModel):
    records: list[AttendanceResponse]
    total: int
