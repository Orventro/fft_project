#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from Tkinter import *
from math import log, ceil, sqrt
from ctypes import *
from numpy.ctypeslib import ndpointer
import numpy 

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

#loading C++ library
lib = CDLL('./libCpart.so')

inputArrSize = 0

inputArr = []

filePath = ' '
bg = '#eee'
fg = '#111'

timeInMeas = 1

fileInfoStr = 'Открыт файл : {} ; Длительность измерений : {} с ;  Измерений в сек : {} ; Размер : {} байт'
sectorInfoStr='Дисперсия входных значений : {} ; Дисперсия выходных значений {}'

curAmlitude = []

xArr = []
yArr = []

avAmpl = []
disp = []

root = Tk()
root.geometry(str(root.winfo_screenwidth())+'x'+str(root.winfo_screenheight())+'+0+0')
root.title('FFT')

dens_entry_content = StringVar()
step_entry_content = StringVar()
sector_entry_content = StringVar()
trendEnabled = IntVar()

sectorSize = 0
tfSectSize = 0
stepSize = 0
sectorQuantity = 0

def dispersion(a):
  sqAv = 0L
  av = 0L
  for i in a:
    sqAv += i*i
    av += i
  sqAv /= len(a)
  av /= len(a)
  return sqrt(sqAv - av*av)

def plotGraphY(valArray, xl, yl):
  plotGraphXY(valArray, xl, yl, 1)

def plotGraphXY(valArray, xl, yl, xs):
  global botbar, xArr, yArr
  f = matplotlib.figure.Figure(figsize = (5, 5), dpi = 100)
  a = f.add_subplot(111)
  yArr = valArray
  xArr = []
  for i in range(len(valArray)):
    xArr.append(xs * (i + 1))
  a.plot(xArr, valArray, 'b-')
  a.set_xlabel(xl)
  a.set_ylabel(yl)
  for widget in botbar.winfo_children():
    widget.destroy()
  canvas = FigureCanvasTkAgg(f, botbar)
  canvas.show()
  canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)
  toolbar = NavigationToolbar2TkAgg(canvas, botbar)
  toolbar.update()
  canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)

def plothist(valArray, xl, yl):
  global botbar
  f = matplotlib.figure.Figure(figsize = (5, 5), dpi = 100)
  a = f.add_subplot(111)
  a.hist(valArray)
  for widget in botbar.winfo_children():
    widget.destroy()
  canvas = FigureCanvasTkAgg(f, botbar)
  canvas.show()
  canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)
  toolbar = NavigationToolbar2TkAgg(canvas, botbar)
  toolbar.update()
  canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)

def openFileBrowser():
  global filePath
  from tkFileDialog import askopenfilename
  filePath = askopenfilename()
  arrPath = create_string_buffer(filePath)
  size = lib.fileSize(arrPath)
  meas = lib.mInSec(arrPath)
  fileInfo['text'] = fileInfoStr.format(filePath, (size-4)/2.0/meas, meas, size)

def amplitude(plot):
  global inputArr, sectorSize, timeInMeas, tfSectSize, curAmlitude, filePath, inputArrSize
  if plot:
    plotGraphXY(curAmlitude, 'frequency, hz', 'amplitude', 1.0/timeInMeas/sectorSize)
  else:
    return curAmlitude

def readF(ssize, marg, timeinm):
  global sectorSize, inputArrSize, sectorQuantity, fileInfo, midbar, fileInfoStr, inputArr, lib, timeInMeas, stepSize, tfSectSize
  arrPath = create_string_buffer(filePath)
  inputArrSize = int((lib.fileSize(arrPath) - 4) / 2 / lib.mInSec(arrPath) / timeinm)
  lib.readf.restype = ndpointer(dtype = c_int, shape = (inputArrSize,))
  inputArr = lib.readf(arrPath, c_double(timeinm))
  timeInMeas = timeinm
  stepSize = marg
  sectorSize = ssize
  tfSectSize = int(2**ceil(log(ssize, 2)))/2
  sectorQuantity = (inputArrSize - sectorSize) / marg
  midbar.pack_forget()
  midbar.pack(side = TOP, fill = X)
  chooseGraph.delete(0, 1000000)
  for i in range(sectorQuantity):
    chooseGraph.insert(i, i)
  chooseGraph.activate(0)

