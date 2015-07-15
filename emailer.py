import smtplib

class emailer:
    def __init__(self, address, url):
        message = """
        From: {0}
        To: {0}
        Subject: Auto Label Authentication

        The Gmail-Auto-labeler needs authentication, please visit the following url to authorise:
        {1}
        """.format(address, url)

        # Send the mail

        server = smtplib.SMTP('myserver')
        server.sendmail(address, [address], message)
        server.quit()