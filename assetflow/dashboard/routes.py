from datetime import datetime, timedelta
from flask import render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, extract

from . import bp
from ..extensions import db
from ..models import Asset, Employee, AuditLog


@bp.route("/")
@login_required
def index():
    total_assets = Asset.query.count()
    assigned_assets = Asset.query.filter(Asset.employee_id.isnot(None)).count()
    available_assets = total_assets - assigned_assets
    total_employees = Employee.query.count()

    departments = db.session.query(func.count(func.distinct(Employee.department))).scalar() or 0
    manufacturers = db.session.query(func.count(func.distinct(Asset.manufacturer))).scalar() or 0

    windows_pcs = Asset.query.filter(Asset.operating_system == "Windows").count()
    linux_pcs = Asset.query.filter(Asset.operating_system == "Linux").count()
    mac_pcs = Asset.query.filter(Asset.operating_system == "macOS").count()

    now = datetime.utcnow()
    added_this_month = Asset.query.filter(
        extract("year", Asset.created_at) == now.year,
        extract("month", Asset.created_at) == now.month,
    ).count()

    # Chart: assigned vs available
    assigned_vs_available = {"labels": ["Assigned", "Available"], "data": [assigned_assets, available_assets]}

    # Chart: assets by department (via assigned employee's department)
    dept_rows = (
        db.session.query(Employee.department, func.count(Asset.id))
        .join(Asset, Asset.employee_id == Employee.id)
        .group_by(Employee.department)
        .all()
    )
    by_department = {"labels": [r[0] for r in dept_rows], "data": [r[1] for r in dept_rows]}

    # Chart: assets by OS
    os_rows = db.session.query(Asset.operating_system, func.count(Asset.id)).group_by(Asset.operating_system).all()
    by_os = {"labels": [r[0] for r in os_rows], "data": [r[1] for r in os_rows]}

    # Chart: assets by manufacturer
    mfr_rows = db.session.query(Asset.manufacturer, func.count(Asset.id)).group_by(Asset.manufacturer).all()
    by_manufacturer = {"labels": [r[0] for r in mfr_rows], "data": [r[1] for r in mfr_rows]}

    recent_assets = Asset.query.order_by(Asset.updated_at.desc()).limit(6).all()
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    recent_assignments = (
        AuditLog.query.filter(AuditLog.action.in_(["Asset Assigned", "Asset Reassigned", "Asset Unassigned"]))
        .order_by(AuditLog.timestamp.desc())
        .limit(6)
        .all()
    )

    stats = {
        "total_assets": total_assets,
        "assigned_assets": assigned_assets,
        "available_assets": available_assets,
        "total_employees": total_employees,
        "departments": departments,
        "manufacturers": manufacturers,
        "windows_pcs": windows_pcs,
        "linux_pcs": linux_pcs,
        "mac_pcs": mac_pcs,
        "added_this_month": added_this_month,
    }

    return render_template(
        "dashboard/index.html",
        stats=stats,
        assigned_vs_available=assigned_vs_available,
        by_department=by_department,
        by_os=by_os,
        by_manufacturer=by_manufacturer,
        recent_assets=recent_assets,
        recent_activity=recent_activity,
        recent_assignments=recent_assignments,
    )


@bp.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("dashboard.index"))

    like = f"%{q}%"
    asset = Asset.query.filter(
        db.or_(
            Asset.asset_id.ilike(like),
            Asset.asset_tag.ilike(like),
            Asset.hostname.ilike(like),
            Asset.model_number.ilike(like),
            Asset.serial_number.ilike(like),
            Asset.mac_address.ilike(like),
            Asset.ip_address.ilike(like),
        )
    ).first()
    if asset:
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    employee = Employee.query.filter(
        db.or_(
            Employee.name.ilike(like),
            Employee.employee_id.ilike(like),
            Employee.department.ilike(like),
        )
    ).first()
    if employee:
        return redirect(url_for("employees.detail", employee_id=employee.employee_id))

    return redirect(url_for("assets.list_assets", q=q))
