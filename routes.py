# ===============================================
# app/routes/work_routes.py (API Routes)
# ===============================================
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.schemas import (
    WorkRecordCreate, WorkRecordResponse, WorkRecordUpdate,
    DailyReportResponse, ProductivityAnalysis, APIResponse,
    WorkerProfileCreate, WorkerProfileResponse, ProductivityStats
)
from app import crud
from app.AI import analyze_worker_productivity

router = APIRouter(tags=["Work Records"])


@router.post("/records", response_model=WorkRecordResponse)
async def create_work_record(record: WorkRecordCreate, db: Session = Depends(get_db)):
    """Create a new work record"""
    try:
        db_record = crud.create_work_record(db, record)

        return WorkRecordResponse(
            id=db_record.id,
            worker_name=db_record.worker_name,
            work_date=db_record.work_date,
            start_time=db_record.start_time,
            end_time=db_record.end_time,
            hours_worked=db_record.hours_worked,
            tasks_completed=db_record.tasks_completed,
            blog_posts_count=db_record.blog_posts_count,
            productivity_score=db_record.productivity_score,
            notes=db_record.notes,
            work_duration_hours=db_record.calculate_work_duration_hours(),
            created_at=db_record.created_at,
            updated_at=db_record.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create work record: {str(e)}")


@router.get("/records", response_model=List[WorkRecordResponse])
async def get_work_records(
        worker_name: Optional[str] = Query(None),
        work_date: Optional[date] = Query(None),
        limit: int = Query(50, ge=1, le=1000),
        db: Session = Depends(get_db)
):
    """Get work records with optional filters"""
    try:
        if work_date:
            records = crud.get_work_records_by_date(db, work_date)
        elif worker_name:
            records = crud.get_work_records_by_worker(db, worker_name, limit)
        else:
            records = crud.get_latest_work_records(db, limit)

        return [
            WorkRecordResponse(
                id=record.id,
                worker_name=record.worker_name,
                work_date=record.work_date,
                start_time=record.start_time,
                end_time=record.end_time,
                hours_worked=record.hours_worked,
                tasks_completed=record.tasks_completed,
                blog_posts_count=record.blog_posts_count,
                productivity_score=record.productivity_score,
                notes=record.notes,
                work_duration_hours=record.calculate_work_duration_hours(),
                created_at=record.created_at,
                updated_at=record.updated_at
            )
            for record in records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch work records: {str(e)}")


@router.get("/records/{record_id}", response_model=WorkRecordResponse)
async def get_work_record(record_id: int, db: Session = Depends(get_db)):
    """Get specific work record by ID"""
    record = crud.get_work_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Work record not found")

    return WorkRecordResponse(
        id=record.id,
        worker_name=record.worker_name,
        work_date=record.work_date,
        start_time=record.start_time,
        end_time=record.end_time,
        hours_worked=record.hours_worked,
        tasks_completed=record.tasks_completed,
        blog_posts_count=record.blog_posts_count,
        productivity_score=record.productivity_score,
        notes=record.notes,
        work_duration_hours=record.calculate_work_duration_hours(),
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.put("/records/{record_id}", response_model=WorkRecordResponse)
async def update_work_record(
        record_id: int,
        update_data: WorkRecordUpdate,
        db: Session = Depends(get_db)
):
    """Update work record"""
    updated_record = crud.update_work_record(db, record_id, update_data)
    if not updated_record:
        raise HTTPException(status_code=404, detail="Work record not found")

    return WorkRecordResponse(
        id=updated_record.id,
        worker_name=updated_record.worker_name,
        work_date=updated_record.work_date,
        start_time=updated_record.start_time,
        end_time=updated_record.end_time,
        hours_worked=updated_record.hours_worked,
        tasks_completed=updated_record.tasks_completed,
        blog_posts_count=updated_record.blog_posts_count,
        productivity_score=updated_record.productivity_score,
        notes=updated_record.notes,
        work_duration_hours=updated_record.calculate_work_duration_hours(),
        created_at=updated_record.created_at,
        updated_at=updated_record.updated_at
    )


@router.delete("/records/{record_id}", response_model=APIResponse)
async def delete_work_record(record_id: int, db: Session = Depends(get_db)):
    """Delete work record"""
    success = crud.delete_work_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Work record not found")

    return APIResponse(success=True, message="Work record deleted successfully")


@router.get("/workers", response_model=List[str])
async def get_all_workers(db: Session = Depends(get_db)):
    """Get all unique worker names"""
    try:
        workers = crud.get_all_workers(db)
        return workers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workers: {str(e)}")


@router.post("/analyze/{record_id}", response_model=ProductivityAnalysis)
async def analyze_productivity(record_id: int, db: Session = Depends(get_db)):
    """Generate AI productivity analysis for a work record"""
    try:
        record = crud.get_work_record_by_id(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Work record not found")

        analysis = analyze_worker_productivity(record)

        return ProductivityAnalysis(
            duration_hours=analysis["duration_hours"],
            productivity_score=analysis["productivity_score"],
            productivity_rating=analysis["productivity_rating"],
            analysis=analysis["analysis"],
            recommendations=analysis["recommendations"],
            is_anomaly=analysis["is_anomaly"],
            anomaly_reason=analysis["anomaly_reason"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze productivity: {str(e)}")


@router.get("/reports/{worker_name}", response_model=List[DailyReportResponse])
async def get_worker_reports(
        worker_name: str,
        limit: int = Query(30, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Get daily reports for a specific worker"""
    try:
        reports = crud.get_daily_reports_by_worker(db, worker_name, limit)
        return [
            DailyReportResponse(
                id=report.id,
                worker_name=report.worker_name,
                report_date=report.report_date,
                total_hours=report.total_hours,
                total_tasks=report.total_tasks,
                total_blog_posts=report.total_blog_posts,
                avg_productivity=report.avg_productivity,
                summary=report.summary,
                created_at=report.created_at,
                updated_at=report.updated_at
            )
            for report in reports
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")


@router.get("/stats/summary", response_model=ProductivityStats)
async def get_productivity_summary(
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        db: Session = Depends(get_db)
):
    """Get overall productivity statistics"""
    try:
        stats = crud.get_productivity_stats(db, start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.post("/workers", response_model=WorkerProfileResponse)
async def create_worker_profile(worker: WorkerProfileCreate, db: Session = Depends(get_db)):
    """Create a new worker profile"""
    try:
        db_worker = crud.create_worker_profile(db, worker)
        return WorkerProfileResponse(
            id=db_worker.id,
            worker_name=db_worker.worker_name,
            email=db_worker.email,
            department=db_worker.department,
            role=db_worker.role,
            hire_date=db_worker.hire_date,
            is_active=db_worker.is_active,
            created_at=db_worker.created_at,
            updated_at=db_worker.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create worker profile: {str(e)}")


@router.get("/workers/profiles", response_model=List[WorkerProfileResponse])
async def get_worker_profiles(
        active_only: bool = Query(True),
        db: Session = Depends(get_db)
):
    """Get all worker profiles"""
    try:
        profiles = crud.get_all_worker_profiles(db, active_only)
        return [
            WorkerProfileResponse(
                id=profile.id,
                worker_name=profile.worker_name,
                email=profile.email,
                department=profile.department,
                role=profile.role,
                hire_date=profile.hire_date,
                is_active=profile.is_active,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            for profile in profiles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch worker profiles: {str(e)}")
