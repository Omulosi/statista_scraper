import requests
from lxml.html import fromstring

LOGIN_URL ='https://www.statista.com/login/'
LOGIN_USERNAME = 'keith.davey@parallaxgeo.com'
LOGIN_PASSWORD = 'D3jaULYw7QKZiUxD'

def parse_form(html):
    tree = fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data

def login(session=None):
    if session is None:
        html = requests.get(LOGIN_URL)
    else:
        html = session.get(LOGIN_URL)
    data = parse_form(html.content)
    data['loginStat[username]'] = LOGIN_USERNAME
    data['loginStat[password]'] = LOGIN_PASSWORD
    print(data)
    if session is None:
        response = requests.post(LOGIN_URL, data, cookies=html.cookies)
    else:
        response = session.post(LOGIN_URL, data)
    assert 'login' not in response.url
    return response, session
