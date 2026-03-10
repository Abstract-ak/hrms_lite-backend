from datetime import datetime
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from app.config import get_database
from app.models.employee import EmployeeCreate, EmployeeResponse


async def create_employee(employee: EmployeeCreate) -> EmployeeResponse:
    db = get_database()

    doc = {
        "employee_id": employee.employee_id.strip(),
        "full_name": employee.full_name.strip(),
        "email": employee.email.lower().strip(),
        "department": employee.department.strip(),
        "created_at": datetime.utcnow(),
    }

    try:
        await db.employees.insert_one(doc)
    except DuplicateKeyError as e:
        error_msg = str(e)
        if "employee_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with ID '{employee.employee_id}' already exists",
            )
        elif "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email '{employee.email}' already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate employee record",
            )

    return EmployeeResponse(**doc)


async def get_all_employees() -> list[EmployeeResponse]:
    db = get_database()
    employees = []
    cursor = db.employees.find({}).sort("created_at", -1)
    async for doc in cursor:
        employees.append(EmployeeResponse(**doc))
    return employees


async def get_employee_by_id(employee_id: str) -> EmployeeResponse:
    db = get_database()
    doc = await db.employees.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found",
        )
    return EmployeeResponse(**doc)


async def delete_employee(employee_id: str) -> dict:
    db = get_database()

    result = await db.employees.find_one({"employee_id": employee_id})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found",
        )

    await db.employees.delete_one({"employee_id": employee_id})
    # Also delete associated attendance records
    await db.attendance.delete_many({"employee_id": employee_id})

    return {"message": f"Employee '{employee_id}' and associated records deleted successfully"}
