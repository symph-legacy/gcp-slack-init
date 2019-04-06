from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from oauth2client.contrib.appengine import AppAssertionCredentials
import logging
import httplib2



class GCloud():
    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default()
        scope = ["https://www.googleapis.com/auth/cloud-platform"]
        self.credentials = AppAssertionCredentials(scope=scope)


    def create_gcloud_project(self, project_id, project_name, parent_id=None, parent_type=None):
        crm = discovery.build(
            'cloudresourcemanager', 'v1', http=self.credentials.authorize(httplib2.Http()))

        body = {
            'project_id': project_id,
            'name': project_name
        }

        if parent_id and parent_type:
            body['parent'] = {}
            body['parent']['type'] = parent_type
            body['parent']['id'] = parent_id

        operation = crm.projects().create(body=body).execute()


    def create_appengine_app(self, project_id, location_id):
        app = discovery.build(
            'appengine', 'v1', http=self.credentials.authorize(httplib2.Http()))

        body = {
            'id': project_id,
            'locationId': location_id
        }

        operation = app.apps().create(body=body).execute()
    

    def enable_service(self, project_id, service_id):
        serviceusage = discovery.build(
            'serviceusage', 'v1', http=self.credentials.authorize(httplib2.Http()))

        logging.debug('trying to enable service {}'.format(service_id))

        service_name = 'projects/{}/services/{}.googleapis.com'.format(project_id, service_id)

        operation = serviceusage.services().enable(name=service_name).execute()


    def create_cloud_build_trigger(self, project_id, description):
        cloudbuild = discovery.build(
            'cloudbuild', 'v1', http=self.credentials.authorize(httplib2.Http()))

        body = {
            'description': 'test'
        }

        operation = cloudbuild.projects().triggers().create(projectId=project_id, body=body).execute()
