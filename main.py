#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import logging
import time
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from symph_gcloud import GCloud
from symph_bitbucket import Bitbucket

from constants import ATLASSIAN_ACCOUNT_ID
from constants import ATLASSIAN_OAUTH_CLIENT_KEY
from constants import ATLASSIAN_OAUTH_CLIENT_SECRET
from constants import DEFAULT_APPENGINE_REGION
from constants import BITBUCKET_REPO_OF_GAE_BOILERPLATE_ID
from constants import BITBUCKET_USERNAME
from constants import GCP_PROJECTS_FOLDER_ID
from constants import POST_REQUEST_API_KEY
from constants import URL_FOR_DEPLOYING_APPENGINE

from utils import slugify

from models import Project


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        self.initialize(request, response)

    def assert_required_params(self, required_params):
        for rp in required_params:
            if not self.request.get(rp):
                self.response.write('Missing {}'.format(rp))
                self.abort(400)
                return


class MainPage(BaseHandler):
    def get(self):
        self.response.write('hello!')


class InitializeAppEngineProject(BaseHandler):
    def post(self):
        if self.request.get('api_key') != POST_REQUEST_API_KEY:
            self.error(403)
            return

        # Project Name
        self.assert_required_params(['project'])

        project = self.request.get('project')
        region = self.request.get('region') or DEFAULT_APPENGINE_REGION
        slug = self.request.get('project_id') or slugify(project)

        if len(slug) < 7:
            logging.error('project id must be at least 7 characters')
            self.error(500)
            return

        # Bitbucket. Fork repo
        bb = Bitbucket(ATLASSIAN_OAUTH_CLIENT_KEY,
                       ATLASSIAN_OAUTH_CLIENT_SECRET)

        username = BITBUCKET_USERNAME
        repository_name = BITBUCKET_REPO_OF_GAE_BOILERPLATE_ID
        fork_name = slug
        account_id = ATLASSIAN_ACCOUNT_ID

        logging.info('creating fork {}'.format(fork_name))
        try:
            bb.create_fork(username, repository_name, fork_name, account_id)
        except:
            logging.exception('error with creating fork')

        # Bitbucket. Add branch/merge permissions
        logging.info('disallowing force push {}'.format(fork_name))
        try:
            bb.restrict_repo_from_force_push(username, fork_name)
        except:
            logging.exception('error with disallowing force push')

        logging.info('disallowing deleting {}'.format(fork_name))
        try:
            bb.disallow_deleting(username, fork_name)
        except:
            logging.exception('error with disallowing deleting history')

        # GCP. Create Project
        project_name = project
        project_id = slug
        parent_id = GCP_PROJECTS_FOLDER_ID
        parent_type = 'folder'

        msg = 'creating gcp project {} / {}'.format(project_name, project_id)
        logging.info(msg)
        try:
            GCloud().create_gcloud_project(project_id, project_name,
                                           parent_id, parent_type)
        except:
            logging.exception('error with creating GCP project')

        # GCP. Create Test Project
        test_project_name = project + ' Test'
        test_project_id = slug + '-test'

        msg = 'creating gcp project {} / {}'.format(test_project_name,
                                                    test_project_id)
        logging.info(msg)
        try:
            GCloud().create_gcloud_project(test_project_id, test_project_name,
                                           parent_id, parent_type)
        except:
            logging.exception('error with creating GCP project test')

        # GCP. Create AppEngine
        logging.info('creating appengine app {} ({})'.format(project_id,
                                                             region))

        # add lull to allow GCP to create project first
        time.sleep(5)

        try:
            GCloud().create_appengine_app(project_id, region)
        except:
            logging.exception('error with creating appengine app')

        # GCP. Create AppEngine Test
        logging.info('creating appengine app {} ({})'.format(test_project_id,
                                                             region))
        try:
            GCloud().create_appengine_app(test_project_id, region)
        except:
            logging.exception('error with creating appengine app test')

        # Add project to list of projects
        project = Project(id=project_id)
        project.project_name = project_name
        project.project_id = project_id
        project.appengine = True
        project.put()

        time.sleep(15)

        body = urllib.urlencode({"project_id": project_id})
        urlfetch.fetch(URL_FOR_DEPLOYING_APPENGINE, method="POST", payload=body)

        try:
            deferred.defer(GCloud().enable_service, project_id, 'datastore')
        except:
            logging.exception('error with enabling service datastore on prod')

        try:
            deferred.defer(GCloud().enable_service, test_project_id, 'datastore')
        except:
            logging.exception('error with enabling service datastore on test')

        self.response.write('Done!')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/api/v1/appengine/initialize', InitializeAppEngineProject)
], debug=True)
