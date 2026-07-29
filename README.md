# 🚀 AssetFlow — IT Asset Management System

A production-ready **Flask-based IT Asset Management System** for managing employees, computers/assets, assignments, QR labels, audit history, dashboards, reports, and organization settings.

## 🌐 Live Demo

**Application URL**

👉 https://assetflow-5.onrender.com/auth/login

### Demo Credentials

| Role | Username | Password |
|------|----------|-----------|
| Admin | `admin` | `admin123` |
| Viewer | `viewer` | `viewer123` |

---

# ✨ Features

- 🔐 Role-Based Authentication (Admin & Viewer)
- 👨‍💼 Employee Management
- 💻 Computer / Asset Management
- 🔄 One-to-One Employee ↔ Asset Assignment
- 🏷 Asset Tags & Model Numbers
- 🌐 MAC Address & IP Address Tracking
- 📱 QR Code Generation & Public Asset Page
- 📜 Complete Audit History
- 📊 Dashboard with Statistics & Charts
- 🌙 Dark Mode
- 📄 Reports & Export
- ⚙ Organization Settings
- 🔒 CSRF Protection
- 🗄 SQLite & PostgreSQL Support

---

# 🛠 Tech Stack

### Backend
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Bcrypt
- Flask-WTF
- Flask-Caching

### Frontend
- Bootstrap 5
- Chart.js
- Bootstrap Icons

### Database
- SQLite
- PostgreSQL (Neon, Render, Railway, etc.)

### Other Libraries
- qrcode
- Pillow

---

# 🚀 Live Deployment

The application is deployed on **Render**.

### Login Page

https://assetflow-5.onrender.com/auth/login

---

# ⚙ Local Installation

```bash
git clone <your-repository-url>

cd AssetFlow

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python seed.py

python app.py
```

Application runs on

```
http://localhost:5000
```

---

# 📁 Project Structure

```
assetflow/
│
├── app.py
├── config.py
├── seed.py
├── requirements.txt
│
├── assetflow/
│   ├── auth/
│   ├── dashboard/
│   ├── employees/
│   ├── assets/
│   ├── history/
│   ├── qr/
│   ├── settings/
│   ├── models.py
│   ├── forms.py
│   ├── utils.py
│   ├── templates/
│   └── static/
│
└── instance/
```

---

# 💻 Core Functionalities

## Employee Management

- Add Employees
- Update Employees
- Delete Employees
- Department Management

---

## Asset Management

- Asset ID
- Asset Tag
- Model Number
- Manufacturer
- Hostname
- Serial Number
- MAC Address
- IP Address
- CPU
- RAM
- Disk Size
- Disk Type
- Operating System

---

## Asset Assignment

Strict **1 Employee ↔ 1 Computer**

- Assign Computer
- Reassign Computer
- Unassign Computer

The application prevents assigning multiple computers to the same employee.

---

## QR Code System

Each computer receives a QR Code.

Scanning the QR opens a public page:

```
/pc/<asset_id>
```

The QR stores only the asset URL.

Asset information is fetched live from the database, so no QR regeneration is required after updates.

---

## Audit History

Every action is automatically logged.

Examples:

- Create Asset
- Update Asset
- Delete Asset
- Assign
- Reassign
- Unassign
- QR View
- QR Print

---

## Dashboard

- Total Assets
- Assigned Assets
- Available Assets
- Total Employees
- Charts
- Search

---

## Reports

Generate reports for:

- Assets
- Employees
- Assignment History

---

## Dark Mode

Dark Mode preference is saved:

- Browser Local Storage
- User Account

---

# 🔒 Validation

Server-side validation includes:

- MAC Address
- IPv4
- IPv6
- Required Fields
- Duplicate Asset IDs
- Duplicate Employee IDs

---

# PostgreSQL Support

Simply update your `.env`:

```env
DATABASE_URL=postgresql://username:password@hostname:5432/database
```

No code changes are required.

---

# 🧪 Acceptance Test

1. Login as **Admin**
2. Create Employees
3. Create Computer
4. Assign Computer
5. Verify one-to-one assignment restriction
6. Generate QR Code
7. Scan QR Code
8. Update Asset Information
9. Reassign Asset
10. Verify Audit History
11. Toggle Dark Mode
12. Logout & Login again

---

# 📸 Screenshots

Add screenshots here.

Examples:

- Login
- Dashboard
- Employees
- Assets
- QR Codes
- Reports
- Dark Mode

---

# 👨‍💻 Author

**Daksh Sharma**

B.Tech CSE (AI & ML)

---

# 🌐 Live Application

**AssetFlow**

https://assetflow-5.onrender.com/auth/login
