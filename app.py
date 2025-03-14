from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# 音频和文本文件存放路径
AUDIO_FOLDER = os.path.join('static', 'audio')
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

@app.route('/')
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