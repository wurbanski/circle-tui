import yaml
import os

class CircleTuiConfig():
    def __init__(self, config_file='~/.circleci/cli.yml', project=None):
        with open(os.path.expanduser(config_file), 'r') as cli_config:
            self.__cli_yml = yaml.load(cli_config)

        self.token = self.__cli_yml['token']
        self.host = self.__cli_yml['host']
        self.project = project or self.__cli_yml.get('project', '')

