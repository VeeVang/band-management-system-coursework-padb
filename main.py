from tkinter import *
from tkinter.ttk import Treeview, Combobox

from messagebox import *
import pymysql

import Model
import Controller

global connection
global cursor
global member_number
global member_name

def start_gui():
    # init
    global connection
    global cursor
    flag, data = Controller.connect_db()
    if flag:
        showerror(u'连接数据库失败', u'连接数据库失败\n请联系管理员\n' + u'错误信息：' + str(data["message"]))
        return
    else:
        connection = data["connection"]
        cursor = data["cursor"]
        login_window()
        return


def login_window():
    global cursor
    global connection

    # 登录
    root = Tk()
    root.title(u"登录")
    root.geometry("+700+300")

    # name
    f1 = Frame(root)
    f1.grid(row=0, column=0, padx=20, pady=5)
    Label(f1, text=u"用户名").grid()
    e1 = Entry(f1, width=30)
    e1.grid()
    # password
    f2 = Frame(root)
    f2.grid(row=1, column=0, padx=20, pady=5)
    Label(f2, text=u"密码").grid()
    e2 = Entry(f2, width=30, show="*")
    e2.grid(row=1, column=0)
    # login_button
    f3 = Frame(root)
    f3.grid(row=2, column=0, pady=10)
    Button(f3, text=u"登录", command=lambda: login(e1.get(), e2.get(), root)).grid(row=3, column=0, padx=10, ipadx=5)
    # register_button
    Button(f3, text=u"注册", command=register_window).grid(row=3, column=1, padx=10, ipadx=5)

    # quit_button
    f4 = Frame(root)
    f4.grid(row=3, column=0, pady=10)
    Button(f4, text=u"退出",
           command=lambda: Controller.quit_window(cursor=cursor, connection=connection, root=root)).grid()

    # mainloop
    root.mainloop()


def login(name, password, root):
    m_num = Controller.login(cursor, connection, name, password)
    if m_num == -1:
        showerror(u'登陆失败', u'用户不存在！')
        return
    elif m_num == -2:
        showerror(u'登陆失败', u'密码错误')
        return
    else:
        global member_number
        member_number = m_num
        global member_name
        member_name = name
        showinfo(u"登陆成功", u"欢迎使用")
        root.destroy()
        home_window()
        return


def register(name, password, confirm_password, gender, root):
    err_flag, box_title, box_message = Controller.register(cursor, connection, name,
                                                           password, confirm_password, gender, root)
    if err_flag:
        showerror(box_title, box_message)
    else:
        showinfo(box_title, box_message)


def register_window():
    root = Tk()
    root.title(u"注册")
    root.geometry("+1000+300")

    # name
    f1 = Frame(root)
    f1.grid(sticky=E, padx=20, pady=5)
    Label(f1, text=u"用户名").grid()
    e1 = Entry(f1, width=30)
    e1.grid()
    # password
    f2 = Frame(root)
    f2.grid(sticky=E, padx=20, pady=5)
    Label(f2, text=u"密码").grid()
    e2 = Entry(f2, width=30, show="*")
    e2.grid()
    # password again
    f3 = Frame(root)
    f3.grid(sticky=E, padx=20, pady=5)
    Label(f3, text=u"确认密码").grid()
    e3 = Entry(f3, width=30, show="*")
    e3.grid()
    # is_male
    f4 = Frame(root)
    f4.grid(padx=20, pady=5, column=0)
    Label(f4, text=u'性别').grid(row=0, column=0)
    gender_combobox = Combobox(f4, width=5, state="readonly")
    gender_combobox['value'] = (u"女", u"男")
    gender_combobox.current(0)
    gender_combobox.grid(row=1, column=0)

    # register_button
    f5 = Frame(root)
    f5.grid(pady=20)
    Button(f5, text=u"注册", command=lambda: register(e1.get(), e2.get(), e3.get(),
                                                    gender_combobox.get(), root)).grid(ipadx=5, ipady=5)

    # 主循环
    root.mainloop()


