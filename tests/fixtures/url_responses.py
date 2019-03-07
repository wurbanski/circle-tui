import re, json, os
import responses
from urllib.parse import urlparse
from tests import FIXTURES_DIR

prefix = '/api/v1.1'

# '/endpoint': (status, headers, response_body_filename)
endpoints = {
    '/me': 
        { 'ret_code': 200, 'headers': {}, 'body': 'me.json'},
    '/projects': 
        { 'ret_code': 200, 'headers': {}, 'body': 'projects.json'},
    # /project/:vcs_type/:username/:project/:build_num/output/:step/:index
    '/project/((\w+)*)/((\w+)*)/((\w+)*)/((\w+)*)/((\w+)*)/((\w+)*)': 
        { 'ret_code': 200, 'headers': {}, 'body': 'log_example'},
    # /project/:vcs_type/:username/:project/:build_num
    '/project/((\w+)*)/((\w+)*)/((\w+)*)/((\w+)*)': 
        { 'ret_code': 200, 'headers': {}, 'body': 'build.json'},
}

def register_callback():
    responses.add_callback(
        responses.GET,
        re.compile('https://circleci.com/api/v1.1/.*'),
        callback=cached_response
    )


def cached_response(request):
    parsed_uri = urlparse(request.url)
    request_endpoint = parsed_uri.path[len(prefix):]

    for endpoint, definition in endpoints.items():
        if re.match(endpoint, request_endpoint):
            filename = os.path.join(FIXTURES_DIR, definition['body'])
            with open(filename) as body:
                return definition['ret_code'], definition['headers'], body.read()
