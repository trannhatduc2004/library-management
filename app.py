from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Book, BorrowRecord
from forms import LoginForm, BookForm, BorrowForm
from datetime import datetime, timedelta
from functools import wraps
import os
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorator kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Khởi tạo database và dữ liệu mẫu
def init_database():
    with app.app_context():
        db.create_all()
        
        # Tạo tài khoản admin nếu chưa có
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Tạo tài khoản user nếu chưa có
        if not User.query.filter_by(username='user').first():
            user = User(username='user', role='user')
            user.set_password('user123')
            db.session.add(user)
        
        # Thêm sách mẫu nếu chưa có
        if Book.query.count() == 0:
            sample_books = [
                Book(title='Đắc Nhân Tâm', author='Dale Carnegie', category='Văn học', quantity=5, available=5),
                Book(title='Sapiens', author='Yuval Noah Harari', category='Lịch sử', quantity=3, available=3),
                Book(title='Tuổi Trẻ Đáng Giá Bao Nhiêu', author='Rosie Nguyễn', category='Văn học', quantity=4, available=4),
                Book(title='Nhà Giả Kim', author='Paulo Coelho', category='Văn học', quantity=6, available=6),
                Book(title='Tôi Tài Giỏi Bạn Cũng Thế', author='Adam Khoo', category='Kinh tế', quantity=3, available=3),
            ]
            for book in sample_books:
                db.session.add(book)
        
        db.session.commit()
        print('✅ Database đã được khởi tạo thành công!')

@app.route('/')
def index():
    books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    return render_template('index.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Chào mừng {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/books')
def books():
    search = request.args.get('search', '')
    if search:
        books = Book.query.filter(Book.title.contains(search) | Book.author.contains(search)).all()
    else:
        books = Book.query.all()
    return render_template('books.html', books=books, search=search)

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            category=form.category.data,
            quantity=form.quantity.data,
            available=form.quantity.data
        )
        db.session.add(book)
        db.session.commit()
        flash(f'Đã thêm sách "{book.title}" thành công!', 'success')
        return redirect(url_for('books'))
    return render_template('book_form.html', form=form, title='Thêm sách mới')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.category = form.category.data
        
        # Cập nhật số lượng có sẵn theo tỷ lệ
        old_quantity = book.quantity
        new_quantity = form.quantity.data
        if old_quantity > 0:
            ratio = book.available / old_quantity
            book.available = int(new_quantity * ratio)
        book.quantity = new_quantity
        
        db.session.commit()
        flash(f'Đã cập nhật sách "{book.title}" thành công!', 'success')
        return redirect(url_for('books'))
    
    return render_template('book_form.html', form=form, title='Chỉnh sửa sách', book=book)

@app.route('/books/delete/<int:id>')
@login_required
@admin_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    
    # Kiểm tra xem có ai đang mượn sách này không
    active_borrows = BorrowRecord.query.filter_by(book_id=id, status='borrowing').count()
    if active_borrows > 0:
        flash(f'Không thể xóa sách "{book.title}" vì còn người đang mượn!', 'danger')
        return redirect(url_for('books'))
    
    db.session.delete(book)
    db.session.commit()
    flash(f'Đã xóa sách "{book.title}" thành công!', 'success')
    return redirect(url_for('books'))

@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    
    # Lấy danh sách sách còn có sẵn
    available_books = Book.query.filter(Book.available > 0).all()
    form.book_id.choices = [(b.id, f'{b.title} - {b.author} (Còn: {b.available})') for b in available_books]
    
    if form.validate_on_submit():
        book = Book.query.get(form.book_id.data)
        
        if book.available <= 0:
            flash('Sách này hiện không còn!', 'danger')
            return redirect(url_for('borrow'))
        
        # Tạo bản ghi mượn sách
        due_date = datetime.utcnow() + timedelta(days=app.config['BORROW_DAYS'])
        record = BorrowRecord(
            book_id=book.id,
            user_id=current_user.id,
            due_date=due_date
        )
        
        # Giảm số lượng sách có sẵn
        book.available -= 1
        
        db.session.add(record)
        db.session.commit()
        
        flash(f'Đã mượn sách "{book.title}" thành công! Hạn trả: {due_date.strftime("%d/%m/%Y")}', 'success')
        return redirect(url_for('my_borrows'))
    
    return render_template('borrow.html', form=form)