def onSelectionChange(listbox):
  global curAmlitude, sectorSize, pos, inputArr, inputArrSize
  arr = (c_double * inputArrSize)(0)
  w = listbox.widget
  pos = w.curselection()[0]*stepSize
  for i in range(inputArrSize):
    arr[i] = inputArr[i]
  lib.amplitude.restype = ndpointer(dtype = c_double, shape = (tfSectSize,))
  curAmlitude = lib.amplitude(arr, sectorSize, pos, bool(trendEnabled.get()))[1:]
  sectorInfo['text'] = sectorInfoStr.format(dispersion(inputArr[pos:pos+sectorSize]), dispersion(curAmlitude))

def generalInfo():
  global inputArr, sectorSize, tfSectSize, stepSize, inputArrSize, botbar, avAmpl, disp
  inArr = (c_double * inputArrSize)(0)
  for i in range(inputArrSize):
    inArr[i] = inputArr[i]
  lib.dispGraph.restype = ndpointer(dtype = c_double, shape = (tfSectSize * 2,))
  arr = lib.dispGraph(inArr, inputArrSize, sectorSize, stepSize, bool(trendEnabled.get()))
  f = matplotlib.figure.Figure(figsize = (5, 5), dpi = 100)
  a = f.add_subplot(111)
  xArr = []
  for i in range(tfSectSize - 1):
    xArr.append(1.0/timeInMeas/sectorSize * (i + 1))
  #average amplitude
  avAmpl = arr[1 : tfSectSize]
  a.plot(xArr, avAmpl, 'r-')
  #dispersion
  disp = arr[tfSectSize + 1 :]
  a.plot(xArr, disp, 'b-')
  a.set_xlabel('frequency, hz')
  a.set_ylabel('amplitude')
  for widget in botbar.winfo_children():
    widget.destroy()
  canvas = FigureCanvasTkAgg(f, botbar)
  canvas.show()
  canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = True)
  toolbar = NavigationToolbar2TkAgg(canvas, botbar)
  toolbar.update()
  canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)

def plotInputArr():
  global inputArr, sectorSize, pos, trendEnabled
  if bool(trendEnabled.get()):
    plotGraphXY(
      [inputArr[i] * abs((i - chooseGraph.curselection()[0] * stepSize + sectorSize / 2) % sectorSize - sectorSize / 2)
      for i in range(chooseGraph.curselection()[0] * stepSize, chooseGraph.curselection()[0] * stepSize + sectorSize)]
      , 'seconds', '', timeInMeas)
  else:
    plotGraphXY( inputArr[chooseGraph.curselection()[0] * stepSize : chooseGraph.curselection()[0] * stepSize + sectorSize]
      , 'seconds', '', timeInMeas)

def saveActive():
  global filePath, pos, sectorSize, trendEnabled, timeInMeas
  from tkFileDialog import asksaveasfile, asksaveasfilename
  from time import strftime
  f = asksaveasfile(mode = 'w', defaultextension = '.txt')
  #f = asksaveasfilename(defaultextension = '.txt')
  if f is None:
    return
  text2save  = strftime("%d/%m/%Y  %H:%M:%S") + '  -  Результаты преобразования Фурье файла : ' + str(filePath) + '\n'
  text2save += 'измерений в сек. : ' + str(1 / timeInMeas) + ' , измерения с ' + str(pos) + ' по ' + str(sectorSize) + '\n'
  text2save += 'тренд включен : ' + ('да' if trendEnabled else 'нет') + '\n\n'
  text2save += 'частота        амплитуда\n'
  for i in range(len(yArr)):
    text2save += str(xArr[i]) + ' ' * (15 - len(str(xArr[i]))) + str(yArr[i]) + '\n'
  f.write(text2save)
  f.close()

def saveGenInfo():
  global avAmpl, disp, filePath, timeInMeas, sectorSize, stepSize
  from tkFileDialog import asksaveasfile, asksaveasfilename
  from time import strftime
  f = asksaveasfile(mode = 'w', defaultextension = '.txt')
  #f = asksaveasfilename(defaultextension = '.txt')
  if f is None:
    return
  text2save  = strftime("%d/%m/%Y  %H:%M:%S") + '  -  Результаты преобразования Фурье файла : \n' + str(filePath) + '\n'
  text2save += 'измерений в сек. : '+str(1/timeInMeas)+' отступ : '+str(stepSize)+' длительнсть измерения : '+str(sectorSize) + '\n'
  text2save += 'тренд включен : ' + ('да' if trendEnabled else 'нет') + '\n\n'
  text2save += 'СРЕДНЯЯ АМПЛИТУДА\n\n'
  text2save += 'частота        амплитуда\n'
  generalInfo()
  for i in range(len(avAmpl)):
    text2save += str(1.0/timeInMeas/sectorSize*(i+1)) + ' ' * (15 - len(str(1.0/timeInMeas/sectorSize*(i+1)))) + str(avAmpl[i])+'\n'
  text2save += '\nДИСПЕРСИЯ\n\n'
  for i in range(len(disp)):
    text2save += str(1.0/timeInMeas/sectorSize*(i+1)) + ' ' * (15 - len(str(1.0/timeInMeas/sectorSize*(i+1)))) + str(disp[i]) + '\n'
  f.write(text2save)
  f.close()

