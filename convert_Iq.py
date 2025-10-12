#!/usr/bin/env python3
import base64, yaml, requests, sys, os

URL = 'https://raw.githubusercontent.com/WeiGiegie/vpm/main/lq.snippet'
OUT = 'Iq.yaml'          # 单独存在，不跟主流程任何文件重名

# 极简 Node → Clash 字典（只取常用字段）
def raw_to_clash(raw: str):
    """vmess/ss/trojan/vless 原始链接 → Clash 字典"""
    try:
        if raw.startswith('vmess://'):
            d = __import__('json').loads(base64.b64decode(raw[8:] + '==').decode())
            return {
                'name': d.get('ps', 'vmess'),
                'type': 'vmess',
                'server': d['add'],
                'port': int(d['port']),
                'uuid': d['id'],
                'alterId': int(d.get('aid', 0)),
                'cipher': d.get('scy', 'auto'),
                'tls': d.get('tls') == 'tls',
                'network': d.get('net', 'tcp'),
                'ws-opts': {'path': d.get('path', ''), 'headers': {'Host': d.get('host', '')}} if d.get('net') == 'ws' else {},
            }
        if raw.startswith('ss://'):
            from urllib.parse import unquote
            body = raw[5:]
            if '#' in body:
                body, name = body.rsplit('#', 1)
                name = unquote(name)
            else:
                name = 'ss'
            if '@' in body:
                cipher_pwd, server_port = body.split('@', 1)
            else:
                cipher_pwd = base64.b64decode(body + '==').decode()
                server_port = ''
            cipher, pwd = cipher_pwd.split(':', 1)
            server, port = server_port.split(':', 1)
            return {
                'name': name,
                'type': 'ss',
                'server': server,
                'port': int(port),
                'cipher': cipher,
                'password': pwd,
            }
        # 其余协议同理，可再补
        return None
    except Exception:
        return None

def main():
    r = requests.get(URL, timeout=15)
    r.raise_for_status()

    proxies = []
    for line in r.text.splitlines():
        line = line.strip()
        if '://' not in line:
            continue
        node = raw_to_clash(line)
        if node:
            proxies.append(node)

    with open(OUT, 'w', encoding='utf-8') as f:
        yaml.dump({'proxies': proxies}, f, allow_unicode=True)

    print(f'::notice ::已生成 {OUT}  共 {len(proxies)} 个节点')

if __name__ == '__main__':
    main()
