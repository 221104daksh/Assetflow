# AssetFlow — IT Asset Management System

A production-ready Flask application for managing employees, computers/assets,
assignments, QR labels, audit history, dashboards, and reports.

## Stack
Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-Bcrypt, Flask-WTF, Flask-Caching,
Bootstrap 5, Chart.js, qrcode/Pillow. SQLite by default; switch to PostgreSQL by changing
`DATABASE_URL` only.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # edit SECRET_KEY / PUBLIC_BASE_URL as needed

python seed.py                  # creates tables + demo data

flask run                       # or: python app.py
```

App runs at http://localhost:5000

### Demo logins
| Role   | Username | Password    |
|--------|----------|-------------|
| Admin  | admin    | Admin@123   |
| Viewer | viewer   | Viewer@123  |

## Project layout

```
assetflow/
├── app.py                  # application factory
├── config.py                # DATABASE_URL / SECRET_KEY / etc.
├── seed.py                  # demo data
├── requirements.txt
├── assetflow/
│   ├── auth/                # login/logout, dark mode toggle
│   ├── dashboard/           # stats + charts + global search
│   ├── employees/           # employee CRUD
│   ├── assets/               # asset CRUD + assignment engine
│   ├── history/              # audit timeline + CSV export
│   ├── qr/                   # admin QR views + public /pc/<id> route
│   ├── settings/             # org settings + reports/export
│   ├── models.py
│   ├── forms.py
│   ├── utils.py              # validators, audit logger, QR generator
│   ├── static/{css,js,images}
│   └── templates/
```

## Key design points

- **Strict 1:1 Employee ↔ Asset** enforced with a `UNIQUE` foreign key
  (`assets.employee_id`) at the database level, not just in application code.
- **Assignment engine** (`assets/routes.py`) blocks assigning a second computer
  to an employee who already has one, with the exact message:
  *"Employee already has an assigned computer. Please unassign the existing
  computer first."* Reassigning automatically clears the previous ownership.
- **Status is derived, never stored/edited** — `Asset.status` and
  `Employee.status` are computed properties based on the FK.
- **QR codes encode only the permanent URL** (`/pc/<asset_id>`), never
  specifications. The public page reads live from the database, so edits
  show up immediately without regenerating the QR.
- **Audit log** row is written on every create/update/delete/assign/
  reassign/unassign/QR-view/QR-print action, with old/new values.
- **Dark mode** is stored both in `localStorage` (instant on load) and on
  `User.dark_mode` (persists across logout/login and devices).
- **MAC/IPv4/IPv6 validation** happens server-side in `utils.py`
  (`validate_mac`, `validate_ip`), independent of any client-side checks.

## Switching to PostgreSQL

Set `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/assetflow
```
No code changes required.

## Running the acceptance test

1. Log in as `admin`.
2. Create employees `EMP-101` (Rahul) and `EMP-102` (Aman) — or use seeded data.
3. Create computer `PC-001`, tag `AST-0001`, model `Dell OptiPlex 7010`,
   MAC `00:1A:2B:3C:4D:5E`.
4. Assign `PC-001` to Rahul from the asset detail page.
5. Try assigning another computer to Rahul — verify the block message appears.
6. Open **QR Codes** → View → Print Label for `PC-001`.
7. Scan the QR with any phone camera — it opens `/pc/PC-001` in the browser.
8. Edit `PC-001`: update RAM and IP address.
9. Reassign `PC-001` to Aman.
10. Scan the same QR again — updated hardware + Aman now show, no QR regeneration needed.
11. Check **History** — every step above is logged with old/new values.
12. Toggle dark mode, log out, log back in — the preference persists.
