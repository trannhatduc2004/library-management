# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

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
        ('Tâm lý', 'Tâm lý'),
        ('Kỹ năng sống', 'Kỹ năng sống'),
        ('Khác', 'Khác')
    ])
    description = TextAreaField('Mô tả sách', validators=[Optional(), Length(max=1000)])
    image = FileField('Ảnh bìa sách', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ chấp nhận file ảnh!')
    ])
    image_url = StringField('Hoặc nhập URL ảnh', validators=[Optional(), Length(max=300)])
    quantity = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Lưu')

class BorrowForm(FlaskForm):
    book_id = SelectField('Chọn sách', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Mượn sách')

class RatingForm(FlaskForm):
    rating = SelectField('Đánh giá', 
                        choices=[(5, '⭐⭐⭐⭐⭐ Xuất sắc'),
                                (4, '⭐⭐⭐⭐ Rất tốt'),
                                (3, '⭐⭐⭐ Tốt'),
                                (2, '⭐⭐ Trung bình'),
                                (1, '⭐ Kém')],
                        coerce=int,
                        validators=[DataRequired()])
    review = TextAreaField('Nhận xét', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Gửi đánh giá')