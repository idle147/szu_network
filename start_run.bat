@echo off 
:: 如果第一个参数为 "h"，则跳转到标签 :begin
if "%1" == "h" goto begin 

:: 使用 mshta 和 vbscript 创建一个隐藏的命令窗口运行当前脚本，再次传递 "h" 参数，并退出当前窗口
mshta vbscript:createobject("wscript.shell").run("%~0 h",0)(window.close)&&exit 

:begin
:: 启动一个后台命令窗口，运行 pythonw，执行指定的 Python 脚本，并保持窗口打开
start /b cmd /k "pythonw ..\auto_connect.py"