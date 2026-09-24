import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run


class RunnerTests(unittest.TestCase):
    def test_path_rejections(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ['../escape', 'C:/file', '/file', '.codex/config.toml', '.env', 'data/ticks.csv', 'secret.txt', 'a\\b', 'holdout/test']:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    run.relative_file(Path(root), name)

    def test_relative_path(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(run.relative_file(Path(root), 'src/a.py'), Path(root).resolve() / 'src/a.py')

    def test_prepare_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            before = (run.BASE / 'fixtures/risk.py').read_bytes()
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            self.assertEqual(run.read_json(job / 'state.json')['status'], 'prepared')
            self.assertEqual((job / 'workspace/src/risk.py').read_bytes(), before)
            self.assertEqual((run.BASE / 'fixtures/risk.py').read_bytes(), before)

    def test_codex_keeps_provider_and_scopes_tools(self):
        with patch('run.shutil.which', return_value='codex.exe'), patch('run.mcp_disable_args', return_value=[]):
            cmd = run.command_for(run.ROLES['reviewer'], run.BASE)
            self.assertIn('read-only', cmd)
            self.assertIn('chatgpt-web/high', cmd)
            self.assertIn('--json', cmd)
            self.assertNotIn('--ignore-user-config', cmd)
            self.assertIn('agents.enabled=false', cmd)
            self.assertFalse(any('model_provider' in x for x in cmd))

    def test_default_roles_prefer_web_gpt(self):
        for name in ('worker', 'reviewer', 'risk-reviewer'):
            self.assertEqual(run.ROLES[name]['model'], 'chatgpt-web/high')
            self.assertEqual(run.ROLES[name]['effort'], 'high')

    def test_disables_only_effective_mcp_entries_and_verifies(self):
        catalog = [{'name': 'unityMCP', 'enabled': True}]
        disabled = [{'name': 'unityMCP', 'enabled': False}]
        responses = [subprocess.CompletedProcess([], 0, json.dumps(catalog)), subprocess.CompletedProcess([], 0, json.dumps(disabled))]
        with patch('run.shutil.which', return_value='codex.exe'), patch('run.subprocess.run', side_effect=responses) as cmd:
            args = run.mcp_disable_args(run.BASE)
            self.assertIn('mcp_servers.unityMCP.enabled=false', args)
            self.assertFalse(any('metaeditor' in a for a in args))
            self.assertIn('plugins', args)
            self.assertEqual(cmd.call_args.kwargs['cwd'], run.BASE)

    def test_mcp_preflight_fails_closed(self):
        result = subprocess.CompletedProcess([], 0, '[{"name":"x","enabled":true}]')
        with patch('run.shutil.which', return_value='codex.exe'), patch('run.subprocess.run', return_value=result), self.assertRaises(ValueError):
            run.mcp_disable_args(run.BASE)

    def test_reviewer_can_inspect_but_not_execute_code(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            prompt = run.build_prompt(job, run.ROLES['reviewer'], run.read_json(job / 'task.json'), {}, run.hashes(job / 'workspace'))
            self.assertIn('Get-Content', prompt)
            self.assertIn('Do not edit files, install, use network or execute source/tests/scripts', prompt)
            self.assertIn('unable to inspect means BLOCKED', prompt)
            self.assertIn('No current passing verification', prompt)

    def test_codex_output_requires_completed_turn_and_response(self):
        result = json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'PASS'}})
        done = json.dumps({'type': 'turn.completed', 'usage': {'output_tokens': 1}})
        self.assertEqual(run.codex_result(result + '\n' + done), ('cli_succeeded', 'PASS', {'output_tokens': 1}))
        for output in ('', result, done, '{}'):
            self.assertEqual(run.codex_result(output)[0], 'empty_response')
        self.assertEqual(run.codex_result('not json')[0], 'invalid_output')
        self.assertEqual(run.codex_result('[1]')[0], 'invalid_output')
        self.assertEqual(run.codex_result('{"type":"turn.failed"}')[0], 'cli_failed')

    def test_verifier_evidence_invalidates_after_edit(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            workspace = job / 'workspace'
            state = {'verification': {'passed': True, 'workspace_hashes': run.hashes(workspace)}}
            (job / 'smoke.verification.txt').write_text('EVIDENCE_MARKER', encoding='utf-8')
            prompt = run.build_prompt(job, run.ROLES['reviewer'], {}, state, run.hashes(workspace))
            self.assertIn('EVIDENCE_MARKER', prompt)
            (workspace / 'src/risk.py').write_text('changed', encoding='utf-8')
            prompt = run.build_prompt(job, run.ROLES['reviewer'], {}, state, run.hashes(workspace))
            self.assertNotIn('EVIDENCE_MARKER', prompt)
            self.assertIn('No current passing verification', prompt)

    def test_agy_never_bypasses_permissions(self):
        with patch('run.shutil.which', return_value='agy.exe'):
            cmd = run.command_for(run.ROLES['ui-worker'], run.BASE)
            self.assertIn('--sandbox', cmd)
            self.assertNotIn('--dangerously-skip-permissions', cmd)

    def test_no_fake_success_from_verifier(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            with self.assertRaises(ValueError):
                run.check_smoke(job)

    def test_attempt_limit_prevents_spawn(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            run.write_json(job / 'state.json', {'attempts': [{}, {}, {}, {}]})
            with patch('run.subprocess.Popen') as spawn, self.assertRaises(ValueError):
                run.invoke(job, 'worker', 20)
            spawn.assert_not_called()

    def test_single_writer_lock(self):
        with tempfile.TemporaryDirectory() as root, patch.object(run, 'RUNS', Path(root)):
            job = run.prepare(run.BASE / 'tasks/smoke.json')
            with patch.object(run, 'BASE', Path(root)):
                (Path(root) / '.run.lock').write_text('occupied')
                with self.assertRaises(FileExistsError):
                    run.invoke(job, 'worker', 20)


if __name__ == '__main__':
    unittest.main()
