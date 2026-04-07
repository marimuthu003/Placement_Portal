import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-placement-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
