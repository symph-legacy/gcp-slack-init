import requests
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()

import logging


class Bitbucket():
    def __init__(self, client_key, client_secret):
        self.BASE_URL = 'https://api.bitbucket.org/2.0'
        self.user = self.get_user(client_key, client_secret)
        self.access_token = self.user['access_token']


    def get_access_token_in_dict(self):
        return {'access_token': self.access_token}


    def get_user(self, client_key, client_secret):
        url = 'https://bitbucket.org/site/oauth2/access_token'

        d = {'grant_type': 'client_credentials'}
        return requests.post(url, data=d, auth=(client_key, client_secret)).json()


    def create_fork(self, username, repository_name, fork_name, account_id):
        # https://api.bitbucket.org/2.0/repositories/evzijst/dogslow/forks
        url = self.BASE_URL + '/repositories/{}/{}/forks'.format(username, repository_name)
        logging.debug(url)

        payload = {}
        payload['name'] = fork_name
        payload['owner'] = {'uuid': account_id}

        return requests.post(url, params=self.get_access_token_in_dict(), json=payload).json()


    def get_account_info(self):
        # /user
        url = self.BASE_URL + '/user'
        payload = self.get_access_token_in_dict()
        return requests.get(url, params=payload).json()


    def restrict_repo_from_force_push(self, repo_username, repo_name):
        url = self.BASE_URL + '/repositories/{}/{}/branch-restrictions'.format(repo_username, repo_name)
        payload = {}
        payload['kind'] = 'force'
        payload['pattern'] = '*'
        return requests.post(url, params=self.get_access_token_in_dict(), json=payload).json()        


    def disallow_deleting(self, repo_username, repo_name):
        url = self.BASE_URL + '/repositories/{}/{}/branch-restrictions'.format(repo_username, repo_name)
        payload = {}
        payload['kind'] = 'delete'
        payload['pattern'] = '*'
        return requests.post(url, params=self.get_access_token_in_dict(), json=payload).json()        


    def get_repo_details(self, repo_username, repo_name):
        url = self.BASE_URL + '/repositories/{}/{}'.format(repo_username, repo_name)
        payload = self.get_access_token_in_dict()
        return requests.get(url, params=payload).json()        

