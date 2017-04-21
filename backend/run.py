import json
from bottle import route, request, response, post, get, run
import pymysql
import xml.etree.ElementTree as ET


with open('config.json') as f:
    config = json.loads(f.read())

conn = pymysql.connect(
    host=config['host'],
    user=config['user'],
    password=config['password'],
    db=config['db'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


@post('/service')
def service():
    body = "".join(r.decode() for r in request.body.readlines())
    try:
        root = ET.fromstring(body)
    except Exception as e:
        print(e)
        response.body = '''<xml>
            <state>Error</state>
            <error>XML Syntax Error</error>
        </xml>'''
        return response

    action = root.find('action')
    if action is None:
        response.body = '''<xml>
        <action>get_user</action>
            <state>Error</state>
            <error>Action not passed</error>
        </xml>'''
        return response

    if action.text == 'get_user':
        params = root.find('parameters')
        if params is None:
            response.body = '''<xml>
            <action>get_user</action>
            <state>Error</state>
            <error>Parameters error</error>
            </xml>'''
            return response

        id = params.find('id')
        if id is None:
            response.body = '''<xml>
            <action>get_user</action>
            <state>Error</state>
            <error>ID not passed</error>
            </xml>'''
            return response

        user = db_get_user(id.text)
        if not user:
            response.body = '''<xml>
            <action>get_user</action>
            <state>Error</state>
            <error>User with ID {0} not found</error>
            </xml>'''.format(id.text)
            return response

        response.body = '''<xml>
            <action>get_user</action>
            <state>OK</state>
            <result>
                <user>
                    <id>{0}</id>
                    <name>{1}</name>
                    <status>{2}</status>
                </user>
            </result>
            </xml>'''.format(user['id'], user['name'], user['status'])
        return response
    elif action.text == 'add_user':
        params = root.find('parameters')
        if params is None:
            response.body = '''<xml>
            <action>add_user</action>
            <state>Error</state>
            <error>Parameters error</error>
            </xml>'''
            return response

        name = params.find('name')
        status = params.find('status')
        if name is None or status is None:
            response.body = '''<xml>
            <action>add_user</action>
            <state>Error</state>
            <error>Name or Status not passed</error>
            </xml>'''
            return response

        user = db_add_user(name.text, status.text)
        if not user:
            response.body = '''<xml>
            <action>add_user</action>
            <state>Error</state>
            <error>User was not added</error>
            </xml>'''
            return response

        response.body = '''<xml>
            <action>add_user</action>
            <state>OK</state>
            <result>
                <user>
                    <id>{0}</id>
                    <name>{1}</name>
                    <status>{2}</status>
                </user>
            </result>
            </xml>'''.format(user['id'], user['name'], user['status'])
        return response
    elif action.text == 'get_users':
        users = db_get_users()
        response.body = '''<xml>
            <action>get_users</action>
            <state>OK</state>
            <result>
            '''
        for user in users:
            response.body  += '''<user>
                    <id>{0}</id>
                    <name>{1}</name>
                    <status>{2}</status>
                </user>
                '''.format(user['id'], user['name'], user['status'])
        response.body += '''
            </result>
            </xml>'''
        return response

    else:
        return 'ERROR'


def db_add_user(name, status):
    try:
        with conn.cursor() as cursor:
            # Create a new record
            cursor.execute("INSERT INTO `users` (`name`, `status`) VALUES ('{0}', '{1}')".format(name, status))
            conn.commit()
            cursor.execute("SELECT `id`, `name`, `status` FROM `users` WHERE `name`='{}'".format(name))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        return None


def db_get_user(id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT `id`, `name`, `status` FROM `users` WHERE `id`={}".format(id))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(e)
        return None


def db_get_users():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT `id`, `name`, `status` FROM `users`")
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
        return None



# Run server
run(host='localhost', port=8080, debug=True, server='tornado')

