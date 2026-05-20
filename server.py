#!/usr/bin/env python3
import errno
import html
import mimetypes
import os
import stat as stat_module
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, quote

import smbclient
from smbprotocol.exceptions import SMBOSError

SMB_HOST = os.environ['SMB_HOST']
SMB_SHARE = os.environ['SMB_SHARE']
SMB_USER = os.environ.get('SMB_USER', 'guest')
SMB_PASSWORD = os.environ.get('SMB_PASSWORD', '')
SMB_DOMAIN = os.environ.get('SMB_DOMAIN', '')
SMB_BASE = os.environ.get('SMB_PATH', '').strip('\\/')

_smb_user = f"{SMB_DOMAIN}\\{SMB_USER}" if SMB_DOMAIN else SMB_USER


def to_smb_path(url_path: str) -> str:
    parts = [p for p in url_path.split('/') if p]
    base = f"\\\\{SMB_HOST}\\{SMB_SHARE}"
    if SMB_BASE:
        base += f"\\{SMB_BASE}"
    if parts:
        base += '\\' + '\\'.join(parts)
    return base


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = unquote(self.path.split('?')[0])
        smb_path = to_smb_path(url_path)

        try:
            st = smbclient.stat(smb_path)
        except SMBOSError as e:
            self.send_error(404 if e.errno == errno.ENOENT else 503)
            return
        except Exception:
            self.send_error(503)
            return

        if stat_module.S_ISDIR(st.st_mode):
            if not url_path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', url_path + '/')
                self.end_headers()
                return
            try:
                self._serve_directory(url_path, smb_path)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            try:
                self._serve_file(url_path, smb_path)
            except Exception as e:
                self.send_error(500, str(e))

    def _serve_directory(self, url_path: str, smb_path: str):
        entries = []
        for entry in smbclient.scandir(smb_path):
            st = entry.stat()
            entries.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'size': st.st_size,
            })
        entries.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))

        body = _render_listing(url_path, entries).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, url_path: str, smb_path: str):
        mime, _ = mimetypes.guess_type(url_path)
        self.send_response(200)
        self.send_header('Content-Type', mime or 'application/octet-stream')
        self.end_headers()
        with smbclient.open_file(smb_path, mode='rb') as f:
            while chunk := f.read(65536):
                self.wfile.write(chunk)

    def log_message(self, fmt, *args):
        print(f'{self.address_string()} {fmt % args}', flush=True)


def _render_listing(url_path: str, entries: list) -> str:
    title = html.escape(url_path)
    rows = []

    if url_path != '/':
        parent = url_path.rstrip('/').rsplit('/', 1)[0] + '/'
        rows.append(f'<tr><td colspan="2"><a href="{parent}">..</a></td></tr>')

    for e in entries:
        href = quote(url_path + e['name']) + ('/' if e['is_dir'] else '')
        display = html.escape(e['name']) + ('/' if e['is_dir'] else '')
        size = '—' if e['is_dir'] else _fmt_size(e['size'])
        rows.append(
            f'<tr><td><a href="{href}">{display}</a></td>'
            f'<td class="sz">{size}</td></tr>'
        )

    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Index of {title}</title>
<style>
  body{{font-family:monospace;padding:1.5rem;background:#fff;color:#222}}
  h1{{font-size:1.1rem;margin-bottom:1rem;word-break:break-all}}
  table{{border-collapse:collapse}}
  td{{padding:.2rem 1.5rem .2rem 0;white-space:nowrap}}
  .sz{{color:#888;text-align:right}}
  a{{color:#1a6;text-decoration:none}}
  a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<h1>Index of {title}</h1>
<table>{''.join(rows)}</table>
</body>
</html>'''


def _fmt_size(n: int) -> str:
    for unit in ('B', 'K', 'M', 'G', 'T'):
        if n < 1024:
            return f'{n:.0f} {unit}'
        n /= 1024
    return f'{n:.1f} P'


if __name__ == '__main__':
    smbclient.register_session(
        SMB_HOST,
        username=_smb_user,
        password=SMB_PASSWORD,
        connection_timeout=30,
    )
    port = int(os.environ.get('PORT', '80'))
    addr = f'//{SMB_HOST}/{SMB_SHARE}' + (f'/{SMB_BASE}' if SMB_BASE else '')
    print(f'samba-web :{port} -> {addr}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
