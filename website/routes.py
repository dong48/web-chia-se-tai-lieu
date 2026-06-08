from flask import Blueprint, render_template, request, flash, redirect, current_app, send_from_directory
from .models import Document, User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    # Lấy từ khóa người dùng gõ vào thanh tìm kiếm
    search_query = request.args.get('search')
    
    # Kéo toàn bộ dữ liệu từ Database ra trước
    all_documents = Document.query.all()
    
    if search_query:
        # Ép từ khóa về chữ thường chuẩn của Python
        search_lower = search_query.lower()
        # Duyệt qua từng tài liệu, ép tiêu đề về chữ thường rồi đem so sánh
        documents = [doc for doc in all_documents if search_lower in doc.title.lower()]
    else:
        documents = all_documents
        search_query = "" # Gán rỗng để màn hình không bị lỗi hiển thị
        
    return render_template('index.html', user=current_user, documents=documents, search_query=search_query)

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Tên đăng nhập đã tồn tại!', 'error')
        else:
            # MẸO NHỎ: Ai đăng ký nick tên 'admin' sẽ tự động thành Admin tối cao
            user_role = 'admin' if username.lower() == 'admin' else 'user'
            
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), role=user_role)
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect('/login')
    return render_template("register.html", user=current_user)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Đăng nhập thành công!', 'success')
            return redirect('/')
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu.', 'error')
    return render_template("login.html", user=current_user)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files['file']

        if file.filename == '':
            flash('Vui lòng chọn file!', 'error')
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
            new_doc = Document(title=title, description=description, filename=filename, user_id=current_user.id)
            db.session.add(new_doc)
            db.session.commit()
            flash('Đã đăng tài liệu!', 'success')
            return redirect('/')
    return render_template("upload.html", user=current_user)

@routes.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    doc = Document.query.get_or_404(id)
    if doc.user_id != current_user.id:
        flash('Bạn không có quyền sửa bài này!', 'error')
        return redirect('/')
        
    if request.method == 'POST':
        doc.title = request.form.get('title')
        doc.description = request.form.get('description')
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
        return redirect('/')
    return render_template('edit.html', user=current_user, doc=doc)

@routes.route('/delete/<int:id>')
@login_required
def delete(id):
    doc = Document.query.get_or_404(id)
    
    # KIỂM TRA QUYỀN: Là chủ bài viết HOẶC là admin thì mới được xóa
    if doc.user_id == current_user.id or current_user.role == 'admin':
        db.session.delete(doc)
        db.session.commit()
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        flash('Đã xóa tài liệu!', 'success')
    else:
        flash('Bạn không có quyền xóa tài liệu của người khác!', 'error')
        
    return redirect('/')
@routes.route('/download/<filename>')
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@routes.route('/admin')
@login_required
def admin_dashboard():
    # Kiểm tra bảo mật cực ngặt: Nếu không phải admin thì đuổi ra trang chủ ngay
    if current_user.role != 'admin':
        flash('CẢNH BÁO: Bạn không có quyền truy cập khu vực Quản trị!', 'error')
        return redirect('/')
    
    # Lấy toàn bộ dữ liệu người dùng và tài liệu để Admin quản lý
    all_users = User.query.all()
    all_docs = Document.query.all()
    
    return render_template('admin.html', user=current_user, all_users=all_users, all_docs=all_docs)