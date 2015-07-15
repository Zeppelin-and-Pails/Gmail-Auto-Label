"""
gmailconnector

A package for communicating with the gmail apis

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os
import sys
import yaml
import logit
import httplib2
import emailer

# google apis
import oauth2client
from oauth2client import client, tools
from apiclient import discovery, errors

class gmailconnector:
    flags = tools.argparser.parse_args(args=[])
    userID = 'me'
    conf = None
    log = None

    def __init__(self):
        DIR = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/gmailconnector.cfg".format(DIR)))
        self.log = logit.logit(self.conf)
        self.log.info('gmailconnector initialised')

    def get_scopes(self):
        return [self.conf['MODIFY_SCOPE'],
                self.conf['LABEL_SCOPE']]

    def get_service(self, reauth=False):
        self.log.info('get_service called')
        credentials = self.get_credentials(reauth)
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_auth_url(self):
        self.log.info('get_auth_url called')
        flow = client.flow_from_clientsecrets(self.conf['CS_FILE'],
                                              ' '.join(self.get_scopes()),
                                              '{}/oauth2callback'.format(self.conf['AUTH_URL']))
        url = flow.step1_get_authorize_url('{}/oauth2callback'.format(self.conf['AUTH_URL']))
        return url

    def get_cred_store(self):
        self.log.info('get_cred_store called')
        credential_dir = os.path.join(self.conf['CRED_DIR'])
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'gmail-auto-label.json')
        return oauth2client.file.Storage(credential_path)

    def get_credentials(self, reauth):
        self.log.info('get_credentials called')
        store = self.get_cred_store()
        credentials = store.get()
        if not credentials or credentials.access_token_expired or credentials.invalid or reauth:
            self.log.info('Failed to find credentials, or existing credentials are invalid, sending email to get new credentials')
            try:
                url = self.get_auth_url()
                emailer.emailer(self.conf['AUTH_ADD'], url)
                raise PermissionError('Authentication failed')
            except errors.HttpError, error:
                self.log.error(error)
            except PermissionError:
                raise
        return credentials

    def set_credentials(self, code):
        self.log.info('set_credentials called')
        try:
            store = self.get_cred_store()
            flow = client.flow_from_clientsecrets(self.conf['CS_FILE'],
                                                  ' '.join(self.get_scopes()),
                                                  '{}/oauth2callback'.format(self.conf['AUTH_URL']))
            credentials = flow.step2_exchange(code)
            self.log.info('New credentials fetched successfully')
            store.put(credentials)
            return '[Success]'
        except client.FlowExchangeError, error:
            self.log.error(error)
        except oauth2client.clientsecrets.InvalidClientSecretsError, error:
            self.log.error(error)
        return '[Failure]'

    def get_labels(self):
        self.log.info('get_labels called')
        try:
            self.log.info('get_labels called')
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service()

            self.log.info('Authenticated, getting label list')
            results = service.users().labels().list(userId=self.userID).execute()
            return results.get('labels', [])
        except errors.HttpError, error:
            self.log.error(error)

    def add_label(self, name):
        self.log.info('add_label called')
        label = {
            "name": name,
            "messageListVisibility": "show",
            "labelListVisibility": "labelShowIfUnread",
        }

        try:
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service()
            label = service.users().labels().create(userId=self.userID,
                                                    body=label).execute()
            print label['id']
            return label
        except errors.HttpError, error:
            self.log.error(error)
        return True

    def get_inbox_messages(self):
        self.log.info('get_inbox_messages called')
        try:
            return self.get_in_msg_inner()
        except errors.HttpError, error:
            self.log.error(error)

    def get_in_msg_inner(self):
        self.log.info('Getting credentials for account, and authorising')
        service = self.get_service()

        self.log.info('Authenticated, getting message list')
        response = service.users().messages().list(userId=self.userID,
                                                   labelIds=self.conf['LABEL']).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=self.userID,
                                                       labelIds=label,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    def get_message_headers(self, msg_id):
        self.log.info('get_message_headers called')
        try:
            service = self.get_service()
            message = service.users().messages().get(userId=self.userID,
                                                    id=msg_id).execute()
            return message['payload']['headers']

        except errors.HttpError, error:
            self.log.error(error)

    def get_address(self, msg_id):
        self.log.info('get_address called')
        try:
            headers = self.get_message_headers(msg_id)
        except errors.HttpError, error:
            self.log.error(error)

        for header in headers:
            if header['name'] == self.conf['STYLE']:
                return header['value']

    def move_msg_to_label(self, msg_id, label):
        msg_labels = {'removeLabelIds': ['INBOX'],
                      'addLabelIds': [label]}

        try:
            service = self.get_service()
            service.users().messages().modify(userId=self.userID,
                                              id=msg_id,
                                              body=msg_labels).execute()

        except errors.HttpError, error:
            self.log.error(error)


