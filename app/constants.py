from os import environ

SENDER_EMAIL = environ.get('SENDER_EMAIL') or 'bmtcmy@gmail.com'
SENDER_PASSWORD = environ.get('SENDER_PASSWORD') or 'shafi20015'
SMS_API_KEY = environ.get('SMS_API_KEY')
SMS_URL = environ.get('SMS_URL')
# print(SENDER_EMAIL)
# print(SENDER_PASSWORD)
# print(SMS_API_KEY)
# print(SMS_URL)
# print(environ)
SESSION_TIME = 10 * 24 * 60 * 60
