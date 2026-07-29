"""Seed the AssetFlow database with demo data.

Usage:
    python seed.py
"""
from app import create_app
from assetflow.extensions import db
from assetflow.models import User, Employee, Asset, Setting
import os

app = create_app()





def run():
    with app.app_context():
        db.create_all()

        # --- Users ---
        if not User.query.filter_by(username="admin").first():
            admin = User(name="Alex Admin", username="admin", email="admin@assetflow.local", role="admin")
            admin.set_password("Admin@123")
            db.session.add(admin)

        if not User.query.filter_by(username="viewer").first():
            viewer = User(name="Vera Viewer", username="viewer", email="viewer@assetflow.local", role="viewer")
            viewer.set_password("Viewer@123")
            db.session.add(viewer)

        db.session.commit()

        # --- Settings ---
        if not Setting.query.filter_by(key="org_name").first():
            Setting.set("org_name", "AssetFlow")
            Setting.set("public_url", "http://localhost:5000")
            Setting.set("qr_label_title", "Scan For Details")
            Setting.set("theme_color", "#4361ee")
            Setting.set("default_theme", "light")
            Setting.set("footer_text", "AssetFlow — IT Asset Management")

        # --- Employees ---
        employees_data = [
            ("EMP-101", "Rahul Verma", "Engineering", "rahul.verma@company.com", "+91 98765 43210"),
            ("EMP-102", "Aman Gupta", "Engineering", "aman.gupta@company.com", "+91 98765 43211"),
            ("EMP-103", "Priya Singh", "Design", "priya.singh@company.com", "+91 98765 43212"),
            ("EMP-104", "Neha Kapoor", "Human Resources", "neha.kapoor@company.com", "+91 98765 43213"),
            ("EMP-105", "Vikram Rao", "Finance", "vikram.rao@company.com", "+91 98765 43214"),
            ("EMP-106", "Sanya Malhotra", "Marketing", "sanya.malhotra@company.com", "+91 98765 43215"),
        ]
        employees = {}
        for emp_id, name, dept, email, phone in employees_data:
            emp = Employee.query.filter_by(employee_id=emp_id).first()
            if not emp:
                emp = Employee(employee_id=emp_id, name=name, department=dept, email=email, phone=phone)
                db.session.add(emp)
            employees[emp_id] = emp
        db.session.commit()

        # --- Assets ---
        assets_data = [
            dict(asset_id="PC-001", asset_tag="AST-0001", model_number="OptiPlex 7010", manufacturer="Dell",
                 hostname="PC-RAHUL-01", serial_number="SN-DL-0001", mac_address="00:1A:2B:3C:4D:5E",
                 ip_address="192.168.1.20", cpu="Intel Core i7-12700", cpu_cores=12, ram="16 GB",
                 disk_size="512 GB", disk_type="SSD", operating_system="Windows", os_version="11 Pro",
                 employee="EMP-101"),
            dict(asset_id="PC-002", asset_tag="AST-0002", model_number="ThinkPad X1 Carbon", manufacturer="Lenovo",
                 hostname="PC-PRIYA-01", serial_number="SN-LN-0002", mac_address="00:1A:2B:3C:4D:5F",
                 ip_address="192.168.1.21", cpu="Intel Core i7-1260P", cpu_cores=12, ram="16 GB",
                 disk_size="1 TB", disk_type="NVMe", operating_system="Windows", os_version="11 Pro",
                 employee="EMP-103"),
            dict(asset_id="PC-003", asset_tag="AST-0003", model_number="MacBook Pro 14", manufacturer="Apple",
                 hostname="PC-NEHA-01", serial_number="SN-AP-0003", mac_address="00:1A:2B:3C:4D:60",
                 ip_address="192.168.1.22", cpu="Apple M3 Pro", cpu_cores=11, ram="18 GB",
                 disk_size="512 GB", disk_type="SSD", operating_system="macOS", os_version="Sonoma 14.5",
                 employee="EMP-104"),
            dict(asset_id="PC-004", asset_tag="AST-0004", model_number="EliteDesk 800", manufacturer="HP",
                 hostname="PC-VIKRAM-01", serial_number="SN-HP-0004", mac_address="00:1A:2B:3C:4D:61",
                 ip_address="192.168.1.23", cpu="Intel Core i5-13500", cpu_cores=14, ram="8 GB",
                 disk_size="256 GB", disk_type="SSD", operating_system="Windows", os_version="10 Pro",
                 employee="EMP-105"),
            dict(asset_id="PC-005", asset_tag="AST-0005", model_number="XPS 15", manufacturer="Dell",
                 hostname="PC-SPARE-01", serial_number="SN-DL-0005", mac_address="00:1A:2B:3C:4D:62",
                 ip_address="192.168.1.24", cpu="Intel Core i7-13700H", cpu_cores=14, ram="32 GB",
                 disk_size="1 TB", disk_type="NVMe", operating_system="Linux", os_version="Ubuntu 24.04",
                 employee=None),
            dict(asset_id="PC-006", asset_tag="AST-0006", model_number="Latitude 5440", manufacturer="Dell",
                 hostname="PC-SPARE-02", serial_number="SN-DL-0006", mac_address="00:1A:2B:3C:4D:63",
                 ip_address="192.168.1.25", cpu="Intel Core i5-1335U", cpu_cores=10, ram="16 GB",
                 disk_size="512 GB", disk_type="SSD", operating_system="Windows", os_version="11 Pro",
                 employee=None),
        ]

        for data in assets_data:
            emp_key = data.pop("employee")
            asset = Asset.query.filter_by(asset_id=data["asset_id"]).first()
            if not asset:
                asset = Asset(**data)
                if emp_key:
                    asset.employee = employees[emp_key]
                db.session.add(asset)
        db.session.commit()

        print("Seed complete.")
        print("  Admin login:  admin / Admin@123")
        print("  Viewer login: viewer / Viewer@123")


if __name__ == "__main__":
    run()
