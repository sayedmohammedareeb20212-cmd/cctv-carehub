"""
Create default admin account.
Run: python seed_admin.py
"""

from app import create_app
from database import db
from models import Admin
from werkzeug.security import generate_password_hash

app = create_app()

# ══════════════════════════════════════════════
# 👇 CHANGE THESE IF YOU WANT
# ══════════════════════════════════════════════
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
ADMIN_NAME = 'MS Enterprises Admin'
# ══════════════════════════════════════════════

with app.app_context():
    print("Creating admin account...")

    existing = Admin.query.filter_by(username=ADMIN_USERNAME).first()
    if existing:
        print(f"Admin '{ADMIN_USERNAME}' already exists")
    else:
        admin = Admin(
            username=ADMIN_USERNAME,
            name=ADMIN_NAME,
            password=generate_password_hash(ADMIN_PASSWORD)
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created!")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Password: {ADMIN_PASSWORD}")

    print("\nDone. Login at: http://127.0.0.1:5000/admin/login")