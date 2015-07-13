"""
gmailconnector

A package for communicating with the gmail apis

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os
import yaml
import logit
import httplib2
import pprint

# google apis
import oauth2client
from oauth2client import client
from oauth2client import tools
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

    def get_service(self, scope, reauth=False):
        if(scope == 'label'):
            credentials = self.get_credentials('LABEL_SCOPE',reauth)
        elif(scope == 'modify'):
            credentials = self.get_credentials('MODIFY_SCOPE', reauth)
        else:
            self.log.error('get_service called without scope')
            return
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_credentials(self, scope, reauth):
        credential_dir = os.path.join(self.conf['CRED_DIR'])
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'gmail-auto-label.json')
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid or reauth:
            self.log.info('Failed to find credentials, or existing credentials are invalid, getting new credentials')
            try:
                flow = client.flow_from_clientsecrets(self.conf['CS_FILE'], self.conf[scope])
                flow.user_agent = self.conf['APP_NAME']
                credentials = tools.run_flow(flow, store, self.flags)
                self.log.info('Storing new credentials in {}'.format(credential_path))
            except errors.HttpError, error:
                self.log.error(error)
        return credentials

    def get_labels(self):
        try:
            self.log.info('get_labels called')
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service('label')

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
            service = self.get_service('label')
            label = service.users().labels().create(userId=self.userID,
                                                    body=label).execute()
            print label['id']
            return label
        except errors.HttpError, error:
            self.log.error(error)
        return True

    def add_labels(self, labels):
        count = 0
        err = 0

        for label in labels:
            try:
                self.add_label(label)
                count += 1
            except:
                err += 1

        return count, err

    def get_inbox_messages(self):
        self.log.info('get_inbox_messages called')
        try:
            return self.get_in_msg_inner()
        except errors.HttpError, error:
            self.log.warn('Preliminary auth failed, trying again')
            try:
                self.get_service('modify', True)
                return self.get_in_msg_inner()
            except errors.HttpError, error:
                self.log.error(error)

    def get_in_msg_inner(self):
        self.log.info('Getting credentials for account, and authorising')
        service = self.get_service('modify')

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
            service = self.get_service('modify')
            message = service.users().messages().get(userId=self.userID,
                                                    id=msg_id).execute()
            return message['payload']['headers']

        except errors.HttpError, error:
            self.log.error(error)

    def get_address(self, msg_id):
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
            service = self.get_service('modify')
            service.users().messages().modify(userId=self.userID,
                                              id=msg_id,
                                              body=msg_labels).execute()

        except errors.HttpError, error:
            self.log.error(error)


