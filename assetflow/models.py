from datetime import datetime
from flask_login import UserMixin
from .extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="viewer")  # admin | viewer
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One employee <-> one asset, backref gives the reverse side.
    asset = db.relationship(
        "Asset",
        back_populates="employee",
        uselist=False,
    )

    @property
    def status(self):
        return "Assigned" if self.asset else "Unassigned"

    def __repr__(self):
        return f"<Employee {self.employee_id} {self.name}>"


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False, index=True)
    model_number = db.Column(db.String(120), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False, index=True)
    hostname = db.Column(db.String(120), nullable=True)
    serial_number = db.Column(db.String(120), unique=True, nullable=False, index=True)
    mac_address = db.Column(db.String(30), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    cpu = db.Column(db.String(150), nullable=True)
    cpu_cores = db.Column(db.Integer, nullable=True)
    ram = db.Column(db.String(30), nullable=True)  # e.g. "16 GB"
    disk_size = db.Column(db.String(30), nullable=True)  # e.g. "512 GB"
    disk_type = db.Column(db.String(20), nullable=True)  # SSD / HDD / NVMe
    operating_system = db.Column(db.String(50), nullable=False, index=True)  # Windows/Linux/macOS
    os_version = db.Column(db.String(50), nullable=True)

    # STRICT 1:1 -- unique constraint at the DB level, nullable so a
    # computer can remain unassigned.
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )
    employee = db.relationship("Employee", back_populates="asset")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def status(self):
        return "Assigned" if self.employee_id else "Available"

    def __repr__(self):
        return f"<Asset {self.asset_id}>"


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id", ondelete="CASCADE"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(80), nullable=False)  # e.g. "Computer Created"
    field_changed = db.Column(db.String(80), nullable=True)
    old_value = db.Column(db.String(255), nullable=True)
    new_value = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    asset = db.relationship("Asset", backref=db.backref("logs", lazy="dynamic", cascade="all,delete"))
    user = db.relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.action} @ {self.timestamp}>"


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get(key, default=None):
        row = Setting.query.filter_by(key=key).first()
        return row.value if row else default

    @staticmethod
    def set(key, value):
        row = Setting.query.filter_by(key=key).first()
        if row:
            row.value = value
        else:
            row = Setting(key=key, value=value)
            db.session.add(row)
        db.session.commit()
