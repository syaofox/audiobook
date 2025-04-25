# Windows环境下的音频书籍应用部署指南

本指南将帮助您在Windows环境中部署音频书籍应用，使用Waitress作为WSGI服务器，可选配置Nginx作为反向代理。

## 前提条件

1. 已安装Python 3.x
2. 安装了uv包管理器
3. 如需使用Nginx，需在Windows上安装Nginx服务器

## 一、基础部署（使用Waitress）

### 1. 安装所需依赖

确保已安装Waitress：

```bash
uv add waitress
```

### 2. 启动服务器

您有两种方式启动应用：

#### 方式一：使用批处理文件

双击`start_server.bat`文件启动应用。

#### 方式二：命令行启动

```bash
uv run python start_waitress.py
```

默认情况下，应用将在8000端口运行，可通过环境变量`PORT`修改：

```bash
set PORT=9000
uv run python start_waitress.py
```

### 3. 作为Windows服务运行

如需将应用作为Windows服务运行，推荐使用NSSM（Non-Sucking Service Manager）：

1. 下载NSSM：https://nssm.cc/download
2. 安装服务：
   ```bash
   nssm install AudiobookService "D:\路径\到\python.exe" "D:\AI\audiobook\start_waitress.py"
   nssm set AudiobookService AppDirectory "D:\AI\audiobook"
   nssm start AudiobookService
   ```

## 二、高级部署（配合Nginx使用）

### 1. 安装Nginx

1. 从[Nginx官网](http://nginx.org/en/download.html)下载Windows版本
2. 解压到合适的位置（如`C:\nginx`）

### 2. 配置Nginx

1. 将`nginx_audiobook.conf`文件复制到Nginx配置目录（如`C:\nginx\conf\sites-enabled\`）
2. 修改`C:\nginx\conf\nginx.conf`，在http块中添加：
   ```
   include sites-enabled/*.conf;
   ```
3. 确保`nginx_audiobook.conf`中的路径已正确设置为Windows格式

### 3. 启动Nginx

从管理员命令提示符运行：

```bash
cd C:\nginx
start nginx
```

### 4. 管理Nginx

- 停止：`nginx -s stop`
- 重启：`nginx -s reload`

## 三、环境变量设置

为了安全性，建议通过环境变量设置敏感信息：

```bash
set SECRET_KEY=your_secure_secret_key
set ACCESS_PASSWORD=your_secure_password
```

要使这些环境变量持久化，请通过系统属性→环境变量进行设置。

## 四、备份策略

使用Windows计划任务创建定期备份：

1. 创建备份脚本`backup.bat`：
   ```batch
   @echo off
   set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
   xcopy /E /I /Y "D:\AI\audiobook\static\audio" "D:\备份\audiobook\%DATE%"
   ```

2. 通过任务计划程序设置定期运行此脚本

## 五、故障排除

1. 如果应用无法启动，检查日志文件（通常在应用目录下）
2. 对于Nginx问题，检查`C:\nginx\logs\error.log`
3. 验证端口是否被其他应用占用：
   ```bash
   netstat -ano | findstr :8000
   ```

## 参考

- [Waitress文档](https://docs.pylonsproject.org/projects/waitress/en/latest/)
- [Windows下的Nginx](http://nginx.org/en/docs/windows.html)
- [NSSM文档](https://nssm.cc/usage) 