"""Task-local MCP diagnostics; strictly allow-listed read operations, no orders."""
import argparse
import json
from pathlib import Path
import tomllib
import urllib.request

ALLOWED = {'get_workspace_info', 'get_time_information', 'list_open_charts',
           'get_marketwatch_symbols', 'get_chart_history', 'get_chart_ticks_history',
           'tester_get_configuration'}
ROOT = Path(__file__).resolve().parent
CONFIG = ROOT.parents[2] / '.codex' / 'config.toml'


class Client:
    def __init__(self):
        s = tomllib.loads(CONFIG.read_text(encoding='utf-8'))['mcp_servers']['terminal']
        if s['url'] != 'http://127.0.0.1:22344/mcp':
            raise ValueError('Unexpected endpoint; review configuration')
        self.url = s['url']
        self.headers = {**s['http_headers'], 'Content-Type': 'application/json',
                        'Accept': 'application/json, text/event-stream'}
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.counter = 0
        self.rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                 'clientInfo': {'name': 'tradingworkspace-readonly', 'version': '1.0'}})
        self.rpc('notifications/initialized', {}, notification=True)

    def rpc(self, method, params, notification=False):
        self.counter += 1
        msg = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if not notification:
            msg['id'] = self.counter
        req = urllib.request.Request(self.url, data=json.dumps(msg).encode(), headers=self.headers)
        with self.opener.open(req, timeout=30) as r:
            if r.headers.get('Mcp-Session-Id'):
                self.headers['Mcp-Session-Id'] = r.headers['Mcp-Session-Id']
            raw = r.read().decode()
        if not raw:
            return {}
        if raw.lstrip().startswith('{'):
            result = json.loads(raw)
        else:
            result = next(json.loads(x[6:]) for x in raw.splitlines() if x.startswith('data: '))
        if 'error' in result:
            raise RuntimeError(f"MCP error code {result['error'].get('code')}")
        return result['result']

    def call(self, name, arguments):
        if name not in ALLOWED:
            raise ValueError('Operation is not in read-only allow list')
        return self.rpc('tools/call', {'name': name, 'arguments': arguments})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['schemas', *sorted(ALLOWED)])
    p.add_argument('--arguments', default='{}')
    p.add_argument('--save', help='New JSON filename under mcp-data; never overwrite')
    a = p.parse_args()
    client = Client()
    if a.operation == 'schemas':
        result = [t for t in client.rpc('tools/list', {}).get('tools', []) if t['name'] in ALLOWED]
    else:
        workspace = client.call('get_workspace_info', {})
        if workspace.get('isError'):
            raise RuntimeError('Workspace preflight failed')
        result = workspace if a.operation == 'get_workspace_info' else client.call(a.operation, json.loads(a.arguments))
    if a.save:
        if Path(a.save).name != a.save or not a.save.endswith('.json'):
            raise ValueError('Use a plain JSON filename')
        folder = ROOT / 'mcp-data'
        folder.mkdir(exist_ok=True)
        with (folder / a.save).open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print('Saved:', folder / a.save)
    else:
        print(json.dumps(result, ensure_ascii=True, indent=2))
