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

class vco_ctune_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		
		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)
		
		self.resizable(0,0)	

		self.parent=parent
		
		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Cancel)
		
	def on_OK(self):
		self.on_Apply()
		self.on_Cancel()
		return  None
	def on_Apply(self):
		if (self.radio_algo.get()):
			self.parent.CTUNE_INTERNAL.set(True)
		else:
			self.parent.CTUNE_INTERNAL.set(False)
		self.parent.SEL_FORCE.set(self.sel_force.get())
		self.parent.FREQ_FORCE.set(self.freq_force.get())
		self.parent.SEL_INIT.set(int(self.combo_sel_init.get()))
		self.parent.FREQ_INIT.set(int(self.combo_freq_init.current()))
		self.parent.FREQ_INIT_POS.set(int(self.combo_freq_pos.current()))
		self.parent.SEL_FREQ_MIN.set(int(self.combo_sel_fmin.current()))
		self.parent.SEL_FREQ_MAX.set(int(self.combo_sel_fmax.current()))
		self.parent.VTUNE_FIX.set(float(self.combo_vtune_fix.get()))
		
	def on_Cancel(self):
		self.parent.vco_ctune_win=None
		self.destroy()
		
	def on_radio(self):
	
		if (self.radio_algo.get()==0):
			self.cbox_freq_force.config(state='disabled')
			self.combo_freq_init.config(state='disabled')
			self.combo_freq_pos.config(state='disabled')
		else:
			self.cbox_freq_force.config(state='enabled')
			self.combo_freq_init.config(state='enabled')
			self.combo_freq_pos.config(state='enabled')

	def initUI(self):
		self.title("LMS8001-PLL-VCO CTUNE")
		
		self.style=Style()
		self.style.theme_use("default")

		self.columnconfigure(0, pad=1)
		self.columnconfigure(1, pad=10)
		self.columnconfigure(2, pad=1)
		#self.columnconfigure(3, pad=1, weight=1)


		self.rowconfigure(0, pad=4)
		self.rowconfigure(1, pad=1, weight=1)
		self.rowconfigure(2, pad=15, weight=1)
		self.rowconfigure(3, pad=1, weight=1)
		self.rowconfigure(4, pad=1, weight=1)
		self.rowconfigure(5, pad=10, weight=1)
		self.rowconfigure(6, pad=1, weight=1)

		self.radio_algo=IntVar()
		self.radio_algo.set(int(self.parent.CTUNE_INTERNAL.get()))
		radio_int=Radiobutton(self, text='Use LMS8001 Internal Coarse Tuning Algorithm', variable=self.radio_algo, value=1, command=self.on_radio)
		radio_int.grid(row=0, column=0, columnspan=3, sticky=W)		
		radio_best=Radiobutton(self, text='Use Software-Method Best-Case Finder', variable=self.radio_algo, value=0, command=self.on_radio)
		radio_best.grid(row=1, column=0, columnspan=3, sticky=W)
		
		self.sel_force=BooleanVar()
		self.sel_force.set(self.parent.SEL_FORCE.get())
		cbox_sel_force=Checkbutton(self, text='Force VCO_SEL value', variable=self.sel_force)
		cbox_sel_force.grid(row=2, column=0, sticky=W)
		self.freq_force=BooleanVar()
		self.freq_force.set(self.parent.FREQ_FORCE.get())
		self.cbox_freq_force=Checkbutton(self, text='Force VCO_FREQ value', variable=self.freq_force)
		self.cbox_freq_force.grid(row=2, column=1, sticky=E)
		
		
		vco_sel_list=range(1,4)
		vco_freq_list=range(0,256)
		frame_sel=Frame(self, relief=RAISED, borderwidth=0)
		frame_sel.columnconfigure(0, pad=0)
		frame_sel.columnconfigure(1, pad=1)
		
		self.combo_sel_init=Combobox(frame_sel, values=vco_sel_list, width=5)
		self.combo_sel_init.current(self.parent.SEL_INIT.get()-1)
		Label(frame_sel, text='SEL_INIT').grid(row=0, column=0, sticky=W)
		self.combo_sel_init.grid(row=0, column=1, sticky=E)
		frame_sel.grid(row=3, column=0, sticky=E)

		
		frame_freq=Frame(self, relief=RAISED, borderwidth=0)
		frame_freq.columnconfigure(0, pad=0)
		frame_freq.columnconfigure(1, pad=1)
		
		self.combo_freq_init=Combobox(frame_freq, values=vco_freq_list, width=5)
		self.combo_freq_init.current(self.parent.FREQ_INIT.get())
		Label(frame_freq, text='FREQ_INIT').grid(row=0, column=0, sticky=W)
		self.combo_freq_init.grid(row=0,column=1, sticky=E)
		frame_freq.grid(row=3, column=1, sticky=E)


		freq_pos_list=range(0,8)
		frame_pos=Frame(self, relief=RAISED, borderwidth=0)
		frame_pos.columnconfigure(0, pad=0)
		frame_pos.columnconfigure(1, pad=1)	

		self.combo_freq_pos=Combobox(frame_pos, values=freq_pos_list, width=5)
		self.combo_freq_pos.current(self.parent.FREQ_INIT_POS.get())
		Label(frame_pos, text='FREQ_INIT_POS').grid(row=0, column=0, sticky=W)
		self.combo_freq_pos.grid(row=0, column=1, sticky=E)
		frame_pos.grid(row=4, column=1, sticky=E)

		frame_sel_fmin=Frame(self, relief=RAISED, borderwidth=0)
		frame_sel_fmin.columnconfigure(0, pad=0)
		frame_sel_fmin.columnconfigure(1, pad=0)
		
		self.combo_sel_fmin=Combobox(frame_sel_fmin, values=vco_freq_list, width=5)
		self.combo_sel_fmin.current(self.parent.SEL_FREQ_MIN.get())
		Label(frame_sel_fmin, text='SEL_FREQ_MIN').grid(row=0, column=0, sticky=W)
		self.combo_sel_fmin.grid(row=0, column=1, sticky=E)
		frame_sel_fmin.grid(row=4, column=0, sticky=E)

		frame_sel_fmax=Frame(self, relief=RAISED, borderwidth=0)
		frame_sel_fmax.columnconfigure(0, pad=0)
		frame_sel_fmax.columnconfigure(1, pad=0)
		
		self.combo_sel_fmax=Combobox(frame_sel_fmax, values=vco_freq_list, width=5)
		self.combo_sel_fmax.current(self.parent.SEL_FREQ_MAX.get())
		Label(frame_sel_fmax, text='SEL_FREQ_MAX').grid(row=0, column=0, sticky=W)
		self.combo_sel_fmax.grid(row=0, column=1, sticky=E)
		frame_sel_fmax.grid(row=5, column=0, sticky=E)

		vtune_fix_list=[str(0.3), str(0.6), str(0.75), str(0.9)]
		frame_vtune_fix=Frame(self, relief=RAISED, borderwidth=0)
		frame_vtune_fix.columnconfigure(0, pad=0)
		frame_vtune_fix.columnconfigure(1, pad=0)
		
		self.combo_vtune_fix=Combobox(frame_vtune_fix, values=vtune_fix_list, width=5)
		self.combo_vtune_fix.set(str(self.parent.VTUNE_FIX.get()))
		Label(frame_vtune_fix, text='VTUNE_FIX').grid(row=0, column=0, sticky=W)
		self.combo_vtune_fix.grid(row=0, column=1, sticky=E)
		frame_vtune_fix.grid(row=5, column=1, sticky=E)

		frame_buttons=Frame(self, relief=RAISED, borderwidth=0)
		frame_buttons.columnconfigure(0, pad=0)
		frame_buttons.columnconfigure(1, pad=0)
		frame_buttons.columnconfigure(2, pad=0)
		button_OK=Button(frame_buttons, text='OK', command=self.on_OK, width=15)
		button_Apply=Button(frame_buttons, text='Apply', command=self.on_Apply, width=15)
		button_Cancel=Button(frame_buttons, text='Quit', command=self.on_Cancel, width=15)
		button_OK.grid(row=0, column=0, sticky=W+E)
		button_Apply.grid(row=0, column=1, sticky=W+E)
		button_Cancel.grid(row=0, column=2,sticky=W+E)
		frame_buttons.grid(row=6,  columnspan=3, sticky=W+E+S)
		
		self.on_radio()
