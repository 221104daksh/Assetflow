from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from . import bp
from ..extensions import db
from ..models import Asset, Employee
from ..forms import AssetForm, AssignForm
from ..utils import admin_required, log_action, diff_and_log, validate_mac, validate_ip, normalize_mac

FIELD_LABELS = {
    "hostname": "Hostname",
    "asset_tag": "Asset Tag",
    "model_number": "Model",
    "mac_address": "MAC",
    "ip_address": "IP",
    "cpu": "CPU",
    "ram": "RAM",
    "disk_size": "Disk",
    "operating_system": "OS",
}


@bp.route("/")
@login_required
def list_assets():
    q = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    manufacturer = request.args.get("manufacturer", "").strip()
    model = request.args.get("model", "").strip()
    ram = request.args.get("ram", "").strip()
    os_filter = request.args.get("os", "").strip()
    status = request.args.get("status", "").strip()

    query = Asset.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Asset.asset_id.ilike(like), Asset.asset_tag.ilike(like), Asset.hostname.ilike(like),
                Asset.model_number.ilike(like), Asset.serial_number.ilike(like),
                Asset.mac_address.ilike(like), Asset.ip_address.ilike(like),
            )
        )
    if manufacturer:
        query = query.filter(Asset.manufacturer == manufacturer)
    if model:
        query = query.filter(Asset.model_number == model)
    if ram:
        query = query.filter(Asset.ram == ram)
    if os_filter:
        query = query.filter(Asset.operating_system == os_filter)
    if status == "assigned":
        query = query.filter(Asset.employee_id.isnot(None))
    elif status == "available":
        query = query.filter(Asset.employee_id.is_(None))
    if department:
        query = query.join(Employee, isouter=True).filter(Employee.department == department)

    assets = query.order_by(Asset.updated_at.desc()).all()

    manufacturers = [r[0] for r in db.session.query(Asset.manufacturer).distinct().all()]
    models = [r[0] for r in db.session.query(Asset.model_number).distinct().all()]
    rams = [r[0] for r in db.session.query(Asset.ram).distinct().all() if r[0]]
    departments = [r[0] for r in db.session.query(Employee.department).distinct().all()]

    return render_template(
        "assets/list.html", assets=assets, q=q, department=department, manufacturer=manufacturer,
        model=model, ram=ram, os_filter=os_filter, status=status,
        manufacturers=manufacturers, models=models, rams=rams, departments=departments,
    )


