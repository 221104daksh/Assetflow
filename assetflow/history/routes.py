import csv
import io
from flask import render_template, request, Response
from flask_login import login_required

from . import bp
from ..extensions import db
from ..models import AuditLog, Asset


@bp.route("/")
@login_required
def index():
    action = request.args.get("action", "").strip()
    asset_id = request.args.get("asset_id", "").strip()

    query = AuditLog.query
    if action:
        query = query.filter(AuditLog.action == action)
    if asset_id:
        asset = Asset.query.filter_by(asset_id=asset_id).first()
        query = query.filter(AuditLog.asset_id == (asset.id if asset else -1))

    logs = query.order_by(AuditLog.timestamp.desc()).limit(500).all()
    actions = [r[0] for r in db.session.query(AuditLog.action).distinct().all()]

    return render_template("history/index.html", logs=logs, actions=actions, action=action, asset_id=asset_id)


@bp.route("/export.csv")
@login_required
def export_csv():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Timestamp", "User", "Action", "Asset", "Field", "Old Value", "New Value"])
    for log in logs:
        writer.writerow([
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            log.user.username if log.user else "system",
            log.action,
            log.asset.asset_id if log.asset else "",
            log.field_changed or "",
            log.old_value or "",
            log.new_value or "",
        ])
    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"},
    )
