#!/usr/bin/env python3
"""
独立脚本：把 https://raw.githubusercontent.com/WeiGiegie/vpm/main/lq.snippet
（Base64 编码的 ss 链接） → 标准 Clash YAML（Iq.yaml）
工作流每 3 小时调用一次即可。
"""
import base64
import urllib.parse
import yaml
import requests
import sys

SRC_URL = 'https://raw.githubusercontent.com/WeiGiegie/vpm/main/lq.snippet'
OUT_FILE = 'Iq.yaml'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def parse_ss(url: str):
    """ss://BASE64#NAME  →  Clash 字典"""
    try:
        if not url.startswith('ss://'):
            return None
        body, _, name_b64 = url[5:].partition('#')
        name = urllib.parse.unquote(name_b64) if name_b64 else 'ss'

        # 情况 1: BASE64@host:port
        if '@' in body:
            cipher_pwd, host_port = body.split('@', 1)
        # 情况 2: 整体 BASE64
        else:
            plain = base64.b64decode(body + '==').decode()
            cipher_pwd, host_port = plain.split('@', 1)

        cipher, password = cipher_pwd.split(':', 1)
        host, port = host_port.rsplit(':', 1)

        return {
            'name': name,
            'type': 'ss',
            'server': host,
            'port': int(port),
            'cipher': cipher,
            'password': password
        }
    except Exception as e:
        print(f'[warn] 解析失败: {url}  {e}', file=sys.stderr)
        return None

def main():
    r = requests.get(SRC_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    nodes = []
    for line in r.text.splitlines():
        line = line.strip()
        node = parse_ss(line)
        if node:
            nodes.append(node)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump({'proxies': nodes}, f, allow_unicode=True)

    print(f'::notice ::已生成 {OUT_FILE}  共 {len(nodes)} 个节点')

if __name__ == '__main__':
    main()
