import tkinter as tk
from functools import partial
#from tkinter.ttk import Combobox

HEIGHT = 500
WIDTH = 500

class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self._master = master
        self._count_of_condition = 0
        self._list_of_condition = []

        self._create_widgets()

    def _create_widgets(self):
        self._tn = tk.Label(root, text='Название таблицы:')
        self._tn.grid(row = 1, column = 1)
        self._ent = tk.Entry(root, width=50)
        self._ent.grid(row = 1, column = 2)
        self._add = tk.Button(root, text="Добавить условие", command=self._add_condition)
        self._add.grid(row=2, column=1)
        #print(self._add.grid_info()['row'])
        #self._add = tk.Button(root, text="Добавить условие", command=self._add_condition).grid(row=2, column=1)
        self._mainbut = tk.Button(root, text="Запуск", command=self.get_result)
        self._mainbut.grid(row = 100, column = 2)
        #print(self._mainbut.grid_info()['row'])

    def _add_condition(self):
        self._count_of_condition += 1
        print('COUNT+ ', self._count_of_condition)
        tn = tk.Label(root, text='Пункт условия:')
        tn.grid(row=self._count_of_condition + 2, column=1)
        ent = tk.Entry(root, width=50)
        ent.grid(row=self._count_of_condition + 2, column=2)
        #sign = ttk.ComboBox(values=(1, 2, 3, 4, 5, "Текст"))\
        #    .grid(row=self._count_of_condition + 2, column=3)
        #combo['values'] = (1, 2, 3, 4, 5, "Текст")
        #print(tn.grid_info()['row'])
        delete = tk.Button(root, text=f"{self._count_of_condition}-", command=partial(self._delete_condition, ent.grid_info()['row']-3))
        delete.grid(row=self._count_of_condition + 2, column=3)
        '''for i in range(0,len(dir(tk.Button))-10,10):
            print(dir(tk.Button)[i:i+10])'''
        print('ADD', [tn, ent, delete])
        self._list_of_condition.append([tn, ent, delete])
        for i in range(len(self._list_of_condition)):
            print(f'\n{i}', self._list_of_condition[i])

    def _delete_condition(self, condition):
        print('PRESS ', self._list_of_condition[condition][2])
        print('COND', condition)
        '''print(len(self._list_of_condition))
        for i in self._list_of_condition[condition]:
            print(type(i))'''
        self._count_of_condition -= 1
        print('COUNT- ', self._count_of_condition)
        print('DESTROY', self._list_of_condition[condition])
        for cond in self._list_of_condition[condition]:
            cond.destroy()
        print('POP', self._list_of_condition.pop(condition))
        for i in range(len(self._list_of_condition)):
            print(f'\n{i}', self._list_of_condition[i])

    def get_result(self):
        pass

root = tk.Tk()
root.title('QueryHelper')  # Название окна
root.geometry(f'{WIDTH}x{HEIGHT}')
MW = MainWindow(master=root)

#def main_move_loop():

#    root.after(5,main_move_loop)

#main_move_loop()
MW.mainloop()