@app.route('/my-borrows')
@login_required
def my_borrows():
    records = BorrowRecord.query.filter_by(user_id=current_user.id).order_by(BorrowRecord.borrow_date.desc()).all()
    
    # Tính phí phạt cho các sách quá hạn
    for record in records:
        if record.status == 'borrowing':
            record.calculate_late_fee(app.config['LATE_FEE_PER_DAY'])
    
    return render_template('my_borrows.html', records=records)

@app.route('/return/<int:id>')
@login_required
def return_book(id):
    record = BorrowRecord.query.get_or_404(id)
    
    # Kiểm tra quyền
    if record.user_id != current_user.id and not current_user.is_admin():
        flash('Bạn không có quyền thực hiện thao tác này!', 'danger')
        return redirect(url_for('my_borrows'))
    
    if record.status == 'returned':
        flash('Sách này đã được trả rồi!', 'warning')
        return redirect(url_for('my_borrows'))
    
    # Cập nhật trạng thái
    record.status = 'returned'
    record.return_date = datetime.utcnow()
    record.calculate_late_fee(app.config['LATE_FEE_PER_DAY'])
    
    # Tăng số lượng sách có sẵn
    book = Book.query.get(record.book_id)
    book.available += 1
    
    db.session.commit()
    
    if record.late_fee > 0:
        flash(f'Đã trả sách "{book.title}". Phí phạt trễ hạn: {record.late_fee:,} VNĐ', 'warning')
    else:
        flash(f'Đã trả sách "{book.title}" thành công!', 'success')
    
    return redirect(url_for('my_borrows'))

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Thống kê tổng quan
    total_books = Book.query.count()
    total_quantity = db.session.query(db.func.sum(Book.quantity)).scalar() or 0
    total_borrowed = db.session.query(db.func.sum(Book.quantity - Book.available)).scalar() or 0
    active_borrows = BorrowRecord.query.filter_by(status='borrowing').count()
    
    # Sách quá hạn
    overdue_records = BorrowRecord.query.filter(
        BorrowRecord.status == 'borrowing',
        BorrowRecord.due_date < datetime.utcnow()
    ).all()
    
    # Tính phí phạt cho sách quá hạn
    for record in overdue_records:
        record.calculate_late_fee(app.config['LATE_FEE_PER_DAY'])
    
    # Sách được mượn nhiều nhất
    popular_books = db.session.query(
        Book, db.func.count(BorrowRecord.id).label('borrow_count')
    ).join(BorrowRecord).group_by(Book.id).order_by(db.desc('borrow_count')).limit(5).all()
    
    # Độc giả tích cực
    active_readers = db.session.query(
        User, db.func.count(BorrowRecord.id).label('borrow_count')
    ).join(BorrowRecord).filter(User.role == 'user').group_by(User.id).order_by(db.desc('borrow_count')).limit(5).all()
    
    return render_template('dashboard.html',
                         total_books=total_books,
                         total_quantity=total_quantity,
                         total_borrowed=total_borrowed,
                         active_borrows=active_borrows,
                         overdue_records=overdue_records,
                         popular_books=popular_books,
                         active_readers=active_readers)

@app.route('/all-borrows')
@login_required
@admin_required
def all_borrows():
    records = BorrowRecord.query.order_by(BorrowRecord.borrow_date.desc()).all()
    
    # Tính phí phạt
    for record in records:
        if record.status == 'borrowing':
            record.calculate_late_fee(app.config['LATE_FEE_PER_DAY'])
    
    return render_template('all_borrows.html', records=records)

# Thêm vào cuối file app.py, thay thế phần if __name__ == '__main__':

if __name__ == '__main__':
    # Only initialize database in development
    if os.environ.get('FLASK_ENV') != 'production':
        init_database()
    app.run(debug=True)
else:
    # In production (when imported by gunicorn)
    init_database()