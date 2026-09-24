"""通过 SSH 通道访问 chemDb 服务端 API 的客户端封装。

连接链路：paramiko SSH（走 SakuraFRP TCP 隧道） ->
服务器 127.0.0.1:8000 的 HTTP 服务。
open_channel 可注入，便于本地用裸 TCP socket 调试。
"""

import http.client
import io
import json
import urllib.parse
import uuid

import paramiko


class APIError(Exception):
    def __init__(self, status, detail):
        self.status = status
        super().__init__(f"HTTP {status}: {detail}")


def _encode_multipart(fields, files):
    """fields: {name: str}; files: [(field, filename, content_type, bytes)]"""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += str(value).encode("utf-8") + b"\r\n"
    for field, filename, ctype, data in files:
        quoted = urllib.parse.quote(filename)
        head = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field}"; '
            f'filename="{quoted}"; filename*=UTF-8\'\'{quoted}\r\n'
            f"Content-Type: {ctype}\r\n\r\n"
        )
        body += head.encode() + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


class ChemDBClient:
    def __init__(self, ssh_host, ssh_port, ssh_user, private_key_str,
                 remote_host="127.0.0.1", remote_port=8000,
                 api_token="", timeout=30, open_channel=None):
        self.remote = (remote_host, remote_port)
        self.api_token = api_token
        self.timeout = timeout
        self._open_channel = open_channel
        self._ssh_args = (ssh_host, ssh_port, ssh_user, private_key_str)
        self.transport = None

    def connect(self):
        if self._open_channel is not None:
            return  # 调试模式，无需 SSH
        host, port, user, key_str = self._ssh_args
        pkey = paramiko.Ed25519Key.from_private_key(io.StringIO(key_str.strip()))
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=user, pkey=pkey)
        self.transport.set_keepalive(30)

    def close(self):
        if self.transport:
            self.transport.close()

    def _open(self):
        if self._open_channel is not None:
            return self._open_channel()
        return self.transport.open_channel(
            "direct-tcpip", self.remote, ("127.0.0.1", 0)
        )

    def request(self, method, path, params=None, fields=None, files=None):
        if params:
            path += "?" + urllib.parse.urlencode(params)
        headers = {"Authorization": f"Bearer {self.api_token}"}
        body = None
        if fields is not None or files:
            body, headers["Content-Type"] = _encode_multipart(fields or {}, files or [])

        conn = http.client.HTTPConnection(*self.remote, timeout=self.timeout)
        conn.sock = self._open()  # 预置通道，跳过 connect()
        try:
            conn.request(method, path, body=body, headers=headers)
            resp = conn.getresponse()
            data = resp.read()
            if resp.status >= 400:
                try:
                    detail = json.loads(data).get("detail", data[:200])
                except Exception:
                    detail = data[:200]
                raise APIError(resp.status, detail)
            return data
        finally:
            conn.close()

    def _json(self, method, path, **kw):
        return json.loads(self.request(method, path, **kw))

    # ---- 高层 API ----

    def health(self):
        return self._json("GET", "/api/health")

    def list_entries(self, q="", limit=50, offset=0):
        return self._json("GET", "/api/entries",
                          params={"q": q, "limit": limit, "offset": offset})

    def get_entry(self, entry_id):
        return self._json("GET", f"/api/entries/{entry_id}")

    def create_entry(self, text, file_paths):
        files = [self._load_file(p) for p in file_paths]
        return self._json("POST", "/api/entries", fields={"text": text}, files=files)

    def update_entry(self, entry_id, text):
        return self._json("PUT", f"/api/entries/{entry_id}", fields={"text": text})

    def delete_entry(self, entry_id):
        return self._json("DELETE", f"/api/entries/{entry_id}")

    def add_attachments(self, entry_id, file_paths):
        files = [self._load_file(p) for p in file_paths]
        return self._json("POST", f"/api/entries/{entry_id}/attachments", files=files)

    def delete_attachment(self, att_id):
        return self._json("DELETE", f"/api/attachments/{att_id}")

    def download_attachment(self, att_id):
        return self.request("GET", f"/api/attachments/{att_id}/file")

    def get_thumb(self, att_id):
        try:
            return self.request("GET", f"/api/attachments/{att_id}/thumb")
        except APIError as e:
            if e.status == 404:
                return None
            raise

    @staticmethod
    def _load_file(path):
        import mimetypes
        import os

        with open(path, "rb") as f:
            data = f.read()
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        return ("files", os.path.basename(path), ctype, data)
