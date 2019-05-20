import logging


def main(myIoTHubMessage):
    logging.info(myIoTHubMessage)
    logging.info('Python EventHub trigger processed an event: %s',
                 myIoTHubMessage.get_body().decode('utf-8'))
