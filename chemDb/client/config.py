"""客户端配置。部署时修改 SSH_HOST/SSH_PORT 为 SakuraFRP 分配的地址和端口。"""

# SakuraFRP TCP 隧道分配的连接地址（指向服务器的 22 端口）
SSH_HOST = "frp-mix.com"  # TODO: 改成你的隧道地址
SSH_PORT = 21961        # TODO: 改成你的隧道端口

# 服务器登录用户名（直接用现有账户）
SSH_USER = "laplace"

# 服务器内部 HTTP 服务地址（服务端只监听本机，不用改）
REMOTE_HOST = "127.0.0.1"
REMOTE_PORT = 8000

# 与服务端 config.py 中的 API_TOKEN 保持一致
API_TOKEN = "demo-token-change-me"

# 共享私钥（demo 用，正式使用请重新生成并替换）
SSH_PRIVATE_KEY = """
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAT5ckc1xkWKM3dYAXqhx7QvcXVs5UtrQ+swvsfUqE2lgAAAJAmhn2EJoZ9
hAAAAAtzc2gtZWQyNTUxOQAAACAT5ckc1xkWKM3dYAXqhx7QvcXVs5UtrQ+swvsfUqE2lg
AAAEBgRvkfIAw/ZAljtAyLyzvU8zENFTD5CfWraHDJZIG74xPlyRzXGRYozd1gBeqHHtC9
xdWzlS2tD6zC+x9SoTaWAAAAC2NoZW1kYi1kZW1vAQI=
-----END OPENSSH PRIVATE KEY-----
"""
