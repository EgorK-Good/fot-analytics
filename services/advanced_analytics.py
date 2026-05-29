from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from models import (
    Absence,
    AbsenceType,
    Company,
    Employee,
    Overtime,
    SalaryHistory,
    WorkScheduleType,
)


class AdvancedAnalyticsService:
    """Сервис для расширенной аналитики ФОТ и кадровых показателей."""

    @staticmethod
    def get_absence_analytics(
        session: Session, 
        company_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Аналитика по отсутствиям сотрудников."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        query = session.query(
            Absence.absence_type,
            func.count(Absence.id).label("count"),
            func.sum(Absence.days_count).label("total_days"),
            func.avg(Absence.days_count).label("avg_days")
        ).join(Employee).filter(
            Absence.start_date >= start_date,
            Absence.start_date <= end_date
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        results = query.group_by(Absence.absence_type).all()

        # Анализ по месяцам
        monthly_query = session.query(
            func.strftime("%Y-%m", Absence.start_date).label("month"),
            Absence.absence_type,
            func.count(Absence.id).label("count")
        ).join(Employee).filter(
            Absence.start_date >= start_date,
            Absence.start_date <= end_date
        )

        if company_id:
            monthly_query = monthly_query.filter(Employee.company_id == company_id)

        monthly_results = monthly_query.group_by(
            func.strftime("%Y-%m", Absence.start_date),
            Absence.absence_type
        ).all()

        return {
            "by_type": [
                {
                    "type": r.absence_type.value,
                    "count": r.count,
                    "total_days": r.total_days,
                    "avg_days": float(r.avg_days) if r.avg_days else 0
                }
                for r in results
            ],
            "monthly_trend": [
                {
                    "month": r.month,
                    "type": r.absence_type.value,
                    "count": r.count
                }
                for r in monthly_results
            ]
        }

    @staticmethod
    def get_overtime_analytics(
        session: Session,
        company_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Аналитика по переработкам."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=180)

        query = session.query(
            Employee.department,
            func.sum(Overtime.hours).label("total_hours"),
            func.avg(Overtime.hours).label("avg_hours"),
            func.count(Overtime.id).label("count")
        ).join(Employee).filter(
            Overtime.date >= start_date,
            Overtime.date <= end_date
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        results = query.group_by(Employee.department).all()

        # Анализ по сотрудникам с наибольшими переработками
        top_overtime_query = session.query(
            Employee.name,
            Employee.department,
            func.sum(Overtime.hours).label("total_hours")
        ).join(Employee).filter(
            Overtime.date >= start_date,
            Overtime.date <= end_date
        )

        if company_id:
            top_overtime_query = top_overtime_query.filter(Employee.company_id == company_id)

        top_overtime = top_overtime_query.group_by(
            Employee.id
        ).order_by(func.sum(Overtime.hours).desc()).limit(10).all()

        return {
            "by_department": [
                {
                    "department": r.department,
                    "total_hours": float(r.total_hours) if r.total_hours else 0,
                    "avg_hours": float(r.avg_hours) if r.avg_hours else 0,
                    "count": r.count
                }
                for r in results
            ],
            "top_employees": [
                {
                    "name": r.name,
                    "department": r.department,
                    "total_hours": float(r.total_hours) if r.total_hours else 0
                }
                for r in top_overtime
            ]
        }

    @staticmethod
    def get_work_schedule_analytics(
        session: Session,
        company_id: Optional[int] = None
    ) -> Dict:
        """Аналитика по графикам работы."""
        query = session.query(
            Employee.work_schedule,
            func.count(Employee.id).label("count"),
            func.avg(Employee.work_hours_per_week).label("avg_hours")
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        results = query.group_by(Employee.work_schedule).all()

        # Анализ по отделам
        dept_query = session.query(
            Employee.department,
            Employee.work_schedule,
            func.count(Employee.id).label("count")
        )

        if company_id:
            dept_query = dept_query.filter(Employee.company_id == company_id)

        dept_results = dept_query.group_by(
            Employee.department,
            Employee.work_schedule
        ).all()

        return {
            "by_schedule": [
                {
                    "schedule": r.work_schedule.value,
                    "count": r.count,
                    "avg_hours": float(r.avg_hours) if r.avg_hours else 0
                }
                for r in results
            ],
            "by_department": [
                {
                    "department": r.department,
                    "schedule": r.work_schedule.value,
                    "count": r.count
                }
                for r in dept_results
            ]
        }

    @staticmethod
    def get_salary_composition_analytics(
        session: Session,
        company_id: Optional[int] = None,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict:
        """Аналитика структуры ФОТ по компонентам."""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        query = session.query(
            func.sum(SalaryHistory.salary).label("total_salary"),
            func.sum(SalaryHistory.bonus).label("total_bonus"),
            func.sum(SalaryHistory.vacation_pay).label("total_vacation"),
            func.sum(SalaryHistory.sick_leave_pay).label("total_sick_leave"),
            func.sum(SalaryHistory.overtime_pay).label("total_overtime"),
            func.sum(SalaryHistory.ndfl).label("total_ndfl")
        ).join(Employee).filter(
            func.strftime("%Y", SalaryHistory.date) == str(year),
            func.strftime("%m", SalaryHistory.date) == f"{month:02d}"
        )

        if company_id:
            query = query.filter(Employee.company_id == company_id)

        result = query.first()

        total_fot = (
            (result.total_salary or 0) +
            (result.total_bonus or 0) +
            (result.total_vacation or 0) +
            (result.total_sick_leave or 0) +
            (result.total_overtime or 0)
        )

        if total_fot == 0:
            return {
                "components": [],
                "total_fot": 0,
                "total_ndfl": result.total_ndfl or 0
            }

        total_fot_f = float(total_fot)
        return {
            "components": [
                {"name": "Оклад", "value": float(result.total_salary or 0), "percentage": float(result.total_salary or 0) / total_fot_f * 100},
                {"name": "Премии", "value": float(result.total_bonus or 0), "percentage": float(result.total_bonus or 0) / total_fot_f * 100},
                {"name": "Отпускные", "value": float(result.total_vacation or 0), "percentage": float(result.total_vacation or 0) / total_fot_f * 100},
                {"name": "Больничные", "value": float(result.total_sick_leave or 0), "percentage": float(result.total_sick_leave or 0) / total_fot_f * 100},
                {"name": "Переработки", "value": float(result.total_overtime or 0), "percentage": float(result.total_overtime or 0) / total_fot_f * 100},
            ],
            "total_fot": total_fot_f,
            "total_ndfl": float(result.total_ndfl or 0)
        }

    @staticmethod
    def get_employee_turnover_analytics(
        session: Session,
        company_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Аналитика текучести кадров."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        # Уволенные сотрудники
        terminated_query = session.query(
            func.count(Employee.id).label("terminated_count"),
            func.avg(
                func.julianday(Employee.termination_date) - func.julianday(Employee.hire_date)
            ).label("avg_tenure_days")
        ).filter(
            Employee.termination_date.isnot(None),
            Employee.termination_date >= start_date,
            Employee.termination_date <= end_date
        )

        if company_id:
            terminated_query = terminated_query.filter(Employee.company_id == company_id)

        terminated_result = terminated_query.first()

        # Принятые сотрудники
        hired_query = session.query(
            func.count(Employee.id).label("hired_count")
        ).filter(
            Employee.hire_date >= start_date,
            Employee.hire_date <= end_date
        )

        if company_id:
            hired_query = hired_query.filter(Employee.company_id == company_id)

        hired_result = hired_query.first()

        # Среднесписочная численность
        avg_headcount_query = session.query(
            func.avg(
                session.query(func.count(Employee.id))
                .filter(
                    Employee.hire_date <= end_date,
                    or_(
                        Employee.termination_date.is_(None),
                        Employee.termination_date >= start_date
                    )
                )
                .scalar_subquery()
            ).label("avg_headcount")
        )

        avg_headcount = avg_headcount_query.scalar() or 0

        turnover_rate = 0
        if avg_headcount > 0 and terminated_result.terminated_count:
            turnover_rate = (terminated_result.terminated_count / avg_headcount) * 100

        return {
            "terminated_count": terminated_result.terminated_count or 0,
            "hired_count": hired_result.hired_count or 0,
            "avg_tenure_days": float(terminated_result.avg_tenure_days or 0),
            "avg_headcount": float(avg_headcount),
            "turnover_rate": float(turnover_rate),
            "net_change": (hired_result.hired_count or 0) - (terminated_result.terminated_count or 0)
        }

    @staticmethod
    def get_productivity_metrics(
        session: Session,
        company_id: Optional[int] = None,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict:
        """Метрики производительности."""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        # ФОТ на сотрудника
        fot_query = session.query(
            func.sum(
                SalaryHistory.salary + 
                SalaryHistory.bonus + 
                SalaryHistory.vacation_pay + 
                SalaryHistory.sick_leave_pay + 
                SalaryHistory.overtime_pay
            ).label("total_fot"),
            func.count(func.distinct(SalaryHistory.employee_id)).label("employee_count")
        ).join(Employee).filter(
            func.strftime("%Y", SalaryHistory.date) == str(year),
            func.strftime("%m", SalaryHistory.date) == f"{month:02d}"
        )

        if company_id:
            fot_query = fot_query.filter(Employee.company_id == company_id)

        fot_result = fot_query.first()

        fot_per_employee = 0
        if fot_result.employee_count and fot_result.total_fot:
            fot_per_employee = fot_result.total_fot / fot_result.employee_count

        # Процент оплачиваемых дней
        days_query = session.query(
            func.sum(SalaryHistory.working_days).label("total_working_days"),
            func.sum(SalaryHistory.actual_worked_days).label("total_actual_days")
        ).join(Employee).filter(
            func.strftime("%Y", SalaryHistory.date) == str(year),
            func.strftime("%m", SalaryHistory.date) == f"{month:02d}"
        )

        if company_id:
            days_query = days_query.filter(Employee.company_id == company_id)

        days_result = days_query.first()

        attendance_rate = 0
        if days_result.total_working_days and days_result.total_actual_days:
            attendance_rate = (days_result.total_actual_days / days_result.total_working_days) * 100

        return {
            "fot_per_employee": float(fot_per_employee),
            "employee_count": fot_result.employee_count or 0,
            "total_fot": float(fot_result.total_fot or 0),
            "attendance_rate": float(attendance_rate),
            "total_working_days": days_result.total_working_days or 0,
            "total_actual_days": days_result.total_actual_days or 0
        }