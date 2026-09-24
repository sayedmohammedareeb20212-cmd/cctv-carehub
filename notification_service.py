"""
Notification Service — Sends WhatsApp alerts when customers submit complaints.
"""

from twilio.rest import Client
from flask import current_app


def send_complaint_notification(complaint):
    """Send complaint alert via WhatsApp to client."""
    body = f"""🚨 New CCTV Complaint: {complaint.complaint_id}

Customer: {complaint.customer_name}
Mobile: {complaint.customer_mobile}
Location: {complaint.customer_location}

Type: {complaint.complaint_type}
Priority: {complaint.priority.upper()}

Description:
{complaint.description}

Submitted: {complaint.created_at.strftime('%d %b %Y, %I:%M %p')}

— MS Enterprises"""

    try:
        client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )
        message = client.messages.create(
            from_=current_app.config['TWILIO_WHATSAPP_FROM'],
            body=body,
            to=current_app.config['ADMIN_WHATSAPP']
        )
        print(f"✅ WhatsApp sent: {message.sid}")
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")