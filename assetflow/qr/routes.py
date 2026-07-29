from flask import render_template, abort
from flask_login import login_required

from . import bp, public_bp
from ..models import Asset, Setting
from ..utils import generate_qr_base64, public_asset_url, log_action, admin_required


@bp.route("/")
@login_required
def index():
    assets = Asset.query.order_by(Asset.asset_id).all()
    qr_codes = {a.asset_id: generate_qr_base64(public_asset_url(a.asset_id)) for a in assets}
    return render_template("qr/index.html", assets=assets, qr_codes=qr_codes)


@bp.route("/<asset_id>/view")
@login_required
def view(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    url = public_asset_url(asset.asset_id)
    qr_image = generate_qr_base64(url)
    log_action("QR Generated", asset=asset)
    return render_template("qr/view.html", asset=asset, qr_image=qr_image, url=url)


@bp.route("/<asset_id>/label")
@login_required
def label(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first_or_404()
    url = public_asset_url(asset.asset_id)
    qr_image = generate_qr_base64(url)
    org_name = Setting.get("org_name", "AssetFlow")
    qr_label_title = Setting.get("qr_label_title", "Scan For Details")
    log_action("QR Printed", asset=asset)
    return render_template(
        "qr/label.html", asset=asset, qr_image=qr_image, url=url,
        org_name=org_name, qr_label_title=qr_label_title,
    )


# --- Public, read-only route. No login required by design. ---
@public_bp.route("/pc/<asset_id>")
def public_view(asset_id):
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if not asset:
        abort(404)
    return render_template("qr/public.html", asset=asset)
