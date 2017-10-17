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

class Preferences_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		
		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)
		
		self.parent=parent
		if (sys.platform=='win32'):
			font_paths=matplotlib.font_manager.win32InstalledFonts(fontext='ttf')
			self.font_names=[]
			for font_path in font_paths:
				font_inst=matplotlib.ft2font.FT2Font(font_path)
				font_prop=matplotlib.font_manager.ttfFontProperty(font_inst)
				self.font_names.append(font_prop.name)
		elif (sys.platform=='linux2'):
			font_list = matplotlib.font_manager.get_fontconfig_fonts()
			self.font_names = [matplotlib.font_manager.FontProperties(fname=fname).get_name() for fname in font_list]
		else:
			print 'Unsupported OS type. Exiting Preferences Window.'
			tkMessageBox.showinfo('Unsupported OS type', 'Exiting Preferences Window')
			self.destroy()

		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Quit)

	def on_OK(self):
		self.on_Apply()
		self.on_Quit()

	def on_Apply(self):
		self.parent.line_color=self.combobox_color.get()
		self.parent.font_name=self.combobox_fonts.get()
		maplotlib_font={'family':self.parent.font_name}
		matplotlib.rc('font', **maplotlib_font)

	def on_Quit(self):
		self.parent.Pref_win=None
		self.destroy()

	def initUI(self):
		self.title('Preferences')
		self.rowconfigure(0, pad=6)
		self.rowconfigure(1, pad=1)
		self.rowconfigure(2, pad=6)
		self.columnconfigure(0, pad=1)
		self.columnconfigure(1, pad=1)
		self.columnconfigure(2, pad=1)
		

		label1=Label(self, text='Graph Font')
		self.combobox_fonts=Combobox(self, values=self.font_names, width=16)
		self.combobox_fonts.current(self.font_names.index(self.parent.font_name))
		label1.grid(row=0, column=0, sticky=W)
		self.combobox_fonts.grid(row=0, column=1, columnspan=2, sticky=W)
		

		label2=Label(self, text='Line Color')
		self.combobox_color=Combobox(self, values=self.parent.line_colors, width=8)
		self.combobox_color.current(self.parent.line_colors.index(self.parent.line_color))
		label2.grid(row=1, column=0, sticky=W)
		self.combobox_color.grid(row=1, column=1, columnspan=2, sticky=W)

		buttonOK=Button(self, text='OK', command=self.on_OK, width=16)
		buttonApply=Button(self, text='Apply', command=self.on_Apply, width=16)
		buttonQuit=Button(self, text='Quit', command=self.on_Quit, width=16)
		buttonOK.grid(row=2, column=0, sticky=W+E+S)
		buttonApply.grid(row=2, column=1, sticky=W+E+S)
		buttonQuit.grid(row=2, column=2, sticky=W+E+S)
