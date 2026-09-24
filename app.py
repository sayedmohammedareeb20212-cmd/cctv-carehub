import os
from flask import Flask, render_template
from database import db

from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.technicians import technicians_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)

    # ==================== SECRET KEY ====================
    app.secret_key = os.environ.get(
        'SECRET_KEY',
        'ms-enterprises-2026-secret-key'
    )

    # ==================== DATABASE ====================
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///cctv.db')

    # Render gives 'postgres://' but SQLAlchemy needs 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==================== TWILIO CONFIG ====================
    # ⚠️ Set these as Environment Variables on Render
    app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_SID', '')
    app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_TOKEN', '')
    app.config['TWILIO_WHATSAPP_FROM'] = os.environ.get('TWILIO_WHATSAPP_FROM', '')
    app.config['ADMIN_WHATSAPP'] = os.environ.get('ADMIN_WHATSAPP', '')

    # ==================== CLIENT EMAIL ====================
    app.config['ADMIN_EMAIL'] = os.environ.get(
        'ADMIN_EMAIL',
        'm.s.enterprises2100@outlook.com'
    )

    # ==================== INIT DATABASE ====================
    db.init_app(app)

    # ==================== REGISTER BLUEPRINTS ====================
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(technicians_bp)
    app.register_blueprint(admin_bp)

    # ==================== ROUTES ====================
    @app.route('/')
    def home():
        return render_template('design.html')

    # ==================== CREATE TABLES ====================
    with app.app_context():
        db.create_all()

    return app


# ==================== RUN ====================
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)