#INTERFACE

#top

topbar = Frame(root, bg = bg, padx = 3, pady = 5)
topbar.pack(side = TOP, fill = X)

dens_label = Label(topbar, text = 'квант времени :', bg = bg, fg= fg)
dens_label.pack(side = LEFT)

dens_entry = Entry(topbar, bg = '#fff', fg = fg, width = 9, textvariable = dens_entry_content)
dens_entry.pack(side = LEFT)

step_label = Label(topbar, text = 'смещение :', bg = bg, fg= fg)
step_label.pack(side = LEFT)

step_entry = Entry(topbar, bg = '#fff', fg = fg, width = 9, textvariable = step_entry_content)
step_entry.pack(side = LEFT, padx = 2)

sector_label = Label(topbar, text = 'длительность измерения :', bg = bg, fg = fg)
sector_label.pack(side = LEFT, padx = 2)

sector_entry = Entry(topbar, bg = '#fff', fg = fg, width = 9, textvariable = sector_entry_content)
sector_entry.pack(side = LEFT, padx = 2)

trend_cbox = Checkbutton(topbar, bg = '#fff', fg = fg, variable = trendEnabled, text = 'Включить тренд', onvalue = 1, offvalue = 0)
trend_cbox.pack(side = LEFT, padx = 2)

openFile_btn = Button(topbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff', text = 'открыть файл',
  bd = 0, command = openFileBrowser)
openFile_btn.pack(side = LEFT, padx = 2)

fourier_btn = Button(topbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Преобразование Фурье', bd = 0,
  command = lambda : readF(int(sector_entry_content.get().replace(' ', '')), int(step_entry_content.get().replace(' ', '')), 
    float(dens_entry_content.get().replace(' ', ''))))
fourier_btn.pack(side = LEFT, padx = 2)

generalInfo_btn = Button(topbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Дисперсия', bd = 0, command = generalInfo)
generalInfo_btn.pack(side = LEFT, padx = 2)

saveGenInfo_btn = Button(topbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Сохранить дисперсию', bd = 0, command = saveGenInfo)
saveGenInfo_btn.pack(side = LEFT)

#middle

midbar = Frame(root, bg = bg, padx = 10, pady = 5)

chooseGraph = Listbox(midbar, bg = '#fff', fg = fg, height = 20, width = 8)
chooseGraph.pack(side = LEFT, padx = 10)
chooseGraph.bind('<<ListboxSelect>>', onSelectionChange)

plot_amplitude_graph_btn = Button(midbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Нарисовать график амплитуды', bd = 0, command = lambda : amplitude(True))
plot_amplitude_graph_btn.pack(side = TOP, padx = 5)

plot_input_graph_btn = Button(midbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Нарисовать график входных значений', bd = 0, command = plotInputArr)
plot_input_graph_btn.pack(side = TOP, padx = 5)

distribution_btn = Button(midbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Распределение значений', bd = 0, command = lambda : plothist(amplitude(False), '', ''))
distribution_btn.pack(side = TOP)

saveActive_btn = Button(midbar, bg = '#fff', activebackground = '#58f', fg = fg, activeforeground = '#fff',
  text = 'Сохранить преобразование', bd = 0, command = saveActive)
saveActive_btn.pack(side = TOP)

sectorInfo = Label(midbar, bg = bg, fg = fg, font = 5)
sectorInfo.pack(side = BOTTOM, fill = X)

#bottom

botbar = Frame(root, bg = bg)
botbar.pack(side = TOP, fill = X)

fileInfo = Label(root, bg = bg, fg = fg, font=5)
fileInfo.pack(side = BOTTOM, fill = X)

root.mainloop()