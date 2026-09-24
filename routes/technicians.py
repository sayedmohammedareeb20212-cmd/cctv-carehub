from flask import Blueprint, jsonify, session
from models import Technician

technicians_bp = Blueprint('technicians', __name__)


@technicians_bp.route('/api/technicians/nearby')
def nearby_technicians():
    if session.get('role') != 'customer':
        return jsonify({'message': 'Access denied'}), 403

    techs = Technician.query.order_by(
        Technician.is_available.desc(),
        Technician.rating.desc()
    ).all()

    return jsonify([{
        'technician_id': t.technician_id,
        'name': t.name,
        'mobile': t.mobile,
        'specialization': t.specialization,
        'experience': t.experience,
        'service_area': t.service_area,
        'is_available': t.is_available,
        'rating': t.rating
    } for t in techs])