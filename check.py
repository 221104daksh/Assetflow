from app import create_app
from assetflow.models import Asset

app = create_app()

with app.app_context():
    for asset in Asset.query.all():
        print(asset.asset_id, asset.ip_address)