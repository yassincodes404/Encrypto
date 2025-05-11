# routes.py
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import emit, join_room, leave_room
import json
import os
import base64
from datetime import datetime
from app import app, db, socketio, login_manager # تأكد من الاستيراد الصحيح
from models import User, Message, UserSettings
from crypto_utils import RSACipher, CTRCipher, encrypt_message, decrypt_message, generate_sha1_hash
from werkzeug.security import generate_password_hash

# --- User loader (يبقى كما هو) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- تعطيل أو حذف المسارات القديمة ---
# @app.route('/login', ...)
# @app.route('/register', ...)
# @app.route('/auth', ...)

# --- المسار الجديد المدمج للمصادقة ---
@app.route('/auth', methods=['GET', 'POST'])
def auth_standalone():
    """
    Handles both displaying the auth page (GET) and processing
    login/registration form submissions (POST).
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'login':
            # --- معالجة تسجيل الدخول ---
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                flash('الرجاء إدخال البريد الإلكتروني وكلمة المرور.', 'warning')
                return redirect(url_for('auth_standalone'))

            # البحث عن المستخدم بواسطة البريد الإلكتروني
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                app.logger.info(f'User {user.username} logged in successfully.')
                # تخزين معلومات تسجيل الدخول في الجلسة (اختياري)
                session['last_login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session['last_login_ip'] = request.remote_addr
                # التوجيه إلى الصفحة المطلوبة قبل تسجيل الدخول أو لوحة التحكم
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                app.logger.warning(f'Failed login attempt for email: {email}')
                flash('بريد إلكتروني أو كلمة مرور غير صالحة.', 'danger')
                return redirect(url_for('auth_standalone'))

        elif form_type == 'register':
            # --- معالجة التسجيل ---
            username = request.form.get('username') # هذا هو الاسم الكامل الآن
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            terms_agreed = request.form.get('terms')

            # --- التحقق من صحة البيانات (Server-side) ---
            errors = []
            if not username: errors.append("الاسم الكامل مطلوب.")
            if not email: errors.append("البريد الإلكتروني مطلوب.")
            if not password: errors.append("كلمة المرور مطلوبة.")
            if not confirm_password: errors.append("تأكيد كلمة المرور مطلوب.")
            if password and len(password) < 8: errors.append("يجب أن تتكون كلمة المرور من 8 أحرف على الأقل.")
            if password and confirm_password and password != confirm_password: errors.append("كلمتا المرور غير متطابقتين.")
            if not terms_agreed: errors.append("يجب الموافقة على الشروط والأحكام.")

            if errors:
                for error in errors:
                    flash(error, 'warning')
                return redirect(url_for('auth_standalone'))

            # التحقق من وجود البريد أو اسم المستخدم مسبقًا
            if User.query.filter_by(email=email).first():
                flash('هذا البريد الإلكتروني مسجل بالفعل.', 'warning')
                return redirect(url_for('auth_standalone'))
            if User.query.filter_by(username=username).first():
                flash('اسم المستخدم هذا مستخدم بالفعل.', 'warning')
                return redirect(url_for('auth_standalone'))
            # --- نهاية التحقق ---

            # إنشاء مفاتيح RSA للمستخدم الجديد
            try:
                key_pair = RSACipher.generate_key_pair()
                app.logger.info(f"Generated RSA keys for new user: {username}")
            except Exception as e:
                app.logger.error(f"Key generation failed for {username}: {e}")
                flash('حدث خطأ فني أثناء إعداد الحساب. يرجى المحاولة مرة أخرى.', 'danger')
                return redirect(url_for('auth_standalone'))

            # إنشاء المستخدم وإعداداته
            new_user = User(
                username=username,
                email=email,
                public_key=key_pair['public_key'],
                private_key=key_pair['private_key']
            )
            new_user.set_password(password)
            settings = UserSettings(user=new_user) # الإعدادات الافتراضية من الموديل

            # حفظ في قاعدة البيانات
            try:
                db.session.add(new_user)
                db.session.add(settings)
                db.session.commit()
                app.logger.info(f'User {username} registered successfully.')
                flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
                # البقاء في نفس الصفحة (سيعيد JavaScript عرض نموذج تسجيل الدخول)
                return redirect(url_for('auth_standalone'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Registration DB error for {username}: {e}")
                flash('حدث خطأ أثناء حفظ بيانات التسجيل.', 'danger')
                return redirect(url_for('auth_standalone'))

        else:
            # إذا كان form_type غير متوقع
            flash('حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.', 'danger')
            return redirect(url_for('auth_standalone'))

    # إذا كان الطلب GET، فقط اعرض الصفحة
    return render_template('auth_standalone.html')

# --- تحديث نقطة الدخول لـ Flask-Login ---
login_manager.login_view = 'auth_standalone'

# --- تحديث مسارات الدخول والخروج ---
@app.route('/')
def index():
    """ Redirects to auth page if not logged in, dashboard otherwise. """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth_standalone'))

@app.route('/logout')
@login_required
def logout():
    """ Logs out the user and redirects to the auth page. """
    username = current_user.username
    logout_user()
    session.clear() # مسح الجلسة عند الخروج
    app.logger.info(f'User {username} logged out.')
    flash('تم تسجيل خروجك بنجاح.', 'info')
    return redirect(url_for('auth_standalone'))

# --- مسارات أخرى للتطبيق (تأكد من وجودها وعملها) ---

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/encryption')
@login_required
def encryption():
    return render_template('encryption.html')

@app.route('/chat')
@login_required
def chat():
    try:
        # جلب آخر 50 رسالة مثلاً
        messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
        messages.reverse() # لعرض الأقدم أولاً في الأعلى
        users = User.query.with_entities(User.id, User.username).all() # جلب ID والاسم فقط
        user_map = {u.id: u.username for u in users}
    except Exception as e:
        app.logger.error(f"Error loading chat data: {e}")
        flash("حدث خطأ أثناء تحميل بيانات الدردشة.", "danger")
        messages = []
        user_map = {}
    return render_template('chat.html', messages=messages, users=user_map) # تمرير user_map إذا كنت تستخدمها في القالب

@app.route('/settings')
@login_required
def settings():
    user_settings = current_user.settings
    if not user_settings: # إنشاء إعدادات إذا لم تكن موجودة (احتياطي)
        user_settings = UserSettings(user_id=current_user.id)
        try:
            db.session.add(user_settings)
            db.session.commit()
            app.logger.info(f"Created missing settings for user {current_user.username}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to create missing settings for user {current_user.username}: {e}")
            flash("خطأ في تحميل الإعدادات.", "danger")
            # قد ترغب في إعادة التوجيه أو عرض خطأ هنا
    return render_template('settings.html', settings=user_settings)

@app.route('/profile')
@login_required
def profile():
    public_key_str = "غير متاح"
    key_fingerprint = "غير متاح"
    try:
        if current_user.public_key:
            if hasattr(current_user.public_key, 'save_pkcs1'):
                public_key_pem = current_user.public_key.save_pkcs1('PEM')
                public_key_str = public_key_pem.decode('utf-8')
                key_fingerprint = generate_sha1_hash(public_key_pem) # استخدام الدالة من crypto_utils
            else:
                public_key_str = str(current_user.public_key)
    except Exception as e:
        app.logger.error(f"Error formatting public key or fingerprint for profile user {current_user.id}: {e}")
        public_key_str = "خطأ في عرض المفتاح"
        key_fingerprint = "خطأ في إنشاء البصمة"

    # استرجاع بيانات تسجيل الدخول من الجلسة إن وجدت
    last_login_time = session.get('last_login_time', current_user.created_at.strftime('%Y-%m-%d %H:%M:%S'))
    last_login_ip = session.get('last_login_ip', "N/A")
    # بيانات أخرى تحتاج لجلبها من قاعدة بيانات أو سجلات
    password_changed_time = None # مثال: UserActivityLog.query...
    password_changed_ip = None
    account_created_ip = "N/A" # مثال: UserRegistrationLog.query...

    return render_template('profile.html',
                           public_key=public_key_str,
                           key_fingerprint=key_fingerprint,
                           last_login_time=last_login_time,
                           last_login_ip=last_login_ip,
                           password_changed_time=password_changed_time,
                           password_changed_ip=password_changed_ip,
                           account_created_ip=account_created_ip)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# --- نقاط النهاية API (Keep as is or adapt if needed) ---
@app.route('/api/encrypt', methods=['POST'])
@login_required
def api_encrypt():
    data = request.json
    algorithm = data.get('algorithm')
    message = data.get('message')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        if algorithm == 'sha1':
            result = generate_sha1_hash(message)
            return jsonify({'result': result})

        elif algorithm == 'ctr':
            key = CTRCipher.generate_key()
            encrypted = CTRCipher.encrypt(message, key)
            return jsonify({
                'result': encrypted,
                'key': base64.b64encode(key).decode('utf-8')
            })

        elif algorithm == 'rsa':
            if not current_user.public_key:
                 return jsonify({'error': 'المفتاح العام للمستخدم غير موجود'}), 500
            encrypted = RSACipher.encrypt(message, current_user.public_key)
            return jsonify({'result': encrypted})

        else:
            return jsonify({'error': 'خوارزمية غير صالحة'}), 400
    except Exception as e:
        app.logger.error(f"API Encryption error for user {current_user.id}: {e}")
        return jsonify({'error': f'فشل التشفير: {e}'}), 500

@app.route('/api/decrypt', methods=['POST'])
@login_required
def api_decrypt():
    data = request.json
    algorithm = data.get('algorithm')
    encrypted = data.get('encrypted')

    if not encrypted:
        return jsonify({'error': 'لا توجد بيانات مشفرة'}), 400

    try:
        if algorithm == 'ctr':
            key_b64 = data.get('key')
            if not key_b64:
                return jsonify({'error': 'مفتاح فك التشفير مفقود'}), 400
            key = base64.b64decode(key_b64)
            decrypted = CTRCipher.decrypt(encrypted, key)
            return jsonify({'result': decrypted})

        elif algorithm == 'rsa':
            if not current_user.private_key:
                 return jsonify({'error': 'المفتاح الخاص للمستخدم غير موجود'}), 500
            decrypted = RSACipher.decrypt(encrypted, current_user.private_key)
            return jsonify({'result': decrypted})

        else:
            return jsonify({'error': 'خوارزمية غير صالحة'}), 400
    except Exception as e:
        app.logger.error(f"API Decryption error for user {current_user.id}: {e}")
        return jsonify({'error': 'فشل فك التشفير. مفتاح أو بيانات غير صالحة.'}), 500

@app.route('/api/settings', methods=['POST'])
@login_required
def api_settings():
    data = request.json
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
         return jsonify({'error': 'لم يتم العثور على الإعدادات'}), 404

    changed = False
    if 'language' in data and data['language'] in ['en', 'ar']: # التحقق من اللغة
        user_settings.language = data['language']
        changed = True
    if 'theme' in data and data['theme'] in ['light', 'dark']: # التحقق من السمة
        user_settings.theme = data['theme']
        changed = True
    if 'notifications' in data:
        user_settings.notifications = bool(data['notifications'])
        changed = True

    if changed:
        try:
            db.session.commit()
            app.logger.info(f"Settings updated for user {current_user.id}")
            return jsonify({'success': True, 'message': 'تم حفظ الإعدادات بنجاح'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Settings save error for user {current_user.id}: {e}")
            return jsonify({'error': 'فشل حفظ الإعدادات'}), 500
    else:
        return jsonify({'success': False, 'message': 'لم يتم تغيير أي إعدادات'})


@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'error': 'الحقول المطلوبة مفقودة'}), 400

    if not current_user.check_password(current_password):
        return jsonify({'error': 'كلمة المرور الحالية غير صحيحة'}), 400

    if len(new_password) < 8:
         return jsonify({'error': 'يجب أن تتكون كلمة المرور الجديدة من 8 أحرف على الأقل'}), 400
    # يمكنك إضافة المزيد من شروط التعقيد هنا

    try:
        current_user.set_password(new_password)
        db.session.commit()
        app.logger.info(f"Password changed successfully for user {current_user.id}")
        # قم بتسجيل هذا الحدث إذا كان لديك سجل نشاط
        return jsonify({'success': True, 'message': 'تم تغيير كلمة المرور بنجاح'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Password change error for user {current_user.id}: {e}")
        return jsonify({'error': 'فشل تغيير كلمة المرور'}), 500

# --- SocketIO Events (Keep as is, with logging improvements from previous response) ---
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room('global')
        app.logger.info(f"Socket connected: User {current_user.username} ({request.sid}) joined room 'global'")
        # يمكنك إرسال رسالة ترحيب خاصة للمستخدم المتصل فقط
        # emit('status', {'msg': f'Welcome, {current_user.username}!'}, room=request.sid)
    else:
        app.logger.warning(f"Unauthenticated socket connection attempt ({request.sid})")
        return False # قطع الاتصال للمستخدم غير المسجل

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room('global')
        app.logger.info(f"Socket disconnected: User {current_user.username} ({request.sid}) left room 'global'")
    else:
         app.logger.info(f"Unauthenticated socket disconnected ({request.sid})")

@socketio.on('message')
@login_required
def handle_message(data):
    if not data or 'message' not in data or not data['message'].strip():
        app.logger.warning(f"Received empty/invalid message data from user {current_user.id}")
        return # تجاهل الرسائل الفارغة أو غير الصالحة

    content = data['message'].strip()
    app.logger.debug(f"Received message from {current_user.username}: '{content[:50]}...'")

    # توقيع الرسالة رقميًا
    try:
        if not current_user.private_key:
             app.logger.error(f"Private key missing for user {current_user.id}. Cannot sign message.")
             emit('error', {'msg': 'خطأ: لا يمكن توقيع الرسالة.'}, room=request.sid)
             return
        signature = RSACipher.sign(content, current_user.private_key)
    except Exception as e:
        app.logger.error(f"Message signing error for user {current_user.id}: {e}")
        emit('error', {'msg': 'خطأ: فشل في توقيع الرسالة.'}, room=request.sid)
        return

    # حفظ الرسالة في قاعدة البيانات
    new_message = Message(
        content=content,
        signature=signature,
        user_id=current_user.id,
        timestamp=datetime.utcnow()
    )
    try:
        db.session.add(new_message)
        db.session.commit()
        app.logger.info(f"Message from {current_user.username} (ID: {new_message.id}) saved to DB.")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Message save DB error for user {current_user.id}: {e}")
        emit('error', {'msg': 'خطأ: فشل في حفظ الرسالة.'}, room=request.sid)
        return

    # بث الرسالة للجميع في الغرفة العامة (مع النص العادي والتوقيع)
    message_payload = {
        'id': new_message.id,
        'sender': current_user.username,
        'user_id': current_user.id,
        'content': content, # النص العادي
        'signature': signature,
        'timestamp': new_message.timestamp.isoformat() + "Z" # تنسيق ISO 8601 UTC
    }
    socketio.emit('message', message_payload, room='global')
    app.logger.debug(f"Broadcasted message ID {new_message.id} to 'global' room.")


# --- Error Handlers (Keep as is) ---
@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"404 Not Found: {request.path}")
    return render_template('error.html', error_code=404, error_message='الصفحة غير موجودة'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # التراجع عن أي تغييرات في قاعدة البيانات قد تكون معلقة
    app.logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return render_template('error.html', error_code=500, error_message='خطأ داخلي في الخادم'), 500

# --- تأكد من وجود باقي الكود مثل إعدادات التطبيق وتشغيله في app.py ---