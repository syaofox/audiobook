from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'asdfasfaer32zdfsa'  # 设置session密钥，建议使用随机字符串

# 设置访问密码
ACCESS_PASSWORD = '0928'  # 设置你的访问密码

# 音频和文本文件存放路径
AUDIO_FOLDER = os.path.join('static', 'audio')
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# 修改登录检查装饰器
def login_required(f):
    @wraps(f)  # 使用 wraps 保持原始函数的属性
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ACCESS_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # 获取音频文件列表
    audio_files = []
    for file in os.listdir(AUDIO_FOLDER):
        if file.endswith(('.mp3', '.wav')):
            name = os.path.splitext(file)[0]
            audio_files.append({
                'name': name,
                'file': file,
                'text': f'{name}.txt'  # 假设文本文件与音频文件同名，仅扩展名不同
            })
    return render_template('index.html', audio_files=audio_files)

@app.route('/get_text/<filename>')
@login_required
def get_text(filename):
    try:
        file_path = os.path.join(AUDIO_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文本文件不存在'})
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'status': 'success', 'content': content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 