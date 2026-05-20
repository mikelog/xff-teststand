#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import datetime

class HeaderInspector(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{datetime.datetime.now().isoformat()}] {fmt % args}")

    def do_GET(self):
        headers_dict = dict(self.headers)

        xff = headers_dict.get("X-Forwarded-For", "<не передан>")
        x_proxy_path = headers_dict.get("X-Proxy-Path", "<не передан>")

        if "curl" in headers_dict.get("User-Agent", "").lower() or \
           self.path.startswith("/raw"):
            body = self._build_text(xff, x_proxy_path, headers_dict)
            content_type = "text/plain; charset=utf-8"
        else:
            body = self._build_html(xff, x_proxy_path, headers_dict)
            content_type = "text/html; charset=utf-8"

        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _build_text(self, xff, proxy_path, headers):
        lines = [
            "=" * 60,
            "  X-Forwarded-For Inspector (text mode)",
            "=" * 60,
            f"  X-Forwarded-For : {xff}",
            f"  X-Proxy-Path    : {proxy_path}",
            "-" * 60,
            "  Все заголовки:",
        ]
        for k, v in sorted(headers.items()):
            lines.append(f"    {k}: {v}")
        lines.append("=" * 60)
        return "\n".join(lines) + "\n"

    def _build_html(self, xff, proxy_path, headers):
        rows = "".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in sorted(headers.items())
        )
        xff_chain = [ip.strip() for ip in xff.split(",")] if xff != "<не передан>" else []
        chain_html = ""
        if xff_chain:
            labels = ["👤 Клиент"] + [f"🔀 Прокси {i}" for i in range(1, len(xff_chain))]
            chain_html = "<div class='chain'>" + "".join(
                f"<span class='node'>{lbl}<br><code>{ip}</code></span>"
                + ("<span class='arrow'>→</span>" if i < len(xff_chain) - 1 else "")
                for i, (lbl, ip) in enumerate(zip(labels, xff_chain))
            ) + "<span class='arrow'>→</span><span class='node'>🖥 App</span></div>"

        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>XFF Inspector</title>
<style>
  body {{ font-family: 'Courier New', monospace; background:#0d1117; color:#e6edf3;
          margin:0; padding:2rem; }}
  h1   {{ color:#58a6ff; border-bottom:1px solid #30363d; padding-bottom:.5rem; }}
  .badge {{ display:inline-block; background:#161b22; border:1px solid #30363d;
            border-radius:6px; padding:1rem 1.5rem; margin-bottom:1.5rem; width:100%;
            box-sizing:border-box; }}
  .badge label {{ color:#8b949e; font-size:.8rem; text-transform:uppercase; }}
  .badge .val  {{ color:#3fb950; font-size:1.1rem; word-break:break-all; }}
  .chain {{ display:flex; align-items:center; flex-wrap:wrap; gap:.4rem;
            margin:1rem 0; }}
  .node  {{ background:#161b22; border:1px solid #30363d; border-radius:6px;
            padding:.4rem .8rem; text-align:center; font-size:.85rem; }}
  .arrow {{ color:#8b949e; font-size:1.2rem; }}
  table  {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
  th,td  {{ padding:.5rem .8rem; border:1px solid #30363d; text-align:left; }}
  th     {{ background:#161b22; color:#8b949e; font-weight:normal; }}
  tr:hover td {{ background:#161b22; }}
  .hi    {{ background:#0d2d1a !important; }}
</style>
</head>
<body>
<h1>🔍 X-Forwarded-For Inspector</h1>

<div class="badge">
  <label>X-Forwarded-For</label><br>
  <span class="val">{xff}</span>
</div>

<div class="badge">
  <label>Цепочка прокси</label>
  {chain_html if chain_html else "<span style='color:#8b949e'>нет данных</span>"}
</div>

<div class="badge">
  <label>X-Proxy-Path (отладка)</label><br>
  <span class="val">{proxy_path}</span>
</div>

<h2 style="color:#8b949e;font-size:1rem;margin-top:2rem">Все заголовки запроса</h2>
<table>
<tr><th>Заголовок</th><th>Значение</th></tr>
{rows}
</table>
</body>
</html>"""


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), HeaderInspector)
    print("XFF Inspector слушает на :8000 ...")
    server.serve_forever()
