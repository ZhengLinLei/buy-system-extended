#!/usr/bin/env python3


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

from datetime import datetime
from shutil import copy


import sqlite3, json, os


# PLUGIN
from plugin.printerConn.script import *
from plugin.receiptMaker.script import ReceiptMaker

# pyinstaller --icon=./dataico.ico --noconsole --add-data './readme.txt;.' --add-data './data/delete.log;data' --add-data './data/ico.ico;data' index.py

DB_PATHNAME = './data/database.db'
BACKUP_PATHNAME = './backup'
TMP_PATHNAME = './tmp'


#SQLITE SQL REQUEST
def run_sqlite_query(query, parameters = ()):
    global DB_PATHNAME

    with sqlite3.connect(DB_PATHNAME) as conection:
        place = conection.cursor()
        response = place.execute(query, parameters)
        conection.commit()

    if "SELECT " in query and query[0] == 'S':
        return response.fetchall()

    return True
def prepare_database():
    querys = [''' CREATE TABLE 'Product_data' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `code` TEXT NOT NULL,
                        `name` TEXT NOT NULL,
                        `price` REAL NOT NULL
                    );''',
                ''' CREATE TABLE 'Product_register_pay' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `date_time` DATETIME NOT NULL,
                        `data` TEXT NOT NULL,
                        `total_price` REAL NOT NULL,
                        `number_product` INTEGER NOT NULL,
                        `method_pay` TEXT NOT NULL
                    );''',
                '''CREATE TABLE 'Product_deletedRegister_pay' (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        `date_time` DATETIME NOT NULL,
                        `data` TEXT NOT NULL,
                        `total_price` REAL NOT NULL,
                        `number_product` INTEGER NOT NULL,
                        `method_pay` TEXT NOT NULL
                    );''']
        
    for query in querys:
        run_sqlite_query(query)

def isFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

