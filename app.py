from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'asdfasfaer32zdfsa'  # 设置session密钥，建议使用随机字符串

# 设置访问密码
ACCESS_PASSWORD = 'fuck0928'  # 设置你的访问密码

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

def scan_audio_files(directory):
    """递归扫描目录获取音频文件"""
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav')):
                # 获取相对于AUDIO_FOLDER的路径，并统一使用正斜杠
                rel_path = os.path.relpath(root, AUDIO_FOLDER).replace('\\', '/')
                if rel_path == '.':
                    rel_path = ''
                    
                name = os.path.splitext(file)[0]
                # 确保文件路径使用正斜杠
                file_path = f"{rel_path}/{file}" if rel_path else file
                text_path = f"{rel_path}/{name}.txt" if rel_path else f"{name}.txt"
                
                # 构建显示名称（包含子目录）
                display_name = f"{rel_path}/{name}" if rel_path else name
                
                audio_files.append({
                    'name': display_name.replace('\\', '/'),
                    'file': file_path.replace('\\', '/'),
                    'text': text_path.replace('\\', '/')
                })
    return sorted(audio_files, key=lambda x: x['name'])

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
    audio_files = scan_audio_files(AUDIO_FOLDER)
    return render_template('index.html', audio_files=audio_files)

@app.route('/get_text/<path:filename>')
@login_required
def get_text(filename):
    try:
        # 规范化文件路径，移除任何多余的斜杠
        safe_filename = os.path.normpath(filename).replace('\\', '/')
        file_path = os.path.join(AUDIO_FOLDER, safe_filename)
        
        # 验证文件路径是否在允许的目录内
        real_path = os.path.realpath(file_path)
        if not real_path.startswith(os.path.realpath(AUDIO_FOLDER)):
            return jsonify({'status': 'error', 'message': '无效的文件路径'})
            
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文本文件不存在'})
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'status': 'success', 'content': content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 