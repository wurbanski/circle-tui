import argparse
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.validation import Validator

from circle_tui.api import CircleApi
from circle_tui.config import CircleTuiConfig

def is_empty(text):
    return bool(text.strip())

empty_validator = Validator.from_callable(is_empty,
                                          error_message="Input can't be empty")

class CircleTuiState():
    build_num = ''
    project = ''
    branch = ''
    step = ''


class CircleTui():
    def __init__(self):

        parser = argparse.ArgumentParser(description='TUI/Log viewer for '
                                         'CircleCI')
        parser.add_argument('--config', default='~/.circleci/cli.yml', 
                            help='Location of config file')
        parser.add_argument('--project', help='Project name in format: '
                            '<vcs>/<username>/<reponame>')
        parser.add_argument('--build_num', default='', help='Build number')
        parser.add_argument('--branch', default='', help='Branch name')
        parser.add_argument('--step', default='', help='Steps')
        parser.add_argument('--non_interactive', action='store_true',
                            help='Use non-interactive mode - just print the '
                            'logs, requires all other parameters')
        args = parser.parse_args()
        self.__args = args

        self.config = CircleTuiConfig(args.config, args.project)
        self.api = CircleApi(token=self.config.token, project=self.config.project,
                             circle_host=self.config.host)
        self.state = CircleTuiState()
        self.state.project = self.api.project or ''
        self.state.build_num = args.build_num
        self.state.step = args.step
        self.state.branch = args.branch

    def select_project(self):
        projects = self.api.my_projects()
        projects_completer = \
        WordCompleter(['{}/{}'.format(proj['vcs_type'], proj['id']) for proj in projects])

        project = prompt("Which project? ", completer=projects_completer,
                         validator=empty_validator,
                         default=self.state.project)
        self.state.project = project
        return project

    def select_branch(self):
        branch = None
        branch_input = prompt("Which branch? (empty for all branches) ",
                               default=self.state.branch).strip()
        if branch_input:
            branch = branch_input
        self.state.branch = branch_input
        return branch

    def select_build(self):
        limit = 50
        builds = self.api.get_builds_for_project(self.state.project,
                                                 limit=limit,
                                                 branch=self.state.branch)
        class BuildCompleter(Completer):
            def get_completions(self, document, complete_event):
                for build in builds:
                    display_string = "{} ({}, {}) on {} ({})".format(build.build_num,
                                                                     build.job_name,
                                                                     build.status,
                                                                     build.branch,
                                                                     build.workflow_name)
                    yield Completion(str(build.build_num),
                                     display=display_string)

        message = ANSI('Last {} builds are suggested, but you can enter any '
                       'number'.format(limit))
        build_num = prompt("Select build: ", completer=BuildCompleter(),
                           default=self.state.build_num,
                           complete_in_thread=True,
                           validator=empty_validator,
                           bottom_toolbar=message)
        self.state.build_num = build_num
        return build_num


    def select_step(self):
        steps = self.api.get_steps_for_build(self.state.build_num, self.state.project)
        class StepsCompleter(Completer):
            def get_completions(self, document, complete_event):
                for step in steps:
                    display_string = "{} ({} on {})".format(step.name,
                                                            step.step_id,
                                                            step.index)
                    yield Completion(str([step.step_id, step.index]),
                                     display=display_string)
                else:
                    yield Completion('all', display='Show all steps')
        message = ANSI('flags: --build_num {} --project {} --step {}'.format(self.state.build_num,
                                                     self.state.project,
                                                     self.state.step))
        step = prompt("Select step: ", completer=StepsCompleter(),
                      default=self.state.step,
                      validator=empty_validator,
                      bottom_toolbar=message)
        self.state.step = step
        if 'all' in step:
            return ['all', 0]
        return json.loads(step)

    def show_step_logs(self, step_id, index):
        print('Showing logs for build {} of {}, step: {}'.format(self.state.build_num,
                                                                 self.state.project,
                                                                 step_id))
        print('*** LOGS START')
        if step_id == "all":
            steps = list(self.api.get_steps_for_build(self.state.build_num,
                                                      self.state.project,
                                                      index=0))
        else:
            steps = list(self.api.get_steps_for_build(self.state.build_num, self.state.project,
                                                      step_id=step_id, index=index))
        for step in steps:
            self.print_log(step)

        print('*** LOGS STOP')


    def print_log(self, step):
        print('*** STEP: {} ({})'.format(step.name, step.index))
        print('    STATUS:', step.status)
        print('*** OUTPUT:')
        print(self.api.get_logs_for_build_step(step.build_num,
                                               step_id=step.step_id,
                                               index=step.index,
                                               project=self.state.project))

    def main(self):
        user = self.api.get_me()
        print("Hello {name} ({login})!".format(**user))
        while not self.__args.non_interactive:
            try:
                print("\nPress ^C to quit at any time, <Tab> for completions.")
                project = self.select_project()
                branch = self.select_branch()
                build_num = self.select_build()
                step, index = self.select_step()
                self.show_step_logs(step, index)
            except KeyboardInterrupt:
                break
        else:
            step, index = self.state.step, 0
            self.show_step_logs(step, index)
