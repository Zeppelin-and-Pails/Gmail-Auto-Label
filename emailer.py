"""
emailer

sends a simple email to a passed in address when re-auth is required

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
import smtplib


def send(address, url):
    """ Send an email to the provided address, with the provided url
    :param address:
    :param url:
    :return:
    """
    message = \
        ("From: {0}\n"
         "To: {0}\n"
         "Subject: Auto Label Authentication\n"
         "\n"
         "The Gmail-Auto-labeler needs authentication, "
         "please visit the following url to authorise:\n"
         "{1}").format(address, url)

    # Send the mail
    server = smtplib.SMTP('myserver')
    server.sendmail(address, [address], message)
    server.quit()