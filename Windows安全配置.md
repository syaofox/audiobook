# Windows环境下的音频书籍应用安全配置

本文档提供了在Windows环境中为音频书籍应用进行安全配置的建议。

## 1. 环境变量配置

不要在代码中硬编码敏感信息，使用环境变量：

```cmd
# 临时设置（命令行）
set SECRET_KEY=your_secure_secret_key
set ACCESS_PASSWORD=your_secure_password

# 永久设置
# 通过控制面板 > 系统 > 高级系统设置 > 环境变量
```

## 2. HTTPS配置

在Windows环境中设置Nginx SSL：

1. 生成或获取SSL证书（可以使用[Win-Acme](https://github.com/win-acme/win-acme)工具获取Let's Encrypt证书）

2. 在Nginx配置中启用SSL：

```
server {
    listen 443 ssl;
    server_name localhost;
    
    ssl_certificate D:/certs/fullchain.pem;
    ssl_certificate_key D:/certs/privkey.pem;
    
    # 其他SSL配置...
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        # ...其他代理设置
    }
}
```

## 3. Windows防火墙设置

配置Windows防火墙只允许必要的端口：

1. 打开Windows防火墙设置（控制面板 > 系统和安全 > Windows Defender 防火墙）
2. 点击"允许应用或功能通过Windows Defender 防火墙"
3. 添加Python和Nginx，只允许所需端口（80/443用于Nginx，8000用于Waitress）

## 4. 文件权限

设置适当的NTFS权限：

1. 音频文件目录：仅授予必要的读取权限
2. 应用程序目录：限制写入权限
3. 配置文件：限制对包含敏感信息的文件的访问

## 5. 定期备份

设置Windows计划任务进行自动备份：

1. 创建备份脚本`backup.bat`：
```batch
@echo off
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
xcopy /E /I /Y "D:\AI\audiobook\static\audio" "D:\备份\audiobook\%DATE%"
```

2. 打开任务计划程序
3. 创建基本任务，设置定期运行此脚本（如每天晚上）

## 6. 日志监控

使用Windows事件查看器监控应用：

1. 将应用日志写入Windows事件日志（可以使用Python的`win32evtlogutil`模块）
2. 定期检查日志中的异常活动

## 7. 更新和维护

1. 定期更新Python、Waitress和Nginx
2. 定期更换访问密码
3. 使用Windows Update保持系统更新

## 8. 杀毒软件配置

确保杀毒软件不会干扰应用运行：

1. 将应用目录添加到杀毒软件的排除列表中
2. 定期进行病毒扫描，确保系统安全 