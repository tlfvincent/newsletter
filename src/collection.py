import base64
import logging
import requests

from urlextract import URLExtract


class NewsletterCollector(object):
    """
    Extract all valid URLs found in newsletters

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        A valid Google API client connection
    newsletter_senders : list
        A list of email addresses that send newsletters of interest
    unwanted_urls : list
        A list of domain that we are not interested in
    """
    def __init__(
        self,
        service,
        newsletter_senders,
        unwanted_urls,
        start_date,
        end_date
    ):

        self._service = service
        self.newsletter_senders = newsletter_senders
        self.unwanted_urls = unwanted_urls
        self.start_date = start_date
        self.end_date = end_date

    def pipeline(self):

        newsletter_urls = []

        for email in self.newsletter_senders:

            unread_msgs = self.get_latest_newsletter(email)

            msg_ids = self.get_message_ids(unread_msgs)

            if msg_ids is not None:

                for msg_id in msg_ids:

                    msg_metadata = self.get_msg_metadata(msg_id)

                    msg_text = self.get_msg_text(msg_metadata)

                    valid_urls = self.extract_urls(msg_text)

                    newsletter_urls.append(valid_urls)

        return newsletter_urls

    def get_latest_newsletter(self, email):
        """
        Extract all emails sent by input email address

        Parameters
        ----------
        email : str
            An email address

        Returns
        -------
        unread_msgs : dict-like
            contains message ids corresponding to emails
            sent by input email address

        Notes
        -----
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
        """
        logging.info(f'Getting all unread messages from {email}')

        unread_msgs = (
            self._service
            .users()
            .messages()
            .list(
                userId='me',
                labelIds=['INBOX'],
                q=f'from:{email} after:{self.start_date} before:{self.end_date}'
            )
            .execute()
        )

        return unread_msgs

    def get_message_ids(self, unread_msgs):
        """
        Extract all message ids

        Parameters
        ----------
        unread_msgs : dict-like
            contains message ids corresponding to emails
            sent by input email address

        Returns
        -------
        message_ids : list
            list of message ids
        """

        if 'messages' in unread_msgs:

            message_ids = [x['id'] for x in unread_msgs['messages']]
            return message_ids

        else:
            return None

    def get_msg_metadata(self, message_id):
        """
        Extract byte-encoded content of email corresponding
        to the input message id

        Parameters
        ----------
        message_ids : list
            list of message ids

        Returns
        -------
        msg_metadata : dict-like
            byte-encoded content of email associated to message id
        """

        logging.info(f'Retrieving all unread messages from {message_id}')

        msg_metadata = (
            self._service
            .users()
            .messages()
            .get(
                userId='me',
                id=f'{message_id}',
                format='full'
            )
            .execute()
        )

        return msg_metadata

    def get_msg_text(self, msg_metadata):
        """
        Convert byte-encoded content to human-readable text

        Parameters
        ----------
        msg_metadata : dict-like
            byte-encoded content of email associated to message id

        Returns
        -------
        msg_text : string
            human-readable content of email associated to message id
        """

        logging.info('Decoding message content from Base64 to UTF-8')
        msg_body = (
            msg_metadata['payload']['parts'][0]['body']['data']
            .replace("-", "+")
            .replace("_", "/")
        )

        msg_text = (
            base64.b64decode(
                bytes(msg_body, 'UTF-8')
            )
            .decode('utf-8')
        )

        return msg_text

    def extract_urls(self, msg_text):
        """
        Extract valud URLs from content of email

        Parameters
        ----------
        msg_text : string
            human-readable content of email associated to message id

        Returns
        -------
        valid_urls : string
            human-readable content of email associated to message id
        """
        urls = URLExtract().find_urls(msg_text)

        valid_urls = []
        for u in urls:
            try:
                redirect_url = requests.get(u).url
            except:
                pass

            is_unwanted_url = self._find_unwanted_url(redirect_url)
            if is_unwanted_url:
                pass
            else:
                valid_urls.append(redirect_url)
                print(redirect_url)

        return valid_urls

    def _find_unwanted_url(self, redirect_url):

        for x in self.unwanted_urls:
            if x in redirect_url:
                return True
        else:
            return False