# home page
def home_window():
    # 主页
    root = Tk()
    root.geometry('+800+400')
    root.title(u"主页")

    menu_bar = Menu(root)
    root["menu"] = menu_bar

    menu = {"band": Menu(menu_bar, tearoff=False),
            "song": Menu(menu_bar, tearoff=False),
            "performance": Menu(menu_bar, tearoff=False)}
    # 乐队check_band：加入乐队
    menu["band"].add_command(label=u'新建乐队', command=insert_band_window)
    menu["band"].add_command(label=u'加入乐队', command=join_band_window)
    menu_bar.add_cascade(label=u'乐队', menu=menu["band"])

    # 乐曲check_song：添加乐曲，查看/删除乐曲
    menu["song"].add_command(label=u'添加乐曲', command=new_song_window)
    menu["song"].add_command(label=u'查看/删除乐曲', command=check_song_window)
    menu_bar.add_cascade(label=u'乐曲', menu=menu["song"])

    # check_performance：添加演出，查看/更新/删除演出
    menu["performance"].add_command(label=u'添加演出', command=insert_performance_window)
    menu["performance"].add_command(label=u'查看/删除演出', command=performance_window)
    menu_bar.add_cascade(label=u'演出', menu=menu["performance"])

    # welcome
    f_welcome = Frame(root)
    f_welcome.grid(padx=100, pady=100)
    Label(f_welcome, text=u"你好！" + str(member_name) + u"\n欢迎来到主页\n请使用上方菜单栏\n管理您的乐队、歌曲与演出", font=(u"微软雅黑", 20)).grid()

    # quit
    f_quit = Frame(root)
    f_quit.grid(padx=10, pady=10)
    Button(f_quit, text=u"退出", command=lambda: Model.quit_window(cursor, connection, root)).grid()

    root.mainloop()


def search_band(string, tree):
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND WHERE NAME LIKE "%' + string + '%"')
    for band_info in cursor.fetchall():
        tree.insert("", int(band_info[0]), values=band_info)


def check_band_window(band_number):
    cursor.execute("SELECT NAME, ESTABLISH_DATE FROM BAND WHERE BAND_NUMBER = " + str(band_number))
    [name, establish_date] = cursor.fetchone()
    root = Tk()
    root.geometry("+800+400")
    root.title(name + u"信息")

    f = Frame(root)
    f.grid()
    Label(f, text=u"乐队编号：" + str(band_number)).grid(padx=30, pady=20)
    Label(f, text=u"乐队名称：" + str(name)).grid(padx=30)
    Label(f, text=u"成立时间：" + str(establish_date)).grid(padx=30, pady=20)

    root.mainloop()


# 查看/加入乐队
def join_band_window():
    # 加入乐队

    root = Tk()
    root.geometry("+800+400")
    root.title(u"查看/加入乐队")
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND')

    search_band_frame = Frame(root)
    search_band_frame.grid()
    search_band_entry = Entry(search_band_frame)
    search_band_entry.grid()
    Button(search_band_frame, text=u"搜索乐队", command=lambda: search_band(search_band_entry.get(), tree)).grid(pady=5)
    # 查询所有可以加入的乐队
    tree = Treeview(root)
    tree["columns"] = ('BAND_NUMBER', 'NAME')
    tree["show"] = 'headings'
    tree.heading('BAND_NUMBER', text=u"乐队编号")
    tree.heading('NAME', text=u"乐队名称")
    for band_info in cursor.fetchall():
        tree.insert("", int(band_info[0]), values=band_info)
    tree.grid()

    operation_frame = Frame(root)
    operation_frame.grid()
    Button(operation_frame, text=u"查看信息",
           command=lambda: check_band_window(str(tree.item(tree.focus())['values'][0]))).grid(row=3, column=0, padx=5)
    Button(operation_frame, text=u"加入乐队", command=lambda: join_band(tree)).grid(row=3, column=1, padx=5)

    root.mainloop()


def join_band(tree):
    # 先看有无这条记录，如果有，则不插入
    tuples_num = cursor.execute('SELECT * FROM MEMBER_BAND WHERE MEMBER_NUMBER = ' + str(member_number) +
                                ' AND BAND_NUMBER = ' + str(tree.item(tree.focus())['values'][0]))
    if tuples_num != 0:
        showerror(u"加入失败", u"您已经在该队伍中！")
        return
    # 原本不在该队伍中，则插入这一条记录
    # print(tree.item(tree.focus()))
    cursor.execute('INSERT INTO MEMBER_BAND (MEMBER_NUMBER, BAND_NUMBER) VALUES (' + str(member_number) +
                   ', ' + str(tree.item(tree.focus())['values'][0]) + ')')
    connection.commit()
    showinfo(u"加入成功", u"加入队伍成功！")
    return


