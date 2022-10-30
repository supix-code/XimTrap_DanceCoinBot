import sqlite3
import random
import time


def db_decorator(incoming_funk):
    def db_handler(*args, **kwargs):
        for _ in range(10):
            try:
                result = incoming_funk(*args, **kwargs)
                return result    
            except sqlite3.OperationalError:
                print('----------------\nOperationalError\n----------------')
                time.sleep(0.5)
        result = incoming_funk(*args, **kwargs)
        return result
    return db_handler


def pass_generation(num):
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789012345678901234567890'
    password = ''
    length = num
    for i in range(length):
        password += random.choice(chars)
    return password


@db_decorator
def make_connect():
    connection = sqlite3.connect('database.db')
    q = connection.cursor()
    return connection, q


@db_decorator
def get_users():
    connection, q = make_connect()
    sql = 'SELECT * FROM users'
    q.execute(sql)
    data = q.fetchall()
    return data


@db_decorator
def get_user(userid):
    connection, q = make_connect()
    sql = 'SELECT * FROM users WHERE userid = ?'
    q = q.execute(sql, [userid])
    data = q.fetchone()
    return data


@db_decorator
def add_user(userid, user_type, group='None', school='None'):
    connection, q = make_connect()
    sql = 'INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)'
    values = (userid, user_type, '0', group, school, 'None', int(time.time()))
    q.execute(sql, values)
    connection.commit()


@db_decorator
def get_schools():
    connection, q = make_connect()
    sql = 'SELECT * FROM schools'
    q = q.execute(sql)
    data = q.fetchall()
    return data


@db_decorator
def get_school(school_id):
    connection, q = make_connect()
    sql = 'SELECT * FROM schools WHERE id = ?'
    q = q.execute(sql, [school_id])
    data = q.fetchone()
    return data


@db_decorator
def del_school(school_id):
    connection, q = make_connect()
    sql = 'DELETE FROM schools WHERE id = ?'
    q = q.execute(sql, [school_id])
    connection.commit()


@db_decorator
def add_school(name, creator):
    connection, q = make_connect()
    sql = 'SELECT MAX(id) FROM schools'
    q.execute(sql)
    max_id = q.fetchone()[0]
    if max_id is None:
        max_id = 0        
    
    code = pass_generation(7)
    new_id = int(max_id) + 1
    sql = 'INSERT INTO schools VALUES (?, ?, ?)'
    q.execute(sql, (new_id, name, code))
    connection.commit()

    add_reg_code(code, creator, 'school', new_id)


@db_decorator
def username_update(message, userid):
    connection, q = make_connect()
    sql = 'SELECT username FROM users WHERE userid = ?'
    q = q.execute(sql, [userid])
    try: 
        username_1 = q.fetchone()[0]
    except TypeError: 
        username_1 = 'None'
    username_2 = str(message.from_user.username)
    if str(username_1).lower() != str(username_2).lower():
        sql = 'UPDATE users SET username = ? WHERE userid = ?'
        q.execute(sql, [str(username_2).lower(), userid])
        connection.commit()


@db_decorator
def add_reg_code(code, creator, code_type, school_id='None', group_id='None'):
    connection, q = make_connect()
    sql = 'INSERT INTO registration_codes VALUES (?, ?, ?, ?, ?, ?, ?)'
    values = (code, creator, code_type, int(time.time()), 'open', school_id, group_id)
    q.execute(sql, values)
    connection.commit()


@db_decorator
def get_reg_code(code):
    connection, q = make_connect()
    sql = 'SELECT * FROM registration_codes WHERE code = ?'
    q = q.execute(sql, [code])
    data = q.fetchone()
    return data


@db_decorator
def del_reg_code(code):
    connection, q = make_connect()
    sql = 'DELETE FROM registration_codes WHERE code = ?'
    q = q.execute(sql, [code])
    connection.commit()


@db_decorator
def get_except(except_id):
    connection, q = make_connect()
    sql = 'SELECT * FROM excepts WHERE id = ?'
    q = q.execute(sql, [except_id])
    data = q.fetchone()
    return data


@db_decorator
def add_except(data):
    connection, q = make_connect()
    sql = 'SELECT MAX(id) FROM excepts'
    q.execute(sql)
    max_id = q.fetchone()[0]
    if max_id is None:
        max_id = 0        
    
    new_id = int(max_id) + 1
    sql = 'INSERT INTO excepts VALUES (?, ?)'
    q.execute(sql, (new_id, data))
    connection.commit()
    return new_id



