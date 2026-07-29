import io
import re
import ipaddress
import base64
from functools import wraps
from datetime import datetime

import qrcode
from flask import abort, current_app
from flask_login import current_user

from .extensions import db
from .models import AuditLog

MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


def validate_mac(value: str) -> bool:
    """Accepts AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF, rejects everything else."""
    if not value:
        return True  # optional field
    return bool(MAC_RE.match(value.strip()))


def validate_ip(value: str) -> bool:
    """Accepts valid IPv4 or IPv6 addresses."""
    if not value:
        return True  # optional field
    try:
        ipaddress.ip_address(value.strip())
        return True
    except ValueError:
        return False


def normalize_mac(value: str) -> str:
    if not value:
        return value
    return value.strip().upper().replace("-", ":")


def admin_required(view_func):
    """Restrict a route to users with role == 'admin'."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def log_action(action, asset=None, field_changed=None, old_value=None, new_value=None):
    """Create an AuditLog row. Safe to call even for actions with no asset context."""
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else None
    entry = AuditLog(
        asset_id=asset.id if asset else None,
        user_id=user_id,
        action=action,
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        timestamp=datetime.utcnow(),
    )
    db.session.add(entry)
    db.session.commit()


def diff_and_log(asset, old_data: dict, new_data: dict, field_labels: dict):
    """Compare old/new dict of field->value and write one AuditLog row per changed field."""
    for field, label in field_labels.items():
        old_val = old_data.get(field)
        new_val = new_data.get(field)
        if str(old_val) != str(new_val):
            log_action(f"{label} Changed", asset=asset, field_changed=field,
                       old_value=old_val, new_value=new_val)


def generate_qr_base64(url: str) -> str:
    """Generate a QR code PNG for the given URL, return base64 data-URI string."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def public_asset_url(asset_id: str) -> str:
    base = current_app.config.get("PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/pc/{asset_id}"
