# Create Projects Using an HTTP POST

This code provides an endpoint that does the following:
1. Fork a Boilerplate for a Google App Engine project from Bitbucket
2. Disallow "force push" and "deletion" on the new repository
3. Under the GCP Organization and Folder, create 2 GCP Projects. (1) Production and (2) Test
4. Create/Enable the App Engine service in both GCP projects

You can add a webhook to your Slack bot to post to the endpoint. You can secure it by using `POST_REQUEST_API_KEY` set in `constants.py`
