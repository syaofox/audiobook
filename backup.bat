@echo off
echo 开始备份音频书籍文件...

REM 设置日期变量，格式为YYYYMMDD
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%

REM 设置备份目录
set BACKUP_DIR=D:\备份\audiobook\%DATE%

REM 创建备份目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM 备份音频文件和文本
xcopy /E /I /Y "D:\AI\audiobook\static\audio" "%BACKUP_DIR%\audio"

REM 备份应用配置
copy "D:\AI\audiobook\config.py" "%BACKUP_DIR%\config.py"
copy "D:\AI\audiobook\app.py" "%BACKUP_DIR%\app.py"
copy "D:\AI\audiobook\wsgi.py" "%BACKUP_DIR%\wsgi.py"
copy "D:\AI\audiobook\start_waitress.py" "%BACKUP_DIR%\start_waitress.py"

echo 备份完成！文件已保存到 %BACKUP_DIR%
echo 备份时间: %date% %time%
pause 