def insert_band(name, establish_date):
    if not name:
        showerror(u"添加失败", u"请输入乐队名，乐队名不可为空！")
        return
    if not establish_date:
        establish_date = 10010101
    try:
        cursor.execute('INSERT INTO BAND (NAME, ESTABLISH_DATE) VALUES ("' +
                       str(name) + '", ' + str(establish_date) + ")")
        connection.commit()
    except pymysql.err.IntegrityError:
        showerror(u"添加失败", u"有重名的乐队！")
    else:
        showinfo(u"添加成功", u"添加乐队成功！")
    return


def insert_band_window():

    root = Tk()
    root.geometry("+800+400")
    root.title(u"新增乐队信息")

    # 乐队信息
    name_entry_frame = Frame(root)
    name_entry_frame.grid(padx=100, pady=5)
    Label(name_entry_frame, text=u"乐队名称").grid()
    name_entry = Entry(root)
    name_entry.grid()
    establish_date_entry_frame = Frame(root)
    establish_date_entry_frame.grid(padx=100, pady=5)
    Label(establish_date_entry_frame, text=u"建立时间").grid()
    establish_date_entry = Entry(root)
    establish_date_entry.grid()

    button_frame = Frame(root)
    button_frame.grid(padx=5, pady=5)
    Button(button_frame, text=u"新增",
           command=lambda: insert_band(name_entry.get(),
                                       establish_date=establish_date_entry.get())).grid(ipadx=5, ipady=5)

    root.mainloop()
    return


def check_song_window():
    def check_song(band_number, tree):
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute('SELECT SONG_NUMBER, NAME FROM SONG WHERE BAND_NUMBER = ' +
                       str(band_number))
        songs = cursor.fetchall()
        for song in songs:
            song_tree.insert("", int(song[0]), values=song)  # 将index索引设置为song_number
        return

    def delete_song(song_number, band_name, song_name):
        try:
            tuples_count = cursor.execute('DELETE FROM SONG WHERE SONG_NUMBER = ' +
                                          str(song_number))
            connection.commit()
        except pymysql.err.IntegrityError:
            showerror(u"删除失败", u"删除失败！\n存在歌单中引用了这首歌！")
        else:
            if tuples_count:
                showinfo(u"删除成功", u"删除了歌曲：" +
                         str(band_name) + ' ' +
                         str(song_name))
            else:
                showerror(u"删除失败", u"库中不存在歌曲：" +
                          str(band_name) + ' ' +
                          str(song_name))
        return

    root = Tk()
    root.geometry("+800+400")
    root.title(u"搜索歌曲")

    # select_band_combobox
    select_band_frame = Frame(root)
    select_band_frame.grid(padx=10, pady=10)
    Label(select_band_frame, text=u"选择乐队").grid()
    band_cbx = Combobox(select_band_frame, state='readonly', width=15)
    # cursor.execute('SELECT BAND.BAND_NUMBER, BAND.NAME '
    #                'FROM BAND '
    #                'INNER JOIN MEMBER_BAND '
    #                'ON BAND.BAND_NUMBER = MEMBER_BAND.BAND_NUMBER '
    #                'WHERE MEMBER_BAND.MEMBER_NUMBER = ' + str(member_number))
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND WHERE BAND_NUMBER IN '
                   '(SELECT BAND_NUMBER FROM MEMBER_BAND WHERE MEMBER_NUMBER = ' + str(member_number) + ')')
    records = cursor.fetchall()
    records_name = []
    for record in records:
        records_name.append(str(record[1]))
    band_cbx['value'] = records_name
    band_cbx.current(0)
    band_cbx.grid()

    song_tree = Treeview(root)
    song_tree["columns"] = ('SONG_NUMBER', 'NAME')
    song_tree["show"] = 'headings'
    song_tree.heading('SONG_NUMBER', text=u"歌曲编号")
    song_tree.heading('NAME', text=u"歌曲名称")

    # f_delete_song
    f_button = Frame(root, width=200)
    f_button.grid()
    Button(f_button, text=u"刷新歌曲表",
           command=lambda: check_song(records[band_cbx.current()][0], song_tree)
           ).grid(row=0, column=0, padx=5, pady=5)
    delete_song_button = Button(f_button, text=u"删除歌曲",
                                command=lambda: delete_song(song_tree.item(song_tree.focus())['values'][0],
                                                            band_cbx.get(),
                                                            song_tree.item(song_tree.focus())['values'][1]))
    delete_song_button.grid(row=0, column=1, padx=5, pady=5)
    delete_song_button['state'] = 'normal'

    song_tree.grid(padx=20, pady=20)

    root.mainloop()


