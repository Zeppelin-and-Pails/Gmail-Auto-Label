"""
autolabel

automatically generates labels for use in gmail,
based on either sender address, or recipient address (use with catch all addresses)

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
import re
import os
import yaml
import logit
import gmailconnector

class autolabel:
    """
    autolabel class,
        connects to GMail and automatically labels all emails in the INBOX
    """
    log = None

    def __init__(self):
        """ Initialise a new autolabel
        :return autolabel: a new instance of a autolabel
        """
        DIR = os.path.dirname(os.path.realpath(__file__))
        self.conf = yaml.safe_load(open("{}/autolabel.cfg".format(DIR)))
        log = logit.logit(self.conf)
        log.info('autolabel initialised')
        self.log = log
        self.con = self.get_gmailcon()

    def get_gmailcon(self):
        """ Intialise a new gmail connector
        :return gmailconnector: the newly initialised gmail connector
        """
        self.log.info('autolabel::get_gmailcon called')
        return gmailconnector.gmailconnector(self.log)

    def get_auth_url(self):
        """ Intialise a new gmail connector
        :return auth_url: the url for google auth
        """
        self.log.info('autolabel::get_auth_url called')
        return self.con.get_auth_url()

    def set_credentials(self, auth_code):
        """ Intialise a new gmail connector
        :return gmailconnector: the newly initialised gmail connector
        """
        self.log.info('autolabel::set_credentials called')
        return self.con.set_credentials(auth_code)

    def run(self):
        """ Run through the autolabeling process
                Get all existing labels
                Get all email in the INBOX
                Put emails into appropriate labels,
                    creating new labels where needed
        :return: the results of the run
        """
        self.log.info('autolabel::run called')
        self.log.info('attempting to get the credentials from store')
        try:
            self.con.get_credentials(False)
        except:
            return -99

        labels = {}

        for label in self.con.get_labels():
            labels[label['name']] = label['id']

        if not labels:
            resp = 'No labels found.'
            self.log.warn(resp)
        else:
            self.log.info('{0} labels found.'.format(len(labels)))

            messages = self.con.get_inbox_messages()

            if not messages:
                resp = 'No messages found.'
                self.log.warn(resp)
            else:
                msg = 0
                bad = 0
                for message in messages:
                    try:
                        address = self.con.get_address(message['id'])
                        radd = re.search(r'(?<=<)(.+)(?=>)', address)
                        if radd:
                            address = radd.group(0)

                        label = re.sub(r'\.', '/', re.search(r'(.+)(?=@)', address).group(0))
                        if label not in labels:
                            print label
                            try:
                                new_label = self.con.add_label(label)
                                labels[new_label['name']] = new_label['id']
                            except:
                                bad += 1
                                pass

                        self.con.move_msg_to_label(message['id'], labels[label])
                        msg += 1
                    except:
                        bad += 1
                resp = "{0} of {2} messages processed; {1} errors;".format(msg, bad, len(messages))
                self.log.info(resp)


        self.log.info("run complete")
        return resp


