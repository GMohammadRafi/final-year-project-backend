from os import environ

SENDER_EMAIL = environ.get('SENDER_EMAIL')
SENDER_PASSWORD = environ.get('SENDER_PASSWORD')
SMS_API_KEY = environ.get('SMS_API_KEY')
SMS_URL = environ.get('SMS_URL')

SESSION_TIME = 10 * 24 * 60 * 60
