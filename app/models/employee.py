from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class EmployeeCreate(BaseModel):
    employee_id: str = Field(
        ..., min_length=1, max_length=20, description="Unique employee identifier"
    )
    full_name: str = Field(
        ..., min_length=1, max_length=100, description="Full name of the employee"
    )
    email: EmailStr = Field(..., description="Email address of the employee")
    department: str = Field(
        ..., min_length=1, max_length=50, description="Department name"
    )


class EmployeeResponse(BaseModel):
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
