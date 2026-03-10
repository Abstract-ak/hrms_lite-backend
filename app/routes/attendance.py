import datetime
from typing import Optional
from fastapi import APIRouter, Query, status
from app.models.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceListResponse,
)
from app.services.attendance_service import (
    mark_attendance,
    get_attendance_by_employee,
    get_attendance_by_date,
    get_all_attendance,
    get_dashboard_stats,
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(attendance: AttendanceCreate):
    """Mark attendance for an employee"""
    return await mark_attendance(attendance)


@router.get("/", response_model=AttendanceListResponse)
async def list_attendance(
    filter_date: Optional[datetime.date] = Query(None, alias="date", description="Filter by date (YYYY-MM-DD)"),
):
    """Get all attendance records, optionally filtered by date"""
    if filter_date:
        records = await get_attendance_by_date(filter_date)
    else:
        records = await get_all_attendance()
    return AttendanceListResponse(records=records, total=len(records))


@router.get("/employee/{employee_id}", response_model=AttendanceListResponse)
async def get_employee_attendance(employee_id: str):
    """Get attendance records for a specific employee"""
    records = await get_attendance_by_employee(employee_id)
    return AttendanceListResponse(records=records, total=len(records))


@router.get("/dashboard/stats")
async def dashboard_stats():
    """Get dashboard statistics"""
    return await get_dashboard_stats()
