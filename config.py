import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình mượn sách
    BORROW_DAYS = 14  # Số ngày mượn tối đa
    LATE_FEE_PER_DAY = 5000  # Phí phạt mỗi ngày trễ (VNĐ)