#-*-coding:utf-8-*-

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import configparser
import subprocess as sp
import os
import sys
import re
import time

maj_version = 1
min_version = 2

info = f'''
18.01.2021 - AVA - Create
version: {maj_version}-{min_version}
Програма-помощник по работе с SQL-запросами (с графическим интерфейсом)
При запуске откроется окно, в которое потребуется ввести некоторую информацию (названия таблицы, условия выборки и т.д.)

***Аутентификация***
При первом запуске потребуется подключиться к БД. После аутентификации, данные сохраняются для последующих запусков.
Однако, если потребуется подключиться к другой БД, можно нажать кнопку "Аутентификация" и произвести ввод новых данных
Поля названия таблицы и output файла так же сохранятся и при следующем запуске появятся в полях ввода автоматически.

***Условия***
Что бы добавить условие выборки, нажмите на "Добавить условие". Появившуюся строку можно убрать, нажав, "Убрать строку" справа
    - Пункт условия. Название поля сравнения;
    - Знак сравнения. Доступны несколько "><, I=, like, in, not in";
    - Значение. Если числа нужно представить как строку, то обязательно использовать одинарные кавычки. В случае ввода 
    даты, использовать синтаксис вида: date'YYYY-MM-DD" В прочих случаях, программа сама форматирует строку. Несколько 
    значений нужно вводить через запятую.

***Формирование запроса***
После ввода, нужно сформировать запрос для проверки, нажав соответствующую кнопку. Если запрос удовлетворяет требованиям,
можно переходить к запуску.

***Запуск***
После нажатия на кнопку "Запуск" (и возможно некоторого времени, которое потребуется на выгрузку) в директории
запуска появится csv-файл с требуемой информацией.

Алленов Владимир
a2lenov@mail.ru
'''

