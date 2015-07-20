# Gmail-Auto-Label
Automatic labelling for catch all email addresses

# Installation and Setup

To start with, clone this repo.

To use Gmail-Auto-Label you will need to either create or obtain a client secrets file from google

1. browse to console.developers.google.com, sign up if needed
2. open an existing project or create a new one
3. select 'APIs & Auth' from the menu
4. under 'Google Apps APIs' select Gmail API
5. enable the Gmail API
6. from the left again select 'Credentials'
7. under 'OAuth' select Create new Client ID
8. make sure your Auth Callback path is listed in the Redirect URI
9. download the client_secret.json file to a location on the server
10. update gmailconnector.cfg with the appropriate details
  * CS_FILE - path of the client secrets file
  * AUTH_ADD - email address to notify if reauthentication is needed
  * AUTH_URL - the url for reauth initialisation e.g. 'testurl.com/oauth2callback'

example client secrets file:
```
{
  "web": {
    "client_id": "asdfjasdljfasdkjf",
    "client_secret": "1912308409123890",
    "redirect_uris": ["https://www.example.com:5002/oauth2callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

# Running

From a cli run autolabelflask.py