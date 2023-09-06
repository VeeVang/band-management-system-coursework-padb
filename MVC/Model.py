import pymysql
from messagebox import *

from tkinter import *
from tkinter.ttk import Treeview, Combobox


def connect_db():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='root', database='band')
    except pymysql.err.OperationalError as err:
        return 1, {'message': err}
    else:
        print('Connected to Database! ')
        cursor = connection.cursor()
        print('Generated Cursor! ')
        return 0, {'connection': connection, 'cursor': cursor}


def quit_window(cursor, connection, root):
    cursor.close()
    connection.close()
    print("Cursor and connection are closed!")
    root.destroy()
    return


def login(cursor, connection, name, password):
    tuple_num = cursor.execute('SELECT PASSWORD, MEMBER_NUMBER FROM MEMBER WHERE NAME = "' + name + '"')
    if tuple_num == 0:
        return -1
    member_info = cursor.fetchone()
    if member_info[0] != password:  # 密码错误
        return -2
    # 无异常
    return member_info[1]


def register(cursor, connection, name, password, confirm_password, gender, root):
    # 检查每个字段是否都输入了
    if not name:
        return 1, u'注册失败', u'用户名未填写！'
    if not gender:
        return 1, u'注册失败', u'性别未选择！'
    # 检验两次输入的密码是否一致
    if password != confirm_password:
        return 1, u'注册失败', u'两次输入的密码不一致！'
    # 两次输入的密码一致
    # 搜索是否存在这个人，如果已经存在，那么不行！
    tuple_num = cursor.execute('SELECT NAME FROM MEMBER WHERE NAME = "' + name + '"')
    if tuple_num != 0:
        return 1, u'注册失败', u'已有此用户，请直接登录！'
    else:   # 这个人没有注册过
        if gender == u"女":
            is_male = 0
        elif gender == u"男":
            is_male = 1
        else:
            showerror(u'注册失败', u'性别不正确！')
            return 1, u'注册失败', u'性别不正确！'
        cursor.execute(
            'INSERT INTO MEMBER (NAME, PASSWORD, IS_MALE) VALUES (' +
            '"' + name + '", "' + password + '", ' + str(is_male) + ')')
        connection.commit()
        root.destroy()
        return 0, u"注册成功", u"注册成功！请使用此账号密码登录！"


def delete_performance(cursor, connection, performance_number):
    tuples_count = cursor.execute('DELETE FROM PERFORMANCE WHERE PERFORMANCE_NUMBER = ' +
                                  str(performance_number))
    connection.commit()
    if tuples_count:
        return 0
    else:
        return 1
