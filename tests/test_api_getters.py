import unittest, re

import responses

from tests.fixtures.url_responses import register_callback
from circle_tui.api import CircleApi

BUILD = 12345
PROJECT = 'github/test/project'

class TestApiGetters(unittest.TestCase):
    def setUp(self):
        self.api = CircleApi(never_cache=True)

    @responses.activate
    def test_get_projects(self):
        register_callback()
        api_projects = self.api.get_projects()
        self.assertIsNotNone(api_projects, msg="API returned no data")
        self.assertEqual(len(api_projects), 2, 
                         msg="API returned wrong number of projects")

    @responses.activate
    def test_get_me(self):
        register_callback()
        api_me = self.api.get_me()
        self.assertIsNotNone(api_me, msg="API returned no data")
        self.assertEqual(api_me['login'], 'tests_user')

    @responses.activate
    def test_my_projects(self):
        register_callback()
        fields = ['username', 'reponame', 'vcs_type', 'url', 'id']
        api_my_projects = self.api.my_projects()
        self.assertIsNotNone(api_my_projects, msg="API returned no data")
        self.assertEqual(len(api_my_projects), 2,
                         msg="API returned wrong number of projects")
        for project in api_my_projects:
            for field in fields:
                self.assertIn(field, project,
                              msg="{} not found in project {}".format(field, project))

    @responses.activate
    def test_get_build_details(self):
        register_callback()
        api_build_details = self.api.get_build_details(BUILD, PROJECT)
        self.assertIsNotNone(api_build_details, msg="API returned no data")
        self.assertEqual('success', api_build_details.status,
                        msg="API returned wrong build status")
        self.assertEqual('build', api_build_details.job_name,
                        msg="API returned wrong job name")
        self.assertNotIn('circle_yml', api_build_details.raw_json,
                        msg="API returned wrong build status")


    @responses.activate
    def test_get_steps_for_build(self):
        register_callback()
        api_build_steps = list(self.api.get_steps_for_build(BUILD, PROJECT))
        self.assertIsNotNone(api_build_steps, msg="API returned no data")
        self.assertEqual(len(api_build_steps), 5,
                        msg="API returned wrong number of steps")


    @responses.activate
    def test_get_logs_for_build_step(self):
        register_callback()
        build_step_logs = self.api.get_logs_for_build_step(BUILD, 5, PROJECT)
        self.assertIsNotNone(build_step_logs, msg="API returned no data")
        self.assertIn('HEAD is now at', build_step_logs,
                        msg="API returned wrong log file")
