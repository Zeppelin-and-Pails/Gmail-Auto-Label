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

import autolabel
import gmailconnector
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

@app.route('/run/labeler')
def labeler():
    """ Run the autolabeler, and return the results
    :return: output of the labeler run
    """
    labeler = autolabel.autolabel()
    return labeler.run()

@app.route('/oauth2callback')
def oauth2callback():
    """ Authenticate the app with the GMail API
    :return: results of the authentication run
    """
    con = gmailconnector.gmailconnector()
    if 'code' not in request.args:
        auth_uri = con.get_auth_url()
        del con
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        try:
            result = con.set_credentials(auth_code)
            del con
        except:
            return 'Get credentials [Failed]'

        del con
        return 'Get credentials {}'.format(result)

app.run(host='localhost', port=5002)