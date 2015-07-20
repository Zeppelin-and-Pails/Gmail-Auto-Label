#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
autolabelflask

REST interface for Autolabeler, starts up a autolabeler via webhooks

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os
import yaml
import autolabel
import gmailconnector
from flask import Flask, request, jsonify, redirect


DIR = os.path.dirname(os.path.realpath(__file__))
conf = yaml.safe_load(open("{}/flask.cfg".format(DIR)))
app = Flask(__name__)

labeler = autolabel.autolabel()

@app.route(conf['RUNCALL'])
def labeler():
    """ Run the autolabeler, and return the results
    :return: output of the labeler run
    """
    return labeler.run()

@app.route(conf['AUTHCALL'])
def oauth2callback():
    """ Authenticate the app with the GMail API
    :return: results of the authentication run
    """
    con = labeler.get_gmailcon()
    if 'code' not in request.args:
        auth_uri = con.get_auth_url()
        del con
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        try:
            result = con.set_credentials(auth_code)
        except:
            return 'Get credentials [Failed]'
        return 'Get credentials {}'.format(result)

app.run(host=conf['HOST'], port=conf['PORT'])