def insert_song(song_name, band_number, band_name):
    if not song_name:
        showerror(u"添加失败", u"歌曲名不能为空！")
        return
    cursor.execute('INSERT INTO SONG (NAME, BAND_NUMBER) VALUES ("' + str(song_name) + '", ' +
                   str(band_number) + ')')
    connection.commit()
    showinfo(u"插入成功", "插入新乐曲成功：\n乐队：" + str(band_name) +
             u"\n曲名：" + str(song_name))
    return


def new_song_window():

    root = Tk()
    root.geometry("+800+400")
    root.title(u"添加歌曲")
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND WHERE BAND_NUMBER IN '
                   '(SELECT BAND_NUMBER FROM MEMBER_BAND WHERE MEMBER_NUMBER = ' + str(member_number) + ')')

    # select_band
    select_band_frame = Frame(root)
    select_band_frame.grid(padx=20, pady=20)
    Label(select_band_frame, text=u"选择乐队").grid()
    band_cbx = Combobox(select_band_frame, state='readonly')
    # print(cursor.fetchall())
    # records = band_number, name
    records = cursor.fetchall()

    records_name = []
    for record in records:
        records_name.append(str(record[1]))
    # print(records_list)
    band_cbx['value'] = records_name

    # print(band_combobox['value'])
    band_cbx.current(0)
    band_cbx.grid()

    # 插入歌曲，insert_song
    f_new_song = Frame(root)
    f_new_song.grid(pady=5)
    l_name = Label(f_new_song, text=u"曲目名")
    l_name.grid()
    e_name = Entry(f_new_song)
    e_name.grid()
    Button(f_new_song, text=u"插入歌曲",
           command=lambda: insert_song(
               song_name=e_name.get(), band_number=records[band_cbx.current()][0], band_name=band_cbx.get())
           ).grid(ipadx=5, ipady=5)

    root.mainloop()


def insert_performance(date, place, band_number):
    cursor.execute("INSERT INTO PERFORMANCE (DATE, PLACE, BAND_NUMBER) VALUES (" +
                   str(date) + ', "' + str(place) + '", ' +
                   str(band_number) + ")")
    connection.commit()
    showinfo(u"添加成功", u"添加演出成功！")
    return


def insert_performance_window():

    root = Tk()
    root.geometry("+800+400")
    root.title(u"新增演出信息")

    # search_band
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND WHERE BAND_NUMBER IN '
                   '(SELECT BAND_NUMBER FROM MEMBER_BAND WHERE MEMBER_NUMBER = ' + str(member_number) + ')')
    # select_band_combobox
    select_band_frame = Frame(root)
    select_band_frame.grid(padx=20, pady=5)
    Label(select_band_frame, text=u"选择乐队").grid()
    band_cbx = Combobox(select_band_frame, state='readonly')
    records = cursor.fetchall()
    records_name = []
    for record in records:
        records_name.append(str(record[1]))
    band_cbx['value'] = records_name
    band_cbx.current(0)
    band_cbx.grid()

    # 演出信息
    date_entry_frame = Frame(root)
    date_entry_frame.grid(padx=20, pady=5)
    Label(date_entry_frame, text=u"时间").grid()
    date_entry = Entry(root)
    date_entry.grid()
    place_entry_frame = Frame(root)
    place_entry_frame.grid(padx=10, pady=5)
    Label(place_entry_frame, text=u"地点").grid()
    place_entry = Entry(root)
    place_entry.grid()

    button_frame = Frame(root)
    button_frame.grid(pady=10)
    Button(button_frame, text=u"新增", command=lambda: insert_performance(date_entry.get(), place_entry.get(), records[band_cbx.current()][0])).grid(ipady=5, ipadx=5)

    root.mainloop()
    return


