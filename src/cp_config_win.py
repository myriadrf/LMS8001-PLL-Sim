from limemicro_pllsim2 import *

from Tkinter import Tk, Toplevel, Menu, LabelFrame, Frame, Label, RIGHT, LEFT, TOP, BOTTOM, BOTH, RAISED, W, E, END, N, S, IntVar, Spinbox, BooleanVar, DoubleVar, Button, Event, CENTER, FLAT
from ttk import Style, Entry, Combobox, Checkbutton, Radiobutton
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk
import webbrowser
import matplotlib.font_manager
import tkFont
from LMS8_SIM_PN_VALUES import *
from gen_INI_win import *
from GUI_Elements import *
# 
from webbrowser import open_new

from centerWindow import *

class cp_config_win(Toplevel):
	def __init__(self,parent):
		Toplevel.__init__(self)

		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)

		self.resizable(0,0)
		self.parent=parent
		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Quit)
		
	def on_OK(self):
		self.on_Apply()
		self.on_Quit()
	def on_Apply(self):
		self.parent.cp_fc.set(float(self.entry_fc.get())*1.0e3)
		self.parent.cp_slope.set(float(self.entry_slope.get()))
		self.parent.pll.cp=lms8001_cp(fc=float(self.parent.cp_fc.get()), slope=float(self.parent.cp_slope.get()))
		self.parent.def_cp()
	def on_Quit(self):
		self.parent.cp_config_win=None
		self.destroy()

	def initUI(self):
		self.title('CP Noise Parameters')
		self.columnconfigure(0, pad=1)
		self.columnconfigure(1, pad=1)
		self.columnconfigure(2, pad=1)
		self.rowconfigure(0, pad=10)
		self.rowconfigure(1, pad=1)
		self.rowconfigure(2, pad=6)

		
		
		label1=Label(self, text='Corner Frequency [kHz]')
		self.entry_fc=Entry(self, width=8)
		self.entry_fc.insert(END, str(self.parent.cp_fc.get()/1.0e3))
		label1.grid(row=0, column=0, sticky=W)
		self.entry_fc.grid(row=0, column=1, sticky=W)

		label2=Label(self, text='Noise slope [dB/dec]')
		self.entry_slope=Entry(self, width=8)
		self.entry_slope.insert(END, str(self.parent.cp_slope.get()))
		label2.grid(row=1, column=0, sticky=W)
		self.entry_slope.grid(row=1, column=1, sticky=W)		

		button_OK=Button(self, text='OK', command=self.on_OK, width=10)
		button_Apply=Button(self, text='Apply', command=self.on_Apply, width=10)
		button_Quit=Button(self, text='Quit', command=self.on_Quit, width=10)
		button_OK.grid(row=2, column=0, sticky=W+E+S)
		button_Apply.grid(row=2, column=1, sticky=W+E+S)
		button_Quit.grid(row=2, column=2, sticky=W+E+S)
		
		
