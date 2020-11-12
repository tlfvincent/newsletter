import os
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class AppSettings(object):

    def __init__(
        self,
        app_config
    ):

        self._app_config = app_config
        self.api_credentials = app_config['gmail']['credentials']
        self.token_file = app_config['gmail']['token']
        self.scopes = app_config['gmail']['scopes']

    def get_email_address(self):

        return self._app_config['email']['email_address']

    def get_gmail_service(self):

        creds = self.check_for_existing_token()

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.api_credentials,
                    self.scopes
                )

                creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        return service

    def check_for_existing_token(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

            return creds

        else:
            return None
