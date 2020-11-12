import argparse
import configparser
import json

from datetime import datetime, timedelta

from src import settings
from src import collection
from src import processing


def run(app_config):
    """
    Main job to run newsletter aggregator

    Parameters
    ----------
    app_config : configparser.ConfigParser
        instance containing all application configurations
    """

    today = datetime.now()
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    app_settings = settings.AppSettings(app_config)

    service = app_settings.get_gmail_service()

    collector = collection.NewsletterCollector(
        service,
        json.loads(app_config['newsletter']['newsletter_senders']),
        json.loads(app_config['newsletter']['unwanted_urls']),
        start_date,
        end_date
    )

    newsletter_urls = collector.pipeline()

    processor = processing.NewsletterSender(
        app_settings,
        service,
        newsletter_urls
    )

    processor.process_and_send_urls()


def read_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--config_file',
        type=str,
        required=True,
        help='the path to your application configuration file'
    )

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    args = read_args()

    app_config = configparser.ConfigParser()
    app_config.read(args.config_file)

    try:
        run(app_config)
    except:
        pass
