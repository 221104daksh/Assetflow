from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from . import bp
from ..extensions import db
from ..models import Employee, AuditLog
from ..forms import EmployeeForm
from ..utils import admin_required, log_action, diff_and_log


@bp.route("/")
@login_required
def list_employees():
    q = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    assignment = request.args.get("assignment", "").strip()

    query = Employee.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Employee.name.ilike(like), Employee.employee_id.ilike(like), Employee.department.ilike(like))
        )
    if department:
        query = query.filter(Employee.department == department)
    if assignment == "assigned":
        query = query.filter(Employee.asset.has())
    elif assignment == "unassigned":
        query = query.filter(~Employee.asset.has())

    employees = query.order_by(Employee.created_at.desc()).all()
    departments = [r[0] for r in db.session.query(Employee.department).distinct().all()]

    return render_template(
        "employees/list.html", employees=employees, departments=departments,
        q=q, department=department, assignment=assignment,
    )


@bp.route("/<employee_id>")
@login_required
def detail(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first_or_404()
    history = (
        AuditLog.query.join(Employee, isouter=True)
        .filter(AuditLog.asset_id == (employee.asset.id if employee.asset else -1))
        .order_by(AuditLog.timestamp.desc())
        .all()
        if employee.asset
        else []
    )
    return render_template("employees/detail.html", employee=employee, history=history)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = EmployeeForm()
    if form.validate_on_submit():
        if Employee.query.filter_by(employee_id=form.employee_id.data.strip()).first():
            flash("Employee ID already exists.", "danger")
            return render_template("employees/form.html", form=form, mode="create")

        employee = Employee(
            employee_id=form.employee_id.data.strip(),
            name=form.name.data.strip(),
            department=form.department.data.strip(),
            email=form.email.data.strip() if form.email.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
        )
        db.session.add(employee)
        db.session.commit()
        log_action("Employee Created", field_changed="employee", new_value=employee.employee_id)
        flash(f"Employee {employee.name} created successfully.", "success")
        return redirect(url_for("employees.detail", employee_id=employee.employee_id))

    return render_template("employees/form.html", form=form, mode="create")


@bp.route("/<employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first_or_404()
    form = EmployeeForm(obj=employee)

    if form.validate_on_submit():
        existing = Employee.query.filter_by(employee_id=form.employee_id.data.strip()).first()
        if existing and existing.id != employee.id:
            flash("Employee ID already exists.", "danger")
            return render_template("employees/form.html", form=form, mode="edit", employee=employee)

        old = {"name": employee.name, "department": employee.department, "email": employee.email}
        employee.employee_id = form.employee_id.data.strip()
        employee.name = form.name.data.strip()
        employee.department = form.department.data.strip()
        employee.email = form.email.data.strip() if form.email.data else None
        employee.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()

        new = {"name": employee.name, "department": employee.department, "email": employee.email}
        if employee.asset:
            diff_and_log(employee.asset, old, new, {"name": "Employee Name", "department": "Department", "email": "Employee Email"})
        flash("Employee updated successfully.", "success")
        return redirect(url_for("employees.detail", employee_id=employee.employee_id))

    return render_template("employees/form.html", form=form, mode="edit", employee=employee)


@bp.route("/<employee_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first_or_404()
    if employee.asset:
        flash("Unassign the employee's computer before deleting.", "warning")
        return redirect(url_for("employees.detail", employee_id=employee.employee_id))

    log_action("Employee Deleted", field_changed="employee", old_value=employee.employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted.", "info")
    return redirect(url_for("employees.list_employees"))
