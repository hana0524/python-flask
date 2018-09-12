import os
from flask import Flask, render_template, request, redirect, url_for,send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = '/image'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hello.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

    def __init__(self, username):
        self.username = username
        
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username == username:
            session['username'] = request.form['username']
            return redirect(url_for('top'))
        else:
            return '''<p>ユーザー名が違います</p>'''
    return render_template('login.html')


        
@app.route("/top")
def top():
    return render_template('top.html')

@app.route("/menu", methods=['GET'])
def menu():
    return render_template('menu.html')
    
@app.route("/regist", methods=['GET'])
def regist():
    return render_template('regist.html')

@app.route("/alluser", methods=['GET'])
def alluser():
    user_list = User.query.all()
    return render_template('alluser.html', title='ユーザ一覧', user_list=user_list)

@app.route("/add_user", methods=['POST'])
def add_user():
    username = request.form.get('username')
    if username:
        user = User(username)
        db.session.add(user)
        db.session.commit()

    return redirect(url_for('alluser'))

@app.route("/user/<int:user_id>", methods=['GET'])
def show_user(user_id):
    target_user = User.query.get(user_id)

    return render_template('show.html', title='ユーザ詳細', target_user=target_user)

@app.route("/user/<int:user_id>", methods=['POST'])
def mod_user(user_id):
    target_user = User.query.get(user_id)
    username = request.form.get('username')
    if target_user and username:
        target_user.username = username
        db.session.commit()

    return redirect(url_for('alluser'))

# del_user メソッドを追加し、ユーザ削除に関する処理を行う
# user_id という変数で、URL に含まれる数字を受け取る
@app.route("/del_user/<int:user_id>", methods=['POST'])
def del_user(user_id):
    # primary key を利用する場合、get メソッドで対象ユーザを取得できる
    target_user = User.query.get(user_id)

    # 一応データの存在確認
    if target_user:
        db.session.delete(target_user)
        db.session.commit()

    return redirect(url_for('alluser'))
    
 #画像アップロード
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/uploads/' + filename
            return render_template('index.html', img_url=img_url)
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('menu'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)