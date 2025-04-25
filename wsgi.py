from app import create_app

# 创建生产环境应用实例
application = create_app('production')

if __name__ == "__main__":
    application.run() 