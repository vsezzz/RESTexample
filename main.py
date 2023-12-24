import requests
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import messagebox
import numpy as np


def IndexPlot():
    try:
        tiker = str(ETiker.get())
        shares = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tiker}.json').json()
        if shares['securities']['data'] == []:
            messagebox.showwarning('Ошибка!', f'Несуществующий тикер {tiker}!')
            return 0

        if int(EStartDay.get()) > 31 or int(EStartDay.get()) < 1:
            messagebox.showwarning('Ошибка!', 'Начальный день не может быть больше значения 31 или отрицательным!')
            return 0
        else: start_day = int(EStartDay.get())

        if int(EStartMonth.get()) > 12 or int(EStartMonth.get()) < 1:
            messagebox.showwarning('Ошибка!', 'Начальный месяц не может быть больше значения 12 или отрицательным!')
            return 0
        else:  start_month = int(EStartMonth.get())

        if int(EStartYear.get()) > int(EEndYear.get()):
            messagebox.showwarning('Ошибка!', 'Начальный год не может быть больше конечного года!')
            return 0
        else:
            start_year = int(EStartYear.get())
            end_year = int(EEndYear.get())

        if int(EEndMonth.get()) > 12 or int(EEndMonth.get()) < 1:
            messagebox.showwarning('Ошибка!', 'Конечный месяц не может быть больше значения 12 или отрицательным!')
            return 0
        else: end_month = int(EEndMonth.get())

        if int(EEndDay.get()) > 31 or int(EEndDay.get()) < 1:
            messagebox.showwarning('Ошибка!', 'Конечный день не может быть больше значения 31 или отрицательным!')
            return 0
        else: end_day = int(EEndDay.get())

        if end_year - start_year > 4:
            messagebox.showwarning('Ошибка!', 'Невозможно вывести результат, если разница в годах больше 3!')
            return 0

        shares = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tiker}/candles.json'
                              f'?from={start_year}-{start_month}-{start_day}&till={end_year}-{end_month}-{end_day}&interval=24').json()
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
            end_day = '0'+str(end_day)
        if end_month < 10:
            end_month = '0'+str(end_month)
        enddate = np.datetime64(f'{end_year}-{end_month}-{end_day}')

        if start_day < 10:
            start_day = '0'+str(start_day)
        if start_month < 10:
            start_month = '0'+str(start_month)

        if len(date) == 500 or today == enddate:
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


root = Tk()
root.title("Графики")
root.geometry("300x100")
root.resizable(False, False)

frame = Frame(root, padx=10, pady=10)
frame.pack()

LIndex = Label(frame, text="Введите тикер")
LIndex.grid(column=0, row=0)

ETiker = Entry(frame, width=16)
ETiker.grid(column=1, row=0, columnspan=10)

LStart = Label(frame, text="Введите дату начала торгов")
LStart.grid(column=0, row=1)

EStartDay = Entry(frame, width=5)
EStartDay.grid(column=1, row=1)

EStartMonth = Entry(frame, width=5)
EStartMonth.grid(column=2, row=1)

EStartYear = Entry(frame, width=5)
EStartYear.grid(column=3, row=1)

LEnd = Label(frame, text="Введите дату окончания торгов")
LEnd.grid(column=0, row=2)

EEndDay = Entry(frame, width=5)
EEndDay.grid(column=1, row=2)

EEndMonth = Entry(frame, width=5)
EEndMonth.grid(column=2, row=2)

EEndYear = Entry(frame, width=5)
EEndYear.grid(column=3, row=2)

BImage = Button(frame, text="Изобразить график", command=IndexPlot)
BImage.grid(column=0, row=3)

root.mainloop()
