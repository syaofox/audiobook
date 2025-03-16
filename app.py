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
    """递归扫描目录获取音频文件,返回树形结构"""
    def build_tree(files):
        # 初始化根节点
        tree = {'files': [], 'dirs': {}}
        # 使用集合来跟踪已添加的文件，避免重复
        added_files = set()
        
        for file_info in files:
            path_parts = [p for p in file_info['name'].split('/') if p]
            current = tree
            
            # 生成用于检查重复的唯一标识符
            file_id = '/'.join(path_parts)
            if file_id in added_files:
                continue
                
            added_files.add(file_id)
            
            # 如果有目录部分
            if len(path_parts) > 1:
                # 处理除最后一个部分（文件名）外的所有部分
                for part in path_parts[:-1]:
                    if part not in current['dirs']:
                        current['dirs'][part] = {'files': [], 'dirs': {}}
                    current = current['dirs'][part]
            
            # 添加文件
            current['files'].append({
                'name': path_parts[-1],
                'full_path': file_info['file']
            })
        return tree

    # 先获取所有文件
    audio_files = []
    seen_files = set()  # 用于跟踪已处理的文件
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav')):
                # 获取相对路径
                rel_path = os.path.relpath(root, AUDIO_FOLDER).replace('\\', '/')
                name = os.path.splitext(file)[0]
                
                # 构建文件路径
                if rel_path == '.':
                    display_name = name
                    file_path = file
                else:
                    display_name = f"{rel_path}/{name}"
                    file_path = f"{rel_path}/{file}"
                
                # 检查是否已经处理过这个文件
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    audio_files.append({
                        'name': display_name,
                        'file': file_path
                    })
    
    # 构建树形结构
    return build_tree(sorted(audio_files, key=lambda x: x['name']))

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

@app.route('/play/<path:filename>')
@login_required
def play_audio(filename):
    try:
        safe_filename = os.path.normpath(filename).replace('\\', '/')
        # 获取音频文件信息
        audio_path = os.path.join(AUDIO_FOLDER, safe_filename)
        text_path = os.path.splitext(audio_path)[0] + '.txt'
        
        if not os.path.exists(audio_path):
            return '音频文件不存在', 404
            
        # 读取文本内容
        text_content = ''
        if os.path.exists(text_path):
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
                
        return render_template('player.html', 
                             audio_file=safe_filename,
                             text_content=text_content,
                             filename=os.path.basename(safe_filename))
    except Exception as e:
        return str(e), 500

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

@app.route('/view_text/<path:filename>')
@login_required
def view_text(filename):
    try:
        safe_filename = os.path.normpath(filename).replace('\\', '/')
        file_path = os.path.join(AUDIO_FOLDER, safe_filename)
        
        real_path = os.path.realpath(file_path)
        if not real_path.startswith(os.path.realpath(AUDIO_FOLDER)):
            return '无效的文件路径', 400
            
        if not os.path.exists(file_path):
            return '文本文件不存在', 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('text_view.html', content=content, filename=filename)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 