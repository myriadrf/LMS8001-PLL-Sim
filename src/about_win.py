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

class about_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		
		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)
		self.parent=parent
		self.resizable(0,0)
		
			
		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Quit)
		#self.center_Window()

	#def center_Window(self):
	#	sw = self.winfo_screenwidth()
	#	sh = self.winfo_screenheight()
	#
	#	self.update()
	#	self.winW=self.winfo_width()
	#	self.winH=self.winfo_height()
	#	
	#	x=int(round((sw-self.winW)/2.0))
	#	y=int(round((sh-self.winH)/2.0))
	#	self.geometry('%dx%d+%d+%d' % (self.winW, self.winH, x, y))
	#	self.update()
	
	def on_Quit(self):
		self.parent.about_win=None
		self.destroy()

	def gotoweb(self, event):
		webbrowser.open_new(event.widget.cget("text"))

	def initUI(self):
		self.title("About LimeMicro PLLSim")
		
		self.rowconfigure(0,pad=10)
		self.rowconfigure(1, pad=1)
		self.rowconfigure(2, pad=1)
		
		script_dir=os.path.dirname(__file__)

		logo = Image.open(os.path.join(script_dir, "Figures/LimeMicroLogo.png"))
		logoImg = ImageTk.PhotoImage(logo)

		label1 = Label(self, image=logoImg)


		label1.image = logoImg


		label1.grid(row=0, sticky=W+E)

		string_about='Lime Microsystems PLLSim for LMS8001 IC\nVersion 1.0\nThis program comes with absolutely NO warranty'
		
		label2 = Label(self, text=string_about, justify='center')
		label2.grid(row=1)

		label3=Label(self, text=r"http://www.limemicro.com", justify='center', foreground='blue', cursor="hand2")
		label3.bind('<Button-1>', self.gotoweb)
		label3.grid(row=2)
