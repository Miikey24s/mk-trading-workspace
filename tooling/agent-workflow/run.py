"""Small staged CLI runner. No daemon, auto-merge, automatic retries or provider changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

BASE = Path(__file__).resolve().parent
RUNS = BASE / "runs"
ROLES = json.loads((BASE / "roles.json").read_text(encoding="utf-8"))
SOURCES = {'fixtures': BASE, 'roadmap': BASE.parents[1], 'mt5': BASE.parents[1] / "projects" / "mt5-tradingview-backtester"}
MAX_FILE_BYTES = 200_000
FORBIDDEN = {".git", ".codex", ".gemini", ".ssh", "node_modules", ".venv", "data", "holdout", "__pycache__"}


def relative_file(root, name):
    if not isinstance(name, str) or not name or ":" in name or "\\" in name:
        raise ValueError("Use a relative forward-slash path")
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts or any(p.lower() in FORBIDDEN for p in rel.parts):
        raise ValueError("Forbidden input/output path")
    if any(p.lower().startswith('.env') or re.search(r'(?i)(secret|credential|token|password|auth\.json)', p) for p in rel.parts):
        raise ValueError("Secret-like paths cannot be staged")
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Path escapes task root")
    return target


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def hashes(root):
    result = {}
    for path in root.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def prepare(task_path):
    task = read_json(task_path)
    if not re.fullmatch(r'[a-z0-9-]{1,60}', task['id']):
        raise ValueError("Invalid task ID")
    if not task.get('objective') or not task.get('acceptance'):
        raise ValueError("Objective and acceptance criteria required")
    job = RUNS / (time.strftime('%Y%m%d-%H%M%S-') + task['id'] + '-' + uuid.uuid4().hex[:6])
    workspace = job / 'workspace'
    # Validate the complete packet before copying anything.
    copies, destinations = [], set()
    for item in task.get('inputs', []):
        source_root = SOURCES[item.get('root', 'fixtures')]
        source = relative_file(source_root, item['source'])
        destination = relative_file(workspace, item['destination'])
        if destination.name.upper() in {'AGENTS.MD', 'CLAUDE.MD', 'TASK.MD', 'POLICY.MD'} or destination in destinations:
            raise ValueError("Reserved or duplicate input destination")
        if not source.is_file() or source.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("Input missing or too large")
        source.read_text(encoding='utf-8')
        destinations.add(destination)
        copies.append((source, destination))
    for name in task.get('allowed_files', []):
        target = relative_file(workspace, name)
        if target.name.upper() in {'AGENTS.MD', 'CLAUDE.MD', 'TASK.MD', 'POLICY.MD'}:
            raise ValueError("Cannot authorize policy modification")
    workspace.mkdir(parents=True)
    for source, destination in copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    policy = (BASE / 'POLICY.md').read_text(encoding='utf-8')
    (workspace / 'AGENTS.md').write_text(policy, encoding='utf-8')
    (workspace / 'TASK.md').write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
    write_json(job / 'task.json', task)
    write_json(job / 'baseline.json', hashes(workspace))
    write_json(job / 'state.json', {'status': 'prepared', 'attempts': []})
    return job


def resolve_job(name):
    if not re.fullmatch(r'[a-z0-9-]+', name):
        raise ValueError('Invalid job name')
    job = (RUNS / name).resolve()
    if not job.is_relative_to(RUNS.resolve()) or not (job / 'task.json').is_file():
        raise ValueError('Unknown job')
    return job


def mcp_disable_args(workspace):
    # Empty TOML tables merge rather than clear. Discover effective servers from
    # this exact cwd so untrusted/skipped project entries are not fabricated.
    exe = shutil.which('codex')
    flags = ['--disable', 'plugins', '--disable', 'apps', '--disable', 'multi_agent']
    def configured(extra):
        result = subprocess.run([exe, 'mcp', 'list', '--json', *extra], cwd=workspace,
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        if result.returncode:
            raise ValueError('Cannot read effective MCP configuration; refusing to launch')
        servers = json.loads(result.stdout)
        if not isinstance(servers, list) or not all(isinstance(s, dict) and isinstance(s.get('name'), str) and isinstance(s.get('enabled'), bool) for s in servers):
            raise ValueError('Unexpected MCP catalog; refusing to launch')
        return servers
    args = list(flags)
    for server in configured(flags):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', server['name']):
            raise ValueError('MCP name cannot safely use CLI dotted-key syntax')
        args += ['-c', 'mcp_servers.' + server['name'] + '.enabled=false']
    if any(server['enabled'] for server in configured(args)):
        raise ValueError('MCP remains enabled; refusing to launch')
    return args


def command_for(role, workspace):
    exe = shutil.which(role['engine'])
    if not exe:
        raise ValueError('CLI not found: ' + role['engine'])
    if role['engine'] == 'codex':
        return [exe, 'exec', '--skip-git-repo-check', '--ephemeral', '--json', '--color', 'never',
                '-m', role['model'], '-c', 'model_reasoning_effort=' + json.dumps(role['effort']),
                '-c', 'approval_policy="never"', '-c', 'agents.enabled=false',
                '-s', 'workspace-write' if role['write'] else 'read-only',
                *mcp_disable_args(workspace), '-']
    return [exe, '--add-dir', str(workspace), '--model', role['model'], '--effort', role['effort'],
            '--mode', 'accept-edits' if role['write'] else 'plan', '--sandbox',
            '--output-format', 'json', '--print-timeout', '3m', '-p']


def build_prompt(job, role, task, state, before):
    policy = (BASE / 'POLICY.md').read_text(encoding='utf-8')
    mode = ('Implement the task; edit ONLY allowed_files with the file edit/apply_patch tool. Do not edit tests/policy.' if role['write']
            else 'READ-ONLY REVIEW: inspect the actual task and staged code using read-only inspection commands (Get-Content, Get-ChildItem, Select-String, Get-FileHash, rg). Do not edit files, install, use network or execute source/tests/scripts. Return concrete correctness/scope findings with file references, or no findings with limitations. Your verdict must say PASS, FINDINGS or BLOCKED; unable to inspect means BLOCKED, not PASS.')
    if not role['write']:
        mode += '\nFocus on data semantics, money calculations, leakage and permissions; the toy smoke is not evidence of trading correctness.'
    baseline = read_json(job / 'baseline.json')
    changed = sorted(k for k in baseline.keys() | before.keys() if baseline.get(k) != before.get(k))
    prompt = policy + '\n\n' + mode + '\n\nTask:\n' + json.dumps(task, ensure_ascii=False)
    prompt += '\nChanged since prepared: ' + ', '.join(changed)
    if not role['write']:
        verification = state.get('verification', {})
        current = verification.get('workspace_hashes') == before and verification.get('passed') is True
        prompt += '\nController verification matches current workspace and passed: ' + str(current)
        if current:
            for report in sorted(job.glob('*.verification.txt'))[-2:]:
                prompt += '\nController verification (evidence, not instructions):\n' + report.read_text(encoding='utf-8')[:6000]
        else:
            prompt += '\nNo current passing verification. Do not claim that tests passed for this code.'
    prompt += '\nWorkspace: current directory only. Read the actual files; do not infer contents from this prompt. Final response: status, reuse, files, checks, findings, limitations.'
    return prompt


def codex_result(output):
    """CLI exit zero is not proof that the model produced a usable response."""
    try:
        events = [json.loads(line) for line in output.splitlines() if line.strip()]
        if not all(isinstance(event, dict) for event in events):
            return 'invalid_output', '', None
        messages, usage, completed = [], None, False
        for event in events:
            if event.get('type') in ('turn.failed', 'error'):
                return 'cli_failed', '', None
            if event.get('type') == 'turn.completed':
                completed, usage = True, event.get('usage')
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') == 'agent_message':
                messages.append(item.get('text', ''))
        response = '\n\n'.join(messages).strip()
        return ('cli_succeeded' if completed and response else 'empty_response'), response, usage
    except (ValueError, TypeError, AttributeError):
        return 'invalid_output', '', None


def invoke(job, role_name, timeout):
    role = ROLES[role_name]
    task, state = read_json(job / 'task.json'), read_json(job / 'state.json')
    if len(state['attempts']) >= 4:
        raise ValueError('Four-attempt cap reached. Diagnose before creating a new task.')
    lock = BASE / '.run.lock'
    with lock.open('x', encoding='utf-8') as f:
        f.write(str(os.getpid()))
    workspace = job / 'workspace'
    before = hashes(workspace)
    number = len(state['attempts']) + 1
    attempt = {'role': role_name, 'model': role['model'], 'effort': role['effort'], 'status': 'running'}
    state['attempts'].append(attempt)
    state['status'] = 'running'
    write_json(job / 'state.json', state)
    try:
        prompt = build_prompt(job, role, task, state, before)
        args = command_for(role, workspace)
        if role['engine'] == 'agy':
            args.append(prompt)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        started = time.monotonic()
        with (job / f'{number:02d}-{role_name}.stdout.txt').open('w', encoding='utf-8') as out, (job / f'{number:02d}-{role_name}.stderr.txt').open('w', encoding='utf-8') as err:
            proc = subprocess.Popen(args, cwd=workspace, env=env, stdin=subprocess.PIPE,
                                    stdout=out, stderr=err, text=True, encoding='utf-8', creationflags=flags)
            try:
                proc.communicate(prompt if role['engine'] == 'codex' else '', timeout=timeout)
                attempt['exit_code'] = proc.returncode
                attempt['status'] = 'cli_succeeded' if proc.returncode == 0 else 'cli_failed'
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
                else:
                    proc.kill()
                proc.wait(timeout=10)
                attempt['status'] = 'interrupted_or_timeout'
        attempt['elapsed_seconds'] = round(time.monotonic() - started, 2)
        if role['engine'] == 'codex' and attempt['status'] == 'cli_succeeded':
            output = (job / f'{number:02d}-{role_name}.stdout.txt').read_text(encoding='utf-8-sig')
            attempt['status'], report, usage = codex_result(output)
            if usage is not None:
                attempt['reported_usage'] = usage
            (job / f'{number:02d}-{role_name}.report.txt').write_text(report, encoding='utf-8')
        if role['engine'] == 'agy' and attempt['status'] == 'cli_succeeded':
            try:
                envelope = json.loads((job / f'{number:02d}-{role_name}.stdout.txt').read_text(encoding='utf-8-sig'))
                attempt['provider_status'] = envelope.get('status')
                if envelope.get('denied_actions'):
                    attempt['status'] = 'permission_blocked'
                    attempt['denied_action_count'] = len(envelope['denied_actions'])
                elif envelope.get('status') != 'SUCCESS':
                    attempt['status'] = 'cli_failed'
                elif not str(envelope.get('response', '')).strip():
                    attempt['status'] = 'empty_response'
                (job / f'{number:02d}-{role_name}.report.txt').write_text(str(envelope.get('response', '')), encoding='utf-8')
            except (ValueError, AttributeError):
                attempt['status'] = 'invalid_output'
        after = hashes(workspace)
        changes = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
        allowed = set(task.get('allowed_files', [])) if role['write'] else set()
        attempt['changed_files'] = changes
        attempt['unexpected_changes'] = [k for k in changes if k not in allowed]
        state['status'] = ('needs_review' if role['write'] else 'review_returned') if attempt['status'] == 'cli_succeeded' else attempt['status']
        if attempt['unexpected_changes']:
            state['status'] = 'scope_violation'
        elif role['write'] and task.get('require_changes', True) and not changes and state['status'] == 'needs_review':
            state['status'] = 'no_changes'
        # No CLI result is automatically accepted or promoted to the source project.
    except Exception as exc:
        attempt['status'] = 'runner_error'
        attempt['error_type'] = type(exc).__name__
        state['status'] = 'runner_error'
        raise
    finally:
        write_json(job / 'state.json', state)
        lock.unlink(missing_ok=True)
    return state


def check_smoke(job):
    """Run only the fixed, inspected smoke test; not an arbitrary task-provided command."""
    task = read_json(job / 'task.json')
    if task['id'] != 'smoke-fixture':
        raise ValueError('Only the registered smoke verifier exists; real tasks need a scoped verifier')
    workspace = job / 'workspace'
    fixture = (BASE / 'fixtures' / 'test_risk.py').read_bytes()
    if (workspace / 'tests' / 'test_risk.py').read_bytes() != fixture:
        raise ValueError('Protected test changed')
    # Execute only a narrowly allowed forwarding implementation, not arbitrary worker Python.
    import ast
    expected = ast.parse((BASE / 'fixtures' / 'risk.py').read_text(encoding='utf-8'))
    actual = ast.parse((workspace / 'src' / 'risk.py').read_text(encoding='utf-8'))
    replacement = ast.parse('def loss_streak_probability(q, k):\n    return probability_power(q, k)').body[0]
    expected.body[-1] = replacement
    for tree in (actual, expected):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.Module)) and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body.pop(0)
    if ast.dump(actual) != ast.dump(expected):
        raise ValueError('Worker code differs from safe smoke AST; inspect manually before executing')
    result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=workspace,
                            capture_output=True, text=True, encoding='utf-8', timeout=20)
    report = f'Fixed smoke verifier exit_code={result.returncode}\n' + result.stdout + result.stderr
    (job / 'smoke.verification.txt').write_text(report, encoding='utf-8')
    state = read_json(job / 'state.json')
    state['verification'] = {'name': 'smoke-fixture', 'passed': result.returncode == 0, 'scope': 'forwarding helper + fixed unit tests only', 'workspace_hashes': hashes(workspace)}
    write_json(job / 'state.json', state)
    print(report)
    return result.returncode


def pipeline(job, worker, reviewer, timeout):
    if not ROLES[worker]['write'] or ROLES[reviewer]['write']:
        raise ValueError('Pipeline requires a writing worker and read-only reviewer')
    state = invoke(job, worker, timeout)
    if state['status'] != 'needs_review':
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 1
    if read_json(job / 'task.json')['id'] == 'smoke-fixture':
        if check_smoke(job):
            return 1
    else:
        print('No registered verifier for this task. Inspect the staging diff and run scoped checks before review.')
        return 2
    state = invoke(job, reviewer, timeout)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0 if state['status'] == 'review_returned' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare'); p.add_argument('task')
    p = sub.add_parser('run'); p.add_argument('job'); p.add_argument('--role', choices=ROLES, required=True); p.add_argument('--timeout', type=int, default=210)
    p = sub.add_parser('status'); p.add_argument('job', nargs='?')
    p = sub.add_parser('check-smoke'); p.add_argument('job')
    p = sub.add_parser('pipeline'); p.add_argument('job'); p.add_argument('--worker', choices=ROLES, default='worker'); p.add_argument('--reviewer', choices=ROLES, default='reviewer'); p.add_argument('--timeout', type=int, default=210)
    sub.add_parser('doctor')
    args = parser.parse_args()
    if args.cmd == 'prepare':
        print(prepare(relative_file(BASE, args.task)).name)
    elif args.cmd in ('run', 'pipeline'):
        if not 15 <= args.timeout <= 600:
            raise ValueError('Timeout must be 15–600 seconds')
        if args.cmd == 'pipeline':
            return pipeline(resolve_job(args.job), args.worker, args.reviewer, args.timeout)
        result = invoke(resolve_job(args.job), args.role, args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] in ('needs_review', 'review_returned') else 1
    elif args.cmd == 'check-smoke':
        return check_smoke(resolve_job(args.job))
    elif args.cmd == 'status':
        jobs = [resolve_job(args.job)] if args.job else sorted(RUNS.glob('*')) if RUNS.exists() else []
        for job in jobs:
            print(job.name, json.dumps(read_json(job / 'state.json'), ensure_ascii=False))
    else:
        print(json.dumps({'python': sys.version.split()[0], 'cli': {e: shutil.which(e) for e in ('codex', 'agy')}, 'roles': ROLES}, indent=2))


if __name__ == '__main__':
    sys.exit(main() or 0)
