import json
from bottle import request, post, get, run, template, static_file, route
import xml.etree.ElementTree as ET
from urllib import request as r


# Get config
with open('config.json') as f:
    config = json.loads(f.read())


@route('/static/css/<filename>')
def server_static(filename):
    return static_file(filename, root='static/css')


@get('/')
def index():
    return template('index.html')


@get('/get_user')
def get_user_get():
    return template('get_user.html', user=None)


@get('/list')
def list():
    users = service_get_users()
    return template('list.html', users=users)


@post('/get_user')
def get_user_post():
    id = request.forms.get('id')
    user = service_get_user(id)
    if not user:
        return 'Error'
    return template('get_user.html', user=user[0])


@get('/add_user')
def add_user_get():
    return template('add_user.html', user=None)


@post('/add_user')
def add_user_post():
    name = request.forms.get('name')
    status = request.forms.get('status')
    user = service_add_user(name, status)
    if not user:
        return 'Error'
    return template('add_user.html', user=user[0])



# Get user service call
def service_get_user(id):
    body = '''<xml>
                <action>get_user</action>
                <parameters>
                    <id>{0}</id>
                </parameters>
            </xml>'''.format(id)
    result = send_request(body)
    if result == 'ERROR':
        return None
    return result


# Get user service call
def service_get_users():
    body = '''<xml>
                <action>get_users</action>
                <parameters>
                </parameters>
            </xml>'''.format(id)
    result = send_request(body)
    if result == 'ERROR':
        return None
    return result


# Add user service call
def service_add_user(name, status):
    body = '''<xml>
                <action>add_user</action>
                <parameters>
                    <name>{0}</name>
                    <status>{1}</status>
                </parameters>
            </xml>'''.format(name, status)
    result = send_request(body)
    if result == 'ERROR':
        return None
    return result


def send_request(body):
    req = r.Request(config['backend'], data=body.encode(), method='POST')
    res = r.urlopen(req)
    try:
        root = ET.fromstring(res.read())
    except Exception as e:
        print(e)
        return 'ERROR'
    state = root.find('state').text
    if state == 'OK':
        users = []
        for u in root.findall('result/user'):
            user = {}
            for t in u:
                user[t.tag] = t.text
            users.append(user)
        return users
    else:
        return 'ERROR'


# Start server
run(host='localhost', port=8081, debug=True, server='tornado')


