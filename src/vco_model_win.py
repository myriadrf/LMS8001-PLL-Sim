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

class vco_model_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		
		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)

		self.resizable(0,0)

		self.parent=parent
		self.pll=self.parent.pll
		
		
		self.initUI()
		center_Window(self)
		self.protocol("WM_DELETE_WINDOW", self.on_Quit)
		
	def initUI(self):
		self.title("LMS8001-PLL-VCO Model Definition")
		
		self.style=Style()
		self.style.theme_use("default")

		self.columnconfigure(0, pad=1)
		self.columnconfigure(1, pad=1)
		self.columnconfigure(2, pad=1)
		#self.columnconfigure(3, pad=1, weight=1)


		self.rowconfigure(0, pad=10)
		self.rowconfigure(1, pad=1, weight=1)
		self.rowconfigure(2, pad=1, weight=1)
		self.rowconfigure(3, pad=15, weight=1)
		self.rowconfigure(4, pad=1, weight=1)
		

		
		self.VCO_EM=BooleanVar()
		self.VCO_EM.set(self.parent.VCO_EM.get())
		self.cbox_vco_em=Checkbutton(self, text='Use EM (RLCK) VCO Model', onvalue=1, offvalue=0, variable=self.VCO_EM, command=self.on_VCO_EM)
		self.cbox_vco_em.grid(row=0, column=0, columnspan=3, sticky=W)

		self.radio_fvco=IntVar()
		self.radio_fvco.set(int(self.parent.VCO_MEAS_FREQ.get()))
		self.radio_fvco_meas=Radiobutton(self, text='Use Measured VCO Frequency Values in Analysis', variable=self.radio_fvco, value=1)
		self.radio_fvco_meas.grid(row=1, column=0, columnspan=2, padx=15, sticky=W+N)
		self.radio_fvco_sim=Radiobutton(self, text='Use Simulated VCO Frequency Values in Analysis', variable=self.radio_fvco, value=0)
		self.radio_fvco_sim.grid(row=2, column=0, columnspan=2, padx=15, sticky=W+N)
		
		buttonFreq=Button(self, text='Plot Freq', command=self.on_FREQ, width=10)
		buttonFreq.grid(row=3, column=0, sticky=W+E)
		
		buttonKVCO=Button(self, text='Plot KVCO', command=self.on_KVCO, width=10)
		buttonKVCO.grid(row=3, column=1, sticky=W+E)

		buttonFSTEP=Button(self, text='Plot FSTEP', command=self.on_FSTEP, width=17)
		buttonFSTEP.grid(row=3, column=2, sticky=W+E)
		
		buttonOK=Button(self, text='OK', command=self.on_OK, width=10)
		buttonOK.grid(row=4, column=0, sticky=W+E)
		
		buttonQuit=Button(self, text='Quit', command=self.on_Quit, width=17)
		buttonQuit.grid(row=4, column=2, sticky=W+E)

		buttonApply=Button(self, text='Apply', command=self.on_Apply, width=10)
		buttonApply.grid(row=4, column=1, sticky=W+E)

		self.on_VCO_EM()

		#self.pack(fill=BOTH, expand=True)
	
	def get_vals(self):
		if (self.VCO_EM.get()):
			EM_MODEL=True
			if (self.radio_fvco.get()):
				MEAS_FREQ=True
			else:
				MEAS_FREQ=False
		else:
			EM_MODEL=False
			MEAS_FREQ=False
		return (EM_MODEL, MEAS_FREQ)

	def on_FREQ(self):
		(EM_MODEL, MEAS_FREQ)=self.get_vals()
		vco=lms8001_vco(EM_MODEL=EM_MODEL, MEAS_FREQ=MEAS_FREQ)
		fvco=np.array(np.empty([3,256]))
		for sel in range(1,4):
			for freq in range(0,256):
				fvco[sel-1, freq]=vco.calcF(sel, freq, 0.6)

		figure(15)
		plt1,=plotsig(range(0,256), fvco[0,:]/1.0e9, 15, xlabel='$Cap. Bank Code$', ylabel='$F_{VCO} [GHz]$', title='VCO Frequency vs. Cap Bank Code', line_color='black', font_name=self.parent.font_name)
		plt2,=plotsig(range(0,256), fvco[1,:]/1.0e9, 15, xlabel='$Cap. Bank Code$', ylabel='$F_{VCO} [GHz]$', title='VCO Frequency vs. Cap Bank Code', line_color='blue', font_name=self.parent.font_name)
		plt3,=plotsig(range(0,256), fvco[2,:]/1.0e9, 15, xlabel='$Cap. Bank Code$', ylabel='$F_{VCO} [GHz]$', title='VCO Frequency vs. Cap Bank Code', line_color='red', font_name=self.parent.font_name)
		setlegend(15, [plt1, plt2, plt3], ['VCO_SEL=1', 'VCO_SEL=2', 'VCO_SEL=3'], font_name=self.parent.font_name)
		show_plots()
		
	def on_KVCO(self):
		(EM_MODEL, MEAS_FREQ)=self.get_vals()
		vco=lms8001_vco(EM_MODEL=EM_MODEL, MEAS_FREQ=MEAS_FREQ)
		fvco=np.array(np.empty([3,256]))
		NDIV=np.array(np.empty([3,256]))
		kvco=np.array(np.empty([3,256]))
		for sel in range(1,4):
			for freq in range(0,256):
				fvco[sel-1, freq]=vco.calcF(sel, freq, 0.6)
				kvco[sel-1, freq]=vco.calcKVCO(sel, freq, 0.6)
				NDIV[sel-1, freq]=1.0*fvco[sel-1, freq]/self.pll.Fref
		

		for sel in range(1,4):
			kvco_avg=1.0
			kvco_over_NDIV_avg=1.0
			for freq in range(0,256):
				kvco_avg=kvco_avg*(kvco[sel-1, freq]/1.0e6)**(1.0/256)
				kvco_over_NDIV_avg=kvco_over_NDIV_avg*((kvco[sel-1, freq]/1.0e6)/NDIV[sel-1, freq])**(1.0/256.0)

			print 'VCO_SEL=%d, KVCO_AVG=%.3f MHz/V, KVCO_over_NDIV_AVG=%.3f MHz/V' %(sel, kvco_avg, kvco_over_NDIV_avg)
		print ''	

		figure(16)
		plt1,=plotsig(fvco[0,:]/1.0e9, kvco[0,:]/1.0e6, 16, xlabel='$F_{VCO} [GHz]$', ylabel='$K_{VCO} [MHz/V]$', title='VCO Sensitivity vs. Frequency', line_color='black', font_name=self.parent.font_name)
		plt2,=plotsig(fvco[1,:]/1.0e9, kvco[1,:]/1.0e6, 16, xlabel='$F_{VCO} [GHz]$', ylabel='$K_{VCO} [MHz/V]$', title='VCO Sensitivity vs. Frequency', line_color='blue', font_name=self.parent.font_name)
		plt3,=plotsig(fvco[2,:]/1.0e9, kvco[2,:]/1.0e6, 16, xlabel='$F_{VCO} [GHz]$', ylabel='$K_{VCO} [MHz/V]$', title='VCO Sensitivity vs. Frequency', line_color='red', font_name=self.parent.font_name)
		setlegend(16, [plt1, plt2, plt3], ['VCO_SEL=1', 'VCO_SEL=2', 'VCO_SEL=3'], font_name=self.parent.font_name)
		show_plots()

	

	def on_FSTEP(self):
		(EM_MODEL, MEAS_FREQ)=self.get_vals()
		vco=lms8001_vco(EM_MODEL=EM_MODEL, MEAS_FREQ=MEAS_FREQ)
		fstep=np.array(np.empty([3,255]))
		for sel in range(1,4):
			for freq in range(0,255):
				fstep[sel-1, freq]=vco.calcF(sel, freq+1, 0.6)-vco.calcF(sel, freq, 0.6)
				

		figure(17)
		plt1,=plotsig(range(0,255), fstep[0,:]/1.0e6, 17, xlabel='$Cap. Bank Code$', ylabel='$F_{STEP} [MHz/V]$', title='VCO Frequency Step Between Adjacent Tuning Bands', line_color='black', font_name=self.parent.font_name)
		plt2,=plotsig(range(0,255), fstep[1,:]/1.0e6, 17, xlabel='$Cap. Bank Code$', ylabel='$F_{STEP} [MHz/V]$', title='VCO Frequency Step Between Adjacent Tuning Bands', line_color='blue', font_name=self.parent.font_name)
		plt3,=plotsig(range(0,255), fstep[2,:]/1.0e6, 17, xlabel='$Cap. Bank Code$', ylabel='$F_{STEP} [MHz/V]$', title='VCO Frequency Step Between Adjacent Tuning Bands', line_color='red', font_name=self.parent.font_name)
		setlegend(17, [plt1, plt2, plt3], ['VCO_SEL=1', 'VCO_SEL=2', 'VCO_SEL=3'], font_name=self.parent.font_name)
		show_plots()

	def on_VCO_EM(self):
		if (self.VCO_EM.get()):
			self.radio_fvco_meas.config(state='enabled')
			self.radio_fvco_sim.config(state='enabled')
		else:
			self.radio_fvco_meas.config(state='disabled')
			self.radio_fvco_sim.config(state='disabled')
				
	
	def on_OK(self):
		self.on_Apply()
		self.on_Quit()


	def on_Quit(self):
		self.parent.vco_model_win=None
		self.destroy()


	def on_Apply(self):
		(EM_MODEL, MEAS_FREQ)=self.get_vals()
		self.parent.VCO_EM.set(EM_MODEL)
		self.parent.VCO_MEAS_FREQ.set(MEAS_FREQ)
		
		self.pll.vco=lms8001_vco(SEL=2, FREQ=128, EM_MODEL=EM_MODEL, MEAS_FREQ=MEAS_FREQ)
