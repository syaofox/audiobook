import os
import secrets

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # 音频文件夹配置
    AUDIO_FOLDER = os.environ.get('AUDIO_FOLDER') or os.path.join('static', 'audio')
    
    # 访问密码
    ACCESS_PASSWORD = os.environ.get('ACCESS_PASSWORD') or 'fuck0928'  # 建议通过环境变量设置

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # 可以添加数据库配置等其他生产环境特定配置

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

# 配置映射字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 