import os
import csv
import io
from flask import render_template, redirect, url_for, flash, current_app, Response
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import bp
from ..models import Setting, Asset, Employee, AuditLog
from ..forms import SettingsForm
from ..utils import admin_required, log_action


@bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    form = SettingsForm()
    if form.validate_on_submit():
        Setting.set("org_name", form.org_name.data.strip())
        Setting.set("public_url", form.public_url.data.strip())
        Setting.set("qr_label_title", form.qr_label_title.data.strip() if form.qr_label_title.data else "Scan For Details")
        Setting.set("theme_color", form.theme_color.data.strip() if form.theme_color.data else "#4361ee")
        Setting.set("default_theme", form.default_theme.data)
        Setting.set("footer_text", form.footer_text.data.strip() if form.footer_text.data else "")

        file = form.org_logo.data
        if file and getattr(file, "filename", ""):
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            Setting.set("org_logo", filename)

        log_action("Settings Updated")
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings.index"))

    form.org_name.data = Setting.get("org_name", "AssetFlow")
    form.public_url.data = Setting.get("public_url", current_app.config.get("PUBLIC_BASE_URL", ""))
    form.qr_label_title.data = Setting.get("qr_label_title", "Scan For Details")
    form.theme_color.data = Setting.get("theme_color", "#4361ee")
    form.default_theme.data = Setting.get("default_theme", "light")
    form.footer_text.data = Setting.get("footer_text", "")

    logo = Setting.get("org_logo", "")
    return render_template("settings/index.html", form=form, logo=logo)


@bp.route("/reports")
@login_required
def reports():
    return render_template("settings/reports.html")


def _csv_response(rows, header, filename):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return Response(buf.getvalue(), mimetype="text/csv",
                     headers={"Content-Disposition": f"attachment; filename={filename}"})


@bp.route("/reports/assets.csv")
@login_required
def export_assets_csv():
    assets = Asset.query.order_by(Asset.asset_id).all()
    rows = [
        [a.asset_id, a.asset_tag, a.model_number, a.manufacturer, a.hostname, a.serial_number,
         a.mac_address, a.ip_address, a.cpu, a.ram, a.disk_size, a.disk_type,
         a.operating_system, a.os_version, a.employee.name if a.employee else "", a.status]
        for a in assets
    ]
    header = ["Asset ID", "Asset Tag", "Model", "Manufacturer", "Hostname", "Serial Number",
              "MAC", "IP", "CPU", "RAM", "Disk", "Disk Type", "OS", "OS Version", "Assigned To", "Status"]
    return _csv_response(rows, header, "assets_report.csv")


@bp.route("/reports/employees.csv")
@login_required
def export_employees_csv():
    employees = Employee.query.order_by(Employee.employee_id).all()
    rows = [
        [e.employee_id, e.name, e.department, e.email, e.phone,
         e.asset.asset_id if e.asset else "", e.status]
        for e in employees
    ]
    header = ["Employee ID", "Name", "Department", "Email", "Phone", "Assigned Computer", "Status"]
    return _csv_response(rows, header, "employees_report.csv")


@bp.route("/reports/audit.csv")
@login_required
def export_audit_csv():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    rows = [
        [log.timestamp.strftime("%Y-%m-%d %H:%M:%S"), log.user.username if log.user else "system",
         log.action, log.asset.asset_id if log.asset else "", log.field_changed or "",
         log.old_value or "", log.new_value or ""]
        for log in logs
    ]
    header = ["Timestamp", "User", "Action", "Asset", "Field", "Old Value", "New Value"]
    return _csv_response(rows, header, "audit_report.csv")
