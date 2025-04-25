from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import os
from functools import wraps
import markdown  # 添加这一行导入markdown库
from config import config  # 导入配置

# 创建应用工厂函数
def create_app(config_name='production'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 音频和文本文件存放路径
    if not app.config.get('AUDIO_FOLDER'):
        app.config['AUDIO_FOLDER'] = os.path.join('static', 'audio')
    
    # 设置访问密码变量
    access_password = app.config.get('ACCESS_PASSWORD')

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
        audio_folder = app.config['AUDIO_FOLDER']
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.mp3', '.wav')):
                    # 获取相对路径
                    rel_path = os.path.relpath(root, audio_folder).replace('\\', '/')
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
            if request.form.get('password') == access_password:
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
        audio_files = scan_audio_files(app.config['AUDIO_FOLDER'])
        return render_template('index.html', audio_files=audio_files)

    @app.route('/play/<path:filename>')
    @login_required
    def play_audio(filename):
        try:
            safe_filename = os.path.normpath(filename).replace('\\', '/')
            # 获取音频文件信息
            audio_folder = app.config['AUDIO_FOLDER']
            audio_path = os.path.join(audio_folder, safe_filename)
            text_path = os.path.splitext(audio_path)[0] + '.txt'
            md_path = os.path.splitext(audio_path)[0] + '.md'  # 添加对md文件的支持
            
            if not os.path.exists(audio_path):
                return '音频文件不存在', 404
                
            # 读取文本内容
            text_content = ''
            is_markdown = False
            
            # 优先检查md文件，如果存在则读取
            if os.path.exists(md_path):
                with open(md_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    is_markdown = True
            # 如果md文件不存在，则尝试读取txt文件
            elif os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            # 如果是Markdown格式，转换为HTML
            if is_markdown:
                text_content = markdown.markdown(text_content, extensions=['extra'])
                    
            return render_template('player.html', 
                                 audio_file=safe_filename,
                                 text_content=text_content,
                                 is_markdown=is_markdown,
                                 filename=os.path.basename(safe_filename))
        except Exception as e:
            return str(e), 500

    @app.route('/get_text/<path:filename>')
    @login_required
    def get_text(filename):
        try:
            # 规范化文件路径，移除任何多余的斜杠
            safe_filename = os.path.normpath(filename).replace('\\', '/')
            audio_folder = app.config['AUDIO_FOLDER']
            file_path = os.path.join(audio_folder, safe_filename)
            
            # 验证文件路径是否在允许的目录内
            real_path = os.path.realpath(file_path)
            if not real_path.startswith(os.path.realpath(audio_folder)):
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
            audio_folder = app.config['AUDIO_FOLDER']
            file_path = os.path.join(audio_folder, safe_filename)
            
            real_path = os.path.realpath(file_path)
            if not real_path.startswith(os.path.realpath(audio_folder)):
                return '无效的文件路径', 400
                
            if not os.path.exists(file_path):
                return '文本文件不存在', 404
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return render_template('text_view.html', content=content, filename=filename)
        except Exception as e:
            return str(e), 500

    @app.route('/get_adjacent_files/<path:filename>')
    @login_required
    def get_adjacent_files(filename):
        try:
            # 规范化文件路径
            safe_filename = os.path.normpath(filename).replace('\\', '/')
            audio_folder = app.config['AUDIO_FOLDER']
            
            # 获取所有音频文件的扁平列表
            flat_files = []
            for root, dirs, files in os.walk(audio_folder):
                for file in sorted(files):
                    if file.endswith(('.mp3', '.wav')):
                        rel_path = os.path.relpath(root, audio_folder).replace('\\', '/')
                        if rel_path == '.':
                            file_path = file
                        else:
                            file_path = f"{rel_path}/{file}"
                        flat_files.append(file_path)
            
            # 查找当前文件在列表中的位置
            try:
                current_index = flat_files.index(safe_filename)
            except ValueError:
                return jsonify({'status': 'error', 'message': '文件不在列表中'})
            
            # 确定前一个和后一个文件
            prev_file = flat_files[current_index - 1] if current_index > 0 else None
            next_file = flat_files[current_index + 1] if current_index < len(flat_files) - 1 else None
            
            return jsonify({
                'status': 'success',
                'prev_file': prev_file,
                'next_file': next_file
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    @app.route('/protected_static/<path:filename>')
    @login_required
    def protected_static(filename):
        # 这个路由用于保护static/audio目录中的文件
        # 只允许已登录用户访问
        if filename.startswith('audio/'):
            return app.send_static_file(filename)
        return '未授权访问', 403

    # 重写默认的静态文件处理，防止直接访问静态目录下的音频文件
    @app.before_request
    def check_static_audio():
        # 检查是否是对静态audio文件夹的直接访问
        if request.path.startswith('/static/audio/') and 'logged_in' not in session:
            return redirect(url_for('login'))
            
    return app

# 应用实例
app = create_app('production')

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000)