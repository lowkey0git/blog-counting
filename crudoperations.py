
# ===============================================
# app/crud.py (Database Operations)
# ===============================================
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from app.env import WorkRecord, DailyReport, WorkerProfile
from app.schemas import WorkRecordCreate, WorkRecordUpdate, DailyReportCreate,WorkerProfileCreate, ProductivityStats

# Work Record CRUD Operations
def create_work_record(db: Session, work_record: WorkRecordCreate) -> WorkRecord:
    """Create new work record"""
    try:
        start_datetime = None
        end_datetime = None

        if work_record.start_time:
            start_datetime = datetime.combine(work_record.work_date, work_record.start_time)
        if work_record.end_time:
            end_datetime = datetime.combine(work_record.work_date, work_record.end_time)

        db_record = WorkRecord(
            worker_name=work_record.worker_name,
            work_date=work_record.work_date,
            start_time=start_datetime,
            end_time=end_datetime,
            hours_worked=work_record.hours_worked,
            tasks_completed=work_record.tasks_completed or 0,
            blog_posts_count=work_record.blog_posts_count or 0,
            productivity_score=work_record.productivity_score,
            notes=work_record.notes
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        db.rollback()
        raise e


def get_work_record_by_id(db: Session, record_id: int) -> Optional[WorkRecord]:
    """Get work record by ID"""
    return db.query(WorkRecord).filter(WorkRecord.id == record_id).first()


def get_work_records_by_worker(db: Session, worker_name: str, limit: int = 100) -> List[WorkRecord]:
    """Get work records for specific worker"""
    return db.query(WorkRecord) \
        .filter(WorkRecord.worker_name.ilike(f"%{worker_name}%")) \
        .order_by(desc(WorkRecord.work_date)) \
        .limit(limit) \
        .all()


def get_work_records_by_date(db: Session, target_date: date) -> List[WorkRecord]:
    """Get all work records for specific date"""
    return db.query(WorkRecord) \
        .filter(WorkRecord.work_date == target_date) \
        .order_by(WorkRecord.worker_name) \
        .all()


def get_latest_work_records(db: Session, limit: int = 10) -> List[WorkRecord]:
    """Get most recent work records"""
    return db.query(WorkRecord) \
        .order_by(desc(WorkRecord.work_date), desc(WorkRecord.created_at)) \
        .limit(limit) \
        .all()


def update_work_record(db: Session, record_id: int, update_data: WorkRecordUpdate) -> Optional[WorkRecord]:
    """Update work record"""
    try:
        record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
        if not record:
            return None

        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field in ['start_time', 'end_time'] and isinstance(value, time):
                work_date = update_dict.get('work_date', record.work_date)
                value = datetime.combine(work_date, value)
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise e


def delete_work_record(db: Session, record_id: int) -> bool:
    """Delete work record"""
    try:
        record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e


# Daily Report CRUD Operations
def create_daily_report(db: Session, report_data: DailyReportCreate) -> DailyReport:
    """Create daily report"""
    try:
        db_report = DailyReport(**report_data.dict())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
    except Exception as e:
        db.rollback()
        raise e


def get_daily_report_by_worker_date(db: Session, worker_name: str, report_date: date) -> Optional[DailyReport]:
    """Get daily report for worker and date"""
    return db.query(DailyReport) \
        .filter(and_(
        DailyReport.worker_name == worker_name,
        DailyReport.report_date == report_date
    )) \
        .first()


def get_daily_reports_by_worker(db: Session, worker_name: str, limit: int = 30) -> List[DailyReport]:
    """Get daily reports for a worker"""
    return db.query(DailyReport) \
        .filter(DailyReport.worker_name.ilike(f"%{worker_name}%")) \
        .order_by(desc(DailyReport.report_date)) \
        .limit(limit) \
        .all()


# Worker Profile CRUD Operations
def create_worker_profile(db: Session, worker_data: WorkerProfileCreate) -> WorkerProfile:
    """Create new worker profile"""
    try:
        db_worker = WorkerProfile(**worker_data.dict())
        db.add(db_worker)
        db.commit()
        db.refresh(db_worker)
        return db_worker
    except Exception as e:
        db.rollback()
        raise e


def get_worker_profile_by_name(db: Session, worker_name: str) -> Optional[WorkerProfile]:
    """Get worker profile by name"""
    return db.query(WorkerProfile) \
        .filter(WorkerProfile.worker_name == worker_name) \
        .first()


def get_all_worker_profiles(db: Session, active_only: bool = True) -> List[WorkerProfile]:
    """Get all worker profiles"""
    query = db.query(WorkerProfile)
    if active_only:
        query = query.filter(WorkerProfile.is_active == True)
    return query.order_by(WorkerProfile.worker_name).all()


# Utility Functions
def get_all_workers(db: Session) -> List[str]:
    """Get list of all unique worker names"""
    workers = db.query(WorkRecord.worker_name) \
        .distinct() \
        .order_by(WorkRecord.worker_name) \
        .all()
    return [worker[0] for worker in workers]


def get_productivity_stats(db: Session, start_date: date = None, end_date: date = None) -> ProductivityStats:
    """Calculate productivity statistics"""
    query = db.query(WorkRecord)

    if start_date and end_date:
        query = query.filter(and_(
            WorkRecord.work_date >= start_date,
            WorkRecord.work_date <= end_date
        ))

    records = query.all()

    if not records:
        return ProductivityStats(
            total_records=0,
            unique_workers=0,
            total_hours=0.0,
            avg_productivity=None
        )

    total_records = len(records)
    unique_workers = len(set(record.worker_name for record in records))
    total_hours = sum(record.hours_worked for record in records)

    productivity_scores = [r.productivity_score for r in records if r.productivity_score is not None]
    avg_productivity = sum(productivity_scores) / len(productivity_scores) if productivity_scores else None

    return ProductivityStats(
        total_records=total_records,
        unique_workers=unique_workers,
        total_hours=round(total_hours, 2),
        avg_productivity=round(avg_productivity, 2) if avg_productivity else None
    )
