from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SelectField,
    IntegerField, SubmitField, TextAreaField
)
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class EmployeeForm(FlaskForm):
    employee_id = StringField("Employee ID", validators=[DataRequired(), Length(max=50)])
    name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    department = StringField("Department", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=150)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=30)])
    submit = SubmitField("Save Employee")


DISK_TYPES = [("SSD", "SSD"), ("HDD", "HDD"), ("NVMe", "NVMe")]
OS_CHOICES = [
    ("Windows", "Windows"),
    ("Linux", "Linux"),
    ("macOS", "macOS"),
]


class AssetForm(FlaskForm):
    asset_id = StringField("Asset ID", validators=[DataRequired(), Length(max=50)])
    asset_tag = StringField("Asset Tag", validators=[DataRequired(), Length(max=50)])
    model_number = StringField("Model Number", validators=[DataRequired(), Length(max=120)])
    manufacturer = StringField("Manufacturer", validators=[DataRequired(), Length(max=100)])
    hostname = StringField("Hostname", validators=[Optional(), Length(max=120)])
    serial_number = StringField("Serial Number", validators=[DataRequired(), Length(max=120)])
    mac_address = StringField("MAC Address", validators=[Optional(), Length(max=30)])
    ip_address = StringField("IP Address", validators=[Optional(), Length(max=50)])
    cpu = StringField("CPU", validators=[Optional(), Length(max=150)])
    cpu_cores = IntegerField("CPU Cores", validators=[Optional(), NumberRange(min=1, max=256)])
    ram = StringField("RAM", validators=[Optional(), Length(max=30)])
    disk_size = StringField("Disk Size", validators=[Optional(), Length(max=30)])
    disk_type = SelectField("Disk Type", choices=DISK_TYPES, validators=[Optional()])
    operating_system = SelectField("Operating System", choices=OS_CHOICES, validators=[DataRequired()])
    os_version = StringField("OS Version", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Save Computer")


class AssignForm(FlaskForm):
    employee_id = SelectField("Employee", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Assign")


class SettingsForm(FlaskForm):
    org_name = StringField("Organization Name", validators=[DataRequired(), Length(max=150)])
    org_logo = FileField("Organization Logo", validators=[
        Optional(), FileAllowed(["jpg", "jpeg", "png", "svg"], "Images only!")
    ])
    public_url = StringField("Public URL", validators=[DataRequired(), Length(max=255)])
    qr_label_title = StringField("QR Label Title", validators=[Optional(), Length(max=150)])
    theme_color = StringField("Theme Color", validators=[Optional(), Length(max=20)])
    default_theme = SelectField("Default Theme", choices=[("light", "Light"), ("dark", "Dark")])
    footer_text = StringField("Footer Text", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save Settings")
