from fastapi import APIRouter, status
from app.models.employee import EmployeeCreate, EmployeeResponse, EmployeeListResponse
from app.services.employee_service import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    delete_employee,
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def add_employee(employee: EmployeeCreate):
    """Add a new employee"""
    return await create_employee(employee)


@router.get("/", response_model=EmployeeListResponse)
async def list_employees():
    """Get all employees"""
    employees = await get_all_employees()
    return EmployeeListResponse(employees=employees, total=len(employees))


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    """Get a single employee by ID"""
    return await get_employee_by_id(employee_id)


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
async def remove_employee(employee_id: str):
    """Delete an employee and their attendance records"""
    return await delete_employee(employee_id)
