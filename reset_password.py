"""
Reset any customer's password.
Edit the values below, then run: python reset_password.py
"""

from app import create_app
from database import db
from models import Customer
from werkzeug.security import generate_password_hash

app = create_app()

# ══════════════════════════════════════════
# 👇 EDIT THESE TWO LINES
# ══════════════════════════════════════════
CUSTOMER_ID = "CUST1001"           # ← Change to YOUR customer ID
NEW_PASSWORD = "demo123"            # ← Set the new password
# ══════════════════════════════════════════

with app.app_context():
    print("=" * 60)
    print("  RESET CUSTOMER PASSWORD")
    print("=" * 60)

    all_customers = Customer.query.all()

    if not all_customers:
        print("\n❌ No customers in database.")
        print("   Register at: http://127.0.0.1:5000/customer-register")
        exit()

    print(f"\nTotal customers: {len(all_customers)}\n")
    print("Available customer IDs:")
    for c in all_customers:
        print(f"   {c.customer_id}  |  {c.name}  |  {c.email}")

    print()

    customer = Customer.query.filter_by(customer_id=CUSTOMER_ID).first()

    if not customer:
        print(f"❌ Customer '{CUSTOMER_ID}' not found.")
        print("   Use one of the IDs listed above.")
    else:
        customer.password = generate_password_hash(NEW_PASSWORD)
        db.session.commit()

        print(f"✅ Password reset successfully!")
        print(f"   Customer ID: {customer.customer_id}")
        print(f"   Name: {customer.name}")
        print(f"   New Password: {NEW_PASSWORD}")
        print()
        print("Now login at: http://127.0.0.1:5000/customer-login")