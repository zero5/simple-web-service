import json
from bottle import route, request, response, post, get, run
import sqlite3
import xml.etree.ElementTree as ET

with open('config.json') as f:
    config = json.loads(f.read())

conn = sqlite3.connect(
    config['dbfile']
)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS `users` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	VARCHAR UNIQUE,
	`status`	VARCHAR
);
''')

conn.commit()


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
            <error>User with ID `{0}` not found</error>
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
            </xml>'''.format(user[0], user[1], user[2])
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
            </xml>'''.format(user[0], user[1], user[2])
        return response
    elif action.text == 'get_users':
        users = db_get_users()
        if users == None:
            response.body = '''<xml>
            <action>get_users</action>
            <state>Error</state>
            <error>Error on getting users</error>
            </xml>'''
            return response

        response.body = '''<xml>
            <action>get_users</action>
            <state>OK</state>
            <result>
            '''
        for user in users:
            response.body += '''<user>
                    <id>{0}</id>
                    <name>{1}</name>
                    <status>{2}</status>
                </user>
                '''.format(user[0], user[1], user[2])
        response.body += '''
            </result>
            </xml>'''
        return response

    else:
        return 'ERROR'


def db_add_user(name, status):
    try:
        c.execute("INSERT INTO `users` (`name`, `status`) VALUES ('{0}', '{1}')".format(name, status))
        conn.commit()
        c.execute("SELECT `id`, `name`, `status` FROM `users` WHERE `name`='{}'".format(name))
        result = c.fetchone()
        return result
    except Exception as e:
        print(e)
        return None


def db_get_user(id):
    try:
        c.execute("SELECT `id`, `name`, `status` FROM `users` WHERE `id`={}".format(id))
        result = c.fetchone()
        return result
    except Exception as e:
        print(e)
        return None


def db_get_users():
    try:
        c.execute("SELECT `id`, `name`, `status` FROM `users` ORDER BY ID DESC LIMIT 100")
        result = c.fetchall()
        return result
    except Exception as e:
        print(e)
        return None


# Run server
run(host='localhost', port=8082, debug=True, server='tornado')