@bp.route("/<asset_id>")
@login_required
def detail(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    logs = asset.logs.order_by(db.desc("timestamp")).all()
    assign_form = AssignForm()
    assign_form.employee_id.choices = [(0, "-- Select Employee --")] + [
        (e.id, f"{e.name} ({e.employee_id})") for e in Employee.query.filter(~Employee.asset.has()).all()
    ]
    return render_template("assets/detail.html", asset=asset, logs=logs, assign_form=assign_form)


def _validate_asset_form(form, current_asset=None):
    """Extra server-side validation not covered by WTForms validators. Returns list of errors."""
    errors = []
    if not validate_mac(form.mac_address.data):
        errors.append("MAC Address must be in the format AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF.")
    if not validate_ip(form.ip_address.data):
        errors.append("IP Address must be a valid IPv4 or IPv6 address.")

    for field_name, label in (("asset_id", "Asset ID"), ("asset_tag", "Asset Tag"), ("serial_number", "Serial Number")):
        value = getattr(form, field_name).data.strip()
        existing = Asset.query.filter(getattr(Asset, field_name) == value).first()
        if existing and (current_asset is None or existing.id != current_asset.id):
            errors.append(f"{label} '{value}' is already in use.")

    return errors


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = AssetForm()
    if form.validate_on_submit():
        errors = _validate_asset_form(form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("assets/form.html", form=form, mode="create")

        asset = Asset(
            asset_id=form.asset_id.data.strip(),
            asset_tag=form.asset_tag.data.strip(),
            model_number=form.model_number.data.strip(),
            manufacturer=form.manufacturer.data.strip(),
            hostname=form.hostname.data.strip() if form.hostname.data else None,
            serial_number=form.serial_number.data.strip(),
            mac_address=normalize_mac(form.mac_address.data) if form.mac_address.data else None,
            ip_address=form.ip_address.data.strip() if form.ip_address.data else None,
            cpu=form.cpu.data.strip() if form.cpu.data else None,
            cpu_cores=form.cpu_cores.data,
            ram=form.ram.data.strip() if form.ram.data else None,
            disk_size=form.disk_size.data.strip() if form.disk_size.data else None,
            disk_type=form.disk_type.data,
            operating_system=form.operating_system.data,
            os_version=form.os_version.data.strip() if form.os_version.data else None,
        )
        db.session.add(asset)
        db.session.commit()
        log_action("Computer Created", asset=asset, field_changed="asset", new_value=asset.asset_id)
        flash(f"Computer {asset.asset_id} created successfully.", "success")
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    return render_template("assets/form.html", form=form, mode="create")


@bp.route("/<asset_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    form = AssetForm(obj=asset)

    if form.validate_on_submit():
        errors = _validate_asset_form(form, current_asset=asset)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("assets/form.html", form=form, mode="edit", asset=asset)

        old_data = {k: getattr(asset, k) for k in FIELD_LABELS}

        asset.asset_id = form.asset_id.data.strip()
        asset.asset_tag = form.asset_tag.data.strip()
        asset.model_number = form.model_number.data.strip()
        asset.manufacturer = form.manufacturer.data.strip()
        asset.hostname = form.hostname.data.strip() if form.hostname.data else None
        asset.serial_number = form.serial_number.data.strip()
        asset.mac_address = normalize_mac(form.mac_address.data) if form.mac_address.data else None
        asset.ip_address = form.ip_address.data.strip() if form.ip_address.data else None
        asset.cpu = form.cpu.data.strip() if form.cpu.data else None
        asset.cpu_cores = form.cpu_cores.data
        asset.ram = form.ram.data.strip() if form.ram.data else None
        asset.disk_size = form.disk_size.data.strip() if form.disk_size.data else None
        asset.disk_type = form.disk_type.data
        asset.operating_system = form.operating_system.data
        asset.os_version = form.os_version.data.strip() if form.os_version.data else None
        db.session.commit()

        new_data = {k: getattr(asset, k) for k in FIELD_LABELS}
        diff_and_log(asset, old_data, new_data, FIELD_LABELS)
        log_action("Computer Updated", asset=asset)
        flash("Computer updated successfully.", "success")
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    return render_template("assets/form.html", form=form, mode="edit", asset=asset)


@bp.route("/<asset_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    log_action("Computer Deleted", asset=None, field_changed="asset", old_value=asset.asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash("Computer deleted.", "info")
    return redirect(url_for("assets.list_assets"))


@bp.route("/<asset_id>/assign", methods=["POST"])
@login_required
@admin_required
def assign(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    form = AssignForm()
    form.employee_id.choices = [(0, "-- Select Employee --")] + [
        (e.id, f"{e.name} ({e.employee_id})") for e in Employee.query.all()
    ]

    if not form.validate_on_submit() or not form.employee_id.data:
        flash("Please select a valid employee.", "danger")
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    employee = Employee.query.get_or_404(form.employee_id.data)

    # STRICT 1:1 enforcement -- reject if the employee already owns a different computer.
    if employee.asset and employee.asset.id != asset.id:
        flash("Employee already has an assigned computer. Please unassign the existing computer first.", "danger")
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    previous_employee = asset.employee
    asset.employee_id = employee.id
    db.session.commit()

    if previous_employee and previous_employee.id != employee.id:
        log_action("Asset Reassigned", asset=asset, field_changed="employee",
                   old_value=previous_employee.name, new_value=employee.name)
        flash(f"{asset.asset_id} reassigned from {previous_employee.name} to {employee.name}.", "success")
    else:
        log_action("Asset Assigned", asset=asset, field_changed="employee", new_value=employee.name)
        flash(f"{asset.asset_id} assigned to {employee.name}.", "success")

    return redirect(url_for("assets.detail", asset_id=asset.asset_id))


@bp.route("/<asset_id>/unassign", methods=["POST"])
@login_required
@admin_required
def unassign(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    if not asset.employee:
        flash("This computer is already unassigned.", "warning")
        return redirect(url_for("assets.detail", asset_id=asset.asset_id))

    old_employee = asset.employee
    asset.employee_id = None
    db.session.commit()
    log_action("Asset Unassigned", asset=asset, field_changed="employee", old_value=old_employee.name, new_value=None)
    flash(f"{asset.asset_id} unassigned from {old_employee.name}.", "info")
    return redirect(url_for("assets.detail", asset_id=asset.asset_id))
