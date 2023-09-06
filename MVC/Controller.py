from tkinter import *
from tkinter.ttk import Treeview, Combobox

from messagebox import *
import pymysql

import Model


def connect_db():
    return Model.connect_db()


def quit_window(cursor, connection, root):
    return Model.quit_window(cursor, connection, root)


def login(cursor, connection, name, password):
    return Model.login(cursor, connection, name, password)


def register(cursor, connection, name, password, confirm_password, gender, root):
    return Model.register(cursor, connection, name, password, confirm_password, gender, root)


def delete_performance(cursor, connection, performance_number):
    return Model.delete_performance(cursor, connection, performance_number)

