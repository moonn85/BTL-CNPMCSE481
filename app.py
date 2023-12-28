from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from flask_login import UserMixin, current_user, login_required, LoginManager, login_user, logout_user
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
# Cấu hình cơ sở dữ liệu (SQLAlchemy)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql+pymysql://thanhphong:852004@localhost/quantri')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.logger.setLevel(logging.INFO)  

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'dn'

# Định nghĩa lớp User kế thừa từ db.Model và UserMixin
class User(db.Model, UserMixin):
    __tablename__ = 'khachhang'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_url = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, default=None)
    sender_id = db.Column(db.Integer, db.ForeignKey('khachhang.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('khachhang.id'), nullable=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Review(db.Model):
    __tablename__ = 'DANHGIA'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80))
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(500))

# Hàm load_user để xác thực người dùng
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Route mặc định trang chủ
@app.route('/')
def home():
    return render_template('home.html')

# Route đăng ký
@app.route('/dk')
def dk():
    return render_template('dk.html')

# Route đăng nhập
@app.route('/dn', methods=['GET', 'POST'])
def dn():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Không tìm thấy người dùng với email đã cung cấp')
        elif bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Đăng nhập thành công!')

            # Lấy các tin nhắn của người dùng
            messages = Message.query.filter(
                (Message.sender_id == user.id) | (Message.receiver_id == user.id)
            ).order_by(Message.timestamp.asc()).all()

            # Chuyển đổi các tin nhắn thành định dạng JSON
            messages_json = [{'text': message.text, 'sender_id': message.sender_id, 'timestamp': message.timestamp} for message in messages]

            if getattr(user, 'is_admin', False):
                return redirect(url_for('admin_post'))
            else:
                return render_template('home.html', messages=messages_json)  # Trả về các tin nhắn cho trang chủ
        else:
            flash('Mật khẩu không hợp lệ')

    return render_template('dn.html')

# Route đăng xuất
@app.route('/logout')
def logout():
    logout_user()
    flash("Đăng xuất thành công", "success")
    return redirect(url_for('home'))

# Route quản trị bài viết
@app.route('/admin/post', methods=['GET', 'POST'])
@login_required
def admin_post():
    if not current_user.is_admin:
        flash('Chỉ quản trị viên mới có quyền truy cập trang này.')
        return redirect(url_for('home'))
    return render_template('admin_post.html')

# Route trang cá nhân
@app.route('/profile', defaults={'username': None})
@app.route('/profile/<username>')
@login_required
def profile(username):
    if username is None:
        user = current_user
    else:
        user = User.query.filter_by(username=username).first_or_404()
    receiver_id = 1 
    return render_template('profile.html', user=user)

# Hàm được gọi trước mỗi request
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

# Route đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')  # Lấy tên người dùng từ form đăng ký
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Mật khẩu không khớp!')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email đã tồn tại.')
            return redirect(url_for('register'))
        
        existing_phone = User.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Số điện thoại đã tồn tại.')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email,username=username, phone=phone, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect(url_for('dn'))
    
    return render_template('dn.html')


# Route tìm kiếm
@app.route('/search')
def search():
    return render_template('search.html')

# Route tìm công thức nấu ăn
@app.route('/find_recipes')
def find_recipes():
    ingredients = request.args.get('ingredients')
    api_key = '3004353c939f497ba0e52212fbe6bc3c'
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        recipes = response.json()
        return render_template('search.html', recipes=recipes)
    else:
        return jsonify({'error': 'Yêu cầu API thất bại'}), response.status_code

@app.route('/sp')
def sp():
    return render_template('sp.html')

@app.route('/danhGia')
def danhGia():
    return render_template('danhGia.html')

@app.route('/gioithieu')
def gioithieu():
    return render_template('gioithieu.html')

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"received message: {data}")  # ghi log tin nhắn nhận được
    sender_id = current_user.id  
    receiver_id = data.get('receiver_id')
    text = data.get('text')

    if sender_id is None or receiver_id is None:
        app.logger.warning("sender_id hoặc receiver_id không được cung cấp")
        return

    if not str(sender_id).isdigit() or not str(receiver_id).isdigit():
        app.logger.warning("Invalid sender_id or receiver_id")
        return

    sender_id = int(sender_id)
    receiver_id = int(receiver_id)

    if text is not None:
        new_message = Message(sender_id=sender_id, receiver_id=receiver_id, text=text, timestamp=datetime.now())
        try:
            db.session.add(new_message)
            db.session.commit()
            app.logger.info("tin nhan da duoc luu thanh cong")  # log success
        except Exception as e:
            app.logger.error(f"Failed to add message to database: {e}")  # log the error
            db.session.rollback()
            return
        socketio.emit('receive_message', data, room=receiver_id)

@socketio.on('broadcast_message')
def handle_broadcast_message_event(data):
    app.logger.info(f"da nhan duoc tin nhan quang ba {data}")  # log the received message
    sender_id = current_user.id  # Get the current user's ID
    text = data.get('text')

    if sender_id is None:
        app.logger.warning("sender_id not provided")
        return

    if not str(sender_id).isdigit():
        app.logger.warning("Invalid sender_id")
        return

    sender_id = int(sender_id)

    if text is not None:
        new_message = Message(sender_id=sender_id, text=text, timestamp=datetime.now())
        try:
            db.session.add(new_message)
            db.session.commit()
            app.logger.info("tin nhan luu thanh cong")  # log success
        except Exception as e:
            app.logger.error(f"Khong the them tin nhan vao co so du lieu {e}")  # log the error
            db.session.rollback()
            return
        socketio.emit('receive_message', data, broadcast=True)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@app.route('/get-messages/<int:receiver_id>')
def get_messages(receiver_id):
    messages = Message.query.filter(
        (Message.sender_id == receiver_id) | (Message.receiver_id == receiver_id)
    ).order_by(Message.timestamp.asc()).all()
    return jsonify([{'text': message.text, 'sender_id': message.sender_id, 'timestamp': message.timestamp} for message in messages])

@socketio.on('start_chat')
def handle_start_chat_event(data):
    app.logger.info(f"Bắt đầu trò chuyện với người dùng có ID: {data['user_id']}")
    # Mã để bắt đầu trò chuyện với người dùng
    
@app.route('/get-contact-list')
def get_contact_list():
    # Lấy ID của người dùng hiện tại
    users = User.query.filter(User.is_admin == False).all()
    return jsonify([{'id': user.id, 'username': user.username, 'email': user.email} for user in users])


@app.route('/review', methods=['POST'])
def review():
    user_id = request.json.get('user_id')
    rating = request.json.get('rating')
    comment = request.json.get('comment')
    new_review = Review(user_id=user_id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Đánh giá thành công'}),200

@app.route('/')
def index():
    reviews = Review.query.all()
    return render_template('danhGia.html', reviews=reviews)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)