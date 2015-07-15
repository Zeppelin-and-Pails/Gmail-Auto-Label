#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gmail-auto-label start

automatically generates labels for use in gmail,
based on either sender address, or recipient address (use with catch all addresses)

@category   Utility
@version    $ID: 1.1.1, 2015-07-01 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""
__version__ = "1.1.1"

#Import some stuff
import autolabel
import gmailconnector
from flask import Flask, request, jsonify, redirect

#Make a Flask app
app = Flask(__name__)

#Add some routes, for the moment we have all stats, and individual stats to deal with
@app.route('/run/labeler')
def labeler():
    #Make the autolabeler
    labeler = autolabel.autolabel()
    return labeler.run()

@app.route('/oauth2callback')
def oauth2callback():
    con = gmailconnector.gmailconnector()
    if 'code' not in request.args:
        auth_uri = con.get_auth_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        try:
            result = con.set_credentials(auth_code)
        except:
            return 'Get credentials [Failed]'

        return 'Get credentials {}'.format(result)

app.run(host='localhost', port=5002)