def update_performance(tree, band_number):
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute('SELECT PERFORMANCE_NUMBER, DATE, PLACE FROM PERFORMANCE WHERE BAND_NUMBER = ' +
                   str(band_number))
    performances = cursor.fetchall()
    for performance in performances:
        # 将index索引设置为performance_number
        tree.insert("", int(performance[0]), values=performance)
    return


def delete_performance(tree):
    try:
        performance_number = tree.item(tree.focus())['values'][0]
        performance_date = tree.item(tree.focus())['values'][1]
        performance_place = tree.item(tree.focus())['values'][2]
        err_flag = Controller.delete_performance(cursor, connection, performance_number)
        if err_flag:
            showerror(u"删除失败", u"不存在该演出！")
        else:
            showinfo(u"删除成功", u"成功删除演出：\n" + str(performance_date) + "\n" + str(performance_place))
    except IndexError:
        showerror(u"删除失败", u"请选择演出！")
    return


def call_performance_song_window(tree):
    print(tree.item(tree.focus())['values'])
    try:
        performance_number = tree.item(tree.focus())['values'][0]
        performance_date = tree.item(tree.focus())['values'][1]
        performance_place = tree.item(tree.focus())['values'][2]
        performance_song_window(performance_number, performance_date, performance_place)
    except IndexError:
        showerror(u"查看歌单失败", u"请选择演出！")
    return


def performance_window():

    # 查看演出窗口
    root = Tk()
    root.geometry("+800+400")
    root.title(u"查看演出")

    # select band combobox
    select_band_frame = Frame(root)
    select_band_frame.grid(pady=5)
    Label(select_band_frame, text=u"选择乐队").grid()
    band_cbx = Combobox(select_band_frame, state='readonly')
    # search band
    cursor.execute('SELECT BAND_NUMBER, NAME FROM BAND WHERE BAND_NUMBER IN '
                   '(SELECT BAND_NUMBER FROM MEMBER_BAND WHERE MEMBER_NUMBER = ' + str(member_number) + ')')
    # put into combobox
    records = cursor.fetchall()
    records_name = []
    for record in records:
        records_name.append(str(record[1]))
    band_cbx['value'] = records_name
    band_cbx.current(0)
    band_cbx.grid()

    # tree view
    tree = Treeview(root)
    tree["columns"] = ('PERFORMANCE_NUMBER', 'DATE', 'PLACE')
    tree["show"] = 'headings'
    tree.heading('PERFORMANCE_NUMBER', text=u"演出编号")
    tree.heading('DATE', text=u"演出日期")
    tree.heading('PLACE', text=u"演出地点")

    # button_frame
    button_frame = Frame(root, width=200)
    button_frame.grid(pady=5)
    Button(button_frame, text=u"刷新演出列表",
           command=lambda:
           update_performance(tree, records[band_cbx.current()][0])).grid(padx=5, row=0, column=0)
    Button(button_frame, text=u"查看演出歌单",
           command=lambda: call_performance_song_window(tree)).grid(padx=5, row=0, column=1)
    delete_performance_button = Button(button_frame, text=u"删除演出", command=lambda: delete_performance(tree))

    delete_performance_button['state'] = 'normal'
    delete_performance_button.grid(padx=5, row=0, column=2)

    tree.grid(padx=20, pady=10)

    root.mainloop()
    return


def generate_song_sheet(song_info, song_order_combobox, performance_song_count, band_number, song_sheet_frame):
    # search songs
    band_song_count = cursor.execute('SELECT SONG_NUMBER, NAME FROM SONG WHERE BAND_NUMBER = '
                                     + str(band_number))
    # put into combobox
    song_info.clear()
    for i in range(band_song_count):
        song_info.append(cursor.fetchone())
    # print(song_info)
    song_name_records = []
    for song_record in song_info:
        song_name_records.append(str(song_record[1]))
    for order in range(len(song_order_combobox)):
        song_order_combobox[order].destroy()

    song_order_combobox.clear()

    for order in range(int(performance_song_count)):
        song_order_combobox.append(Combobox(song_sheet_frame))
        song_order_combobox[order]['value'] = song_name_records
        song_order_combobox[order].grid()
    return


