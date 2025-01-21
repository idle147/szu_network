# SZU 校园网自动重连工具

这是一个用于深圳大学校园网自动重连的工具。
当检测到网络断开时,会自动尝试重新登录校园网。

## 功能特点
- 自动检测有线网络连接状态
- 自动检测网络可访问性
- 断网后自动重新登录校园网
- 支持配置文件自定义设置
- 日志记录功能,包含控制台彩色输出和文件记录

## 环境要求
- Python 3.12+
- Windows 操作系统
- Chrome浏览器

## 安装步骤

1. 克隆或下载本项目
2. 安装依赖包:
```bash
pip install -r requirements.txt
```

主要依赖包包括:
- loguru: 日志记录
- selenium: 网页自动化
- requests: 网络请求
- wmi: Windows系统接口
- pyyaml: 配置文件解析

## 配置说明

在 config.yaml 文件中配置以下内容:

```yaml
username: "your_username"    # 校园网账号
password: "your_password"    # 校园网密码
url: "https://net.szu.edu.cn"  # 登录地址
check_interval: 30    # 检查间隔(秒)
connection_timeout: 2  # 连接超时时间(秒)
test_urls:   # 用于测试网络连通性的网站
  - "https://www.baidu.com"
  - "https://www.qq.com" 
  - "https://www.bing.com"
```

## 运行方式
**运行前行编辑config.yaml文件, 写入用户名密码**

### 方式1: 直接运行
```bash
python auto_connect.py
```

### 方式2: 后台运行
双击运行下述文件, 将在后台静默运行。
```
./script/start_run.bat
```


## 日志说明

- 控制台实时显示彩色日志输出
- 日志文件保存在 `logs/szu_connect_日期.log`
- 每天自动轮转日志文件
- 保留最近30天的日志记录
- 自动压缩历史日志文件

## 注意事项

1. 首次运行会自动创建配置文件模板
2. 请确保已正确配置账号密码
3. 需要安装Chrome浏览器
4. 仅支持Windows系统
5. 建议使用 

start_run.bat

 在后台运行

## 工作原理

1. 定期检查有线网络物理连接状态
2. 通过访问测试网站验证网络连通性
3. 发现断网后使用Selenium模拟浏览器登录
4. 登录成功后继续监控网络状态

## 常见问题

1. 如遇到启动错误,请检查Chrome浏览器是否正确安装
2. 确保账号密码配置正确
3. 如需调整检查频率,可修改配置文件中的 check_interval 遍历
4. 有无法解决的问题请发起issue
