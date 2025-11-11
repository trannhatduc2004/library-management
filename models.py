# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' hoặc 'user'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)  # Mô tả sách
    image_url = db.Column(db.String(300))  # Đường dẫn ảnh bìa
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Thống kê rating
    total_ratings = db.Column(db.Integer, default=0)
    sum_ratings = db.Column(db.Integer, default=0)
    
    @property
    def average_rating(self):
        """Tính rating trung bình"""
        if self.total_ratings > 0:
            return round(self.sum_ratings / self.total_ratings, 1)
        return 0
    
    def __repr__(self):
        return f'<Book {self.title}>'

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowing')  # 'borrowing' hoặc 'returned'
    late_fee = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer)  # Đánh giá từ 1-5 sao
    review = db.Column(db.Text)  # Review của người dùng
    
    book = db.relationship('Book', backref='borrow_records')
    user = db.relationship('User', backref='borrow_records')
    
    def calculate_late_fee(self, fee_per_day=5000):
        if self.status == 'returned' and self.return_date:
            if self.return_date > self.due_date:
                days_late = (self.return_date - self.due_date).days
                self.late_fee = days_late * fee_per_day
        elif self.status == 'borrowing':
            if datetime.utcnow() > self.due_date:
                days_late = (datetime.utcnow() - self.due_date).days
                self.late_fee = days_late * fee_per_day
        return self.late_fee
    
    def is_overdue(self):
        return self.status == 'borrowing' and datetime.utcnow() > self.due_date
    
    def days_until_due(self):
        """Số ngày còn lại đến hạn trả"""
        if self.status == 'borrowing':
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    def __repr__(self):
        return f'<BorrowRecord {self.id}>'