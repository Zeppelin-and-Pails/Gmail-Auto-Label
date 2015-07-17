"""
gmailconnector

A package for communicating with the GMail APIs

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os
import yaml
import logit
import httplib2
import emailer

# google apis
import oauth2client
from oauth2client import client, tools
from apiclient import discovery, errors


class gmailconnector:
    """
    Gmail connector class, used to talk to the GMail API
    """
    flags = tools.argparser.parse_args(args=[])
    UID = 'me'
    conf = None
    log = None

    def __init__(self):
        """ Initialise a new gmailconnector
        :return gmailconnector: a new instance of a gmailconnector
        """
        DIR = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/gmailconnector.cfg".format(DIR)))
        self.log = logit.logit(self.conf)
        self.log.info('gmailconnector initialised')

    def get_scopes(self):
        """ Get the scopes required for operation
        :return array: An array of needed scopes to be passed to the GMail API
        """
        return [self.conf['MODIFY_SCOPE'],
                self.conf['LABEL_SCOPE']]

    def get_service(self, reauth=False):
        """ Get a resource object to interact with the service.
        :param reauth: [True/False] - Default = False - force reauthentication
                            if False stored details will be used where possible
        :return:
            A Resource object with methods for interacting with the service.
        """
        self.log.info('get_service called')
        credentials = self.get_credentials(reauth)
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_auth_url(self):
        """ Get the URL from google for authorising this app
        :return string: the authorisation url for redirection
        """
        self.log.info('get_auth_url called')
        callback_path = '{}/oauth2callback'.format(self.conf['AUTH_URL'])
        flow = client.flow_from_clientsecrets(self.conf['CS_FILE'],
                                              ' '.join(self.get_scopes()),
                                              callback_path)
        url = flow.step1_get_authorize_url(callback_path)
        return url

    def get_cred_store(self):
        """ Get the credentials store from file
        :return oauth2client.file.Storage:
                    a new instance of Storage for access the stored credentials
        """
        self.log.info('get_cred_store called')
        credential_dir = os.path.join(self.conf['CRED_DIR'])
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'gmail-auto-label.json')
        return oauth2client.file.Storage(credential_path)

    def get_credentials(self, reauth):
        """ Get a credentials object initialised from file
        :param reauth: [True/False] - force reauthentication
                            if False stored details will be used where possible
        :return: Credentials for use in GMail API connections
        """
        self.log.info('get_credentials called')
        store = self.get_cred_store()
        credentials = store.get()
        if not credentials \
           or credentials.access_token_expired \
           or credentials.invalid \
           or reauth:
            self.log.info('Failed to find credentials, or existing credentials'
                          ' are invalid, sending email to get new credentials')
            try:
                url = self.get_auth_url()
                emailer.send(self.conf['AUTH_ADD'], url)
                raise PermissionError('Authentication failed')
            except errors.HttpError, error:
                self.log.error(error)
            except PermissionError:
                raise
        return credentials

    def set_credentials(self, code):
        """ Get a credentials object from google and store it for later use
        :param code: authorisation code to exchange for GMail credentials
        :return string: a string representation of the result
        """
        self.log.info('set_credentials called')
        callback_path = '{}/oauth2callback'.format(self.conf['AUTH_URL'])
        try:
            store = self.get_cred_store()
            flow = client.flow_from_clientsecrets(self.conf['CS_FILE'],
                                                  ' '.join(self.get_scopes()),
                                                  callback_path)
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
        """ Get a list of labels from the GMail API
        :return: a list of label objects from the GMail API
        """
        self.log.info('get_labels called')
        try:
            self.log.info('get_labels called')
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service()

            self.log.info('Authenticated, getting label list')
            results = service.users().labels().list(userId=self.UID).execute()
            return results.get('labels', [])
        except errors.HttpError, error:
            self.log.error(error)

    def add_label(self, name):
        """ Add a label to the GMail account via the API
        :param name: The new label's name
                folders can be defined using / e.g. 'folder/label'
        :return:
        """
        self.log.info('add_label called')
        label = {
            "name": name,
            "messageListVisibility": "show",
            "labelListVisibility": "labelShowIfUnread",
        }

        try:
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service()
            label = service.users().labels().create(userId=self.UID,
                                                    body=label).execute()
            return label
        except errors.HttpError, error:
            self.log.error(error)
        return True

    def get_inbox_messages(self):
        """ Get a list of the messages in the GMail account's inbox
        :return: a list of GMail message objects
        """
        self.log.info('get_inbox_messages called')
        try:
            self.log.info('Getting credentials for account, and authorising')
            service = self.get_service()

            self.log.info('Authenticated, getting message list')
            response = service.users().messages() \
                .list(userId=self.UID,
                      labelIds=self.conf['LABEL']).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages() \
                    .list(userId=self.UID,
                          labelIds=label,
                          pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except errors.HttpError, error:
            self.log.error(error)
            raise

    def get_message_headers(self, msg_id):
        """ Get the messages headers for a given message ID
        :param msg_id: The ID for the message as provided by google
        :return: A message headers object
        """
        self.log.info('get_message_headers called')
        try:
            service = self.get_service()
            message = service.users().messages().get(userId=self.UID,
                                                     id=msg_id).execute()
            return message['payload']['headers']

        except errors.HttpError, error:
            self.log.error(error)
            raise

    def get_address(self, msg_id):
        """ Get the from of to address attached to a message (set by config)
        :param msg_id: The ID for the message as provided by google
        :return: the appropriate address string e.g. 'ap <aperson@gmail.com>'
        """
        self.log.info('get_address called')
        try:
            headers = self.get_message_headers(msg_id)
        except errors.HttpError, error:
            self.log.error(error)

        for header in headers:
            if header['name'] == self.conf['STYLE']:
                return header['value']

    def move_msg_to_label(self, msg_id, label):
        """ Move a message from the INBOX to another label via the GMail API
        :param msg_id: The ID for the message as provided by google
        :param label: The ID for the label to move the message to
        """
        msg_labels = {'removeLabelIds': ['INBOX'],
                      'addLabelIds': [label]}

        try:
            service = self.get_service()
            service.users().messages().modify(userId=self.UID,
                                              id=msg_id,
                                              body=msg_labels).execute()
        except errors.HttpError, error:
            self.log.error(error)