class MainWindow(tk.Tk):
    def __init__(self):#,master=None):
        super(). __init__()
        self._HEIGHT = 500
        self._WIDTH = 900
        self.title('QueryHelper') #название окна
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._work_dir = os.getcwd()
        self._connect_data = ''
        self._TEMP = os.environ.get('LOCALAPPDATA') #директория с ini-файлом
        self._spool = f'spool {self._work_dir}'
        self._list_of_widgets = []
        self._list_of_condition = []
        self._query = '' #запрос
        self._DB_username = ''
        self._DB_passwd = ''
        self._DB_server_name = ''
        self._table_name = '' #название таблицы
        self._sort_field = '' #поле сортировки
        self._output_file_name = '' #название конечного файла
        self._auth = False
        self._break_flag = False
        self._config = configparser. RawConfigParser()
        self._create_widgets()
        self._servers_dict = {'OLAP':'crn.rs.ru:000/TNS','DWH':'dwn.rs.ru:0800/TNS','OLTP':'crn-dialer.rs.ru:0800/TNS'}
        self._count_of_condition = 0 #количество условий
        self._select = 'select * from'

        self._sqlp_settings = '''
-- https://chartio.com/resources/tutorials/how-to-write-to-a-csv-file-using-oracle-sql-plus/
-- Sqlplus/nolog @exp.sqlp
set echo off
set colsep,
set headsep off
set pagesize 0
set trimspool on
set linesize 32000
set numwidth 15
set feedback off\n'''

        #Если еще нет іnі файла, то аутентификация и сохранение в QueryHelper.ini
        if not os.path.exists(f'{self._TEMP}\\QueryHelper.ini'):
            self._auth_form()
        else:
            self._ini_import()
        self._check_version()
        try:
            self._ent.insert(tk.INSERT, self._table_name)
            self._e_sort.insert(tk.INSERT, self._sort_field)
            self._E_of.insert(tk.INSERT, self._output_file_name)
            self._query_space.insert(tk.INSERT, self._query)
        except Exception as e:
            pass

    def _create_widgets(self):
        "Инициализация основных виджетов окна"
        self._main_buttons_width = 20
        self._tn = tk. Label(self, text='Название таблицы:')
        self._tn.grid(row = 1, column = 1)
        self._list_of_widgets.append(self._tn)
        #Поле ввода названия таблицы
        self._ent = tk.Entry(self, width=40)
        self._ent.grid(row = 1, column = 2)
        self._list_of_widgets.append(self._ent)
        #Добавление строки условия
        self._add = tk.Button(self, text='Добавить условие', command=self._add_condition)
        self._add.grid(row=2, column=1)
        self._list_of_widgets.append(self._add)
        #Названия полей каждого условия
        self._L_pu = tk.Label(self, text='Пункт условия')
        self._L_pu.grid(row=2, column=2)
        self._L_pu.grid_remove()
        self._L_zs = tk.Label(self, text='Знак сравнения')
        self._L_zs.grid(row=2, column=3)
        self._L_zs.grid_remove()
        self._L_value = tk.Label(self, text='Значение')
        self._L_value.grid(row=2, column=4)
        self._L_value.grid_remove()
        self._I_sort = tk.Label(self, text='Поле сортировки (если требуется):')
        self._I_sort.grid(row = 96, column = 1)
        self._list_of_widgets.append(self._I_sort)
        #Поле по которому будет производиться сортировка
        self._e_sort = tk.Entry(self, width=40)
        self._e_sort.grid(row = 96, column = 2)
        self._list_of_widgets.append(self._e_sort)
        #Основная кнопка запуска
        self._query_form = tk. Button(self,
                                      text="Сформировать запрос",
                                      width=self._main_buttons_width,
                                      command=self._show_query)
        self._query_form.grid(row = 97, column= 2)
        self._list_of_widgets.append(self._query_form)
        #Основная кнопка аутентификации
        self._B_auth = tk.Button(self,
                                 text="Аутентификация",
                                 width=self._main_buttons_width,
                                 command=self._auth_form)
        self._B_auth.grid(row = 97, column = 4)
        self._list_of_widgets.append(self._B_auth)
        #Помощь
        self._help = tk.Button(self, text="Help", command=self._help)
        self._help.grid(row = 97, column = 5)
        #self._list_of_widgets.append(self._help)
        #Вывод запроса
        self._query_space = tk.Text(self, width=110, height=10)
        self._query_space.grid(row = 98, column = 1, columnspan = 5)
        self._list_of_widgets.append(self._query_space)
        self._L_of = tk. Label(self, text='Название output файла:')
        self._L_of.grid(row = 99, column = 1)
        self._list_of_widgets.append(self._L_of)
        #Поле ввода названия таблицы
        self._E_of = tk.Entry(self, width=50)
        self._E_of.grid(row = 99, column = 2)
        self._list_of_widgets.append(self._E_of)
        #Автоген имени файла (export_YYYY_MM_DD.csv)
        self._def_file_name = tk.Button(self, text="По умолчанию", command=self._autogen_file_name)
        self._def_file_name.grid(row = 99, column = 3)
        self._list_of_widgets.append(self._def_file_name)
        #Вывод сообщений и хода выполнения
        self._info_space = tk.Text(self, width=110, height=10)
        self._info_space.grid(row = 100, column = 1, columnspan = 5)
        self._info_space.insert(tk.INSERT, '''После нажатия кнопки "Запуск" может понадобится какое-то время на 
выполнение требуемого запроса и формирования файла с ответом. Процесс можно посмотреть на втором окне, 
которое открылось при запуске''')
        self._list_of_widgets.append(self._info_space)
        #вкл/выкл отладчик
        '''self._chk_state = tk. BooleanVar()
        self._chk_state.set(False) # задайте проверку состояния чекбокса
        self._chk = trk. Checkbutton(self, text="Отладчик", varself._chk_state)
        self._chk.grid(row = 101, column = 3)
        self._list_of_widgets.append(self._chk)'''
        #Основная кнопка запуска
        self._mainbut = tk.Button(self, text="Запуск", width=self._main_buttons_width, command=self._get_result)
        self._mainbut.grid(row = 101, column = 4)
        self._list_of_widgets.append(self._mainbut)
        #Кнопка выхода
        self._exit = tk.Button(self, text="Выход", command=self._exit)
        self._exit.grid(row = 101, column = 5)
        self._list_of_widgets.append(self._exit)

    def _ini_import(self):
        '''
        Раскрытие inl файла в переменные класса
        '''
        self._config.read(f'{self._TEMP}\\QueryHelper.ini')
        if self._config.has_option('LAST', 'table_name'):
            self._table_name = self._config['LAST']['table_name']
        if self._config.has_option('LAST', 'sort_field'):
            self._sort_field = self._config['LAST']['sort_field']
        if self._config.has_option('LAST', 'output_file_name'):
            self._output_file_name = self._config['LAST']['output_file_name']
        if self._config.has_option('LAST', 'query'):
            self._query = self._config['LAST']['query']
        if not self._config.has_option('DB', 'username'):
            self._auth = False
            return
        else:
            self._DB_username = self._config['DB']['username']
        if not self._config.has_option('DB', 'password'):
            self._auth = False
            return
        else:
            self._DB_passwd = self._config['DB']['password']
        if not self._config.has_option('DB', 'server_name'):
            self._auth = False
            return
        else:
            self._DB_server_name = self._config['DB']['server_name']
        self._auth = True

    def _ini_save(self):
        '''
        Сохранение изменений в іnі-файл
        '''
        with open(f'{self._TEMP}\QueryHelper.ini', 'w') as f:
            self._config.write(f)

    def _check_version(self):
        '''
        Проверка версии проекта и обновление (если потребуется)
        '''
        if not self._config.has_section('MAIN'):
            self._config.add_section('MAIN')
        up_major = False
        if not self._config.has_option('MAIN', 'maj_version'):
            self._config.set('MAIN','maj_version', str(maj_version))
        else:
            up_major = True if maj_version > int(self._config.get('MAIN','maj_version')) else False
        up_minor = False

        if not self._config.has_option('MAIN', 'min_version'):
            self._config.set('MAIN','min_version', str(min_version))
        else:
            up_minor = True if min_version > int(self._config.get('MAIN', 'min_version')) else False
        self._update_version(up_major, up_minor)
        self._config.set('MAIN','maj_version', str(maj_version))
        self._config.set('MAIN','min_version', str(min_version))

    def _update_version(self, major, minor):
        '''
        Процедура на случай, если после внесения изменений в проект, потребуется что-то сделать
        программой
        '''
        if major:
            pass
        if minor:
            pass

    #Авторенерация имени выходного файла
    def _autogen_file_name(self):
        tm = time.gmtime(time.time())
        mon = tm.tm_mon if len(str(tm.tm_mon)) > 1 else 'O' + str(tm.tm_mon)
        day = tm.tm_mday if len(str(tm.tm_mday)) > 1 else 'O' + str(tm.tm_mday)
        self._output_file_name = f'export_{tm.tm_year}_{mon}_{day}.csv'
        self._E_of.delete(0, 'end')
        self._E_of.insert(tk.INSERT, self._output_file_name)

    def _add_condition(self):
        '''
        Добавление строки условия
        '''
        #Увеличение окна после добавления новой строки
        self._HEIGHT += 25
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')

    def _add_condition(self):
        '''
        Добавление строки условия
        '''
        #Увеличение окна после добавления новой строки
        self._HEIGHT += 25
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        if not self._count_of_condition:
            self._L_pu.grid()
            self._L_zs.grid()
            self._L_value.grid()
        self._count_of_condition += 1
        ent = tk.Entry(self, width=40)
        ent.grid(row=self._count_of_condition + 2, column=2)
        ent2 = ttk.Combobox(self, width=10, values=['=','>','<','!=','like','in','not in'])
        ent2.grid(row=self._count_of_condition + 2, column=3)
        ent3 = tk.Entry(self, width=30)
        ent3.grid(row=self._count_of_condition + 2, column=4)

        #Кнопка удаления данной строки
        delete = tk.Button(self, text=f'Удалить строку')
        delete.grid(row=self._count_of_condition + 2, column=5)
        delete['command'] = lambda: self._delete_condition(delete.grid_info()['row']-3)
        self._list_of_condition.append([ent, ent2, ent3, delete])

    def _delete_condition(self, condition):
        "Удаление строки условия"
        #Уменьшение окна после удаления строки
        self._HEIGHT -= 25
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._count_of_condition -= 1
        if not self._count_of_condition:
            self._L_pu.grid_remove()
            self._L_zs.grid_remove()
            self._L_value.grid_remove()
        for cond in self._list_of_condition[condition]:
            cond.destroy()
        self._list_of_condition.pop(condition)

        #Смещение полей и кнопок, идущих ниже удаленной
        for string in self._list_of_condition[condition:]:
            for element in string:
                element.grid(row=element.grid_info()['row']-1)

    def _get_result(self):
        '''
        Запуск основной процедуры выполнения запроса и записи результата в файл
        '''
        if not self._auth:
            mb.showerror('Ошибка!', 'Не произведена аутентификация!')
            return
        if not self._E_of.get():
            mb.showerror('Ошибка!','Название output файла не заполнено!')
            return
        if not self._query:
            mb.showerror('Ошибка!','Сначала сформируйте запрос!')
            return
        '''Проверка, был ли сформирован запрос повторно после внесения изменений в пoля ввода
        self._query_build()
        if self._query_space.get(1.0, 'end').strip() I= self._query.strip():
        mb.showwarning('Предупреждениеl","Вы исправили информацию в полях ввода, но не нажали "Сформировать запрос"!')
        return!'''
        #Если поле с названием таблицы пустое, то ошибка
        if self._ent.get():
            self._query_build()
            if self._break_flag:
                self._break_flag = False
                return
            #Запись в config названия последней таблицы
            if not self._config.has_section('LAST'):
                self._config.add_section('LAST')
            self._config.set('LAST', 'table_name', self._ent.get())
            #и последнего запроса
            self._config.set('LAST','query', self._query_space.get(1.0, 'end'))
            #Запись в config названия последнего поля сортировки
            if self._e_sort.get():
                self._config.set('LAST','sort_field', self._e_sort.get())
            if self._E_of.get():
                if self._E_of.get()[-4:] != r'.csv':
                    self._output_file_name = self._E_of.get() + r'.csv'
                    self._config.set('LAST','output_file_name', self._E_of.get() + r'.csv')
                else:
                    self._output_file_name = self._E_of.get()
                    self._config.set('LAST','output_file_name', self._E_of.get())
            self._ini_save()
            self._output_file_name = fr'{self._work_dir}\{self._output_file_name}'.split(r'\\')
            #self._output_file_name = #self._output_file_name'
            #Ограждение двойными ковычками директорий с пробелами
            self._output_file_name = r'\\'.join([i if' ' not in i else fr'''{i}''' for i in self._output_file_name])
            print(self._output_file_name)

            #Формирование информации для .sqlp файла
            self._final = self._sqlp_settings
            self._connect_data = f'''connect {self._DB_username}/{self._DB_passwd}@{self._servers_dict[self._DB_server_name]}'''
            self._final += f'{self._connect_data}\n\nspool (self._output_file_name)\n\n'
            #self._final += self._query
            self. final += self._query_space.get(1.0, 'end')
            self._final += '\nspool off \nexit'
            try:
                os.mkdir(f'{self._work_dir}\\files')
            except OSError as e:
                pass

            #Формирование .sqlp файла
            with open(f'{self._work_dir}\\files\\exp_csv.sqlp', 'w') as f:
                f.write(self._final)
            #if self._chk_state.get():
            #stream = os.popen('sqlplus/nolog @files\\exp_csv.sqlp')
            stream = sp. Popen(['sqlplus', '/nolog', '@files\\exp_csv.sqlp'])

            #output = stream.read()
            #stream.wait()
            #self._error = research(r(ORA-\d{5}:. *\n) | (SP2-\d{4}:. *\n)", output)
            #if self._error:
                #print(self._error.group(0)[self._error.group(0).find(r':') + 2:))
            # os.remove(self._output_file_name) )
            # mb.showerror("Ошибкаl",fОшибка при извлечении информации\n(self._error.group(0)))
            # return
            #else:
            # os.system('sqlplus /nolog @files\\exp_csv.sqlp %*')
            self._info_space.delete(0.0, 'end')
            self._info_space.insert(tk.INSERT, f'''Процесс выгрузки из БД будет отображаться в окне консоли. По 
окончании, вся требуемая информация будет находиться в файле {self._output_file_name}''')
            mb.showinfo("Готово!", f'''Процесс выгрузки из БД будет отображаться в окне консоли. По окончании, вся 
требуемая информация будет находиться в файле {self._output_file_name}''')
        else:
            mb.showerror('Ошибка! Не введено название таблицы')

    def _show_query(self):
        '''
        Отрисовка запроса в поле вывода
        '''
        if not self._ent.get():
            mb.showerror('Ошибка!', 'Не введено название таблицы')
            return
        self._query_build()
        self._query_space.delete(0.0, 'end')
        self._query_space.insert(tk.INSERT, self._query)

    def _query_build(self):
        '''
        Конструирование запроса из входных полей
        '''
        self._query = f'{self._select} {self._ent.get()}'
        if self._count_of_condition:
            self._conditions = ''
            for string in self._list_of_condition:
                tmp = ''
                for element in range(len(string)):
                    if 'entry' in str(string[element]).lower() or 'combobox' in str(string[element]).lower():
                        if not string[element].get():
                            mb.showerror("Ошибка!", '''Не заполнено одно или несколько полей услови(й)\nЗаполните их или удалите строку(и) условия''')
                            self._query += ';'
                            self._break_flag = True
                            return
                        if element == 2:
                            tmp += self._string_converter(string[element].get())
                        else:
                            tmp += f'{string[element].get()}'
                    if tmp != '':
                        self._conditions += '\nand' + tmp
                self._query += 'where 1=1'
                self._query += self._conditions
            if self._e_sort.get():
                self._query += f'\norder by {self._e_sort.get()};\n\n'
        else:
            self._query += ';\n\n'

    def _string_converter(self, string):
        '''
        Преобразование входящей строки
        1) если число, то возвращается оно же
        2) строка оборачивается одинарными ковычками
        3) дата вида dаtа'YYY-MM-DD' остается без изменений
        Функция создана на всякий случай, так как предполагаю, что вариантов будет больше
        '''
        #Если несколько значений в строке
        if ',' in string:
            finlist = []
            lst = string.split(',')
            lst = [i.strip() for i in lst]
            for element in lst:
                if not element: continue
                if element[0] == "'" and element[-1] == "'":
                    finlist.append(element)
                    continue
                try:
                    int(element)
                except Exception:
                    if 'date''' in element:
                        finlist.append(element)
                    else:
                        finlist.append(f'\'{element}\'')
                else:
                    finlist.append(element)
            return '/' + ','.join(finlist) + ')'
        else:
            if string[0] == "'" and string(-1) == "'":
                return string
            try:
                int(string)
            except Exception:
                if'date''' in string:
                    return string
                else:
                    return f'\'{string}\''
            else:
                return string

    def _help(self):
        mb.showinfo('Информация о программе', info)

    #Скрыть/показать виджеты !
    def _show_hide_widgets(self, visible=True, *list_of_lists):
        for lst in list_of_lists:
            if lst:
                for el in lst:
                    if isinstance(el, list): [i.grid() if visible else i.grid_remove() for i in el]
                    else:
                        el.grid() if visible else el.grid_remove()

    #Запуск формы аутентификации
    def _auth_form(self):
        columnspan = 4 #Ширина кнопок
        pady = 3 #расстояние между полями ввода (сверху/снизу)
        self.geometry(f'{400}x{120}')
        self._show_hide_widgets(False, self._list_of_widgets, self._list_of_condition)
        self._auth_windows = []
        self._L_login = tk. Label(self, text='Логин:')
        self._L_login.grid(row = 1, column = 1)
        self._auth_windows.append(self._L_login)
        #Поле ввода названия таблицы
        self._ent1 = tk.Entry(self, width=50)
        self._ent1.grid(row = 1, column = 2, columnspan = columnspan, pady = pady)
        self._ent1.insert(0,self._DB_username)
        self._auth_windows.append(self._ent1)
        self._L_password = tk. Label(self, text='Пароль:')
        self._L_password.grid(row = 2, column = 1)
        self._auth_windows.append(self._L_password)
        #Поле ввода пароля
        self._ent2 = tk.Entry(self, width=50, show="*")
        self._ent2.grid(row = 2, column = 2, columnspan= columnspan, pady = pady)
        self._ent2.insert(0,self._DB_passwd)
        self._auth_windows.append(self._ent2)
        self._L_DSN = tk.Label(self, text='Cepeep:')
        self._L_DSN.grid(row = 3, column = 1)
        self._auth_windows.append(self._L_DSN)
        #Поле ввода названия сервера
        self._ent3 = ttk.Combobox(self, width=47, values=['OLAP', 'DWH', 'OLTP'])
        self._ent3.grid(row = 3, column = 2, columnspan = columnspan, pady = pady)
        self._ent3.insert(0,self._DB_server_name)
        self._auth_windows.append(self._ent3)
        self._B_save = tk.Button(self, text="Сохранить", command=self._get_values)
        self._B_save.grid(row=97, column=2)
        self._auth_windows.append(self._B_save)
        self._B_cancel = tk.Button(self, text="Отмена", command=self._cancel)
        self._B_cancel.grid(row=97, column=3)
        self._auth_windows.append(self._B_cancel)

    #Получение значений аутентификации
    def _get_values(self):
        if self._ent1.get() and self._ent2.get() and self._ent3.get():
            self._DB_username = self._ent1.get()
            self._DB_passwd = self._ent2.get()
            self._DB_server_name = self._ent3.get()
            if not self._config.has_section('DB'):
                self._config.add_section('DB')
            self._config.set('DB', 'username', self._DB_username)
            self._config.set('DB', 'password', self._DB_passwd)
            self._config.set('DB','server_name', self._ent3.get())
            self._ini_save()
            self._auth = True
            self._show_hide_widgets(False, self._auth_windows)
            self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
            self._show_hide_widgets(True, self._list_of_widgets, self._list_of_condition)
        else:
            mb.showerror('Ошибка!",Одно или несколько полей не заполнены')

    def _cancel(self):
        if not self._auth:
            # os.remove(f'{self._TEMP}\\QueryHelper.ini')
            exit()
        for el in self._auth_windows:
            el.destroy()
        self.geometry(f'{self._WIDTH}x{self._HEIGHTY}')
        self._show_hide_widgets(True, self._list_of_widgets, self._list_of_condition)

    def _exit(self):
        self.destroy()
        exit()


if __name__ =="__main__":
    MW = MainWindow()
    MW.mainloop()
