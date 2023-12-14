from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, current_user, login_required, LoginManager, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Cấu hình cơ sở dữ liệu (SQLAlchemy)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql+pymysql://thanhphong:852004@localhost/khachhang')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')


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

class MonAn(db.Model):
    __tablename__ = 'monan'
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=False)
    noi_dung = db.Column(db.Text)
    moi = db.Column(db.Boolean, default=False)
    noibat = db.Column(db.Boolean, default=False)
    hienthi = db.Column(db.Boolean, default=False)
    hinh_anh = db.Column(db.LargeBinary)

class NguoiDung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True)

class BaiViet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(255))
    noi_dung = db.Column(db.Text)

class BinhLuan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    noi_dung = db.Column(db.Text, nullable=False)
    trang_thai = db.Column(db.Enum('dang_cho', 'duoc_phe_duyet', 'spam', 'thung_rac'), default='dang_cho')
    ngay_dang = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    nguoi_dung_id = db.Column(db.Integer, db.ForeignKey('nguoi_dung.id'))
    bai_viet_id = db.Column(db.Integer, db.ForeignKey('bai_viet.id'))


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

            if getattr(user, 'is_admin', False):
                return redirect(url_for('admin_post'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Mật khẩu không hợp lệ')

    return render_template('dn.html')

# Route đăng xuất
@app.route('/logout')
def logout():
    logout_user()
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
        new_user = User(email=email, phone=phone, password=hashed_password)
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

# Cấu hình thư mục để lưu file tải lên
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Hàm kiểm tra loại file được phép
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route để thêm món ăn mới
@app.route('/admin/post/monan', methods=['GET', 'POST'])
@login_required
def post_monan():
    # Kiểm tra xem người dùng hiện tại có phải là quản trị viên hay không
    if not current_user.is_admin:
        flash('Chỉ quản trị viên mới có quyền truy cập trang này.')
        return redirect(url_for('home'))

    # Xử lý yêu cầu POST để thêm món ăn mới
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ten_mon_an = request.form.get('tenMonAn')
        mo_ta = request.form.get('moTa')
        noi_dung = request.form.get('noiDung')
        moi = 'moi' in request.form
        noibat = 'noibat' in request.form
        hienthi = 'hienthi' in request.form
        hinh_anh_file = request.files.get('hinhAnh')
        hinh_anh_data = None

        # Lưu file hình ảnh được tải lên
        if hinh_anh_file and allowed_file(hinh_anh_file.filename):
            filename = secure_filename(hinh_anh_file.filename)
            hinh_anh_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            hinh_anh_file.save(hinh_anh_path)
            with open(hinh_anh_path, 'rb') as file:
                hinh_anh_data = file.read()

        # Tạo đối tượng món ăn mới
        mon_an = MonAn(
            ten=ten_mon_an, 
            mo_ta=mo_ta, 
            noi_dung=noi_dung, 
            moi=moi, 
            noibat=noibat, 
            hienthi=hienthi, 
            hinh_anh=hinh_anh_data
        )
        # Thêm món ăn vào cơ sở dữ liệu
        db.session.add(mon_an)
        db.session.commit()

        flash('Món ăn đã được đăng thành công!')
        return redirect(url_for('admin_post'))

    return render_template('admin_post_monan.html')

if __name__ == '__main__':
    app.run(debug=True)
