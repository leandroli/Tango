import requests
import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import Canvas
from tkinter import Frame
from tkinter import Scrollbar
from tkinter import messagebox as msg
import csv
from TangoClient.user import User
from TangoClient.logger import Logger


class Tango(object):
    def __init__(self):
        """
        Set basic configuration of the client server
        """
        self.word_pool_path = '../Resource/word_pool/'
        self._mline = str
        self._mlist = list()
        self.filename = str
        self._recite_file = list()
        self._wptr = 0
        self._wptr_end = 0
        self._n_step1 = int()
        self._n_mark = 0
        self._n_step2 = list()
        self._user = User()
        self.logger = Logger("../Resource/TangoLogger.log")
        self._logged = False
        self.server_addr = 'localhost:7000'

    def initUI(self):
        """
        Set initialization interface.
        """
        root = tk.Tk()
        root.geometry("+620+300")
        root.title('Tango')
        root.resizable(0, 0)

        tabControl = ttk.Notebook(root)

        # create a Frame named tab1
        tab1 = ttk.Frame(tabControl)
        # add a tab showing "log in"
        tabControl.add(tab1, text='log in')

        # Add a second tab named tab2
        tab2 = ttk.Frame(tabControl)
        # add the second tab showing "register"
        tabControl.add(tab2, text='register')

        # Pack to make visible
        tabControl.pack(expand=1, fill="both")

        self.__log_in(tab1, root)
        self.__register(tab2, root)

        # MainLoop
        root.mainloop()

    def open_wrong_window(self, reason):
        """
        Display error information which included in the function argument "reason"
        when the user cannot log in.
        """
        # create a window with the title of 'Tango--Log in Failed.'
        # win = tk.Tk()
        # win.geometry('+600+320')
        # win.title('Tango--ERROR.')
        # win.resizable(0, 0)
        #
        # frame = ttk.LabelFrame(win, text='*** Wrong ***')
        # frame.grid(column=0, row=0, padx=20, pady=10, sticky='S')
        text = ''

        # Display the error of duplicate entries, and log it in the log file
        if reason == 'The user has logged in.':
            text = 'You are online now!'
            log_message = str(self._user.username) + " duplicate entries"
            self.logger.error(log_message)

        # Display the error of Duplicate registration, and log it in the log file
        elif reason == 'The user name is existed.':
            text = 'The user name has been registered. Please change another one.'
            log_message = str(self._user.username) + " re-register"
            self.logger.error(log_message)

        # Display the error of connection, and log it in the log file
        elif reason == 'Connection Error.':
            text = 'Cannot connect server. Please check your connection.'
            log_message = "Cannot connect server"
            self.logger.error(log_message)

        # Display error window, the file user try to open is empty
        elif reason == 'Fail to open file.':
            text = 'Format of the file you want to open is wrong, please use others.'
            self.logger.error('Try to open a empty file.')

        # Display the error of wrong username or password, and log it in the log file
        elif reason == 'The user is not exists.':
            text = 'Username or Password is wrong.\n\nIf you don\'t have an account, please register first.'
            log_message = str(self._user.username) + " enter a wrong password:" + str(self._user.password)
            self.logger.war(log_message)

        # message = ttk.Label(frame, text=text)
        # message.grid(column=0, row=0, padx=10, pady=5)
        #
        # # the function to close this window
        # def click():
        #     win.destroy()
        #
        # # the action to Try again
        # action = ttk.Button(win, text='Try Again', command=click)
        # action.grid(column=0, row=1, padx=20, pady=10, sticky='E')
        # win.mainloop()
        msg.showerror('Tango-ERROR', text)
        return

    def send_request(self, father, request):
        """
        Send request to server to try to log in or register
        """
        if request == 'log_in':
            try:
                # Use Post request to log in
                user_info = json.dumps(eval(str(self._user)))
                r1 = requests.post('http://' + self.server_addr + '/login', data=user_info)
            except Exception as err:
                self.logger.error(str(err))
                self.open_wrong_window('Connection Error.')
            else:
                if r1.text == 'Successfully log in.':
                    self._logged = True
                    father.destroy()
                    self.start()
                else:
                    self.open_wrong_window(r1.text)

        elif request == 'register':
            try:
                # Use Post request to log in
                r2 = requests.post('http://' + self.server_addr + '/register', data=json.dumps(eval(str(self._user))))
            except Exception as err:
                self.logger.error(str(err))
                self.open_wrong_window('Connection Error.')

            else:
                # display the result of register successfully
                if r2.text == 'Successfully registered.':
                    temp_win = tk.Tk()
                    temp_win.geometry('+600+320')
                    temp_win.title('Congratulation!')
                    temp_win.resizable(0, 0)
                    message = ttk.Label(temp_win, text='Successfully Registered!')
                    message.grid(column=0, row=0, padx=10, pady=5)

                    # the function to close the window
                    def click():
                        temp_win.destroy()

                    # the button to go back to the window of log in
                    ttk.Button(temp_win, text='Go to Log in!', command=click).grid(
                        column=1, row=1, padx=20, pady=10, sticky='E')

                    temp_win.mainloop()

                # open the error window to display the wrong of this register
                else:
                    self.open_wrong_window(r2.text)

        elif request == 'log_out':
            try:
                # Use Post request to log in
                requests.post('http://' + self.server_addr + '/log_out', data=json.dumps(eval(str(self._user))))
            except Exception as err:
                self.logger.error(str(err))

    def __click_log_in(self, father, username, password):
        """
        Handle the login process.

        If user click the button of "log in",
        this function call another function send_request()
        with the request = "log_in"
        """
        # Change text on the button to "Logging in..."
        log_message = str(username.get()) + " tries to log in"
        self.logger.info(log_message)

        self._user.username = username.get()
        self._user.password = password.get()
        self.send_request(father, 'log_in')

    def __log_in(self, table, root):

        mighty = ttk.LabelFrame(table, text=' Tango Log in ')
        mighty.grid(column=0, row=0, padx=20, pady=10)

        # Adding a Label: username
        label1 = ttk.Label(mighty, text="username:")
        label1.grid(column=0, row=0, padx=8, pady=4, sticky='W')

        # Adding a Label: password
        label2 = ttk.Label(mighty, text="password:")
        label2.grid(column=0, row=2, padx=8, pady=4, sticky='W')

        # Adding a Username Entry widget
        username = tk.StringVar()
        name_entered = ttk.Entry(mighty, width=15, textvariable=username)
        name_entered.grid(column=1, row=0, padx=8, pady=4, sticky='W')

        # Adding a Password Entry widget
        password = tk.StringVar()
        password_entered = ttk.Entry(mighty, width=15, textvariable=password, show='*')
        password_entered.grid(column=1, row=2, padx=8, pady=4, sticky='W')

        # Adding a Button
        button_log_in = ttk.Button(
            mighty, text="Log in", command=lambda: self.__click_log_in(root, username, password))
        button_log_in.grid(column=1, row=3, padx=4, pady=4, sticky='E')

        def click_exit():
            root.destroy()

        # Adding a Exit Button
        button_exit = ttk.Button(mighty, text="Exit", command=click_exit)
        button_exit.grid(column=0, row=3, padx=4, pady=4, sticky='W')

    def __click_register(self, father, action, username, password):
        """
        Handle the register process.

        If user click the button of "register",
        this function call another function send_request()
        with the request = "register"
        """
        # log
        log_message = "Try to register a new user: " + str(username.get())
        self.logger.info(log_message)
        # Change text on the button to "Registering"
        action.configure(text='Register')

        self._user.username = username.get()
        self._user.password = password.get()
        self.logger.info("Try to register with password:" + str(self._user.password))
        self.send_request(father, 'register')

    def __register(self, table, root):
        frame = ttk.LabelFrame(table, text=' Tango Register ')
        frame.grid(column=0, row=0, padx=20, pady=10)

        # Adding a Label: username
        label1 = ttk.Label(frame, text="username:")
        label1.grid(column=0, row=0, padx=8, pady=4, sticky='W')

        # Adding a Label: password
        label2 = ttk.Label(frame, text="password:")
        label2.grid(column=0, row=2, padx=8, pady=4, sticky='W')

        # Adding a Label: password
        label3 = ttk.Label(frame, text="enter again:")
        label3.grid(column=0, row=4, padx=8, pady=4, sticky='W')

        # Adding a Username Entry widget
        username = tk.StringVar()
        name_entered = ttk.Entry(frame, width=15, textvariable=username)
        name_entered.grid(column=1, row=0, padx=8, pady=4, sticky='W')  # align left/West

        # Adding a Password Entry widget
        password = tk.StringVar()
        password_entered = ttk.Entry(frame, width=15, textvariable=password, show='*')
        password_entered.grid(column=1, row=2, padx=8, pady=4, sticky='W')  # align left/West

        # Adding a Password Entry widget
        password_c = tk.StringVar()
        password_c_entered = ttk.Entry(frame, width=15, textvariable=password_c, show='*')
        password_c_entered.grid(column=1, row=4, padx=8, pady=4, sticky='W')  # align left/West

        # Adding a Button
        button_log_in = ttk.Button(
            frame, text="Register", command=lambda: self.__click_register(root, button_log_in, username, password))
        button_log_in.grid(column=1, row=5, padx=4, pady=4, sticky='E')

        def click_exit():
            root.destroy()

        # Adding a Exit Button
        button_exit = ttk.Button(frame, text="Exit", command=click_exit)
        button_exit.grid(column=0, row=5, padx=4, pady=4, sticky='W')

    def __get_num(self):
        self.step1_count = 0
        # get the number of step1
        for row in self._recite_file:
            if int(row[5]) > self.step1_count:
                self.step1_count += 1
        # get the number of words that in every step1
        self.step2_array = [0] * self.step1_count
        i_step1 = 1
        for row in self._recite_file:
            if int(row[5]) > i_step1:
                i_step1 += 1
            self.step2_array[i_step1 - 1] += 1

    def __write_new_line(self, user_file_name, choice_str):
        self.__get_num()
        umfile = open(user_file_name, "a+")
        umfile.write(choice_str + "\n")
        new_line_str = "0" * len(self._recite_file)
        new_line_str += "\n"
        umfile.write(new_line_str)
        umfile.close()
        return new_line_str

    def __read_user_file(self, choice_str):
        inflag = 0
        user_file_name = "../Resource/data/" + self._user.username + ".tangomemory"
        umfile = open(user_file_name, 'a+')
        umfile.seek(0, 0)
        for line in umfile.readlines():
            if inflag == 1:
                memory_line = line
                umfile.close()
                return memory_line
            if line == choice_str + "\n":
                inflag = 1
        if inflag == 0:
            umfile.close()
            memory_line = self.__write_new_line(user_file_name, choice_str)
            umfile.close()
            return memory_line

    def display_tips(self):
        self._wptr = self._wptr_end - self.step2_array[self._n_step1]
        tips_win = tk.Tk()
        tips_win.geometry('+600+320')
        tips_win.title('Tango--Tips')
        tips_win.resizable(0, 0)
        frame = ttk.LabelFrame(tips_win, text='*** ATTENTION ***')
        frame.grid(column=0, row=0, padx=20, pady=10, sticky='S')
        text = "您所选择的单词已经记忆过一遍了。\n您可以点击查看其它单词类别，\n或者点击“下一个”从头查看此类别单词。"
        message = ttk.Label(frame, text=text)
        message.grid(column=0, row=0, padx=10, pady=5)

        def click():
            tips_win.destroy()

        action = ttk.Button(tips_win, text='我知道了', command=click)
        action.grid(column=0, row=1, padx=20, pady=10, sticky='E')
        tips_win.mainloop()

    def recite_window(self, choice_str):
        """
        The window to display the words that user has chosen,
        and record the user's rate of reciting.
        """
        self._wptr = 0

        def read_recite_file(choice_str):
            # input file that the user has chosen to self.recite_file
            self._recite_file.clear()
            file_name_str = self.word_pool_path + choice_str
            with open(file_name_str, 'r', encoding='utf-8', newline='') as file:
                if file.read(1) == '':
                    return False
                else:
                    file.seek(0)
                file_ptr = csv.reader(file)
                for row in file_ptr:
                    self._recite_file.append(row)
            try:
                self.__get_num()
            except Exception:
                self.logger.error('wrong word file format.')
                return False
            # add the column to the recite_file
            self._mline = self.__read_user_file(choice_str)
            self._mlist = []
            for j in range(0, len(self._recite_file)):
                self._mlist.append(self._mline[j])
            return True

        if not read_recite_file(choice_str):  # 读入选择的单词文件
            self.open_wrong_window(reason='Fail to open file.')
            return

        win = tk.Tk()
        win.geometry("+600+250")
        win.title('Tango')
        win.resizable(0, 0)
        # set a combobox to choose level
        frame = Frame(win)
        frame.pack()
        label_choose_level = ttk.Label(frame, text='单词等级')
        label_choose_level.grid(column=1, row=1, padx=8, pady=4)
        level_num = tk.StringVar()
        step1_array = []
        for i in range(0, self.step1_count):
            step1_array.append(str(i))
        combo_choose_level = ttk.Combobox(frame, width=9, textvariable=level_num, state='readonly')
        combo_choose_level['values'] = step1_array
        combo_choose_level.grid(column=2, row=1)

        # set a combobox to choose memory mark
        label_choose_mark = ttk.Label(frame, text='熟悉程度')
        label_choose_mark.grid(column=3, row=1, padx=8, pady=4)
        mark_str = tk.StringVar
        combo_choose_mark = ttk.Combobox(frame, width=9, textvariable=mark_str, state='readonly')
        combo_choose_mark['values'] = ["认识", '陌生', '所有']
        combo_choose_mark.grid(column=4, row=1)

        # display the word
        def display_word():
            can.delete("word", "meaning")
            text1 = self._recite_file[self._wptr][0]
            can.create_text(200, 100, text=text1, fill='white', tags="word", font=('MS Serif', 20))

        def init_display_word():
            self._wptr_end = len(self._recite_file)
            display_word()

        # set a canvas to display the word and its meaning

        # set a canvas
        frame3 = Frame(win)
        frame3.pack()
        can = Canvas(frame3, width=400, height=300, bg='#000000', yscrollincrement=1, scrollregion=(0, 0, 500, 500))
        hbar = Scrollbar(frame3, orient='horizontal')
        hbar.pack(side='bottom', fill='x')
        hbar.config(command=can.xview)
        vbar = Scrollbar(frame3, orient='vertical')
        vbar.pack(side='right', fill='y')
        vbar.config(command=can.yview)
        can.config(width=400, height=300)
        can.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        can.pack(side='left', expand=True, fill='both')
        init_display_word()

        # display the meaning
        def display_meaning():
            can.create_text(200, 150, text=self._recite_file[self._wptr][1],
                            fill='white', tags="meaning", font=('Courier New', 10))
            can.create_text(200, 200, text=self._recite_file[self._wptr][3],
                            fill='white', tags="meaning", font=('MS Serif', 10))
            can.create_text(200, 250, text=self._recite_file[self._wptr][4],
                            fill='white', tags="meaning", font=('Times New Roman', 10))

        # hide the meaning
        def hide_meaning():
            can.delete("meaning")

        # display the next word
        def next_word():
            flag = 0
            mark_str = str(self._n_mark)
            if self._n_mark == -1:
                if self._wptr < self._wptr_end:
                    self._wptr += 1
                    flag = 1
                else:
                    self.display_tips()
            else:
                self._wptr += 1
                while self._wptr < self._wptr_end and self._mlist[self._wptr] != mark_str:
                    self._wptr += 1
                if self._wptr < self._wptr_end:
                    flag = 1
                elif self._wptr >= self._wptr_end:
                    self._wptr = self._wptr_end - self.step2_array[self._n_step1]
                    while self._wptr < self._wptr_end and self._mlist[self._wptr] != mark_str:
                        self._wptr += 1
                    if self._wptr < self._wptr_end:
                        flag = 1
                    elif self._wptr >= self._wptr_end:
                        can.delete("word", "meaning")
                        mark_dic = {1: "认识", 0: "陌生", -1: "所有"}
                        textstr = "这一级已经没有" + mark_dic[self._n_mark] + "的单词了"
                        can.create_text(200, 150, text=textstr,
                                        fill='white', tags="meaning")
            if flag == 1:
                display_word()

        # read the word that user has chosen from the list:'recite_file'
        def choose_level():
            # get the level and mark that the user has chosen
            flag = 0
            level = combo_choose_level.get()
            mark = combo_choose_mark.get()
            mark_dic = {"认识": 1, "陌生": 0, "所有": -1}
            self._n_step1 = int(level)
            self._n_mark = mark_dic[mark]

            self._wptr = 0
            self._wptr_end = 0
            for j in range(0, self._n_step1):
                self._wptr += self.step2_array[j]
                self._wptr_end += self.step2_array[j]
            self._wptr_end = self._wptr_end + self.step2_array[self._n_step1] - 1

            if self._n_mark == -1:
                flag = 1
            else:
                while self._wptr < self._wptr_end:
                    if self._mlist[self._wptr] == str(self._n_mark):
                        flag = 1
                        break
                    self._wptr += 1
                if self._wptr >= self._wptr_end:
                    if self._n_mark == 1:
                        can.delete("word", "meaning")
                        text_str = "该等级没有已经认识的单词",
                        can.create_text(200, 150, text=text_str, fill='white', tags="meaning")
                    elif self._n_mark == 0:
                        can.delete("word", "meaning")
                        text_str = "该等级没有陌生的单词",
                        can.create_text(200, 150, text=text_str, fill='white', tags="meaning")
            if flag == 1:
                display_word()

        def not_remembered():
            self._mlist[self._wptr] = "0"

        def remembered():
            self._mlist[self._wptr] = '1'

        # set a button to sure the choice
        button_sure = ttk.Button(frame, text='确定', command=choose_level)
        button_sure.grid(column=6, row=1, padx=8, pady=4)

        frame2 = Frame(win)
        frame2.pack()

        # set a button to show the meaning of the word
        button_show = ttk.Button(frame2, text='显示释义', command=display_meaning)
        button_show.grid(column=4, row=7, padx=8, pady=4)

        # set a button to hide the meaning of the word
        button_hide = ttk.Button(frame2, text='隐藏释义', command=hide_meaning)
        button_hide.grid(column=2, row=7, padx=8, pady=4)

        # set a button to mark the word:be remembered
        button_remembered = ttk.Button(frame2, text='记住了', command=remembered)
        button_remembered.grid(column=2, row=8, padx=8, pady=4)

        # set a button to display next word of the word
        button_next = ttk.Button(frame2, text='下一个', command=next_word)
        button_next.grid(column=3, row=8, padx=8, pady=4)

        # set a button to mark the word:be not remembered
        button_notremembered = ttk.Button(frame2, text='没记住', command=not_remembered)
        button_notremembered.grid(column=4, row=8, padx=8, pady=4)

        self.filename = choice_str

        def save_and_quit():

            user_file_name = "../Resource/data/" + self._user.username + ".tangomemory"
            new_line = ""
            for j in range(0, len(self._mlist)):
                new_line += self._mlist[j]
            change_file = open(user_file_name, "a+")
            flag = 0
            new_file = []
            change_file.seek(0, 0)
            for line in change_file:
                if line == self.filename + "\n":
                    flag = 1
                    new_file.append(line)
                    continue
                if flag == 1:
                    flag = 0
                    new_file.append(new_line)
                else:
                    new_file.append(line)
            change_file.close()
            change_file = open(user_file_name, "w+")
            for line in new_file:
                change_file.write(line)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", save_and_quit)
        win.mainloop()

    def message_board(self):
        """
        Set the layout of the information window
        """
        msg_win = tk.Tk()
        msg_win.geometry('+610+100')
        msg_win.title('Tango--message board')
        msg_win.resizable(0, 0)

        tip3 = tk.Label(msg_win,
                        text='Here is message board.\nYou can send your message to all users!\nHave a good time!',
                        anchor='w', font=('Courier New', 10), justify='left')
        tip3.grid(padx=20, pady=10)

        scrol_w = 30
        scrol_h = 15
        scrol = scrolledtext.ScrolledText(msg_win, width=scrol_w, height=scrol_h, wrap=tk.WORD,
                                          font=('Courier New', 10))
        scrol.grid(column=0, row=1, sticky='WE', padx=8, pady=4, columnspan=2)

        scrol_w2 = 30
        scrol_h2 = 5
        scrol2 = scrolledtext.ScrolledText(msg_win, width=scrol_w2, height=scrol_h2, wrap=tk.WORD,
                                           font=('Courier New', 10))
        scrol2.grid(column=0, row=2, sticky='WE', padx=8, pady=4, columnspan=2)

        def get_message():
            # get message from the server and print it in the chat box
            r3 = requests.get('http://' + self.server_addr + '/script=get_msg')
            scrol.delete('1.0', tk.END)
            scrol.insert(tk.INSERT, str(r3.text))

        def send_message_to_server():
            # send message to the server and print it in the chat box
            message = scrol2.get("1.0", "end-1c")
            data = json.dumps({'username': self._user.username, 'msg': message})
            requests.post('http://' + self.server_addr + '/send_msg', data=data)
            get_message()

        send_button = ttk.Button(msg_win, text='Send!', command=send_message_to_server)
        send_button.grid(row=3, column=1, padx=8, pady=4, sticky='E')

        get_message()
        send_button = ttk.Button(msg_win, text='Refresh', command=get_message)
        send_button.grid(row=3, column=0, padx=8, pady=4, sticky='W')

        # =============
        # mainloop
        # =============
        msg_win.mainloop()

    def start(self):
        """
        Choose a word loop and download some new here.
        """
        start_window = tk.Tk()
        start_window.geometry('+610+280')
        start_window.title('Tango--start')
        start_window.resizable(0, 0)

        menu_bar = Menu(start_window)
        start_window.config(menu=menu_bar)

        def _quit():
            start_window.quit()
            start_window.destroy()
            log_message = str(self._user.username) + " exit"
            self.logger.info(log_message)
            self.send_request(start_window, 'log_out')
            exit()

        # Add menu items
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=_quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Display a Message Box
        def _msg_box():
            msg.showinfo('Tango version 1.0', 'A funny application for reciting words\nDeveloped by Li')

        tool_menu = Menu(menu_bar, tearoff=0)
        tool_menu.add_command(label='Message Board', command=self.message_board)
        menu_bar.add_cascade(label="Tool", menu=tool_menu)

        # Add another Menu to the Menu Bar and an item
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=_msg_box)  # display message box when clicked
        menu_bar.add_cascade(label="Help", menu=help_menu)

        tabControl = ttk.Notebook(start_window)

        tab1 = ttk.Frame(tabControl)  # Create a tab
        tabControl.add(tab1, text='start')  # Add the tab
        tab2 = ttk.Frame(tabControl)  # Add a second tab
        tabControl.add(tab2, text='download')  # Make second tab visible

        tabControl.pack(expand=1, fill="both")  # Pack to make visible

        # ==============
        # tab1: start
        # ==============
        hello = ttk.Label(tab1, text='Hello ' + self._user.username + '!!!', font=('Courier New', 10))
        hello.grid(column=0, row=0, padx=10, pady=8, sticky='W')

        tip = ttk.Label(tab1, text='Please choose word pool which fit you:')
        tip.grid(column=0, row=1, padx=8, pady=4)

        word_pool = tk.StringVar()
        choice = ttk.Combobox(tab1, width=12, textvariable=word_pool, state='readonly')
        choice['values'] = os.listdir(self.word_pool_path)
        choice.grid(column=0, row=2, padx=8, pady=4)
        choice.current(0)
        button = ttk.Button(tab1, text='Start', command=lambda: self.recite_window(choice.get()))
        button.grid(column=1, row=2, padx=8, pady=4)

        # ==============
        # tab2: download
        # ==============
        tip2 = ttk.Label(tab2, text='Please choose word pool which fit you,\n\tdownload will start quickly:',
                         anchor='w', justify='left')
        tip2.grid(column=0, row=1, padx=8, pady=4)

        def get_server_word_list():
            r = requests.get('http://' + self.server_addr + '/script=word_pool_list')
            word_pool_list_new = eval(r.text)
            choice2['values'] = word_pool_list_new
            choice2.current(0)

        button2 = ttk.Button(tab2, text='Refresh', command=get_server_word_list)
        button2.grid(column=1, row=1, padx=8, pady=4)

        word_pool_list = ['']
        choice2 = ttk.Combobox(tab2, width=12, state='readonly')
        choice2['values'] = word_pool_list
        choice2.grid(column=0, row=2, padx=8, pady=4)
        choice2.current(0)

        def download_word_pool():
            r = requests.get('http://' + self.server_addr + '/getcsv=' + choice2.get())
            try:
                word_pool_file = open(self.word_pool_path + choice2.get(), 'wb')
            except Exception as err:
                self.logger.error(str(err))
            else:
                word_pool_file.write(r.content)
                self.logger.info('Successfully download' + choice2.get())
                word_pool_file.close()
            choice['values'] = os.listdir(self.word_pool_path)
            msg.showinfo('Tango--Download Finished.', 'Download Finished.')
            choice.current(0)

        button3 = ttk.Button(tab2, text='Download', command=download_word_pool)
        button3.grid(column=1, row=2, padx=8, pady=4)

        start_window.protocol("WM_DELETE_WINDOW", _quit)
        # ==============
        # mainloop
        # ==============
        start_window.mainloop()


if __name__ == '__main__':
    Tango().initUI()
