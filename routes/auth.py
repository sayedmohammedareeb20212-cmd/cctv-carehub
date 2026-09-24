from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Customer, Technician

auth_bp = Blueprint('auth', __name__)


# ==================== CUSTOMER REGISTER ====================
@auth_bp.route('/customer-register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        location = request.form.get('location', '').strip()
        password = request.form.get('password', '')

        if not all([name, mobile, email, location, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.customer_register'))

        if Customer.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.customer_register'))

        count = Customer.query.count()
        customer_id = f"CUST{1001 + count}"
        hashed = generate_password_hash(password)

        new_customer = Customer(
            customer_id=customer_id,
            name=name, mobile=mobile, email=email,
            location=location, password=hashed
        )
        db.session.add(new_customer)
        db.session.commit()

        flash(f'Registration successful! Your Customer ID is {customer_id}', 'success')
        return redirect(url_for('auth.customer_login'))

    return render_template('customer_register.html')


# ==================== CUSTOMER LOGIN ====================
@auth_bp.route('/customer-login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        customer_id = request.form.get('customerId', '').strip().upper()
        password = request.form.get('password', '')

        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if not customer or not check_password_hash(customer.password, password):
            flash('Invalid Customer ID or Password', 'error')
            return redirect(url_for('auth.customer_login'))

        session.permanent = True
        session['user_id'] = customer.id
        session['customer_id'] = customer.customer_id
        session['user_name'] = customer.name
        session['role'] = 'customer'

        return redirect(url_for('complaints.customer_dashboard'))

    return render_template('customer_login.html')


# ==================== TECHNICIAN LOGIN ====================
@auth_bp.route('/technician-login', methods=['GET', 'POST'])
def technician_login():
    if request.method == 'POST':
        technician_id = request.form.get('technicianId', '').strip().upper()
        password = request.form.get('password', '')

        tech = Technician.query.filter_by(technician_id=technician_id).first()

        if not tech or not check_password_hash(tech.password, password):
            flash('Invalid Technician ID or Password', 'error')
            return redirect(url_for('auth.technician_login'))

        session.permanent = True
        session['user_id'] = tech.id
        session['technician_id'] = tech.technician_id
        session['user_name'] = tech.name
        session['role'] = 'technician'

        return redirect(url_for('complaints.technician_dashboard'))

    return render_template('technician_login.html')


# ==================== FORGOT CUSTOMER ID ====================
@auth_bp.route('/forgot-id', methods=['GET', 'POST'])
def forgot_id():
    customer = None
    error = None

    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()

        if not mobile:
            error = 'Please enter your registered mobile number'
        else:
            customer = Customer.query.filter_by(mobile=mobile).first()

            if not customer:
                error = f'No account found with mobile number: {mobile}'

    return render_template('forgot_id.html', customer=customer, error=error)


# ==================== FORGOT PASSWORD ====================
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    customer = None
    error = None
    success = None

    if request.method == 'POST':
        customer_id = request.form.get('customerId', '').strip().upper()
        mobile = request.form.get('mobile', '').strip()
        new_password = request.form.get('newPassword', '')

        if not all([customer_id, mobile, new_password]):
            error = 'All fields are required'
        elif len(new_password) < 6:
            error = 'Password must be at least 6 characters'
        else:
            customer = Customer.query.filter_by(customer_id=customer_id).first()

            if not customer:
                error = f'No account found with ID: {customer_id}'
            elif customer.mobile != mobile:
                error = 'Mobile number does not match our records'
            else:
                customer.password = generate_password_hash(new_password)
                db.session.commit()
                success = 'Password reset successfully! You can now login.'
                customer = None

    return render_template('forgot_password.html', error=error, success=success)


# ==================== LOGOUT ====================
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))