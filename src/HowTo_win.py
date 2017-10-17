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


class HowTo_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)

		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)
		self.parent=parent
		self.resizable(0,0)
		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Quit)
	
	def on_Quit(self):
		self.parent.howTo_win=None
		self.destroy()

	def initUI(self):
		self.title('Quick-Guide to LimeMicro PLL-Sim')

		str_lbl='To specify the Reference Frequency, enter in the appropriate field desired value in MHz.\nClick on Set&Plot REF Phase Noise button.\n'+'To define Frequency Offset Sweep for PLL Analysis choose the values for start and stop frequency\nand define number of steps per decade. Click on Set PLL Frequency Sweep Button.\n'+'Define the settings for various PLL subblocks using dedicated fields on the root window.\nVarious PLL subblock parameters can be ploted in separate windows by clicking to the appropriate buttons.'+'\n\nTo coarse tune the VCO click on the VCO COARSE TUNE button. This button implements method\nwhich finds the optimal VCO configuration and calculates the appropriate FB-DIV fields.\nIf Integer-N mode is selected, VCO is tuned the integer multiple of the reference frequency \nthat is closest to the targeted VCO frequency value.\nVCO Coarse Tuning Algorithm can be defined in\n more details using separate window that can be activated through the drop-down menu, Edit->Configure->VCO->Coarse 
Tune Algo.\nPLL Status can be viewed in the down-left corner of the root window.'+'\n\nLoopFilter optimization can be performed by clicking on the Optimize/Update LPF button.\nPreviously user is advised to tune the VCO to the targeted frequency,\ndefine CP pulse current\nvalue, desired open-loop crossover frequency, Fc [kHZ],\nand phase margin of the PLL loop. Loop Filter component values will be calculated and updated\nin the dedicated widgets of the root window.\n\nFour types of analysis are available to the user: Open-Loop PLL Analysis, Close-Loop PLL Analysis,\nPLL Transient Response and PLL Phase Noise Analysis.\nButtons for starting the analysis are available in the last row of the root window.\nIn the rows above them there are a lot of options that allow to the user to choose, for example,\nthe signals that are to be shown in the graphs.\n\nIf user wants to specify its own frequency-noise pairs for PLL subblocks, first,\ndedicacated GUI widgets should be enabled by clicking on GUI Values radio button 
in the down-right corner of the main GUI window, in the PNOISE ANALYSIS SETUP frame.'
		label=Label(self, text=str_lbl)
		label.grid(row=0, column=0, sticky=W+E, padx=10, pady=10)

