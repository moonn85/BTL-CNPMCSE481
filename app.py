from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import flash
import requests
from flask import Flask, jsonify

import os

app = Flask(__name__)

# Sử dụng biến môi trường cho thông tin nhạy cảm
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql+pymysql://thanhphong:852004@localhost/khachhang')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'khachhang'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Tăng độ dài cho mật khẩu đã được băm


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dk')
def dk():
    return render_template('dk.html')

@app.route('/sreach')
def sreach():
    return render_template('sreach.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(email=email, phone=phone, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('dn'))  # Chuyển hướng đến trang đăng nhập
        except Exception as e:
            flash('An error occurred: ' + str(e))
            return redirect(url_for('register'))


    return render_template('dn.html')

@app.route('/dn', methods=['GET', 'POST'])
def dn():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('home'))  # Chuyển hướng đến trang chủ


    return render_template('dn.html')

@app.route('/forgot_password')
def forgot_password():
    # Implement password recovery logic here
    return "Password recovery not implemented yet."


@app.route('/api/data')
def get_api_data():
    api_key = '3004353c939f497ba0e52212fbe6bc3c'
    url = 'https://api.spoonacular.com/recipes/complexSearch'  # Replace with the actual API endpoint

    # Assuming the API key is used as a header
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())  # Send the API response data to the client
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code
    
@app.route('/find_recipes')
def find_recipes():
    ingredients = request.args.get('ingredients')  # Lấy các thành phần từ tham số truy vấn
    api_key = '3004353c939f497ba0e52212fbe6bc3c'  # Thay thế bằng khóa API của bạn
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
        recipes = response.json()
        return render_template('sreach.html', recipes=recipes)
    else:
        return jsonify({'error': 'API request failed'}), response.status_code
    data = get_api_data()  # Giả sử hàm này trả về dữ liệu API của bạn
    return render_template('sreach.html', recipes=data)


if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False for production
