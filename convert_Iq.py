#!/usr/bin/env python3
"""
独立脚本：把 https://raw.githubusercontent.com/WeiGiegie/vpm/main/lq.snippet
生成**完整可用** Clash 配置 Iq.yaml
工作流每 3 小时调用一次即可。
"""
import base64
import urllib.parse
import yaml
import requests

SRC_URL = 'https://raw.githubusercontent.com/WeiGiegie/vpm/main/lq.snippet'
OUT_FILE = 'Iq.yaml'

# ---------- 工具 ----------
def parse_ss(url: str):
    """ss://BASE64#NAME  →  Clash 字典"""
    try:
        if not url.startswith('ss://'):
            return None
        body, _, name_b64 = url[5:].partition('#')
        name = urllib.parse.unquote(name_b64) if name_b64 else 'ss'

        if '@' in body:                       # 新版：cipher:pwd@host:port
            cipher_pwd, host_port = body.split('@', 1)
        else:                                 # 旧版：整体 BASE64
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
            'password': password,
            'udp': True
        }
    except Exception:
        return None

# ---------- 主逻辑 ----------
def main():
    r = requests.get(SRC_URL, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
    r.raise_for_status()

    proxies = []
    for line in r.text.splitlines():
        node = parse_ss(line.strip())
        if node:
            proxies.append(node)

    # 构造完整配置（端口/日志/规则等随你改）
    clash = {
        'port': 7890,
        'socks-port': 7891,
        'redir-port': 7892,
        'mixed-port': 7893,
        'allow-lan': False,
        'mode': 'rule',
        'log-level': 'info',
        'ipv6': True,
        'external-controller': '0.0.0.0:9090',
        'proxies': proxies,
        'proxy-groups': [
            {'name': 'Proxies', 'type': 'select', 'proxies': [p['name'] for p in proxies]}
        ],
        'rules': [
            'GEOIP,CN,DIRECT',
            'MATCH,Proxies'
        ]
    }

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(clash, f, allow_unicode=True)

    print(f'::notice ::已生成 {OUT_FILE}  共 {len(proxies)} 个节点')

if __name__ == '__main__':
    main()
