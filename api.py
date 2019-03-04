import requests
import requests_cache
import json
from urllib.parse import quote_plus as urlencode

requests_cache.install_cache('circleci-cache', expire_after=30)

class CircleApiError(Exception):
    def __init__(self, error):
        self.error = error

class BuildStep():
    def __init__(self, json, build_num):
        self.build_num = build_num
        self.raw_json = json
        self.name = json['name']
        self.step_id = json['step']
        self.index = json['index']
        self.status = json['status']

    def __repr__(self):
        return '"{}" (step: {}, index {})'.format(self.name, self.step_id,
                                                  self.index)

class Build():
    def __init__(self, json):
        self.raw_json = json
        self.build_num = json['build_num']
        self.build_url = json['build_url']
        self.status = json['status']
        self.outcome = json['outcome']
        self.job_name = json['workflows']['job_name']
        self.workflow_name = json['workflows']['workflow_name']
        self.workflow_id = json['workflows']['workflow_id']
        self.branch = json['branch']

    def __repr__(self):
        return "{} {} in {} {}".format(self.job_name,
                                       self.build_num,
                                       self.workflow_name,
                                       self.workflow_id)

class CircleApi():
    def __init__(self, token=None, circle_host='https://circleci.com',
                 api_version='v1.1', username=None, reponame=None,
                vcs_type=None, project=None):
        self.__url = "{}/api/{}".format(circle_host, api_version)
        self.__token = token
        if project:
            vcs_type, username, reponame = project.split('/')
            self.__vcs_type = vcs_type
            self.__username = username
            self.__reponame = reponame
        else:
            self.__vcs_type = vcs_type
            self.__username = username
            self.__reponame = reponame

    @property
    def project(self):
        if self.__vcs_type and self.__username and self.__reponame:
            return "{}/{}/{}".format(self.__vcs_type, self.__username, self.__reponame)
        else:
            return None

    @project.setter
    def project(self, project):
        vcs_type, username, reponame = project.split('/')
        self.__vcs_type = vcs_type
        self.__username = username
        self.__reponame = reponame

    def __get(self, route, data={}, json=True, no_cache=False):
        url = "{}/{}".format(self.__url, route)
        headers = {'Accept': 'application/json'}
        data['shallow'] = 'true'
        if no_cache:
            with requests_cache.disabled():
                r = requests.get(url, auth=(self.__token, ''), params=data,
                                 headers=headers)
        else:
            r = requests.get(url, auth=(self.__token, ''), params=data,
                             headers=headers)
        if r.status_code != 200:
            raise CircleApiError(error=r.status_code)
        if json:
            return self.__sanitize(r.json())
        else:
            return r.text

    @staticmethod
    def __sanitize(response):
        try:
            del response['circle_yml']
        except:
            pass
        return response

    def get_me(self):
        return self.__get('me')

    def get_projects(self):
        return self.__get('projects')

    def my_projects(self):
        projects = []
        for project in self.get_projects():
            project_id = "{}/{}".format(project['username'],project['reponame'])
            projects.append({'username': project['username'],
                             'reponame': project['reponame'],
                             'vcs_type': project['vcs_type'],
                             'url': project['vcs_url'],
                             'id': project_id})
        return projects

    def my_organizations(self):
        organizations = []
        for project in self.get_projects():
            organizations.append(project['username'])
        return set(organizations)

    def get_builds_for_project(self, project=None, limit=30,
                               offset=0, build_filter=None, branch=None):
        project = project or self.project
        data = {'filter': build_filter, 'limit': limit, 'offset': offset}
        if branch and branch.strip():
            url = "project/{}/tree/{}".format(project, urlencode(branch))
        else:
            url = "project/{}".format(project)
        builds = self.__get(url, data)
        for build in builds:
            yield Build(build)

    def get_logs_for_build_step(self, build_num, step_id, index=0, project=None):
        project =  project or self.project
        url = 'project/{}/{}/output/{}/{}'.format(project, build_num, step_id,
                                                  index)
        data = {'file': 'true'}
        logs = self.__get(url, data, json=False, no_cache=True)
        return logs

    def get_build_details(self, build_num, project=None):
        project = project or self.project
        url = 'project/{}/{}'.format(project, build_num)
        return Build(self.__get(url, no_cache=True))
    
    def get_steps_for_build(self, build_num, project=None, step_id=None,
                            index=0):
        project = project or self.project
        build = self.get_build_details(build_num, project)
        for step in build.raw_json['steps']:
            for action in step['actions']:
                bs = BuildStep(action, build_num)
                if index == bs.index and not step_id or step_id == bs.step_id:
                    yield bs


    def get_step_id_by_name(self, build_num, step_name='', project=None):
        project = project or self.project
        build_steps = self.get_steps_for_build(build_num, project)
        for step in build_steps:
            if step.name.contains(step_name):
                yield step.step_id

