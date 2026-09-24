from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from models import Complaint, Technician
from datetime import datetime
from notification_service import send_complaint_notification

complaints_bp = Blueprint('complaints', __name__)


# ==================== CUSTOMER DASHBOARD ====================
@complaints_bp.route('/customer-dashboard')
def customer_dashboard():
    if session.get('role') != 'customer':
        flash('Please login as customer', 'error')
        return redirect(url_for('auth.customer_login'))

    complaints = Complaint.query.filter_by(
        customer_id=session['customer_id']
    ).order_by(Complaint.created_at.desc()).all()

    technicians = Technician.query.order_by(
        Technician.is_available.desc(),
        Technician.rating.desc()
    ).all()

    return render_template(
        'customer_dashboard.html',
        user_name=session['user_name'],
        customer_id=session['customer_id'],
        complaints=complaints,
        technicians=technicians
    )


# ==================== SUBMIT COMPLAINT ====================
@complaints_bp.route('/complaint/submit', methods=['POST'])
def submit_complaint():
    if session.get('role') != 'customer':
        flash('Please login as customer', 'error')
        return redirect(url_for('auth.customer_login'))

    complaint_type = request.form.get('complaintType', '').strip()
    description = request.form.get('description', '').strip()

    if not complaint_type or not description:
        flash('Complaint type and description required', 'error')
        return redirect(url_for('complaints.customer_dashboard'))

    priority = 'medium'
    if 'Not Working' in complaint_type or 'Emergency' in complaint_type:
        priority = 'high'
    elif 'Installation' in complaint_type:
        priority = 'low'

    count = Complaint.query.count()
    complaint_id = f"CMP{1001 + count}"

    new_complaint = Complaint(
        complaint_id=complaint_id,
        customer_id=session['customer_id'],
        customer_name=session['user_name'],
        customer_mobile=request.form.get('mobile', ''),
        customer_location=request.form.get('location', ''),
        complaint_type=complaint_type,
        description=description,
        priority=priority,
        status='pending'
    )
    db.session.add(new_complaint)
    db.session.commit()

    # 🔔 Send WhatsApp notification to client
    send_complaint_notification(new_complaint)

    flash(f'Complaint submitted! Your Complaint ID is {complaint_id}', 'success')
    return redirect(url_for('complaints.customer_dashboard'))


# ==================== TECHNICIAN DASHBOARD ====================
@complaints_bp.route('/technician-dashboard')
def technician_dashboard():
    if session.get('role') != 'technician':
        flash('Please login as technician', 'error')
        return redirect(url_for('auth.technician_login'))

    my_id = session['technician_id']

    complaints = Complaint.query.filter(
        db.or_(
            db.and_(Complaint.status == 'pending', Complaint.technician_id.is_(None)),
            Complaint.technician_id == my_id
        )
    ).order_by(Complaint.created_at.desc()).all()

    tech = Technician.query.filter_by(technician_id=my_id).first()

    stats = {
        'assigned': Complaint.query.filter_by(technician_id=my_id, status='in-progress').count(),
        'pending': Complaint.query.filter_by(status='pending', technician_id=None).count(),
        'completed': tech.completed_jobs if tech else 0,
        'rating': tech.rating if tech else 5.0
    }

    return render_template(
        'technician_dashboard.html',
        user_name=session['user_name'],
        technician_id=my_id,
        complaints=complaints,
        stats=stats,
        technician=tech
    )


# ==================== ACCEPT COMPLAINT ====================
@complaints_bp.route('/complaint/<int:complaint_id>/accept', methods=['POST'])
def accept_complaint(complaint_id):
    if session.get('role') != 'technician':
        flash('Please login as technician', 'error')
        return redirect(url_for('auth.technician_login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.technician_id = session['technician_id']
    complaint.status = 'in-progress'
    db.session.commit()

    flash('Job accepted!', 'success')
    return redirect(url_for('complaints.technician_dashboard'))


# ==================== COMPLETE COMPLAINT ====================
@complaints_bp.route('/complaint/<int:complaint_id>/complete', methods=['POST'])
def complete_complaint(complaint_id):
    if session.get('role') != 'technician':
        flash('Please login as technician', 'error')
        return redirect(url_for('auth.technician_login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = 'resolved'
    complaint.resolved_at = datetime.utcnow()

    tech = Technician.query.filter_by(technician_id=session['technician_id']).first()
    if tech:
        tech.completed_jobs = (tech.completed_jobs or 0) + 1

    db.session.commit()

    flash('Job marked as complete!', 'success')
    return redirect(url_for('complaints.technician_dashboard'))


# ==================== TOGGLE AVAILABILITY ====================
@complaints_bp.route('/technician/toggle-availability', methods=['POST'])
def toggle_availability():
    if session.get('role') != 'technician':
        flash('Please login as technician', 'error')
        return redirect(url_for('auth.technician_login'))

    tech = Technician.query.filter_by(technician_id=session['technician_id']).first()
    if tech:
        tech.is_available = not tech.is_available
        db.session.commit()
        flash(f"Status: {'Available' if tech.is_available else 'Offline'}", 'success')

    return redirect(url_for('complaints.technician_dashboard'))


# ==================== PUBLIC COMPLAINT TRACKING ====================
@complaints_bp.route('/track', methods=['GET', 'POST'])
@complaints_bp.route('/track/<complaint_id>', methods=['GET'])
def track_complaint(complaint_id=None):
    complaint = None
    error = None

    if not complaint_id and request.method == 'POST':
        complaint_id = request.form.get('complaintId', '').strip().upper()

    if complaint_id:
        complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
        if not complaint:
            error = f"No complaint found with ID: {complaint_id}"

    return render_template(
        'track_complaint.html',
        complaint=complaint,
        complaint_id=complaint_id,
        error=error
    )