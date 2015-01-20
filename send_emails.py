import requests

key = 'key-5b043e50a4c56d9ff6b8c73b5d23c3e4'
sandbox = 'sandboxa8420b597da7412d906e170e6e810830.mailgun.org'

request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(sandbox)

def send_new_member_email(email, code):
    body = 'Welcome to WeatherWatch. To get your weather quickly, just enter /weather/{}'.format(code)
    request = requests.post(request_url, auth=('api', key), data={
        'from': 'dee@deekras.com',
        'to': email,
        'subject': 'Your WeatherWatch account',
        'text': body })

    print 'Status: {0}'.format(request.status_code)
    print 'Body:   {0}'.format(request.text)


