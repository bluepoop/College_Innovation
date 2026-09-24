# chemDb

小组共用的文字+附件小数据库。服务端跑在本机（SQLite + FastAPI，只监听 127.0.0.1），
Windows 客户端通过 SakuraFRP TCP 隧道 + SSH 通道访问。

```
Windows 客户端(exe) --SSH(paramiko)--> SakuraFRP TCP 隧道 --> 服务器 sshd(22)
                                                              │ 端口转发
                                                              ▼
                                                  127.0.0.1:8000 FastAPI
                                                              ▼
                                              data/chemdb.db + data/files/
```

## 服务端部署

1. 安装依赖（需要 Python 3.10+）：

```bash
cd server
python3 -m venv .venv           # Debian/Ubuntu 需先 apt install python3-venv
.venv/bin/pip install -r requirements.txt
```

2. 创建专用低权限账户并限制 key 只能做端口转发：

```bash
sudo useradd -m -s /usr/sbin/nologin chemdb
sudo -u chemdb mkdir -p /home/chemdb/.ssh
# 把 client/chemdb_demo_key.pub 的内容写成下面这样一行（注意前面的限制参数）：
# permitopen="127.0.0.1:8000",no-pty,no-agent-forwarding,no-X11-forwarding ssh-ed25519 AAAA... chemdb-demo
sudo -u chemdb $EDITOR /home/chemdb/.ssh/authorized_keys
sudo -u chemdb chmod 600 /home/chemdb/.ssh/authorized_keys
```

注意：`nologin` shell 下 `paramiko` 不开 shell、只做 direct-tcpip 转发是可以工作的。
sshd 配置需保持 `AllowTcpForwarding yes`（默认值）。

3. 修改配置（可选）：环境变量 `CHEMDB_TOKEN`（API token，务必改掉默认值）、
`CHEMDB_DATA`（数据目录）、`CHEMDB_MAX_UPLOAD_MB`（附件大小上限，默认 50MB）。

4. 启动：

```bash
CHEMDB_TOKEN=你的token ./run.sh
```

或用 systemd（把 `server/chemdb.service` 按实际路径改好后放到 /etc/systemd/system/）。

5. SakuraFRP：建一条 TCP 隧道，本地地址 `127.0.0.1`，本地端口 `22`，
把分配的连接地址和端口填到 `client/config.py` 的 `SSH_HOST` / `SSH_PORT`。

## 客户端（Windows）

直接用源码跑：

```
cd client
pip install -r requirements.txt
python main.py
```

打包绿色版 exe：双击 `build.bat`，产物在 `dist\chemDb-client.exe`，单文件双击即用。

发布前记得修改 `client/config.py`：

- `SSH_HOST` / `SSH_PORT`：SakuraFRP 分配的隧道地址和端口
- `API_TOKEN`：与服务端一致
- `SSH_PRIVATE_KEY`：demo 自带的测试私钥，正式使用请重新生成一对
  （`ssh-keygen -t ed25519 -f chemdb_key -N ''`），私钥贴进 config.py，
  公钥按上面的格式加到服务器 `chemdb` 账户的 authorized_keys。

## 功能

- 新建记录：文字 + 任意多个附件（图片/常见文件）
- 中文全文检索（SQLite FTS5，CJK 单字分词）
- 查看/修改文字，图片缩略图预览，附件下载
- 删除整条记录或单独删除某个附件

## 数据与备份

所有数据在 `server/data/` 下：`chemdb.db`（SQLite，WAL 模式）、`files/`（附件）、
`thumbs/`（缩略图缓存）。备份直接整个目录拷走即可。
