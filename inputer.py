import os
import sys
import webbrowser
from tkinter import Label, Entry, Button, Tk, StringVar, PhotoImage
from tkinter.messagebox import showinfo

# подключение библиотек
# tkinter - графический интерфейс
# os - для работы с файлами, директориями и т.д
# webbrowser - открытие ссылки на my.telegram.org

# директория файлов вшитых в архив (exe)
path = os.getcwd()+"\\data\\ico"
# path = getattr(sys, '_MEIPASS', os.getcwd())

# словарь с текстами элементов на окне
names_for_elements = {"save": ["Сохранить", "Save"],
                      "api_id_label": ["введите api_id", "enter api_id"],
                      "api_hash_label": ["введите api_hash", "enter api_hash"],
                      "text_label": ["Переключите ракладку на en\nДля получения данных нажмите кнопку телеграм",
                                     "Switch the layout to en\nTo receive data, press the telegram button"]
                      }

# словарь с координатами элементов на окне
coordinates = {"save": [250, 100],
               "api_id_label": [-60, 45],
               "api_hash_label": [-47, 70],
               "text_label": [130, 0]}

# словарь элементов
elements = dict()

# первоначальный язык (0 - ru, 1 - en)
lang = 0


# функция кнопки telegram
def open_telegram():
    webbrowser.open('https://my.telegram.org/')


# функция смены языка
def change_lang(btn):
    global lang, imgs, names_for_elements
    lang = abs(lang - 1)
    btn.config(image=imgs[lang])
    for name in names_for_elements.keys():
        elements[name].config(text=names_for_elements[name][lang])


# функция кнопки сохранить
def btn_funk():
    api_id = id_.get()
    api_hash = hash_.get()
    if len(api_hash) == 32 and api_id.isdigit():
        with open(r"data\.env", "w") as fout:
            print('файл создан')
            fout.write(f"api_id = {api_id}\napi_hash = \'{api_hash}\'")
            fout.close()
            root.quit()
            os.startfile('ct.py')
            exit(0)
    else:
        if lang:
            text = "invalid hash or id entered"
        else:
            text = "введен неверный hash или id"
        showinfo('ERROR', text)


root = Tk()  # __init__
root.title("Conversation translator")
root.geometry("570x145")
root.resizable(False, False)
root.iconbitmap(f'{path}\\telegram_icon-icons.com_72055.ico')
# создание окна


id_ = StringVar()  # подключение считывателя из Entry
hash_ = StringVar()

telegram_img = PhotoImage(file=f"{path}\\telegram.gif")
imgs = list()
imgs.append(PhotoImage(file=f"{path}\\russian.gif"))
imgs.append(PhotoImage(file=f"{path}\\english.gif"))

# создание кнопки смены языка
lang_btn = Button(root, image=imgs[lang])
lang_btn.config(command=lambda: change_lang(lang_btn))
lang_btn.place(x=0, y=0)

# создание кнопки открытия браузера
Button(root, image=telegram_img, command=open_telegram).place(x=70, y=0)

# создание всех элементов
elements['api_id_label'] = Label(root, text=names_for_elements['api_id_label'][lang], width=25, height=1, fg='black',
                                 font='arial 15')
elements['api_hash_label'] = Label(root, text=names_for_elements['api_hash_label'][lang], width=25, height=1,
                                   fg='black', font='arial 15')
elements['save'] = Button(root, text=names_for_elements['save'][lang], font='arial 15', bg='blue', fg='black',
                          command=btn_funk)
elements['text_label'] = Label(root, text=names_for_elements['text_label'][lang], fg='black',
                               font='arial 14')
Entry(font='arial 15', width=32, textvariable=id_).place(x=200, y=45)
Entry(font='arial 15', width=32, textvariable=hash_).place(x=200, y=70)

# расположение всех элементов на окне
for i in elements.keys():
    elem = elements[i]
    elem.place(x=coordinates[i][0], y=coordinates[i][1])

# запуск окна
root.mainloop()
