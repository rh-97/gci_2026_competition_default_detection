"""Small local-venv entry point for the completed competition project.

Frozen fitters stay at their original paths because saved encoders and source
signatures depend on them. This interface never starts training.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MODELING = ROOT / 'improvements/high_upside'


def read(name):
    return json.loads((MODELING / 'artifacts' / name).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'verify', 'reproduce', 'report'])
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        parser.error('Use the project interpreter: Competition/.venv/bin/python Competition/project.py ' + args.command)
    if args.command == 'status':
        final = read('model_final_results.json')
        average = read('model_averaging.json')
        observation = read('model_public_leaderboard_observation.json')
        print(json.dumps({
            'submission': final['submission'], 'sha256': final['sha256'],
            'rows': final['rows'], 'local_validation_baseline_auc': average['baseline']['auc'],
            'local_validation_candidate_auc': average['candidate']['auc'],
            'latest_public_leaderboard_observation': observation['public_auc'],
            'public_observation_filename_confirmed': observation['submitted_filename_explicitly_confirmed'],
            'report': 'PROJECT_REPORT.md',
        }, indent=2))
        return
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if args.command == 'report':
        subprocess.run([sys.executable, str(ROOT / 'tools/build_project_report.py')], cwd=ROOT, env=env, check=True)
    else:
        script, phase = ('h_verify_package.py', 'verify') if args.command == 'verify' else ('h_launch.py', 'reproduce')
        subprocess.run([sys.executable, str(MODELING / script), phase], cwd=MODELING, env=env, check=True)


if __name__ == '__main__':
    main()