#start root window
class AppOpen:
    second_windowOpen = root_window_fullScreen = False
    totalPrice_arr_toPay = {}

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('算账页面')
        
        # self.root_window.tk.call('wm', 'iconphoto', self.root_window._w, tk.PhotoImage(file='./data/ico.jpg'))
        
        # self.root_window.iconphoto(True, tk.PhotoImage(file='./data/ico.ico'))
        
        # self.root_window.iconbitmap('@./data/ico.ico')

        self.root_window.iconbitmap('./data/ico.ico')


        self.root_window.bind("<F11>", lambda event: self.toggle_fullScreen())
        self.root_window.bind("<f>", lambda event: self.toggle_fullScreen())
        self.root_window.bind("<Control-e>", lambda event: self.root_window.destroy())

        
        self.root_window.focus_force()
        #More option Buttons
        addProduct_open_window = tk.Button(self.root_window, text = '添加', padx = 20, cursor = 'hand2', command = lambda : self.open_newWindowConfig('add'))
        addProduct_open_window.grid(row = 0, column = 0) #Add products
        #FastKey
        self.root_window.bind("<Control-t>", lambda event: self.open_newWindowConfig('add'))
        CreateToolTip(addProduct_open_window, text = '打开添加新物品页面。可用Ctrl+t键，快开启')

        changeProduct_open_window = tk.Button(self.root_window, text = '更改', padx = 20, cursor = 'hand2', command = lambda : self.open_newWindowConfig('change'))
        changeProduct_open_window.grid(row = 0, column = 1) #Modify and delete product
        #FastKey
        self.root_window.bind("<Control-k>", lambda event: self.open_newWindowConfig('change'))
        CreateToolTip(changeProduct_open_window, text = '更改和查看物品。可用Ctrl+k键，快开启')

        self.root_window_fullScreenButton = tk.Button(self.root_window, text= '页面变大',padx = 20, cursor = 'hand2', command = self.toggle_fullScreen)
        self.root_window_fullScreenButton.grid(row = 0, column = 2, padx = (20, 0)) #Full Screen

        helpProduct_open_window = tk.Button(self.root_window, text = '帮助', padx = 20, cursor = 'hand2', command = lambda : self.open_newWindowConfig('help'))
        helpProduct_open_window.grid(row = 0, column = 3, padx = (0, 20)) #Help 
        #FastKey
        self.root_window.bind("<Control-h>", lambda event: self.open_newWindowConfig('help'))
        CreateToolTip(helpProduct_open_window, text = '帮助页面。可用Ctrl+h键，快开启')

        autoRepair_button = tk.Button(self.root_window, text = '自修', padx = 20, cursor = 'hand2', command = self.auto_repair)
        autoRepair_button.grid(row = 0, column = 4, padx = 15) #Auto repair

        history_button = tk.Button(self.root_window, text = '查看销售记录', padx = 20, cursor = 'hand2', command = lambda : self.open_newWindowConfig('history'))
        history_button.grid(row = 0, column = 5, padx = 15) #Sended history
        #FastKey
        self.root_window.bind("<Control-j>", lambda event: self.open_newWindowConfig('history'))
        CreateToolTip(history_button, text = '此页面可查看所有卖出去的客人记录。快速键 Ctrl+j， 可快速打开')
        
        backup_button = tk.Button(self.root_window, text = '备份', padx = 20, cursor = 'hand2', command = lambda : self.copy_db())
        backup_button.grid(row = 0, column = 6, padx = 25) #Sended history
        #FastKey
        self.root_window.bind("<Control-b>", lambda event: self.copy_db())
        CreateToolTip(backup_button, text = '备份数据库。快速键 Ctrl+b， 可快速打开')
        
        #FullScreen Button ToolTips
        CreateToolTip(self.root_window_fullScreenButton, text = '按F11或者F可变大/小')
        #Autorepair Button ToolTips
        #FastKey
        self.root_window.bind("<F8>", lambda event: print(event))
        CreateToolTip(autoRepair_button, text = '系统出问题或卡住，请按可自动修复。 如系统/软件继续出现故障，请按帮助。按住F8可快速修复')

        #LabelFrame to write code and click button
        self.root_window_firstLabelFrame = tk.LabelFrame(self.root_window, text = '输入条码', padx = 20, pady = 20)
        self.root_window_firstLabelFrame.grid(row = 2, column = 0, pady = 30, columnspan = 4)

        #LabelFrame > input
        self.root_window_firstLabelFrame_code = tk.Entry(self.root_window_firstLabelFrame, width = 30)
        self.root_window_firstLabelFrame_code.grid(row = 0, column = 0)
        self.root_window_firstLabelFrame_code.focus()

        #LabelFrame > button
        add_productsFase1Button = tk.Button(self.root_window_firstLabelFrame, text = '加入', command = lambda : self.open_newWindowConfig('amount_product'))
        add_productsFase1Button.grid(row = 1, column = 0, sticky = tk.W + tk.E, pady = (10, 0))

        self.root_window.bind("<Return>", lambda event: self.open_newWindowConfig('amount_product'))
        CreateToolTip(add_productsFase1Button, text = '扫完码请加入到购物廊, 按Enter键可快速加入 <回车键>')

        #Table Div Frame
        root_window_tableProductsFrame = tk.Frame(self.root_window)
        root_window_tableProductsFrame.grid(row = 3, column = 0, columnspan = 150, sticky = tk.W+tk.E)
        #Table 
        self.root_window_tableProducts = ttk.Treeview(root_window_tableProductsFrame, columns = ("name", "price", "amount", "total"), selectmode = tk.EXTENDED, height = 23)

        self.root_window_tableProducts.heading('#0', text = '条码', anchor = tk.CENTER)
        self.root_window_tableProducts.column("#0", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('name', text = '产品', anchor = tk.CENTER)
        self.root_window_tableProducts.column("name", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('price', text = '价格', anchor = tk.CENTER)
        self.root_window_tableProducts.column("price", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('amount', text = '数量', anchor = tk.CENTER)
        self.root_window_tableProducts.column("amount", width = int(self.root_window.winfo_screenwidth()/5), stretch = False)
        self.root_window_tableProducts.heading('total', text = '总价', anchor = tk.CENTER)
        self.root_window_tableProducts.column("total", width = int(self.root_window.winfo_screenwidth()/5)-25, stretch = False)

        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        self.root_window_tableProducts.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)

        #SCROLL
        root_window_tableProductsScroll = tk.Scrollbar(root_window_tableProductsFrame, orient = tk.VERTICAL, command = self.root_window_tableProducts.yview)
        root_window_tableProductsScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.root_window_tableProducts.configure(yscrollcommand = root_window_tableProductsScroll.set)

        #NEW window DELETE AND CHANGE AMOUNT BUTTONS
        newWindow_to_open = tk.Button(self.root_window, text = '新页面', cursor = 'hand2', command = lambda : newAPP())
        newWindow_to_open.grid(row = 4, column = 0, pady = (10, 0), sticky = tk.W + tk.E)
        #FastKey
        self.root_window.bind("<Control-n>", lambda event: newAPP())
        CreateToolTip(newWindow_to_open, text = '新的顾客新页面。可用Ctrl+n键，快开启')


        # Free price
        freePrice = tk.Button(self.root_window, text = '自由价格', cursor = 'hand2', command = lambda : self.freeProduct())
        freePrice.grid(row = 4, column = 1, pady = (10, 0), sticky = tk.W + tk.E)
        #FastKey
        self.root_window.bind("<Control-l>", lambda event: self.freeProduct())
        CreateToolTip(freePrice, text = '输入自由价格。可用Ctrl+l键，快开启')

        root_window_tableProductsDelete = tk.Button(self.root_window, text = '删除', padx = 40, cursor = 'hand2', command = self.removeProduct_addToPay)
        root_window_tableProductsDelete.grid(row = 4, column = 8, pady = (10, 0))
        #FastKey
        self.root_window.bind("<Delete>", lambda event: self.removeProduct_addToPay())
        CreateToolTip(root_window_tableProductsDelete, text = '可用Delete键，快速删除')
        
        root_window_tableProductsChange = tk.Button(self.root_window, text = '更改数量', padx = 40, cursor = 'hand2', command = lambda : self.to_open_amountTable_number())
        root_window_tableProductsChange.grid(row = 4, column = 9, pady = (10, 0))
        #FastKey
        self.root_window.bind("<F10>", lambda event: self.to_open_amountTable_number())
        CreateToolTip(root_window_tableProductsChange, text = '可用F10键，快速更改')

        #Total Price
        root_window_priceFrame = tk.Frame(self.root_window, bg = "#fff", borderwidth = 3, relief= tk.RAISED)
        root_window_priceFrame.grid(row = 2, column = 7, sticky = tk.W + tk.E, pady = 20)

        tk.Label(root_window_priceFrame, text ="总共: ", bg = '#fff', anchor = tk.W, font = ("", 20, "bold")).grid(row = 0, column = 0, sticky = tk.N + tk.S, padx = 15, pady = 20)
        self.root_window_totalPrice = tk.Label(root_window_priceFrame, text ="0.00", bg = '#fff', anchor = tk.E, font = ("", 20))
        self.root_window_totalPrice.grid(row = 0, column = 1, sticky = tk.N + tk.S, padx = 15, pady = 20)
        #Pay
        root_window_payButton = tk.Button(root_window_priceFrame, text = '算账', padx = 30, cursor = 'hand2', font = ("", 14), command = self.allProduct_payAllPrice)
        root_window_payButton.grid(row = 0, column = 4, sticky = tk.W + tk.E + tk.N + tk.S, pady = (0, 1))
        #FastKey
        self.root_window.bind("<F12>", lambda event: self.allProduct_payAllPrice())
        CreateToolTip(root_window_payButton, text = '可用F12键，快速结账')

    def copy_db(self):
        copy(DB_PATHNAME, f"{BACKUP_PATHNAME}/{datetime.today().strftime('%Y-%m-%d')}.db")
        messagebox.showinfo('备份', '备份完毕')

    def open_newWindowConfig(self, type, amounttype = False):
        open_trueWindowAcceptParameter = ('add', 'change', 'help', 'history', 'earn')
        if type in open_trueWindowAcceptParameter:

            if type == 'add':
                addRoot = tk.Tk()
                applicationAdd = AppAdd(addRoot)

                addRoot.mainloop()
            elif type == 'change':
                changeRoot = tk.Tk()
                applicationChange = AppChange(changeRoot)

                changeRoot.mainloop()
            elif type == 'history':
                historyRoot = tk.Tk()
                applicationHistory = AppHistory(historyRoot)

                historyRoot.mainloop()
            elif type == 'help':
                self.second_window = tk.Toplevel(self.root_window)
                self.second_window.title('帮助')

                tk.Label(self.second_window, text = '帮助', font = ('times', 18, 'bold')).grid(row = 0, column = 0, sticky = tk.W + tk.E, padx = 10, pady = (3, 0))
                
                #How to Use Frame
                div_howToUse = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_howToUse.grid(row = 1, column = 0, padx = 10, pady = 10)

                tk.Label(div_howToUse, text = '如何使用: ', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '1. 使用前请按添加，然后添加你想卖出去的货。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '2. 如果有什么错误请安更改再进行更改。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '3. 物品添加完成， 请确认扫码机使用正常。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '4. 检查完请安心使用， 扫完码后系统会自动把货加入到购物廊里。 如你输入的条码不存在，系统会显示出错误，扫码后可选择数量。', wrap = 800,  anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '5. 如果扫码过程中需要更改， 先点击需要更改的然后下方有可以选择。', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_howToUse, text = '6. 如果有新顾客， 可以新开一个页面，这样可以同时两个使用。', anchor = tk.W).pack(fill = tk.BOTH)

                #How to Use Frame
                div_erro = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_erro.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = tk.W + tk.E)

                tk.Label(div_erro, text = '解决错误: ', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = '如果使用过程中出现什么问题或无法正常使用， 请按着自修。 可让系统自修起来， 过程有可能需要时间', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = '如果自修后继续无法使用，请进行手动修复', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_erro, text = '1. 请在'+os.getcwd()+'找到data文件夹然后找database.db文件', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '2. 把此文件复制一份， 记得复制名字要一致 database.db', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '3. 再重新把系统下载过来', anchor = tk.W, wrap = 780).pack(fill = tk.BOTH, padx = (20, 0))
                tk.Label(div_erro, text = '4. 下载完， 请把复制好的文件database.db移动到data文件夹里 在'+os.getcwd(), anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '4. 移动完毕后可以打开正常使用了', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))
                tk.Label(div_erro, text = '5. 如果没解决问题 请联系开发者', anchor = tk.W).pack(fill = tk.BOTH, padx = (10, 0))

                #How to Use Frame
                div_creator = tk.Frame(self.second_window, width = 800, padx = 20, pady = 20, borderwidth = 3, relief= tk.RAISED )
                div_creator.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = tk.W + tk.E)

                tk.Label(div_creator, text = '开发者: 郑林磊', anchor = tk.W, font = ('times', 12, 'bold')).pack(fill = tk.BOTH)
                tk.Label(div_creator, text = '邮件: zheng9112003@gmail.com', anchor = tk.W).pack(fill = tk.BOTH)
                tk.Label(div_creator, text = '版本 1.0 2020年', anchor = tk.W).pack(fill = tk.BOTH)
        else:
            if type == 'amount_product':
                if self.root_window_firstLabelFrame_code.get() != "" and self.root_window_firstLabelFrame_code.get().isnumeric():
                    self.open_amountTable_number(False)



    # Every product has an code for control so, the free prices product must have one to delete and remove then in the call
    # The code is 自由价格x

    freeProductIndex = 0

    # The function
               
    def freeProduct(self):
        if not self.second_windowOpen:


            # Level status

            self.levelStatus = 0

            #Only can open one
            #Check if it's openned
            self.second_windowOpen = True

            self.second_window = tk.Toplevel()
            self.second_window.title('自由价格')
            def closeSecond_window():
                self.second_windowOpen = False
                self.root_window_firstLabelFrame_code.focus()
                self.second_window.destroy()
                            
            self.second_window.protocol("WM_DELETE_WINDOW", closeSecond_window)
            self.second_window.focus_force()

            #Title
            tk.Label(self.second_window, text = '自由价格', font = ('times', 18), anchor = tk.CENTER).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
            #---------------------------------
            second_window_firstLabelFrame = tk.LabelFrame(self.second_window, text = '输入数量和名称', padx = 20, pady = 20)
            second_window_firstLabelFrame.grid(row = 1, column = 0, pady = 30, columnspan = 2, sticky = tk.W + tk.E, padx = 20)

            #amount
            tk.Label(second_window_firstLabelFrame, text = '数量: ', font = ('', 14, 'bold')).grid(row = 0, column = 0, padx = (0, 15))
            second_window_firstLabelFrame_amount = tk.Entry(second_window_firstLabelFrame, width = 50)
            second_window_firstLabelFrame_amount.insert(tk.END, '1')
            second_window_firstLabelFrame_amount.grid(row = 0, column = 1, padx = 5)


            #name
            tk.Label(second_window_firstLabelFrame, text = '名称: ', font = ('', 14, 'bold')).grid(row = 1, column = 0, padx = (0, 15))
            second_window_firstLabelFrame_name = tk.Entry(second_window_firstLabelFrame, width = 50)
            second_window_firstLabelFrame_name.grid(row = 1, column = 1, padx = 5)
            #focus
            second_window_firstLabelFrame_name.focus_force()

            #----------------------------------
            second_window_secondLabelFrame = tk.LabelFrame(self.second_window, text = '输入价格', padx = 20, pady = 20)
            second_window_secondLabelFrame.grid(row = 2, column = 0, pady = 30, sticky = tk.W + tk.E, padx = 20)

            second_window_secondLabelFrame_price = tk.Entry(second_window_secondLabelFrame,)
            second_window_secondLabelFrame_price.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.W + tk.E)

            number_button_frame = tk.Frame(second_window_secondLabelFrame)
            number_button_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

            def amountInputButton(number):
                if number == 'del':
                    second_window_secondLabelFrame_price.delete(len(second_window_secondLabelFrame_price.get())-1)
                else:
                    second_window_secondLabelFrame_price.insert(tk.END, number) 

            tk.Button(number_button_frame, text = 7, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 8, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 9, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                                #----------
            tk.Button(number_button_frame, text = 4, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 5, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 6, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                                #----------
            tk.Button(number_button_frame, text = 1, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 2, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = 3, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                                #----------
            tk.Button(number_button_frame, text = 0, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = '.', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('.')).grid(row = 3, column = 1, padx = 5, pady = 5)
            tk.Button(number_button_frame, text = '删除', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5)
            #------------------------


            # Add to table and then can load into the receipt
            def addProductFnc():

                if second_window_firstLabelFrame_amount.get() and second_window_secondLabelFrame_price.get():
                    amount = int(second_window_firstLabelFrame_amount.get())
                    name = second_window_firstLabelFrame_name.get()
                    price = float(second_window_secondLabelFrame_price.get())

                    totalPrice = float("{:.2f}".format(price*amount))

                    self.root_window_tableProducts.insert('', tk.END, text = '自由价格{}'.format(self.freeProductIndex), values = (name, price, int(amount), totalPrice))
                    self.totalPrice_arr_toPay['自由价格{}'.format(self.freeProductIndex)] = "{:.2f}".format(totalPrice)
                    self.root_window_totalPrice['text'] = self.calc_totalPrice()

                    # Plus one index for free products
                    self.freeProductIndex = self.freeProductIndex + 1

                    self.root_window_firstLabelFrame_code.focus()
                    self.second_window.destroy()
                    self.second_windowOpen = False


            #-----------------------
            def nextLevel():
                second_window_secondLabelFrame_price.focus_force()
                self.levelStatus = 1


            number_continue_frame = tk.Frame(self.second_window)
            number_continue_frame.grid(row = 2, column = 1, padx = 5, pady = 30, sticky = tk.W + tk.E + tk.N + tk.S)

            addProduct = tk.Button(number_continue_frame, text = '添加', cursor = 'hand2', font = ('', 10, 'bold'), width = 10, command = addProductFnc)
            addProduct.pack(pady = 30)

            self.second_window.bind('<Return>', lambda e:(nextLevel() if self.levelStatus == 0 else addProductFnc()))

            CreateToolTip(addProduct, text = '加入到购物车。 快速键 Enter (回车键)，必须要在添加完毕信息才能使用')

        else:
            self.second_window.focus_force()
            messagebox.showwarning('关闭', '请先关闭其他小页面')     


    def auto_repair(self):
        if os.path.isfile('./data/database.db'):
            if os.path.isdir('./data'):
                messagebox.showwarning('没有找到错误', '我们没有找到任何错误。 请继续，让后跟着指令手动修复')

            else:
                messagebox.showwarning('找到错误', '我们发现此文件不在真确的地址。 请继续，让后跟着指令手动修复')


            messagebox.showinfo('手动修复', '请在 {}\\data\\ 让后找到 database.db， 然后复制或保存起来。 \n \n 再重新安装系统。 \n \n 把复制或保存起来的文件移动到 {}\\data\\里'.format(os.getcwdb(), os.getcwdb()))


        else:
            messagebox.showwarning('找到错误', '有一个文件我们无法找到， 我们会尽量的把文件找到的')

            if os.path.isfile('./database.db'):
                os.replace("./database.db", "./data/database.db")

                messagebox.showinfo('修复完毕', '错误已修复完毕')
            else:
                messagebox.showwarning('找到错误', '对不起， 我们未找到此文件。 我们会重新给你创建和设置。 可是由于此文件是本系统的数据库， 你将会丢失全部数据 \n\n\n或者你可以手动去找一下此文件 database.db 有可能在回收站里， 请检查。 我们将会帮你先准备， 如果有找到的话请把它移动到 {}'. format(os.getcwd()))
                prepare_database()

    def open_amountTable_number(self, type):
        if not self.second_windowOpen:
            #Only can open one
            #Check if it's openned
            self.second_windowOpen = True

            self.second_window = tk.Toplevel()
            self.second_window.title('数量')
            def closeSecond_window():
                self.second_windowOpen = False
                self.root_window_firstLabelFrame_code.focus()
                self.second_window.destroy()
                            
            self.second_window.protocol("WM_DELETE_WINDOW", closeSecond_window)

            inputNumber_frame = tk.Frame(self.second_window, padx = 40, pady = 15)
            inputNumber_frame.grid(row = 0, column = 0, sticky = tk.W + tk.E)

            add_productAmountInput = tk.Spinbox(inputNumber_frame, from_ = 1, to = 9999, wrap = True)
            add_productAmountInput.pack(fill = tk.BOTH, padx = 5, ipadx = 2, ipady = 10)
            add_productAmountInput.focus()

            buttonNumber_frame = tk.Frame(self.second_window, padx = 25, pady = 25)
            buttonNumber_frame.grid(row = 1, column = 0)

            def amountInputButton(number):
                if number == 'del':
                    add_productAmountInput.delete(len(add_productAmountInput.get())-1)
                else:
                    add_productAmountInput.insert(tk.END, number) 

            tk.Button(buttonNumber_frame, text = 7, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 8, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 9, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 4, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 5, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 6, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 1, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 2, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
            tk.Button(buttonNumber_frame, text = 3, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
            tk.Button(buttonNumber_frame, text = 0, cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 20, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 2, sticky = tk.W + tk.E)
            tk.Button(buttonNumber_frame, text = '删除', cursor = 'hand2', pady = 10, padx = 10, font = ('consolas', 14, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5, sticky = tk.N + tk.S)

            self.second_window.focus_force()

            if type:
                add_productsFase2Button = tk.Button(buttonNumber_frame, text = '更换', cursor = 'hand2', bd = 3, font = ('times', 16), command = lambda : self.editProduct_addToPay(add_productAmountInput.get()))
                self.second_window.bind("<Return>", lambda event: self.editProduct_addToPay(add_productAmountInput.get()))
            else:
                add_productsFase2Button = tk.Button(buttonNumber_frame, text = '继续', cursor = 'hand2', bd = 3, font = ('times', 16), command = lambda : self.secondWindow_addToPay(self.root_window_firstLabelFrame_code.get(), add_productAmountInput.get()))
                self.second_window.bind("<Return>", lambda event: self.secondWindow_addToPay(self.root_window_firstLabelFrame_code.get(), add_productAmountInput.get()))

                            
            add_productsFase2Button.grid(row = 4, column = 0, columnspan = 3, sticky = tk.W + tk.E, pady = (15, 0))

            CreateToolTip(add_productsFase2Button, text = '选择数量后请继续, 按Enter键可快速加入 <回车键>')         
        else:
            self.second_window.focus_force()
        

    def toggle_fullScreen(self):
        self.root_window_fullScreen = not self.root_window_fullScreen

        if self.root_window_fullScreen:
            self.root_window_fullScreenButton['text'] = '页面变小'
        else:
            self.root_window_fullScreenButton['text'] = '页面变大'

        self.root_window.attributes("-fullscreen", self.root_window_fullScreen)

    #Show all total Price    
    def calc_totalPrice(self):
        if len(self.totalPrice_arr_toPay) == 0:
            totalPrice = 0.00
        else:
            totalPrice = 0

            prices = self.totalPrice_arr_toPay.values()
            for price in prices:
                totalPrice += float(price)

        return "{:.2f}".format(totalPrice)

    def secondWindow_addToPay(self, code, amount):
        if (code != "" and amount != "") and (code.isnumeric() and amount.isnumeric()):
            query = 'SELECT `code`, `name`, `price` FROM `Product_data` WHERE `code` = ?'
            parameters = (code, )
            responseData = run_sqlite_query(query, parameters = parameters)

            if len(responseData) == 0:
                messagebox.showwarning("错误", "没有任何消息关于这条码，请添加到里面")
            else:
                return_ifAdded = self.checkProduct_added_before(code)

                if return_ifAdded:
                    child_toDelete = self.root_window_tableProducts.item(return_ifAdded)
                    #----------
                    amount_number = int(child_toDelete['values'][2]) + int(amount)
                    #------------------------
                    self.root_window_tableProducts.delete(return_ifAdded)

                else:
                    amount_number = amount

                totalPrice_product = float("{:.2f}".format((float(responseData[0][2]))*(float(amount_number))))

                self.root_window_tableProducts.insert('', tk.END, text = responseData[0][0], values = (responseData[0][1], responseData[0][2], int(amount_number), totalPrice_product))
                self.totalPrice_arr_toPay[code] = "{:.2f}".format(totalPrice_product)

                self.root_window_totalPrice['text'] = self.calc_totalPrice()

            self.root_window_firstLabelFrame_code.delete(0, tk.END)
            self.root_window_firstLabelFrame_code.focus()
            self.second_window.destroy()
            self.second_windowOpen = False

    def checkProduct_added_before(self, code):
        allChilds = self.root_window_tableProducts.get_children()

        for child in allChilds:
            if str(self.root_window_tableProducts.item(child)['text']) == code:
                return child


        return False

    #EDIT AND DELETE
    def checkProduct_is_selected(self):
        if len(str(self.root_window_tableProducts.item(self.root_window_tableProducts.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("错误", "没有任何物品选中， 请选择")
            self.root_window_firstLabelFrame_code.focus()
            return False


    def removeProduct_addToPay(self):
        if(self.checkProduct_is_selected()):
            code = str(self.root_window_tableProducts.item(self.root_window_tableProducts.selection())['text'])
            
            del self.totalPrice_arr_toPay[code]
            self.root_window_tableProducts.delete(self.root_window_tableProducts.selection())

            self.root_window_totalPrice['text'] = self.calc_totalPrice()

            self.root_window_firstLabelFrame_code.focus()
    def to_open_amountTable_number(self):
        if(self.checkProduct_is_selected()):
            self.open_amountTable_number(True)

    def editProduct_addToPay(self, amount):
        item_selectedId = self.root_window_tableProducts.selection()
        item_selectedValues = self.root_window_tableProducts.item(item_selectedId)

        totalPrice_product = float("{:.2f}".format((float(item_selectedValues['values'][1]))*(int(amount))))

        self.root_window_tableProducts.insert('', tk.END, text = item_selectedValues['text'], values = (item_selectedValues['values'][0], item_selectedValues['values'][1], int(amount), totalPrice_product))
        self.totalPrice_arr_toPay[str(item_selectedValues['text'])] = totalPrice_product

        self.root_window_tableProducts.delete(item_selectedId)
            
        self.root_window_totalPrice['text'] = self.calc_totalPrice()

        self.root_window_firstLabelFrame_code.focus()
        self.second_window.destroy()
        self.second_windowOpen = False

    
    #Pay the price
    def allProduct_payAllPrice(self):
        if len(self.totalPrice_arr_toPay) == 0:
            messagebox.showerror("物品", "购物廊空的，我们无法计算价格")
            self.root_window_firstLabelFrame_code.focus()
        else:
            self.chooseType_forPay()

    def chooseType_forPay(self):
        if not self.second_windowOpen:
            #Only can open one
            #Check if it's openned
            self.second_windowOpen = True
            self.second_window = tk.Toplevel(self.root_window)
            self.second_window.focus_force()
            self.second_window.title('算账')

            def closeSecond_window():
                self.second_windowOpen = False
                self.root_window_firstLabelFrame_code.focus()
                self.second_window.destroy()
                                
            self.second_window.protocol("WM_DELETE_WINDOW", closeSecond_window)

            tk.Label(self.second_window, text = '选择支付方式', anchor = tk.CENTER, font = ('', 18, 'bold')).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E, pady = (10, 0))
            moneyMethod_pay = tk.Button(self.second_window, text = '现金', padx = 15, pady = 15, font = ('times', 18, 'bold'), command = lambda : self.payAll_priceToFinish('money'))
            moneyMethod_pay.grid(row = 1, column = 0, padx = 20, pady = (60, 90))
            #FastKey
            self.second_window.bind("<F1>", lambda event: self.payAll_priceToFinish('money'))
            CreateToolTip(moneyMethod_pay, text = '快速键: F1')

            creditCardMethod_pay = tk.Button(self.second_window, text = '银行卡', padx = 15, pady = 15, font = ('times', 18, 'bold'), command = lambda : self.payAll_priceToFinish('card'))
            creditCardMethod_pay.grid(row = 1, column = 3, padx = 20, pady = (60, 90))
            #FastKey
            self.second_window.bind("<F2>", lambda event: self.payAll_priceToFinish('card'))
            CreateToolTip(creditCardMethod_pay, text = '快速键: F2')


            #Print
            receiptPrint = tk.Button(self.second_window, text = '打印', padx = 15, pady = 15, font = ('times', 18, 'bold'), command = lambda : self.printReceipt())
            receiptPrint.grid(row = 1, column = 3, padx = 20, pady = (60, 90))
            #FastKey
            self.second_window.bind("<F3>", lambda event: self.printReceipt())
            CreateToolTip(receiptPrint, text = '快速键: F3')
        else:
            messagebox.showwarning("无法继续", "有别的系统程序开着，请关闭再继续")
            self.second_window.focus_force()

    def payAll_priceToFinish(self, typeOf):
        #Create a datetime 
        datetimeVar = datetime.now()
        #-------------
        methodPay = typeOf
        date = datetimeVar.strftime('%Y-%m-%d')
        time = datetimeVar.strftime("%H:%M:%S")

        totalPrice = self.calc_totalPrice()
        numberProduct = len(self.totalPrice_arr_toPay)

        dataProduct = {'data': []}

        for product in self.root_window_tableProducts.get_children():
            data_of_product = self.root_window_tableProducts.item(product)

            jsonToStr = {
                    'code': data_of_product['text'], 
                    'name': data_of_product['values'][0], 
                    'price': data_of_product['values'][1], 
                    'amount': data_of_product['values'][2], 
                    'total_price': data_of_product['values'][3]
                    }

            dataProduct['data'].append(jsonToStr)

        dataProduct_str = json.dumps(dataProduct)

        query = 'INSERT INTO `Product_register_pay` (`date_time`,`data`, `total_price`, `number_product`, `method_pay`) VALUES (?, ?, ?, ?, ?)'
        parameters = ('{} {}'.format(date, time), dataProduct_str, totalPrice, numberProduct, methodPay)

        if run_sqlite_query(query, parameters = parameters):
            self.second_window.destroy()
            self.second_windowOpen = False
            #Reset system----------
            self.reset_allSystem_toNew()


    def getLastHistoryRow(self):
        # GET LAST ID
        query = 'SELECT * FROM `Product_register_pay` ORDER BY `id` DESC LIMIT 1;'
        return run_sqlite_query(query, parameters = ())[0]


    # Print the receipt
    def printReceipt(self):

        id = str(self.getLastHistoryRow()[0]+1)
        subtotal = self.calc_totalPrice()
        tax = 0.00

        dataList = {
            'product': [],
            'subtotal': subtotal,
            'tax': tax,
            'total': '{:.2f}'.format(float(subtotal) + float(tax)),
            'id': id
        }

        if self.root_window_tableProducts.get_children():
            for product in self.root_window_tableProducts.get_children():
                data_of_product = self.root_window_tableProducts.item(product)

                data = ['{:.2f}'.format(float(data_of_product['values'][1])), data_of_product['values'][0], data_of_product['values'][2], '{:.2f}'.format(float(data_of_product['values'][3]))]

                dataList['product'].append(data)



        # Create receipt template 

        HtmlText = ReceiptMaker(dataList)


        # Print in the printer
        Printer = PrintHTML(TMP_PATHNAME, options = {
            'page-height': '210mm',
            'page-width': '72mm',
            'encoding': "UTF-8",

        })
        
        Printer.addHTML(HtmlText, f'单号:{id}', {})

        # Start printing
        Printer.printAll()
                

    def reset_allSystem_toNew(self):
        self.second_window.destroy()
        
        self.totalPrice_arr_toPay.clear()
        self.root_window_totalPrice['text'] = self.calc_totalPrice()

        for element in self.root_window_tableProducts.get_children():
            self.root_window_tableProducts.delete(element)

        self.root_window_firstLabelFrame_code.focus()

        # Reset the free products index
        self.freeProductIndex = 0


class AppAdd():
    addProduct_status_level = 0

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('添加物品')

        self.root_window.bind('<Return>', lambda event : self.check_status_level())
        self.root_window.focus_force()

        #Title
        tk.Label(self.root_window, text = '添加物品', font = ('times', 18), anchor = tk.CENTER).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        #---------------------------------
        self.root_window_firstLabelFrame = tk.LabelFrame(self.root_window, text = '输入条码和名称', padx = 20, pady = 20)
        self.root_window_firstLabelFrame.grid(row = 1, column = 0, pady = 30, columnspan = 2, sticky = tk.W + tk.E, padx = 20)

        #code
        tk.Label(self.root_window_firstLabelFrame, text = '条码: ', font = ('', 14, 'bold')).grid(row = 0, column = 0, padx = (0, 15))
        self.root_window_firstLabelFrame_code = tk.Entry(self.root_window_firstLabelFrame, width = 50)
        self.root_window_firstLabelFrame_code.grid(row = 0, column = 1, padx = 5)

        #focus
        self.root_window_firstLabelFrame_code.focus_force()

        #name
        tk.Label(self.root_window_firstLabelFrame, text = '名称: ', font = ('', 14, 'bold')).grid(row = 1, column = 0, padx = (0, 15))
        self.root_window_firstLabelFrame_name = tk.Entry(self.root_window_firstLabelFrame, width = 50)
        self.root_window_firstLabelFrame_name.grid(row = 1, column = 1, padx = 5)
        #----------------------------------
        self.root_window_secondLabelFrame = tk.LabelFrame(self.root_window, text = '输入价格', padx = 20, pady = 20)
        self.root_window_secondLabelFrame.grid(row = 2, column = 0, pady = 30, sticky = tk.W + tk.E, padx = 20)

        self.root_window_secondLabelFrame_price = tk.Entry(self.root_window_secondLabelFrame,)
        self.root_window_secondLabelFrame_price.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.number_button_frame = tk.Frame(self.root_window_secondLabelFrame)
        self.number_button_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

        def amountInputButton(number):
            if number == 'del':
                self.root_window_secondLabelFrame_price.delete(len(self.root_window_secondLabelFrame_price.get())-1)
            else:
                self.root_window_secondLabelFrame_price.insert(tk.END, number) 

        tk.Button(self.number_button_frame, text = 7, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 8, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 9, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 4, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 5, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 6, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 1, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 2, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 3, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 0, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '.', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('.')).grid(row = 3, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '删除', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5)
        #------------------------
        self.number_continue_frame = tk.Frame(self.root_window)
        self.number_continue_frame.grid(row = 2, column = 1, padx = 5, pady = 30, sticky = tk.W + tk.E + tk.N + tk.S)

        checkExist = tk.Button(self.number_continue_frame, text = '检查是否存在', cursor = 'hand2', font = ('', 10, 'bold'), width = 10, command = self.checkProduct_inDB)
        checkExist.pack(pady = 30)
        self.root_window.bind('<F1>', lambda event : self.checkProduct_inDB())
        CreateToolTip(checkExist, text = '检查此物品是否存在或者， 有类似的物品。 快速键 F1')

        addProduct = tk.Button(self.number_continue_frame, text = '添加物品', cursor = 'hand2', font = ('', 10, 'bold'), width = 10, command = self.addProduct_toDB)
        addProduct.pack(pady = 30)

        CreateToolTip(addProduct, text = '添加前系统会查此物品是否存在， 如果存在不会被添加。 快速键 Enter (回车键)，必须要在添加完毕信息才能使用')
    
        self.root_window_statusText = tk.Label(self.root_window, text = '', padx = 20, pady = 20, fg = 'green')
        self.root_window_statusText.grid(row = 3, column = 0, columnspan = 2, sticky = tk.W + tk.E)

    def check_status_level(self):
        if self.addProduct_status_level == 0:
            self.root_window_statusText["text"] = ''
            self.root_window_firstLabelFrame_name.focus()
        elif self.addProduct_status_level == 1:
            self.root_window_secondLabelFrame_price.focus()
        elif self.addProduct_status_level == 2:
            self.addProduct_toDB()

        self.addProduct_status_level += 1

    def checkProduct_inDB(self, code = False):
        self.root_window_statusText["text"] = ''
        if not code:
            code = self.root_window_firstLabelFrame_code.get()

        query = 'SELECT `name`, `price` FROM `Product_data` WHERE `code` = ?'
        parameters = (code, )

        returnResponse_query = run_sqlite_query(query, parameters = parameters)

        if len(returnResponse_query) == 0:
            self.root_window_statusText['fg'] = 'green'
            self.root_window_statusText["text"] = '此物品未添加过， 可安心添加'
            return True
        else:
            self.root_window_statusText['fg'] = 'red'
            self.root_window_statusText['text'] = '您已添加过此物品 名称: {}, 价格: {}'.format(returnResponse_query[0][0], returnResponse_query[0][1])
            return False


    def addProduct_toDB(self):
        self.root_window_statusText["text"] = ''
        code = self.root_window_firstLabelFrame_code.get()
        if code.isnumeric() and len(code) != 0:

            ifExist = self.checkProduct_inDB(code)

            if ifExist:
                self.root_window_statusText["text"] = ''
                name = self.root_window_firstLabelFrame_name.get()
                price = self.root_window_secondLabelFrame_price.get()

                if name != 0 and isFloat(price):
                    query = 'INSERT INTO `Product_data` (`code`, `name`, `price`) VALUES (?, ?, ?)'
                    parameters = (code, name, price)

                    if run_sqlite_query(query, parameters = parameters):
                        self.root_window_statusText["fg"] = 'green'
                        self.root_window_statusText["text"] = '物品已被添加: {} | {} | {}'.format(code, name, price)

                        self.root_window_firstLabelFrame_code.delete(0, tk.END)
                        self.root_window_firstLabelFrame_name.delete(0, tk.END)

                        self.root_window_secondLabelFrame_price.delete(0, tk.END)

                        self.addProduct_status_level = 0
                        self.root_window_firstLabelFrame_code.focus_force()
                else:
                    self.root_window_statusText["fg"] = 'red'
                    self.root_window_statusText["text"] = '请检查物品名称和价格是否真确'
        else:
            self.root_window_statusText["fg"] = 'red'
            self.root_window_statusText["text"] = '请输入真确的条码'


class AppChange():

    addProduct_status_level = code_condition = 0

    def __init__(self, window):
        self.root_window = window
        self.root_window.title('更改物品')

        self.root_window.focus_force()

        tk.Label(self.root_window, text = '输入要寻找的物品去更改', pady = 10, font = ('', 12, 'bold')).grid(row = 0, column = 0, sticky = tk.N + tk.S)
        #First div
        first_frame = tk.Frame(self.root_window, pady = 10, padx = 10)
        first_frame.grid(row = 1, column = 0, sticky = tk.N + tk.S)

        self.search_value_input = tk.Entry(first_frame, width = 80)
        self.search_value_input.grid(row = 0, column = 0)
        
        self.search_value_input.focus_force()

        self.choose_type_search = ttk.Combobox(first_frame, values = ('条码', '名称', '价格'), state = 'readonly')
        self.choose_type_search.grid(row = 0, column = 1, padx = (0, 5))

        self.choose_type_search.set('名称')

        button_toSearch = tk.Button(first_frame, text = '查找', padx = 10, command = self.search_data_fromValue)
        button_toSearch.grid(row = 0, column = 2, padx = (5, 0))
        #----------------------------
        self.root_window.bind("<Return>", lambda event: self.search_data_fromValue())
        CreateToolTip(button_toSearch, text = '快速键: Enter <回车>')

        #-----------------------------------------
        #Second div
        second_frame = tk.Frame(self.root_window)
        second_frame.grid(row = 2, column = 0)

        self.showProduct_table = ttk.Treeview(second_frame, columns = ("name", "price"), selectmode = tk.EXTENDED, height = 28)
        #Prepare
        self.showProduct_table.heading('#0', text = '条码', anchor = tk.CENTER)
        self.showProduct_table.column("#0", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)
        self.showProduct_table.heading('name', text = '名称', anchor = tk.CENTER)
        self.showProduct_table.column("name", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)
        self.showProduct_table.heading('price', text = '价格', anchor = tk.CENTER)
        self.showProduct_table.column("price", width = int(self.root_window.winfo_screenwidth()/3), stretch = False)

        self.showProduct_table.grid(row = 0, column = 0)
        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        #SCROLL
        showProductScroll = tk.Scrollbar(second_frame, orient = tk.VERTICAL, command = self.showProduct_table.yview)
        showProductScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.showProduct_table.configure(yscrollcommand = showProductScroll.set)

        #Third div
        third_frame = tk.Frame(self.root_window)
        third_frame.grid(row = 3, column = 0, sticky = tk.W + tk.E)

        changeButton = tk.Button(third_frame, text = '更改', padx = 25, cursor = 'hand2', command = self.change_product_fromDB)
        changeButton.grid(row = 0, column = 0, padx = 10, pady = (10, 20))
        #FastKey
        self.root_window.bind("<F10>", lambda event: self.change_product_fromDB())
        CreateToolTip(changeButton, text = '快速键: F10')

        deleteButton = tk.Button(third_frame, text = '删除', padx = 25, cursor = 'hand2', command = self.delete_product_fromDB)
        deleteButton.grid(row = 0, column = 1, padx = 10, pady = (10, 20))
        #FastKey
        self.root_window.bind("<Delete>", lambda event: self.delete_product_fromDB())
        CreateToolTip(deleteButton, text = '快速键: Delete')

    def search_data_fromValue(self):

        if len(self.search_value_input.get()) != 0:
            type = ['code', 'name', 'price']

            query = 'SELECT `code`, `name`, `price` FROM `Product_data` WHERE `{}` LIKE ?'.format(type[self.choose_type_search.current()])

            parameters = ('%'+self.search_value_input.get()+'%',)

            responseData = run_sqlite_query(query, parameters = parameters)

            for element in self.showProduct_table.get_children():
                self.showProduct_table.delete(element)

            if responseData:
                self.show_data_in_table(responseData)
            else:
                self.showProduct_table.insert('', tk.END, text = '空', values = ('没有任何', '物品'))
        
    def show_data_in_table(self, data):
        for element in data:
            self.showProduct_table.insert('', tk.END, text = element[0], values = (element[1], element[2]))
    def change_product_fromDB(self):
        if self.checkRegister_is_selected():
            item_to_change = self.showProduct_table.item(self.showProduct_table.selection())
            if item_to_change['text'] != '空':
                self.open_second_window_toChange(item_to_change)

                self.code_condition = item_to_change['text']

    def open_second_window_toChange(self, element):
        self.second_window = tk.Toplevel()

        self.second_window.title('更改数据')
        self.second_window.focus_force()

        self.second_window.bind('<Return>', lambda event : self.check_status_level())
        #Title
        tk.Label(self.second_window, text = '更改物品', font = ('times', 18), anchor = tk.CENTER).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        #---------------------------------
        self.second_window_firstLabelFrame = tk.LabelFrame(self.second_window, text = '输入要更改的条码或名称', padx = 20, pady = 20)
        self.second_window_firstLabelFrame.grid(row = 1, column = 0, pady = 30, columnspan = 2, sticky = tk.W + tk.E, padx = 20)

        #code
        tk.Label(self.second_window_firstLabelFrame, text = '条码: ', font = ('', 14, 'bold')).grid(row = 0, column = 0, padx = (0, 15))
        self.second_window_firstLabelFrame_code = tk.Entry(self.second_window_firstLabelFrame, width = 50)
        self.second_window_firstLabelFrame_code.insert(0, element['text'])

        self.second_window_firstLabelFrame_code.grid(row = 0, column = 1, padx = 5)


        #focus
        self.second_window_firstLabelFrame_code.focus_force()

        #name
        tk.Label(self.second_window_firstLabelFrame, text = '名称: ', font = ('', 14, 'bold')).grid(row = 1, column = 0, padx = (0, 15))
        self.second_window_firstLabelFrame_name = tk.Entry(self.second_window_firstLabelFrame, width = 50)
        self.second_window_firstLabelFrame_name.grid(row = 1, column = 1, padx = 5)
        
        self.second_window_firstLabelFrame_name.insert(0, element['values'][0])
        #----------------------------------
        self.second_window_secondLabelFrame = tk.LabelFrame(self.second_window, text = '输入更改的价格', padx = 20, pady = 20)
        self.second_window_secondLabelFrame.grid(row = 2, column = 0, pady = 30, sticky = tk.W + tk.E, padx = 20)

        self.second_window_secondLabelFrame_price = tk.Entry(self.second_window_secondLabelFrame,)
        self.second_window_secondLabelFrame_price.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.second_window_secondLabelFrame_price.insert(0, element['values'][1])

        self.number_button_frame = tk.Frame(self.second_window_secondLabelFrame)
        self.number_button_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

        def amountInputButton(number):
            if number == 'del':
                self.second_window_secondLabelFrame_price.delete(len(self.second_window_secondLabelFrame_price.get())-1)
            else:
                self.second_window_secondLabelFrame_price.insert(tk.END, number) 

        tk.Button(self.number_button_frame, text = 7, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(7)).grid(row = 0, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 8, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(8)).grid(row = 0, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 9, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(9)).grid(row = 0, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 4, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(4)).grid(row = 1, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 5, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(5)).grid(row = 1, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 6, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(6)).grid(row = 1, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 1, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(1)).grid(row = 2, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 2, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(2)).grid(row = 2, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = 3, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(3)).grid(row = 2, column = 2, padx = 5, pady = 5)
                            #----------
        tk.Button(self.number_button_frame, text = 0, cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton(0)).grid(row = 3, column = 0, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '.', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('.')).grid(row = 3, column = 1, padx = 5, pady = 5)
        tk.Button(self.number_button_frame, text = '删除', cursor = 'hand2', pady = 5, padx = 8, font = ('consolas', 10, 'bold'), command = lambda : amountInputButton('del')).grid(row = 3, column = 2, padx = 5, pady = 5)
        #------------------------
        self.number_continue_frame = tk.Frame(self.second_window)
        self.number_continue_frame.grid(row = 2, column = 1, padx = 5, pady = 30, sticky = tk.W + tk.E + tk.N + tk.S)

        checkExist = tk.Button(self.number_continue_frame, text = '检查是否存在一样的物品', cursor = 'hand2', font = ('', 10, 'bold'), width = 30, command = self.checkProduct_inDB)
        checkExist.pack(pady = 30)

        self.second_window.bind('<F1>', lambda event : self.checkProduct_inDB())
        CreateToolTip(checkExist, text = '检查此物品是否存在或者， 有类似的物品。 快速键 F1')

        addProduct = tk.Button(self.number_continue_frame, text = '更改此物品', cursor = 'hand2', font = ('', 10, 'bold'), width = 30, command = lambda : self.addProduct_toDB())
        addProduct.pack(pady = 30)

        CreateToolTip(addProduct, text = '添加前系统会查此物品是否存在， 如果存在不会被更改。 快速键 Enter (回车键)，必须要在添加完毕信息才能使用')
    
        self.second_window_statusText = tk.Label(self.second_window, text = '', padx = 20, pady = 20, fg = 'green')
        self.second_window_statusText.grid(row = 3, column = 0, columnspan = 2, sticky = tk.W + tk.E)
    
    
    def check_status_level(self):
        if self.addProduct_status_level == 0:
            self.second_window_statusText["text"] = ''
            self.second_window_firstLabelFrame_name.focus()
        elif self.addProduct_status_level == 1:
            self.second_window_secondLabelFrame_price.focus()
        elif self.addProduct_status_level == 2:
            self.addProduct_toDB()

        self.addProduct_status_level += 1
    def addProduct_toDB(self):
        self.second_window_statusText["text"] = ''
        code = self.second_window_firstLabelFrame_code.get()
        if code.isnumeric() and len(code) != 0:

            ifExist = self.checkProduct_inDB(code)

            if ifExist:
                self.second_window_statusText["text"] = ''
                name = self.second_window_firstLabelFrame_name.get()
                price = self.second_window_secondLabelFrame_price.get()

                if name != 0 and isFloat(price):
                    query = 'UPDATE `Product_data` SET `code` = ?, `name` = ?, `price` = ? WHERE `code` = ?'
                    parameters = (code, name, price, self.code_condition)

                    if run_sqlite_query(query, parameters = parameters):
                        self.second_window_statusText["fg"] = 'green'
                        self.second_window_statusText["text"] = '物品已被更改: {} | {} | {}'.format(code, name, price)

                        self.second_window_firstLabelFrame_code.delete(0, tk.END)
                        self.second_window_firstLabelFrame_name.delete(0, tk.END)

                        self.second_window_secondLabelFrame_price.delete(0, tk.END)

                        self.addProduct_status_level = self.code_condition = 0

                        self.search_data_fromValue()
                        
                        self.second_window.destroy()

                        self.second_window_firstLabelFrame_code.focus_force()
                else:
                    self.second_window_statusText["fg"] = 'red'
                    self.second_window_statusText["text"] = '请检查物品名称和价格是否真确'
        else:
            self.second_window_statusText["fg"] = 'red'
            self.second_window_statusText["text"] = '请输入真确的条码'

    def checkProduct_inDB(self, code = False):
        self.second_window_statusText["text"] = ''
        if not code:
            code = self.second_window_firstLabelFrame_code.get()

        if str(self.code_condition) != code:
            query = 'SELECT `name`, `price` FROM `Product_data` WHERE `code` = ?'
            parameters = (code, )

            returnResponse_query = run_sqlite_query(query, parameters = parameters)

            if len(returnResponse_query) == 0:
                self.second_window_statusText['fg'] = 'green'
                self.second_window_statusText["text"] = '此物品未添加过， 可安心更改'
                return True
            else:
                self.second_window_statusText['fg'] = 'red'
                self.second_window_statusText['text'] = '您已添加过此物品 名称: {}, 价格: {}'.format(returnResponse_query[0][0], returnResponse_query[0][1])
                return False
        else:
            self.second_window_statusText['fg'] = 'black'
            self.second_window_statusText["text"] = '你未更改条码'
            return True

    def delete_product_fromDB(self):
        if self.checkRegister_is_selected():
            item_to_delete = self.showProduct_table.item(self.showProduct_table.selection())
            if item_to_delete['text'] != '空':
                msgReturn = messagebox.askokcancel('确认', '确定要删这份物品吗? 删完后是无法重新找回的')

                if msgReturn:
                    query = 'DELETE FROM `Product_data` WHERE `code` = ? AND `name` = ? AND `price` = ?'
                    parameters = (item_to_delete['text'], item_to_delete['values'][0], item_to_delete['values'][1])

                    if run_sqlite_query(query, parameters = parameters):
                        messagebox.showinfo('删除', '物品已被删除')
                        self.search_data_fromValue()

                        self.root_window.focus_force()

                        self.search_value_input.focus()
                else:
                    self.root_window.focus_force()


    def checkRegister_is_selected(self):
        if len(str(self.showProduct_table.item(self.showProduct_table.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("错误", "没有任何物品选中， 请选择")
            self.root_window.focus_force()
            return False

class AppHistory():
    def __init__(self, window):
        self.root_window = window
        self.root_window.title('查看历史')

        self.root_window.focus_force()
        #First div
        first_frame = tk.Frame(self.root_window)
        first_frame.grid(row = 0, column = 0, sticky = tk.N + tk.S)

        tk.Label(first_frame, text = '查找销售记录', anchor = tk.CENTER).grid(row = 0, column = 0, sticky = tk.W + tk.E, pady = (10, 5))

        self.root_window_firstLabelFrame = tk.LabelFrame(first_frame, text = ' 日期时间查找 ', padx = 10, pady = 10)
        self.root_window_firstLabelFrame.grid(row = 2, column = 0, padx = 5, pady = 5)

        tk.Label(self.root_window_firstLabelFrame, text = '日期', anchor = tk.W).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        self.startDate = DateEntry(self.root_window_firstLabelFrame, width = 15)
        self.startDate.grid(row = 1, column = 0, padx = 10, pady = (5, 15))

        self.endDate = DateEntry(self.root_window_firstLabelFrame, width = 15)
        self.endDate.grid(row = 1, column = 1, padx = 10, pady = (5, 15))

        tk.Label(self.root_window_firstLabelFrame, text = '时间 (hh:mm:ss) 默认24h', anchor = tk.W).grid(row = 2, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        self.startTime = tk.Entry(self.root_window_firstLabelFrame, width = 18, bd = 1, relief = tk.RAISED)
        self.startTime.insert(0, '00:00:00')
        self.startTime.grid(row = 3, column = 0, padx = 10, pady = (5, 15))

        self.endTime = tk.Entry(self.root_window_firstLabelFrame, width = 18, bd = 1, relief = tk.RAISED)
        self.endTime.insert(0, '23:59:59')
        self.endTime.grid(row = 3, column = 1, padx = 10, pady = (5, 15))

        searchHistory_register = tk.Button(self.root_window_firstLabelFrame, cursor = 'hand2', text = '查找', pady = 5, command = self.searchData_inDB)
        searchHistory_register.grid(row = 4, column = 0, columnspan = 2, sticky = tk.W + tk.E, pady = (10, 5))
        #FastKey
        self.root_window.bind("<Return>", lambda event: self.searchData_inDB())
        CreateToolTip(searchHistory_register, text = '输入完查找消息可使用 Enter <回车键> 快速查找')

        #---------------
        checkHistory_element = tk.Button(first_frame, text = '查看记录', pady = 5, cursor = 'hand2', command = self.check_register)
        checkHistory_element.grid(row = 3, column = 0, pady = (80, 5), sticky = tk.W + tk.E, padx = 10)
        #FastKey
        self.root_window.bind("<F1>", lambda event: self.check_register())
        CreateToolTip(checkHistory_element, text = '快速键 F1')

        deleteHistory_element = tk.Button(first_frame, text = '删除记录', pady = 5, cursor = 'hand2', command = self.delete_register)
        deleteHistory_element.grid(row = 4, column = 0, pady = 5, sticky = tk.W + tk.E, padx = 10)
        #FastKey
        self.root_window.bind("<F2>", lambda event: self.delete_register())
        CreateToolTip(deleteHistory_element, text = '快速键 F2')


        #-----------------------------------------
        #Second div
        second_frame = tk.Frame(self.root_window)
        second_frame.grid(row = 0, column = 1)

        self.showHistory_searched = ttk.Treeview(second_frame, columns = ("date_time", "total_price", "number_product", "method_pay"), selectmode = tk.EXTENDED, height = 28)
        #Prepare
        self.showHistory_searched.heading('#0', text = 'id', anchor = tk.CENTER)
        self.showHistory_searched.column("#0", width = 230, stretch = False)
        self.showHistory_searched.heading('date_time', text = '时间日期', anchor = tk.CENTER)
        self.showHistory_searched.column("date_time", width = 200, stretch = False)
        self.showHistory_searched.heading('total_price', text = '总共付费', anchor = tk.CENTER)
        self.showHistory_searched.column("total_price", width = 120, stretch = False)
        self.showHistory_searched.heading('number_product', text = '物品数量', anchor = tk.CENTER)
        self.showHistory_searched.column("number_product", width = 110, stretch = False)
        self.showHistory_searched.heading('method_pay', text = '支付方式', anchor = tk.CENTER)
        self.showHistory_searched.column("method_pay", width = 140, stretch = False)

        self.showHistory_searched.grid(row = 0, column = 0)
        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        #-----------------------------
        # Earn frame 
        self.third_frame = tk.Frame(first_frame, bg="#fff")
        self.third_frame.grid(row=7, column = 0, pady = 30, sticky = tk.W + tk.E)

        # Total
        self.total_label_text = tk.Label(self.third_frame, text = '', bg = "#fff", font = ('consolas', 10, 'bold'))
        self.total_label_text.grid(row = 0, column = 0, sticky = tk.W + tk.E, padx = 70, pady = (10, 0))

        self.total_num = tk.Label(self.third_frame, text = '', bg = "#fff", font = ('consolas', 8))
        self.total_num.grid(row = 0, column = 1, sticky = tk.W + tk.E, padx = 70, pady = (10, 0))
        
        # Amount
        self.amount_label_text = tk.Label(self.third_frame, text = '', bg = "#fff", font = ('consolas', 10, 'bold'))
        self.amount_label_text.grid(row = 1, column = 0, sticky = tk.W + tk.E, padx = 70, pady = (10, 0))

        self.amount_num = tk.Label(self.third_frame, text = '', bg = "#fff", font = ('consolas', 8))
        self.amount_num.grid(row = 1, column = 1, sticky = tk.W + tk.E, padx = 70, pady = (10, 0))


        #SCROLL
        showHistoryScroll = tk.Scrollbar(second_frame, orient = tk.VERTICAL, command = self.showHistory_searched.yview)
        showHistoryScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        self.showHistory_searched.configure(yscrollcommand = showHistoryScroll.set)

    def searchData_inDB(self):
        start_date = self.startDate.get_date().strftime("%Y-%m-%d")
        end_date = self.endDate.get_date().strftime("%Y-%m-%d")

        start_time = self.startTime.get()
        end_time = self.endTime.get()

        if (self.checkIf_is_a_timeDate(start_time, 'time') and self.checkIf_is_a_timeDate(end_time, 'time')) and (self.checkIf_is_a_timeDate(start_date, 'date') and self.checkIf_is_a_timeDate(end_date, 'date')):
            query = 'SELECT `id`, `date_time`, `total_price`, `number_product`, `method_pay` FROM `Product_register_pay` WHERE `date_time` BETWEEN ? AND ?'
            parameters = ('{} {}'.format(start_date, start_time), '{} {}'.format(end_date, end_time))
            
            returnResponse = run_sqlite_query(query, parameters = parameters)

            for element in self.showHistory_searched.get_children():
                self.showHistory_searched.delete(element)
            if returnResponse:
                self.show_register_in_table(returnResponse)

                # Earn and total data

                earnData = 0 # set 0 for earn
                for x in returnResponse:
                    earnData = earnData + x[2]
            
                self.total_label_text['text'] = '总共收入'
                self.total_num['text'] = '{:.2f} €'.format(earnData)

                self.amount_label_text['text'] = '总共数量'
                self.amount_num['text'] = '{} 次数'.format(len(returnResponse))
            
            else:
                self.showHistory_searched.insert('', tk.END, text = '空', values = ('没有任何记录', '在这个', '时间', '日期内'))
        else:
            messagebox.showerror('时间格式错误', "请检查时间格式是否有错误， 只可写数字用 hh:mm:ss 格式")
            self.root_window.focus_force()

    def show_register_in_table(self, response):
        for element in response:
            self.showHistory_searched.insert('', tk.END, text = element[0], values = (element[1], element[2], element[3], element[4]))
    
    def check_register(self):
        if self.checkRegister_is_selected():
            item_to_check = self.showHistory_searched.item(self.showHistory_searched.selection())
            if item_to_check['text'] != '空':

                values = (item_to_check['text'], item_to_check['values'][0], item_to_check['values'][1], item_to_check['values'][2], item_to_check['values'][3])
                
                self.open_to_showDataRegister(values)

    def open_to_showDataRegister(self, parameters):
        self.second_window = tk.Toplevel()

        self.second_window.title('数据')
        self.second_window.focus()

        first_frame = tk.Frame(self.second_window)
        first_frame.grid(row = 0, column = 0)

        show_data_table = ttk.Treeview(first_frame, columns = ("name", "price", "amount", "total"), selectmode = tk.EXTENDED, height = 23)

        show_data_table.heading('#0', text = '条码', anchor = tk.CENTER)
        show_data_table.column("#0", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('name', text = '产品', anchor = tk.CENTER)
        show_data_table.column("name", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('price', text = '价格', anchor = tk.CENTER)
        show_data_table.column("price", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('amount', text = '数量', anchor = tk.CENTER)
        show_data_table.column("amount", width = int(self.second_window.winfo_screenwidth()/5), stretch = False)
        show_data_table.heading('total', text = '总价', anchor = tk.CENTER)
        show_data_table.column("total", width = int(self.second_window.winfo_screenwidth()/5)-25, stretch = False)

        ttk.Style().configure('Treeview.Heading', font = ('consolas', 8, 'bold'))

        show_data_table.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)

        #SCROLL
        show_data_tableScroll = tk.Scrollbar(first_frame, orient = tk.VERTICAL, command = show_data_table.yview)
        show_data_tableScroll.grid(row = 0, column = 1, sticky = tk.N + tk.S)

        show_data_table.configure(yscrollcommand = show_data_tableScroll.set)

        #----------------------------
        second_frame = tk.Frame(self.second_window)
        second_frame.grid(row = 1, column = 0, sticky = tk.W + tk.E)

        tk.Label(second_frame, text = 'ID : {}'.format(parameters[0]), font = ('', 10, 'bold')).grid(row = 0, column = 0, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = '时间 : {}'.format(parameters[1]), font = ('', 10, 'bold')).grid(row = 0, column = 1, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = '总共价格 : {}'.format(parameters[2]), font = ('', 10, 'bold')).grid(row = 0, column = 2, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = '物品数量 : {}'.format(parameters[3]), font = ('', 10, 'bold')).grid(row = 0, column = 3, padx = 40, pady = (50, 100))
        tk.Label(second_frame, text = '支付方式 : {}'.format("现金" if parameters[4] == 'money' else "银行卡"), font = ('', 10, 'bold')).grid(row = 0, column = 4, padx = 40, pady = (50, 100))

        query = 'SELECT `data` FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ? AND `method_pay` = ?'

        responseData = run_sqlite_query(query, parameters = parameters)

        if responseData:
            self.json_to_table_register(json.loads(responseData[0][0]), show_data_table)

    def json_to_table_register(self, jsonArr, table):
        for jsonElement in jsonArr['data']:
            table.insert('', tk.END, text = jsonElement['code'], values = (jsonElement['name'], jsonElement['price'], jsonElement['amount'], jsonElement['total_price']))


    def delete_register(self):
        if self.checkRegister_is_selected():
            item_to_delete = self.showHistory_searched.item(self.showHistory_searched.selection())
            if item_to_delete['text'] != '空':
                msgReturn = messagebox.askokcancel('确认', '确定要删这份记录吗? 删完后是无法重新找回的')

                if msgReturn:

                    #--------------
                    parameters = (item_to_delete['text'], item_to_delete['values'][0], item_to_delete['values'][1], item_to_delete['values'][2])
                    #--------------
                    query_add = 'INSERT INTO `Product_deletedRegister_pay` SELECT * FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ?'
                    if run_sqlite_query(query_add, parameters = parameters):
                        query_delete = 'DELETE FROM `Product_register_pay` WHERE `id` = ? AND `date_time` = ? AND `total_price` = ? AND `number_product` = ?'
                        if run_sqlite_query(query_delete, parameters = parameters):
                            messagebox.showinfo('删除', '该记录已被删除')
                            self.root_window.focus_force()

                            self.searchData_inDB()
                            return True

                    messagebox.showerror('删除', '删除过程中出现问题，请重新')
                else:
                    self.root_window.focus_force()

    def checkIf_is_a_timeDate(self, timeDate_str, typeOf):
        if typeOf == 'time':
            checkArr = timeDate_str.split(':')
        else:
            checkArr = timeDate_str.split('-')

        if len(checkArr) == 3:
            
            isNumber = 0

            for num in checkArr:
                if num.isnumeric():
                    isNumber += 1

            if isNumber == 3:
                return True

        return False

    def checkRegister_is_selected(self):
        if len(str(self.showHistory_searched.item(self.showHistory_searched.selection())['text'])) != 0:
            return True
        else:
            messagebox.showerror("错误", "没有任何记录选中， 请选择")
            self.root_window.focus_force()
            return False

#Create ToolTips
class CreateToolTip(object):
    '''
        Create a tooltip
    '''
    def __init__ (self, element, text = 'text'):
        self.toolTip_element = element
        self.toolTip_text = text
        self.toolTip_element.bind("<Enter>", self.enter_toolTip)
        self.toolTip_element.bind("<Leave>", self.close_toolTip)

    def enter_toolTip(self, event = None):
        x = y = 0
        x, y, cx, cy = self.toolTip_element.bbox("insert")

        x += self.toolTip_element.winfo_rootx() + 45
        y += self.toolTip_element.winfo_rooty() + 20

        # Create a toplevel window z-index
        self.toolTip_element_topLevel = tk.Toplevel(self.toolTip_element)
        
        self.toolTip_element_topLevel.wm_overrideredirect(True)
        self.toolTip_element_topLevel.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.toolTip_element_topLevel, text = self.toolTip_text, wraplength = 200, justify = 'left', background='#d8ffa1', relief='solid', borderwidth=1, font=("times", "8", "normal"), padx = 3, pady = 3)
        
        label.pack(ipadx = 1)

    def close_toolTip(self, event = None):
        if self.toolTip_element_topLevel:
            self.toolTip_element_topLevel.destroy()



# newApp
def newAPP():
    root = tk.Tk()
    application = AppOpen(root)
        
    root.mainloop()


#Check if it is the main py
if __name__ == '__main__':
    if not os.path.isfile('./data/database.db') and os.path.isfile('./data/delete.log'):

        prepare_database()
        os.remove('./data/delete.log')
        os.startfile('./readme.txt')

        messagebox.showinfo('数据', '成功安装系统, 可以使用了。 重新点击文件即可使用')



    else:

        newAPP()
        
        
