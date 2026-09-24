"""
Create demo technicians + owner account.
Run: python seed_technicians.py
"""

from app import create_app
from database import db
from models import Technician
from werkzeug.security import generate_password_hash

app = create_app()

TECHNICIANS = [
    {
        "technician_id": "TECH1001",
        "name": "Arjun Mehta",
        "mobile": "9876500001",
        "email": "arjun@msenterprises.com",
        "specialization": "CCTV Installation & DVR Repair",
        "experience": 7,
        "service_area": "Mangalore, Kinnikambla",
        "password": "Arjun@123"
    },
    {
        "technician_id": "TECH1002",
        "name": "Priya Nair",
        "mobile": "9876500002",
        "email": "priya@msenterprises.com",
        "specialization": "CCTV Maintenance",
        "experience": 5,
        "service_area": "Bajpe, Mangalore",
        "password": "Priya@123"
    },
    {
        "technician_id": "OWNER01",
        "name": "Sayed Mohammed Areeb",
        "mobile": "8722782100",
        "email": "m.s.enterprises2100@outlook.com",
        "specialization": "Owner / Manager",
        "experience": 10,
        "service_area": "Mangalore",
        "password": "cctv@123"
    },
]

with app.app_context():
    print("Seeding accounts...")
    added = 0
    for t in TECHNICIANS:
        if Technician.query.filter_by(technician_id=t["technician_id"]).first():
            print(f"SKIP: {t['technician_id']} exists")
            continue

        tech = Technician(
            technician_id=t["technician_id"],
            name=t["name"],
            mobile=t["mobile"],
            email=t["email"],
            specialization=t["specialization"],
            experience=t["experience"],
            service_area=t["service_area"],
            password=generate_password_hash(t["password"])
        )
        db.session.add(tech)
        added += 1
        print(f"ADDED: {t['technician_id']} ({t['name']})")

    db.session.commit()
    print(f"\n✅ Added: {added}")