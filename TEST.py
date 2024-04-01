import requests
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import numpy as np


def indexplot():
    try:
        tiker = str(ChooseTiker.get())

        mark = str(ChooseMarket.get())
        market = name[title.index(mark)]
        shares = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/{market}/securities/{tiker}.json').json()

        if not shares['securities']['data'] or tiker == '':
            messagebox.showwarning('Ошибка!', f'Несуществующий тикер {tiker}!')
            return 0

        e_start_info = EStart.get().split('.')
        e_end_info = EEnd.get().split('.')
        if len(e_start_info) != 3 or len(e_end_info) != 3:
            messagebox.showwarning('Ошибка!', 'Введите дату в формате дд.мм.гггг')
            return 0

        if int(e_start_info[0]) > 31 or int(e_start_info[0]) < 1 or int(e_end_info[0]) > 31 or int(e_end_info[0]) < 1:
            messagebox.showwarning('Ошибка!', 'День не может превышать значение 31 или быть отрицательным!')
            return 0
        else:
            start_day = int(e_start_info[0])
            end_day = int(e_end_info[0])

        if int(e_start_info[1]) > 12 or int(e_start_info[1]) < 1 or int(e_end_info[1]) > 12 or int(e_end_info[1]) < 1:
            messagebox.showwarning('Ошибка!', 'Месяц не может превышать значения 12 или быть отрицательным!')
            return 0
        else:
            start_month = int(e_start_info[1])
            end_month = int(e_end_info[1])

        if int(e_start_info[2]) > int(e_end_info[2]):
            messagebox.showwarning('Ошибка!', 'Начальный год не может быть больше конечного года!')
            return 0
        else:
            start_year = int(e_start_info[2])
            end_year = int(e_end_info[2])

        shares = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/{market}/securities/{tiker}/candles.json'
                              f'?from={start_year}-{start_month}-{start_day}'
                              f'&till={end_year}-{end_month}-{end_day}&interval=24').json()

        if shares['candles']['data'] == [] or len(shares['candles']['data']) == 1:
            messagebox.showwarning('Ошибка!', f'Нет данных. Неверно выбрана дата.')
            return 0

        today = requests.get('http://worldtimeapi.org/api/timezone/europe/moscow').json()
        today = np.datetime64(today['datetime'][0:10])

        date = []
        money = []
        for colum in shares['candles']['data']:
            date.append(np.datetime64(colum[6][0:10]))
            money.append(colum[1])

        if end_day < 10:
            end_day = '0' + str(end_day)
        if end_month < 10:
            end_month = '0' + str(end_month)
        enddate = np.datetime64(f'{end_year}-{end_month}-{end_day}')

        while date[-1] != enddate:
            date_upd = requests.get(
                f'http://iss.moex.com/iss/engines/stock/markets/{market}/securities/{tiker}/candles.json'
                f'?from={date[-1] + 1}&till={enddate}&interval=24').json()
            if not date_upd['candles']['data']:
                break
            for colum in date_upd['candles']['data']:
                date.append(np.datetime64(colum[6][0:10]))
                money.append(colum[1])

        if today == enddate or date[-1] < enddate:
            messagebox.showwarning('Внимание!',
                                   f'Возможно, выведен результат не за весь выбранный период! '
                                   f'\nОтображен период с {date[0]} до {date[-1]}')

        graphic, graph = plt.subplots()
        graph.plot(date, money)
        cdf = mpl.dates.ConciseDateFormatter(graph.xaxis.get_major_locator())
        graph.xaxis.set_major_formatter(cdf)

        tiker_plot = Toplevel(root)
        tiker_plot.resizable(False, False)
        tiker_plot.title(f'{tiker} plot')
        tiker_plot.geometry("650x510")

        label = Label(tiker_plot, text=f'График для котировок {tiker} в дату {date[0]}-{date[-1]}')
        label.pack(side=TOP)

        canvas = FigureCanvasTkAgg(graphic, master=tiker_plot)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=BOTTOM, expand=1)
    except ValueError:
        messagebox.showwarning('Ошибка!', 'Значения в ячейках ввода дат должны быть целочисленными!')


def callback(eventObject):
    tik = ChooseMarket.get()
    nam = name[title.index(tik)]
    rolling_tiker = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/{nam}/securities.json?iss.meta=off'
                                 f'&iss.only=securities&securities.columns=SECID').json()
    combo_data_tiker = []
    for l in range(len(rolling_tiker['securities']['data'])):
        combo_data_tiker.append(rolling_tiker['securities']['data'][l])
    combo_data_tiker = tuple(combo_data_tiker)
    ChooseTiker.config(values=combo_data_tiker)


root = Tk()
root.title("Графики")
root.geometry("530x130")
root.resizable(False, False)

frame = Frame(root, padx=10, pady=10)
frame.pack()

LMarket = Label(frame, text="Выберите рынок")
LMarket.grid(column=0, row=0)

LIndex = Label(frame, text="Введите или выберите тикер")
LIndex.grid(column=0, row=1)

name_req = requests.get(f'http://iss.moex.com/iss/engines/stock/markets.json'
                        f'?iss.meta=off&iss.only=markets&markets.columns=NAME').json()
title_req = requests.get(f'http://iss.moex.com/iss/engines/stock/markets.json'
                         f'?iss.meta=off&iss.only=markets&markets.columns=title').json()
name = []
title = []
for i in range(len(name_req['markets']['data'])):
    name.append(name_req['markets']['data'][i])
    title.append(title_req['markets']['data'][i])
name = sum(name, [])
title = sum(title, [])

title_var = StringVar(value=title[1])
ChooseMarket = ttk.Combobox(frame, textvariable=title_var, values=title, state="readonly")
ChooseMarket.grid(column=1, row=0)

ChooseTiker = ttk.Combobox(frame, width=37)
ChooseTiker.grid(row=1, column=1)
ChooseTiker.bind('<ButtonPress>', callback)

LStart = Label(frame, text="Введите дату начала торгов (дд.мм.гггг)")
LStart.grid(column=0, row=2)

EStart = Entry(frame, width=16)
EStart.grid(column=1, row=2)

LEnd = Label(frame, text="Введите дату окончания торгов (дд.мм.гггг)")
LEnd.grid(column=0, row=3)

EEnd = Entry(frame, width=16)
EEnd.grid(column=1, row=3)

BImage = Button(frame, text="Изобразить график", command=indexplot)
BImage.grid(column=0, row=4)

root.mainloop()
