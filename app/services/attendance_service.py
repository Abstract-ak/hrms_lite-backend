from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from app.config import get_database
from app.models.attendance import AttendanceCreate, AttendanceResponse


async def mark_attendance(attendance: AttendanceCreate) -> AttendanceResponse:
    db = get_database()

    # Verify employee exists
    employee = await db.employees.find_one({"employee_id": attendance.employee_id})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{attendance.employee_id}' not found",
        )

    doc = {
        "employee_id": attendance.employee_id,
        "date": attendance.date.isoformat(),
        "status": attendance.status.value,
        "created_at": datetime.utcnow(),
    }

    try:
        await db.attendance.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Attendance for employee '{attendance.employee_id}' on {attendance.date} already exists",
        )

    return AttendanceResponse(
        employee_id=doc["employee_id"],
        employee_name=employee.get("full_name"),
        date=attendance.date,
        status=attendance.status,
        created_at=doc["created_at"],
    )


async def get_attendance_by_employee(employee_id: str) -> list[AttendanceResponse]:
    db = get_database()

    # Verify employee exists
    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found",
        )

    records = []
    cursor = db.attendance.find({"employee_id": employee_id}).sort("date", -1)
    async for doc in cursor:
        records.append(
            AttendanceResponse(
                employee_id=doc["employee_id"],
                employee_name=employee.get("full_name"),
                date=doc["date"],
                status=doc["status"],
                created_at=doc["created_at"],
            )
        )
    return records


async def get_attendance_by_date(filter_date: date) -> list[AttendanceResponse]:
    db = get_database()

    records = []
    cursor = db.attendance.find({"date": filter_date.isoformat()}).sort("employee_id", 1)
    async for doc in cursor:
        # Fetch employee name
        employee = await db.employees.find_one({"employee_id": doc["employee_id"]})
        employee_name = employee.get("full_name") if employee else "Unknown"
        records.append(
            AttendanceResponse(
                employee_id=doc["employee_id"],
                employee_name=employee_name,
                date=doc["date"],
                status=doc["status"],
                created_at=doc["created_at"],
            )
        )
    return records


async def get_all_attendance() -> list[AttendanceResponse]:
    db = get_database()

    records = []
    cursor = db.attendance.find({}).sort("date", -1)
    async for doc in cursor:
        employee = await db.employees.find_one({"employee_id": doc["employee_id"]})
        employee_name = employee.get("full_name") if employee else "Unknown"
        records.append(
            AttendanceResponse(
                employee_id=doc["employee_id"],
                employee_name=employee_name,
                date=doc["date"],
                status=doc["status"],
                created_at=doc["created_at"],
            )
        )
    return records


async def get_dashboard_stats() -> dict:
    db = get_database()
    from datetime import date as date_type

    total_employees = await db.employees.count_documents({})
    today = date_type.today().isoformat()

    today_present = await db.attendance.count_documents(
        {"date": today, "status": "Present"}
    )
    today_absent = await db.attendance.count_documents(
        {"date": today, "status": "Absent"}
    )

    # Get recent attendance records (last 10)
    recent_records = []
    cursor = db.attendance.find({}).sort("created_at", -1).limit(10)
    async for doc in cursor:
        employee = await db.employees.find_one({"employee_id": doc["employee_id"]})
        employee_name = employee.get("full_name") if employee else "Unknown"
        recent_records.append(
            AttendanceResponse(
                employee_id=doc["employee_id"],
                employee_name=employee_name,
                date=doc["date"],
                status=doc["status"],
                created_at=doc["created_at"],
            )
        )

    # Get present days count per employee
    pipeline = [
        {"$match": {"status": "Present"}},
        {"$group": {"_id": "$employee_id", "present_days": {"$sum": 1}}},
    ]
    present_counts = {}
    async for doc in db.attendance.aggregate(pipeline):
        present_counts[doc["_id"]] = doc["present_days"]

    return {
        "total_employees": total_employees,
        "today_present": today_present,
        "today_absent": today_absent,
        "today_total_marked": today_present + today_absent,
        "recent_attendance": recent_records,
        "present_days_per_employee": present_counts,
    }