def insert_song_into_performance(song_info, song_order_combobox, tree, performance_number):
    print(song_info)
    cursor.execute('DELETE FROM PERFORMANCE_SONG WHERE PERFORMANCE_NUMBER = ' + str(performance_number))
    connection.commit()
    for performance_order in range(0, len(song_order_combobox)):
        cursor.execute(
            "INSERT INTO PERFORMANCE_SONG (PERFORMANCE_NUMBER, SONG_NUMBER, PERFORMANCE_ORDER) VALUES ("
            + str(performance_number) + ", " +
            str(song_info[song_order_combobox[performance_order].current()][0])  # song number
            + ", " + str(performance_order) + ")")
        connection.commit()
    showinfo(u"生成成功", u"生成歌单成功！")
    check_performance_song(tree, performance_number)
    return


def check_performance_song(tree, performance_number):
    cursor.execute(
        'SELECT PERFORMANCE_SONG.PERFORMANCE_ORDER, SONG.NAME '
        'FROM PERFORMANCE_SONG, SONG WHERE '
        'PERFORMANCE_SONG.SONG_NUMBER = SONG.SONG_NUMBER '
        'AND PERFORMANCE_SONG.PERFORMANCE_NUMBER = ' + str(performance_number) +
        ' ORDER BY PERFORMANCE_SONG.PERFORMANCE_ORDER ASC')
    song_performance_records = cursor.fetchall()
    # print(song_performance_records)
    for row in tree.get_children():
        tree.delete(row)
    for song_performance in song_performance_records:
        # 将index索引设置为performance_order
        tree.insert("", int(song_performance[0]), values=song_performance)
    return


# 每个演出的详细歌单
def performance_song_window(performance_number, performance_time, performance_place):

    # band_number必须采用查询，否则很容易导致两者不一致
    cursor.execute("SELECT BAND_NUMBER FROM PERFORMANCE WHERE PERFORMANCE_NUMBER = " +
                   str(performance_number))
    band_number = cursor.fetchall()[0][0]

    root = Tk()
    root.geometry("+800+400")
    root.title(u"演出歌单" + ' ' + str(performance_time) + ' ' + str(performance_place))

    performance_song_count_frame = Frame(root)
    performance_song_count_frame.grid(pady=5)
    Label(performance_song_count_frame, text=u"演出歌曲数目").grid(row=0, column=0)
    performance_song_count_entry = Entry(performance_song_count_frame, width=5)
    # performance_song_window_song_number_entry.insert(END, u"此次演出的歌曲数目")
    performance_song_count_entry.insert(END, "0")
    performance_song_count_entry.grid(row=0, column=1)

    check_performance_song_tree = Treeview(root)
    check_performance_song_tree["columns"] = ('PERFORMANCE_ORDER', 'NAME')
    check_performance_song_tree["show"] = 'headings'
    check_performance_song_tree.heading('PERFORMANCE_ORDER', text=u"演出顺序")
    check_performance_song_tree.heading('NAME', text=u"歌曲名称")

    song_order_combobox = []  # 生成表单后，存放歌曲的顺序
    song_records = []

    performance_song_window_button_frame = Frame(root)
    performance_song_window_button_frame.grid(pady=5)
    Button(performance_song_window_button_frame, text=u"生成插入表单",
           command=lambda:
           generate_song_sheet(
               song_records, song_order_combobox, performance_song_count_entry.get(), band_number, song_sheet_frame
           )).grid(row=0, column=0, padx=5)
    Button(performance_song_window_button_frame, text=u"生成歌单",
           command=lambda: insert_song_into_performance(
               song_records, song_order_combobox, check_performance_song_tree, performance_number
           )).grid(row=0, column=1, padx=5)
    Button(performance_song_window_button_frame, text=u"刷新演出歌单",
           command=lambda: check_performance_song(
               check_performance_song_tree, performance_number)).grid(row=0, column=2, padx=5)

    song_sheet_frame = Frame(root)
    song_sheet_frame.grid(pady=5)
    generate_song_sheet(song_records, song_order_combobox,
                        performance_song_count_entry.get(), band_number, song_sheet_frame)

    check_performance_song_tree.grid(pady=10, padx=10)

    root.mainloop()
    return


if __name__ == "__main__":
    start_gui()
