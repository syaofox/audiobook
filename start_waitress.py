from waitress import serve
from app import create_app
import os

# 获取端口配置，默认为8000
PORT = int(os.environ.get('PORT', 5000))

# 创建生产环境应用实例
app = create_app('production')

if __name__ == '__main__':
    print(f"服务器启动，监听端口{PORT}...")
    serve(app, host='0.0.0.0', port=PORT, threads=4)
    print("服务器已关闭！") 