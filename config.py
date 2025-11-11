# -*- coding: utf-8 -*-
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Get database URL from environment
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Fix for Render PostgreSQL URL (postgres:// -> postgresql://)
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Use PostgreSQL in production, SQLite in development
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình mượn sách
    BORROW_DAYS = 14  # Số ngày mượn tối đa
    LATE_FEE_PER_DAY = 5000  # Phí phạt mỗi ngày trễ (VNĐ)
    
    # Cấu hình upload file
    UPLOAD_FOLDER = 'static/uploads/books'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}