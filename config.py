import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cctv-carehub-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cctv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False