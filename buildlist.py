from circle_tui.api import CircleApi, CircleApiError
from circle_tui.config import CircleTuiConfig
from collections import defaultdict
import colorama

import sys

RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
BLUE = colorama.Fore.BLUE
RESET = colorama.Style.RESET_ALL

def main():
    colorama.init()
    config = CircleTuiConfig()
    api = CircleApi(token=config.token, project=config.project)

    offset = 0
    limit = 4
    bucket = 10
    branch = 'master'
    context = 5

    workflows = {}
    builds = []
    print("rendering list of last {} workflows on branch {}...".format(limit,
                                                                       branch))
    while len(workflows) < limit: 
        builds = api.get_builds_for_project(limit=bucket,
                                            offset=offset,
                                            branch=branch)
        offset = offset + bucket

        for build in builds:
            if build.workflow_id not in workflows:
                workflows[build.workflow_id] = {'name': build.workflow_name, 
                                                    'builds': []}
            workflows[build.workflow_id]['builds'].append(build)

    workflows_status = defaultdict(int)
    for w_id, workflow in workflows.items():
        failed = False
        running = False
        failed_builds = []
        for build in workflow['builds']:
            if build.status == "failed":
                failed = True
                failed_builds.append((build, build.build_url))
                break
            if build.status == "running":
                running = True
        workflow['failed'] = failed
        workflow['running'] = running
        workflow['failed_builds'] = failed_builds
        workflow['url'] = api._workflow_url(w_id)
        if workflow['failed']:
            workflows_status['failed'] += 1
            COLOR = RED
            status = 'FAIL'
        elif workflow['running']:
            workflows_status['running'] += 1
            COLOR = BLUE
            status = ' RUN'
        else:
            workflows_status['success'] += 1
            COLOR = GREEN
            status = 'PASS'

        header_line = "{}: {} ({})".format(status, workflow['name'], workflow['url'])
        print(RESET + COLOR + '-'*len(header_line))
        print(header_line)
        if workflow['failed']:
            for build in workflow['failed_builds']:
                print("  - {}: {}".format(build[0].job_name, build[1]))
                
                output = None
                failed_steps = [step for step in
                                api.get_steps_for_build(build[0].build_num)
                                if step.status not in ("success", "running")]
                last_step = failed_steps[-1]
                output = api.get_logs_for_build_step(build[0].build_num,
                                                     last_step.step_id)
                print('    {}: {}'.format(last_step.name, last_step.status))
                print('\n    '.join([''] + output.splitlines()[-context:]))
                print()

    print(RESET + "Summary:")
    for status, count in workflows_status.items():
        print("{}: {}".format(status, count))

    return 0

if __name__ == '__main__':
    sys.exit(main())
