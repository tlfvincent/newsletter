import base64
import itertools
import logging

from collections import OrderedDict
from email.mime.text import MIMEText


class NewsletterSender(object):
    """
    Extract all valid URLs found in newsletters

    Parameters
    ----------
    app_settings : settings.AppSettings
        Contains application settings
    service : googleapiclient.discovery.Resource
        A valid Google API client connection
    newsletter_urls : list
        A list of URLs collected from newsletters
    """
    def __init__(
        self,
        app_settings,
        service,
        newsletter_urls
    ):

        self._app_settings = app_settings
        self._service = service
        self.newsletter_urls = newsletter_urls

    def process_and_send_urls(self):

        urls = self._process_newsletter_urls()

        message_text = '\n\n'.join(urls)

        body = self._create_message(message_text)

        self._send_message(body)

    def _process_newsletter_urls(self):

        logging.info('Flatten list of lists containing URLs.')
        all_urls = list(
            itertools.chain.from_iterable(self.newsletter_urls)
        )

        logging.info('Remove duplicate URLs.')
        urls = sorted(list(OrderedDict.fromkeys(all_urls)))

        return urls

    def _create_message(
        self,
        message_text,
        subject='Weekly ML Newsletter'
    ):
        """
        Create a message for an email.

        Parameters
        ----------
        sender : str
            Email address of the sender.
        to : str
            Email address of the receiver.
        subject : str
            The subject of the email message.
        message_text : str
            The text of the email message.

        Returns : dict-like
            An object containing a base64url encoded email object.
        """

        message = MIMEText(message_text)
        message['to'] = self._app_settings.get_email_address()
        message['from'] = self._app_settings.get_email_address()
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()

        body = {'raw': raw}

        return body

    def _send_message(self, body):
        """
        Send an email message.

        Parameters
        ----------
        body : dict-like
            An object containing a base64url encoded email object.

        Returns:
          Sent Message.
        """
        message = (
            self._service
            .users()
            .messages()
            .send(
                userId='me',
                body=body
            )
            .execute()
        )

        return message
