from tkinter import Tk, ttk, BooleanVar, StringVar
from tkinter import Toplevel, VERTICAL, END, N, S
from tkinter.messagebox import showerror
import requests
from bs4 import BeautifulSoup

import sqlite3
from settings import url


class conn_to_site:
    # Парсим курс доллара
    def __init__(self, url):
        self.url = url

    def make_conn(self):
        try:
            response = requests.get(self.url)
            self.soup = BeautifulSoup(response.text, 'lxml')
            self.find_price()
        except Exception as ex:
            showerror(f"[bold red]Что-то пошло не так!\n{ex}")

    def find_price(self):
        # Пытаемся спарсить курс доллара с сайта
        try:
            price = self.soup.find(
                'td',
                class_='currency-table__rate currency-table__bordered-col'
            )
            price = price.find('div', class_='currency-table__large-text').text
            price = price.replace(',', '.')
            self.price = float(price)
        except Exception as ex:
            showerror.message(f"Что-то пошло не так!\n{ex}")


class conn_to_db:
    # Коннектимся к мускулу и выполняем сказанные задачи
    def conn(self):
        # Присоединяемся к БД, проверяем наличие таблицы
        try:
            with sqlite3.connect('money_sys.db') as conn:
                query = ('''CREATE TABLE IF NOT EXISTS history (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         f_val REAL,
                         s_val REAL,
                         oper INTEGER,
                         time DATETIME)''')
                cursor = conn.cursor()
                cursor.execute(query)

                # Если не получается, то говорим почему
        except sqlite3.Error as err:
            showerror(
                message=f'Что-то пошло не так!\n{err}',
                title='SQL ошибка')

    def select(self):
        try:
            with sqlite3.connect('money_sys.db') as conn:
                query = query = ('''SELECT      id
                                                , f_val
                                                , s_val
                                                , oper
                                                , time
                                    FROM        history
                                    ORDER BY    time DESC
                                ''')

                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()

        except sqlite3.Error as err:
            showerror(
                message=f'Что-то пошло не так!\n{err}',
                title='SQL ошибка'
            )

    def insert(self, f_val, s_val, oper):
        try:
            with sqlite3.connect('money_sys.db') as conn:
                query = f'''INSERT INTO     history(f_val, s_val, oper, time)
                            VALUES          ({f_val}, {s_val},
                            {oper}, DATETIME('NOW'))
                        '''

                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        except sqlite3.Error as err:
            showerror(
                message=f'Что-то пошло не так!!!\n{err}',
                title='SQL ошибка'
            )

    def delete(self, new_str):
        try:
            with sqlite3.connect('money_sys.db') as conn:
                query = (f'''DELETE FROM    history
                             WHERE          id IN ({new_str})
                                            OR "{new_str}" = "0"
                         ''')

                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        except sqlite3.Error as err:
            showerror(
                message=f'Что-то пошло не так!\n{err}',
                title='SQL ошибка'
            )


class win:
    def __init__(self):
        self.window = Tk()
        self.window.title('Рубль в доллар и обратно')
        self.window.geometry('400x300')
        self.frame = ttk.Frame(
            self.window,
        )
        self.frame.pack(expand=True)

    def create_lab_entr(self):
        first_lb = ttk.Label(
            self.frame,
            text="Введите количество денег  "
        )
        first_lb.grid(row=3, column=1)

        second_lb = ttk.Label(
            self.frame,
            text="Итого",
            justify='right'
        )
        second_lb.grid(row=4, column=1)

        self.first_tf = ttk.Entry(
            self.frame,
            font=('Helvetica 11'),
            justify='center'
        )
        self.first_tf.grid(row=3, column=2, pady=5)

        self.str_var = StringVar()
        self.str_var.set('Здесь будет сумма')

        self.second_tf = ttk.Label(
            self.frame,
            font=('Helvetica 11'),
            textvariable=self.str_var
        )
        self.second_tf.grid(row=4, column=2, pady=5)

        self.str_price = StringVar()
        self.str_price.set(
            f'Курс доллара на данный момент: {my_conn_to_site.price}₽'
        )

        price_lb = ttk.Label(
            self.frame,
            font='Helvetica 11',
            justify='center',
            textvariable=self.str_price
        )
        price_lb.grid(
            row=6,
            column=1,
            columnspan=2,
            pady=20
        )

    def create_but(self):

        self.r_var = BooleanVar()
        self.r_var.set(0)

        r_but_one = ttk.Radiobutton(
            self.frame,
            text='Доллар в рубль',
            variable=self.r_var,
            value=1
        )
        r_but_one.grid(row=0, column=1)

        r_but_two = ttk.Radiobutton(
            self.frame,
            text='Рубль в доллар',
            variable=self.r_var,
            value=0)
        r_but_two.grid(row=0, column=2)

        cal_btn = ttk.Button(
            self.frame,
            text='ИТОГО',
            command=lambda: self.choice()
        )
        cal_btn.grid(row=5, column=2)

        his_btn = ttk.Button(
            self.frame,
            text='История',
            command=self.show_his
        )
        his_btn.grid(row=5, column=1)

    def choice(self):
        price = my_conn_to_site.price
        self.val = None
        self.oper = None
        try:
            self.val = float(self.first_tf.get())
        except Exception:
            showerror(message='Неверное выражение!', title='Ошибка ввода')
            return False
        if self.r_var.get() == 1:
            self.oper = 1
            self.str_var.set(f'{calc.to_rub(price=price, val=self.val)}₽')
        else:
            self.oper = 0
            self.str_var.set(f'{calc.to_dol(price=price, val=self.val)}$')

    def show_his(self):
        new_win = Toplevel(self.window)
        new_win.title('История')
        new_win.geometry('300x400')

        colums = ('#1', '#2', '#3', '#4', '#5')
        tree = ttk.Treeview(new_win, show='headings', columns=colums)
        tree.heading('#1', text='id')
        tree.heading('#2', text='Перв_знач')
        tree.heading('#3', text='Втор_знач')
        tree.heading("#4", text="Действие")
        tree.heading("#5", text="Время")
        ysb = ttk.Scrollbar(new_win, orient=VERTICAL, command=tree.yview)
        tree.configure(yscroll=ysb.set)

        array = my_conn_to_db.select()
        for info in array:
            tree.insert("", END, values=info)

        tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky=N + S)
        new_win.rowconfigure(0, weight=1)
        new_win.columnconfigure(0, weight=1)

        new_win.mainloop()

    def loop(self):
        self.window.mainloop()


class calc:
    @classmethod
    def to_rub(cls, price, val):
        result = val * price
        return calc.ret(result=result)

    @classmethod
    def to_dol(self, price, val):
        result = val / price
        return self.ret(result=result)

    @classmethod
    def ret(self, result):
        fin = None
        if result % 1 == 0:
            result = int(result)
        if 0 < result < 0.1:
            fin = round(result, 4)
        elif result > 1000000000000 or result < 0:
            showerror(message='Try harder')
            return ''
        else:
            fin = round(result, 2)
        my_conn_to_db.insert(
            my_win.val,
            my_conn_to_site.price,
            my_win.oper)
        return fin


if __name__ == '__main__':
    my_conn_to_site = conn_to_site(url=url)
    my_conn_to_site.make_conn()

    my_conn_to_db = conn_to_db()
    my_conn_to_db.conn()

    my_win = win()
    my_win.create_lab_entr()
    my_win.create_but()
    my_win.loop()
