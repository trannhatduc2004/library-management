from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class BookForm(FlaskForm):
    title = StringField('Tên sách', validators=[DataRequired(), Length(max=200)])
    author = StringField('Tác giả', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Thể loại', choices=[
        ('Văn học', 'Văn học'),
        ('Khoa học', 'Khoa học'),
        ('Lịch sử', 'Lịch sử'),
        ('Công nghệ', 'Công nghệ'),
        ('Kinh tế', 'Kinh tế'),
        ('Nghệ thuật', 'Nghệ thuật'),
        ('Khác', 'Khác')
    ])
    quantity = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Lưu')

class BorrowForm(FlaskForm):
    book_id = SelectField('Chọn sách', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Mượn sách')