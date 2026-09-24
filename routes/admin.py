from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Admin, Customer, Technician, Complaint
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required():
    """Check if admin is logged in."""
    return session.get('role') == 'admin'


# ==================== ADMIN LOGIN ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        if not admin or not check_password_hash(admin.password, password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin.login'))

        session['user_id'] = admin.id
        session['admin_username'] = admin.username
        session['user_name'] = admin.name
        session['role'] = 'admin'

        return redirect(url_for('admin.dashboard'))

    return render_template('admin_login.html')


# ==================== ADMIN LOGOUT ====================
@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))


# ==================== DASHBOARD ====================
@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    # Stats
    total_customers = Customer.query.count()
    total_technicians = Technician.query.count()
    total_complaints = Complaint.query.count()

    pending = Complaint.query.filter_by(status='pending').count()
    in_progress = Complaint.query.filter_by(status='in-progress').count()
    resolved = Complaint.query.filter_by(status='resolved').count()

    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_complaints = Complaint.query.filter(Complaint.created_at >= today_start).count()

    # This week
    week_start = datetime.utcnow() - timedelta(days=7)
    week_complaints = Complaint.query.filter(Complaint.created_at >= week_start).count()
    week_resolved = Complaint.query.filter(
        Complaint.resolved_at >= week_start
    ).count()

    # Recent complaints (10)
    recent_complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).limit(10).all()

    # Technicians list
    technicians = Technician.query.order_by(
        Technician.is_available.desc()
    ).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        user_name=session['user_name'],
        stats={
            'customers': total_customers,
            'technicians': total_technicians,
            'complaints': total_complaints,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved,
            'today': today_complaints,
            'week': week_complaints,
            'week_resolved': week_resolved
        },
        recent_complaints=recent_complaints,
        technicians=technicians
    )


# ==================== COMPLAINTS ====================
@admin_bp.route('/complaints')
def complaints():
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    # Filters
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    search_query = request.args.get('search', '').strip()

    query = Complaint.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    if search_query:
        query = query.filter(
            db.or_(
                Complaint.complaint_id.ilike(f'%{search_query}%'),
                Complaint.customer_name.ilike(f'%{search_query}%'),
                Complaint.customer_mobile.ilike(f'%{search_query}%'),
                Complaint.complaint_type.ilike(f'%{search_query}%')
            )
        )

    all_complaints = query.order_by(Complaint.created_at.desc()).all()

    # For assignment dropdown
    technicians = Technician.query.order_by(Technician.name).all()

    return render_template(
        'admin_complaints.html',
        user_name=session['user_name'],
        complaints=all_complaints,
        technicians=technicians,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search_query=search_query
    )


# ==================== ASSIGN COMPLAINT ====================
@admin_bp.route('/complaint/<int:complaint_id>/assign', methods=['POST'])
def assign_complaint(complaint_id):
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    technician_id = request.form.get('technician_id', '').strip()

    if technician_id:
        complaint.technician_id = technician_id
        if complaint.status == 'pending':
            complaint.status = 'in-progress'
        db.session.commit()
        flash(f'Assigned to {technician_id}', 'success')
    else:
        flash('No technician selected', 'error')

    return redirect(url_for('admin.complaints'))


# ==================== DELETE COMPLAINT ====================
@admin_bp.route('/complaint/<int:complaint_id>/delete', methods=['POST'])
def delete_complaint(complaint_id):
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint deleted', 'success')
    return redirect(url_for('admin.complaints'))


# ==================== CUSTOMERS ====================
@admin_bp.route('/customers')
def customers():
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    search_query = request.args.get('search', '').strip()

    query = Customer.query

    if search_query:
        query = query.filter(
            db.or_(
                Customer.customer_id.ilike(f'%{search_query}%'),
                Customer.name.ilike(f'%{search_query}%'),
                Customer.mobile.ilike(f'%{search_query}%'),
                Customer.email.ilike(f'%{search_query}%')
            )
        )

    all_customers = query.order_by(Customer.created_at.desc()).all()

    # Complaint count per customer
    complaint_counts = {}
    for c in all_customers:
        complaint_counts[c.customer_id] = Complaint.query.filter_by(
            customer_id=c.customer_id
        ).count()

    return render_template(
        'admin_customers.html',
        user_name=session['user_name'],
        customers=all_customers,
        complaint_counts=complaint_counts,
        search_query=search_query
    )


# ==================== DELETE CUSTOMER ====================
@admin_bp.route('/customer/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted', 'success')
    return redirect(url_for('admin.customers'))


# ==================== TECHNICIANS ====================
@admin_bp.route('/technicians', methods=['GET', 'POST'])
def technicians():
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        # Add new technician
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        specialization = request.form.get('specialization', '').strip()
        experience = request.form.get('experience', '0')
        service_area = request.form.get('service_area', '').strip()
        password = request.form.get('password', '')

        if not all([name, mobile, email, password]):
            flash('Required fields missing', 'error')
            return redirect(url_for('admin.technicians'))

        if Technician.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('admin.technicians'))

        count = Technician.query.count()
        technician_id = f"TECH{2001 + count}"

        hashed = generate_password_hash(password)

        new_tech = Technician(
            technician_id=technician_id,
            name=name,
            mobile=mobile,
            email=email,
            specialization=specialization or 'CCTV Technician',
            experience=int(experience) if experience else 0,
            service_area=service_area,
            password=hashed
        )
        db.session.add(new_tech)
        db.session.commit()

        flash(f'Technician added! ID: {technician_id}', 'success')
        return redirect(url_for('admin.technicians'))

    all_techs = Technician.query.order_by(Technician.created_at.desc()).all()

    # Jobs completed per technician
    job_counts = {}
    for t in all_techs:
        job_counts[t.technician_id] = Complaint.query.filter_by(
            technician_id=t.technician_id,
            status='resolved'
        ).count()

    return render_template(
        'admin_technicians.html',
        user_name=session['user_name'],
        technicians=all_techs,
        job_counts=job_counts
    )


# ==================== DELETE TECHNICIAN ====================
@admin_bp.route('/technician/<int:technician_id>/delete', methods=['POST'])
def delete_technician(technician_id):
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    tech = Technician.query.get_or_404(technician_id)
    db.session.delete(tech)
    db.session.commit()
    flash('Technician removed', 'success')
    return redirect(url_for('admin.technicians'))


# ==================== TOGGLE TECHNICIAN AVAILABILITY ====================
@admin_bp.route('/technician/<int:technician_id>/toggle', methods=['POST'])
def toggle_technician(technician_id):
    if not admin_required():
        flash('Please login as admin', 'error')
        return redirect(url_for('admin.login'))

    tech = Technician.query.get_or_404(technician_id)
    tech.is_available = not tech.is_available
    db.session.commit()
    flash(f'{tech.name} is now {"Available" if tech.is_available else "Offline"}', 'success')
    return redirect(url_for('admin.technicians'))