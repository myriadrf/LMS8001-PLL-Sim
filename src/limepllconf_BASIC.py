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

from centerWindow import *
from Preferences_win import *
from cp_config_win import *
from about_win import *
from vco_model_win import *
from vco_ctune_win import *
from gen_INI_win import *
from GUI_Elements import *
# 
from webbrowser import open_new

# Default fonts for GUI widgets
font_linux='Droid Sans'
font_windows='Segoe UI'
# Default fonts for Matplotlib graphs
mpl_font_linux='CMU Serif'
mpl_font_windows='Segoe UI'


VTH_HIGH=0.9
VTH_LOW=0.3

C1_def=8
C2_def=8
C3_def=8
R2_def=1
R3_def=1

vco_sel_def=2
vco_freq_def=128
vco_vtune_def=0.6

ffdiv_mod_def=1

fbdiv_nint_def=150
fbdiv_nfrac_def=100000

cp_fc_def=0.6e6
cp_slope_def=-10.0



flog_vals=['1.0e2', '1.0e3', '1.0e4', '1.0e5', '1.0e6', '1.0e7', '1.0e8', '1.0e9']

#ref_src=ref()
#lms8001_pll=pll(name='LMS8001_PLL', IC_name='LMS8001', VCO_EM_MODEL=True, VCO_MEAS_FREQ=True)

#flog=0



	
class limepllconf(Frame):
	def __init__(self, parent):
		Frame.__init__(self,parent)

		self.parent=parent

		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.parent.tk.call('wm', 'iconphoto', self.parent._w, img)
		
		self.GUI_font=tkFont.nametofont('TkDefaultFont')

		# sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()

		if (sys.platform=='linux2'):
			self.GUI_font.configure(family=font_linux, size=10) if (sh>950) else self.GUI_font.configure(family=font_linux, size=9)
			
		else:
			#self.GUI_font.configure(family=font_windows, size=9)
			self.GUI_font.configure(family=font_windows, size=9) if (sh>950) else self.GUI_font.configure(family=font_windows, size=8)
		

		self.parent.option_add('*Font', self.GUI_font)

		self.ref=ref()

		self.VCO_EM=BooleanVar()
		self.VCO_EM.set(True)
		self.VCO_MEAS_FREQ=BooleanVar()
		self.VCO_MEAS_FREQ.set(True)

		self.pll=pll(name='LMS8001_PLL', IC_name='LMS8001', VCO_EM_MODEL=bool(self.VCO_EM.get()), VCO_MEAS_FREQ=bool(self.VCO_MEAS_FREQ.get()))
		self.flog=0

		self.line_color='black'
		self.line_colors=['black', 'red', 'grey', 'green', 'pink', 'orange', 'blue']
		if (sys.platform=='win32'):
			self.font_name=mpl_font_windows
			maplotlib_font={'family':self.font_name, 'size':10}
		else:
			self.font_name=mpl_font_linux
			maplotlib_font={'family':self.font_name}
		matplotlib.rc('font', **maplotlib_font)
		
		self.initUI()
		self.pack(fill=BOTH, expand=True)
		#self.center_Window()
		center_Window(self.parent, rootWin=True)
		self.winW=self.parent.winfo_width()
		self.winH=self.parent.winfo_height()
		
	def on_Pref(self):
		if (not hasattr(self, 'Pref_win')):
			self.Pref_win=Preferences_win(self)
		else:
			if (self.Pref_win!=None):
				self.Pref_win.lift()
			else:
				self.Pref_win=Preferences_win(self)
		
	
	def on_gen_INI_Files(self):
		if (not hasattr(self, 'gen_INI_win')):
			self.gen_INI_win=gen_INI_win(self)
		else:
			if (self.gen_INI_win!=None):
				self.gen_INI_win.lift()
			else:
				self.gen_INI_win=gen_INI_win(self)

	#def center_Window(self, force_WH=False):
	#	sw = self.parent.winfo_screenwidth()
	#	sh = self.parent.winfo_screenheight()
		
	#	self.parent.update()
	#	if not force_WH:
	#		self.winW=self.parent.winfo_width()
	#		self.winH=self.parent.winfo_height()
			#print winW, ' ', winH
			#print sw, ' ', sh
		
			# Manualy set window dimension
			#winW=952
			#winH=783
		
		#x=int(round((sw-self.winW)/4.0))
		#y=int(round((sh-self.winH)/4.0))
		#self.parent.geometry('%dx%d+%d+%d' % (self.winW, self.winH, x, y))
		#self.parent.update()

	def calc_pn_ref(self):
		if (self.radio_pnoise.get()>1):
			#self.ref.setNoise(fpn=fpn_ref, pn=pn_ref, noise_floor=noise_floor_ref)
			pn_refonly=self.ref.calc_pnoise(f=self.flog)
			pn_xbuf=self.xbuf.calc_pnoise(f=self.flog)
			pn_ref=10.0*np.log10(np.power(10.0, pn_refonly/10.0)+np.power(10.0, pn_xbuf/10.0))
		else:
			pn_ref=self.ref.calc_pnoise(f=self.flog)

		return pn_ref

	def on_Reset(self, e=None):
		self.initUI()
		#self.center_Window(force_WH=True)
		
		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
		self.parent.update()

		self.parent.geometry('%dx%d' % (self.winW, self.winH))
		self.parent.update()
	
	def on_config_CP(self):
		if (not hasattr(self, 'cp_config_win')):
			self.cp_config_win=cp_config_win(self)
		else:
			if (self.cp_config_win!=None):
				self.cp_config_win.lift()
			else:
				self.cp_config_win=cp_config_win(self)

	def on_open_Config(self):
		ftypes = [('Config files', '*.cfg'), ('All files', '*')]
	

		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fname=dlg.show()

		try:
			f=open(fname, 'r')
		except:
			f=None
		if (f is None):
			return None
	
		lines=f.readlines()
		f.close()
		for line in lines:
			line_vals=line.split()
			e=self.GUI_ElemList.get_GUIelem_byNameType(line_vals[0], line_vals[1])
			if not (e==None):
				e.setVal(line_vals[2].strip())
			if (e.name=='AAC_EN'):
				self.on_VCO_AAC_EN()
		

		self.pll.vco=lms8001_vco(SEL=2, FREQ=128, EM_MODEL=bool(self.VCO_EM.get()), MEAS_FREQ=bool(self.VCO_MEAS_FREQ.get()))
		self.pll.cp=lms8001_cp(fc=float(self.cp_fc.get()), slope=float(self.cp_slope.get()))
		
		self.update_cp_vals()
		self.def_ALL()
		self.update_pnoise()

	def on_save_Config(self):
		f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".cfg", filetypes=[("Config files", "*.cfg")])
   		if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
       			 return None

		for wtype in self.GUI_ElemList.widget_types:
			elem_list=self.GUI_ElemList.get_elemList_ofType(wtype)
			for e in elem_list:
				#print e.name
				f.write(str(e.name)+'\t'+str(e.wtype)+'\t'+str(e.getVal())+'\n')
				
		f.close()

	def make_GUI_ElemList(self):		
		self.GUI_ElemList.add(self.entry_ref, name='entry_ref', widget='entry')
		self.GUI_ElemList.add(self.entry_ref_foff, name='entry_ref_foff', widget='entry')
		self.GUI_ElemList.add(self.entry_ref_pn, name='entry_ref_pn', widget='entry')
		self.GUI_ElemList.add(self.entry_ref_floor, name='entry_ref_floor', widget='entry')

		self.GUI_ElemList.add(self.combobox_fsweep_fmin, name='combobox_fsweep_fmin', widget='combo')
		self.GUI_ElemList.add(self.combobox_fsweep_fmax, name='combobox_fsweep_fmax', widget='combo')
		self.GUI_ElemList.add(self.entry_fsweep_nstep, name='entry_fsweep_nstep', widget='entry')

		self.GUI_ElemList.add(self.combobox_pfddel, name='combobox_pfddel', widget='combo')
		self.GUI_ElemList.add(self.combobox_cp_pulse, name='combobox_cp_pulse', widget='combo')
		self.GUI_ElemList.add(self.combobox_cp_offset, name='combobox_cp_offset', widget='combo')
		self.GUI_ElemList.add(self.combobox_cp_ict, name='combobox_cp_ict', widget='combo')

		self.GUI_ElemList.add(self.combobox_C1, name='combobox_C1', widget='combo')
		self.GUI_ElemList.add(self.combobox_C2, name='combobox_C2', widget='combo')
		self.GUI_ElemList.add(self.combobox_C3, name='combobox_C3', widget='combo')
		self.GUI_ElemList.add(self.combobox_R2, name='combobox_R2', widget='combo')
		self.GUI_ElemList.add(self.combobox_R3, name='combobox_R3', widget='combo')

		self.GUI_ElemList.add(self.entry_fvco, name='entry_fvco', widget='entry')
		self.GUI_ElemList.add(self.combobox_vcosel, name='combobox_vcosel', widget='combo')
		self.GUI_ElemList.add(self.combobox_vcofreq, name='combobox_vcofreq', widget='combo')
		self.GUI_ElemList.add(self.combobox_vcovtune, name='combobox_vcovtune', widget='combo')
		#self.GUI_ElemList.add(self.combobox_vcoamp, name='combobox_vcoamp', widget='combo')
		#self.GUI_ElemList.add(self.combobox_vcoswvdd, name='combobox_vcoswvdd', widget='combo')
		#self.GUI_ElemList.add(self.AAC_EN, name='AAC_EN', widget='checkbutton_var')
		
		self.GUI_ElemList.add(self.combobox_ffmod, name='combobox_ffmod', widget='combo')
		self.GUI_ElemList.add(self.combobox_fbint, name='combobox_fbint', widget='combo')
		self.GUI_ElemList.add(self.combobox_fbfrac, name='combobox_fbfrac', widget='combo')

		self.GUI_ElemList.add(self.INTMOD_EN, name='INTMOD_EN', widget='checkbutton_var')
		self.GUI_ElemList.add(self.PDIV2_EN, name='PDIV2_EN', widget='checkbutton_var')

		self.GUI_ElemList.add(self.entry_lpf_fc, name='entry_lpf_fc', widget='entry')
		self.GUI_ElemList.add(self.entry_PM, name='entry_PM', widget='entry')

		self.GUI_ElemList.add(self.entry_vco_foff, name='entry_vco_foff', widget='entry')
		self.GUI_ElemList.add(self.entry_vco_pn, name='entry_vco_pn', widget='entry')
		self.GUI_ElemList.add(self.entry_vco_fc, name='entry_vco_fc', widget='entry')

		self.GUI_ElemList.add(self.entry_fbdiv_foff, name='entry_fbdiv_foff', widget='entry')
		self.GUI_ElemList.add(self.entry_fbdiv_pn, name='entry_fbdiv_pn', widget='entry')
		self.GUI_ElemList.add(self.entry_fbdiv_floor, name='entry_fbdiv_floor', widget='entry')

		self.GUI_ElemList.add(self.cloop_ref, name='cloop_ref', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cloop_vco, name='cloop_vco', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cloop_cp, name='cloop_cp', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cloop_fbdiv, name='cloop_fbdiv', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cloop_lpf, name='cloop_lpf', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cloop_sdm, name='cloop_sdm', widget='checkbutton_var')

		self.GUI_ElemList.add(self.tran_vtune, name='tran_vtune', widget='checkbutton_var')
		self.GUI_ElemList.add(self.tran_fvco, name='tran_fvco', widget='checkbutton_var')
		self.GUI_ElemList.add(self.tran_ferr, name='tran_ferr', widget='checkbutton_var')
		self.GUI_ElemList.add(self.tran_fpll, name='tran_fpll', widget='checkbutton_var')
		self.GUI_ElemList.add(self.tran_pherr, name='tran_pherr', widget='checkbutton_var')
		self.GUI_ElemList.add(self.entry_fstep, name='tran_fstep', widget='entry')


		self.GUI_ElemList.add(self.radio_pnoise, name='radio_pnoise', widget='radiobutton_var')
		self.GUI_ElemList.add(self.cont_vco, name='cont_vco', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cont_ref, name='cont_ref', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cont_lpf, name='cont_lpf', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cont_fbdiv, name='cont_fbdiv', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cont_pfdcp, name='cont_pfdcp', widget='checkbutton_var')
		self.GUI_ElemList.add(self.cont_sdm, name='cont_sdm', widget='checkbutton_var')

		self.GUI_ElemList.add(self.VCO_EM, name='VCO_EM', widget='var')
		self.GUI_ElemList.add(self.VCO_MEAS_FREQ, name='VCO_MEAS_FREQ', widget='var')

		self.GUI_ElemList.add(self.SEL_FORCE, name='SEL_FORCE', widget='var')
		self.GUI_ElemList.add(self.FREQ_FORCE, name='FREQ_FORCE', widget='var')
		self.GUI_ElemList.add(self.SEL_INIT, name='SEL_INIT', widget='var')
		self.GUI_ElemList.add(self.FREQ_INIT, name='FREQ_INIT', widget='var')
		self.GUI_ElemList.add(self.FREQ_INIT_POS, name='FREQ_INIT_POS', widget='var')
		self.GUI_ElemList.add(self.SEL_FREQ_MIN, name='SEL_FREQ_MIN', widget='var')
		self.GUI_ElemList.add(self.SEL_FREQ_MAX, name='SEL_FREQ_MAX', widget='var')
		self.GUI_ElemList.add(self.VTUNE_FIX, name='VTUNE_FIX', widget='var')
		self.GUI_ElemList.add(self.CTUNE_INTERNAL, name='CTUNE_INTERNAL', widget='var')

		self.GUI_ElemList.add(self.cp_fc, name='cp_fc', widget='var')
		self.GUI_ElemList.add(self.cp_slope, name='cp_slope', widget='var')

	def on_save_PLL_summary(self):
		self.def_ALL()
		self.update_pnoise()

		pn_ref=self.calc_pn_ref()
		
		f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt", filetypes=[("Text files", "*.txt")])
   		if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
       			 return None
		summary_file_name=f.name
		f.close()
		summary=self.pll.gen_summary(print_to_file=True, file_name=summary_file_name, fmin=min(self.flog), fmax=max(self.flog), pn_ref=pn_ref, SDM_NOISE=(not bool(self.INTMOD_EN.get())))
		
   		#text2save = 'pavle' # starts from `1.0`, not `0.0`
   		#f.write(text2save)
		#print f.name
   		#f.close()

	def on_print_PLL_summary(self):
		self.def_ALL()
		self.update_pnoise()
		
		pn_ref=self.calc_pn_ref()

		summary=self.pll.gen_summary(print_to_file=False, fmin=min(self.flog), fmax=max(self.flog), pn_ref=pn_ref, SDM_NOISE=(not bool(self.INTMOD_EN.get())))
		
		

	def on_VCO_model(self):
		if (not hasattr(self, 'vco_model_win')):
			self.vco_model_win=vco_model_win(self)
		else:
			if (self.vco_model_win!=None):
				self.vco_model_win.lift()
			else:
				self.vco_model_win=vco_model_win(self)
		#rootWindow2=Tk()
		#app2=vco_model_win(rootWindow2, self.pll)
		#rootWindow2.resizable(0,0) # This removes maximize button from the main window	
		#rootWindow2.mainloop()

	def on_VCO_ctune(self):
		if (not hasattr(self, 'vco_ctune_win')):
			self.vco_ctune_win=vco_ctune_win(self)
		else:
			if (self.vco_ctune_win!=None):
				self.vco_ctune_win.lift()
			else:
				self.vco_ctune_win=vco_ctune_win(self)
	
	def onExit(self):
		plt.close('all')
		self.parent.destroy()
		#self.quit()

	def onAbout(self):
		if (not hasattr(self, 'about_win')):
			self.about_win=about_win(self)
		else:
			if (self.about_win!=None):
				self.about_win.lift()
			else:
				self.about_win=about_win(self)
	
	def onHowTo(self):
		#if (not hasattr(self, 'howTo_win')):
		#	self.howTo_win=HowTo_win(self)
		#else:
		#	if (self.howTo_win!=None):
		#		self.howTo_win.lift()
		#	else:
		#		self.howTo_win=HowTo_win(self)

		# Get working directory absolute path
		work_dir=os.path.dirname(__file__)
		# Open PDF containing quick-guide to LMS8001 PLLSim Software
		path_to_handbook_PDF=os.path.join(work_dir,'help/handbook.pdf')
		webbrowser.open_new(str(path_to_handbook_PDF))

	def combobox_control(self, e):
		#print e.type
		widget=e.widget
		txt=widget.get()
		values=widget.cget('values')
		
		try:
			input_val=float(txt)
		except:
			print "Value %s cannot be converted to float." %(txt)
			input_val=1.0e9
			if (txt=='EXT-LO'):
				print "Value %s cannot be converted to float." %(txt)
				input_val=0
			elif(txt=='Open'):
				print "Value %s cannot be converted to float." %(txt)
				input_val=1.0e9
			else:
				print "Value %s cannot be converted to float." %(txt)
				
		
	
		err=1.0e20
		ind=-1
		
		for i in range(0, len(values)):
			if (values[i]=='EXT-LO'):
				tmp=0
			elif (values[i]=='Open'):
				tmp=1.0e9
			else:
				tmp=float(values[i])
			curr_err=abs(tmp-input_val)
			if curr_err<=err:
				ind=i
				err=curr_err

		widget.current(ind)
		
		#return float(values[ind])
		return ind
	
	def def_ALL(self):
		self.def_ref()
		self.def_fsweep()
		self.def_pfd()
		self.def_cp()
		self.def_lpf()
		self.def_vco()
		self.def_div()
		self.update_pnoise()
		self.check_pll_status()
		#print self.pll

		
	def def_ref(self, e=None):
		try:
			self.ref.setFref(float(self.entry_ref.get())*1.0e6)
			self.pll.setFref(float(self.entry_ref.get())*1.0e6)
			self.check_pll_status()
			return 1
		except:
			tkMessageBox.showinfo('Error! Reference Freq Definition', 'Wrong Reference Frequency: Please enter REAL number value')
			return None
		


	def def_fsweep(self, e=None):
		
		try:
			fmin=float(self.combobox_fsweep_fmin.get())
			exp_min=log10(fmin)
			fmax=float(self.combobox_fsweep_fmax.get())
			exp_max=log10(fmax)
			pt_per_dec=int(self.entry_fsweep_nstep.get())
		except:
			tkMessageBox.showinfo('Error! Frequency Sweep Definion', 'Steps per Decade: Please enter positive INTEGER value')
			return None

		if (fmin>=1.0e6):
			tkMessageBox.showinfo('Error! Frequency Sweep Definion', 'Start Frequency: Settinng to minimum value which 1.0e5 Hz')
			self.combobox_fsweep_fmin.current(3)
			fmin=float(self.combobox_fsweep_fmin.get())
			exp_min=log10(fmin)

		if (fmin<fmax and pt_per_dec>0):
			self.flog=self.pll.set_flog(exp_min, exp_max, pt_per_dec)
			return 1
		elif (fmax<=fmin):
			print "Error: Frequency Sweep Definition: fmin should be lower then fmax"
			tkMessageBox.showinfo('Error! Frequency Sweep Definion', 'Start-Stop Freq: fmin should be lower then fmax')
			return None

		elif (pt_per_dec<=0):
			print "Error: Frequency Sweep Definition: Point per decade should be positive integer."
			tkMessageBox.showinfo('Error! Frequency Sweep Definion', 'Steps per Decade: Please enter positive INTEGER value')
			return None
		
		#print "Definition of Frequency Sweep!!!!!"

	def def_pfd(self, e=None):
		#print e.type
		if (e==None):
			PFD_DEL=int(self.combobox_pfddel.get())
		else:
			if (int(e.type)==2 or int(e.type)==10): # this means if event is equal to '<Return>' or '<FocusOut>'
				PFD_DEL=self.combobox_control(e)
			else:
				PFD_DEL=int(self.combobox_pfddel.get())
		
		self.pll.def_pfd(pfdname='PFD', PFD_FLIP=0, PFD_DEL=PFD_DEL)
		#print self.pll.pfd

	def update_cp_vals(self, event=None):
		# Combobox methods
		#	current() - gets the index of current element
		#	get() - gets the value of current element, returns string

		cp_pulse_ind=self.combobox_cp_pulse.current()
		cp_offset_ind=self.combobox_cp_offset.current()
		ict_cp_ind=self.combobox_cp_ict.current()
		cp_bias=25.0*ict_cp_ind*1.0/16.0
		
		inds_cp_current=range(0,64)
		vals_cp_pulse=[]
		vals_cp_offset=[]
		for i in inds_cp_current:
			vals_cp_pulse.append(str(cp_bias*i))
			vals_cp_offset.append(str(cp_bias/4.0*i))

		self.combobox_cp_pulse.configure(values=vals_cp_pulse)
		self.combobox_cp_pulse.current(cp_pulse_ind)
		
		self.combobox_cp_offset.configure(values=vals_cp_offset)
		self.combobox_cp_offset.current(cp_offset_ind)

		#if (self.gen_INI_win):
		if hasattr(self, 'gen_INI_win'):
			self.gen_INI_win.update_FLOCK_CP()
		

	
	def def_cp(self, e=None):
		if (e==None):
			ICT_CP=int(self.combobox_cp_ict.current())
			PULSE_CP=int(self.combobox_cp_pulse.current())
			OFFSET_CP=int(self.combobox_cp_offset.current())
		else:
			if (int(e.type)==2 or int(e.type)==10): # this means if event is equal to '<Return>' or '<FocusOut>'
				cp_val=self.combobox_control(e)
			else:
				cp_val=int(e.widget.current())
		
			if (e.widget==self.combobox_cp_ict):
			
				ICT_CP=cp_val
				PULSE_CP=int(self.combobox_cp_pulse.current())
				OFFSET_CP=int(self.combobox_cp_offset.current())
				self.update_cp_vals()
		

			elif (e.widget==self.combobox_cp_pulse):
				ICT_CP=int(self.combobox_cp_ict.current())
				PULSE_CP=cp_val
				OFFSET_CP=int(self.combobox_cp_offset.current())
			#elif (e.widget==self.combobox_cp_offset):
			else:	
				ICT_CP=int(self.combobox_cp_ict.current())
				PULSE_CP=int(self.combobox_cp_pulse.current())
				OFFSET_CP=cp_val

		

		self.pll.def_cp(cpname='CP', PULSE=PULSE_CP, OFS=OFFSET_CP, ICT=ICT_CP)
		#print self.pll.cp

	def def_lpf(self, e=None):
		if (e==None):
			C1_CODE=int(self.combobox_C1.current())
			C2_CODE=int(self.combobox_C2.current())
			C3_CODE=int(self.combobox_C3.current())
			R2_CODE=int(self.combobox_R2.current())
			R3_CODE=int(self.combobox_R3.current())

		else:
			if (int(e.type)==2 or int(e.type)==10): # this means if event is equal to '<Return>' or '<FocusOut>'
				LPF_VAL=self.combobox_control(e)
			else:
				LPF_VAL=int(e.widget.current())

			if (e.widget==self.combobox_C1):
				C1_CODE=LPF_VAL
				C2_CODE=int(self.combobox_C2.current())
				C3_CODE=int(self.combobox_C3.current())
				R2_CODE=int(self.combobox_R2.current())
				R3_CODE=int(self.combobox_R3.current())
			elif (e.widget==self.combobox_C2):
				C1_CODE=int(self.combobox_C1.current())
				C2_CODE=LPF_VAL
				C3_CODE=int(self.combobox_C3.current())
				R2_CODE=int(self.combobox_R2.current())
				R3_CODE=int(self.combobox_R3.current())
			elif (e.widget==self.combobox_C3):
				C1_CODE=int(self.combobox_C1.current())
				C2_CODE=int(self.combobox_C2.current())
				C3_CODE=LPF_VAL
				R2_CODE=int(self.combobox_R2.current())
				R3_CODE=int(self.combobox_R3.current())
			elif (e.widget==self.combobox_R2):
				C1_CODE=int(self.combobox_C1.current())
				C2_CODE=int(self.combobox_C2.current())
				C3_CODE=int(self.combobox_C3.current())
				R2_CODE=LPF_VAL
				R3_CODE=int(self.combobox_R3.current())
			elif (e.widget==self.combobox_R3):
				C1_CODE=int(self.combobox_C1.current())
				C2_CODE=int(self.combobox_C2.current())
				C3_CODE=int(self.combobox_C3.current())
				R2_CODE=int(self.combobox_R2.current())
				R3_CODE=LPF_VAL

		self.pll.def_lpf(lpfname='LPF', C1_CODE=C1_CODE, C2_CODE=C2_CODE, C3_CODE=C3_CODE, R2_CODE=R2_CODE, R3_CODE=R3_CODE)
		#print self.pll.lpf

	def def_vco(self, e=None):
		if (e==None):
			SEL=int(self.combobox_vcosel.current())
			FREQ=int(self.combobox_vcofreq.current())
			VTUNE=float(self.combobox_vcovtune.get())
		else:
			if (int(e.type)==2 or int(e.type)==10): # this means if event is equal to '<Return>' or '<FocusOut>'
				VCO_VAL=self.combobox_control(e)
			else:
				VCO_VAL=int(e.widget.current())
			
			if (e.widget==self.combobox_vcosel):
				SEL=VCO_VAL
				FREQ=int(self.combobox_vcofreq.current())
				VTUNE=float(self.combobox_vcovtune.get())
			elif (e.widget==self.combobox_vcofreq):
				SEL=int(self.combobox_vcosel.current())
				FREQ=VCO_VAL
				VTUNE=float(self.combobox_vcovtune.get())
			elif (e.widget==self.combobox_vcovtune):
				SEL=int(self.combobox_vcosel.current())
				FREQ=int(self.combobox_vcofreq.current())
				VTUNE_vals=self.combobox_vcovtune.cget('values')
				VTUNE=float(VTUNE_vals[VCO_VAL])

		self.pll.def_vco(vconame='VCO', SEL=SEL, FREQ=FREQ, VTUNE=VTUNE)
		self.check_pll_status()

		if (self.combobox_vcosel.current()==0):	
			self.button_vco_ctune.config(state='disabled')
			self.button_vcopn.config(state='disabled')
			self.button_VCOTUNE.config(state='disabled')

			self.oLoopTFButton.config(state='disabled')
			self.cLoopTFButton.config(state='disabled')
			self.trRespButton.config(state='disabled')
			self.phNoiseButton.config(state='disabled')
			tkMessageBox.showinfo('Warning', 'Warning: External LO Mode Selected. PLL Analysis Disabled.' )
			
		else:
			self.button_vco_ctune.config(state='normal')
			self.button_vcopn.config(state='normal')
			self.button_VCOTUNE.config(state='normal')
			
			self.oLoopTFButton.config(state='normal')
			self.cLoopTFButton.config(state='normal')
			self.trRespButton.config(state='normal')
			self.phNoiseButton.config(state='normal')
		#print self.pll.vco

	def def_div(self, e=None):
		if (e==None):
			FFMOD=int(self.combobox_ffmod.current())
			INT=int(self.combobox_fbint.current())
			FRAC=float(self.combobox_fbfrac.current())
		else:
			if (int(e.type)==2 or int(e.type)==10): # this means if event is equal to '<Return>' or '<FocusOut>'
				DIV_VAL=self.combobox_control(e)
			else:
				DIV_VAL=int(e.widget.current())

			if (e.widget==self.combobox_ffmod):
				FFMOD=DIV_VAL
				INT=int(self.combobox_fbint.current())
				FRAC=float(self.combobox_fbfrac.current())
			elif (e.widget==self.combobox_fbint):
				FFMOD=int(self.combobox_ffmod.current())
				INT=DIV_VAL
				FRAC=float(self.combobox_fbfrac.current())
			elif (e.widget==self.combobox_fbfrac):
				FFMOD=int(self.combobox_ffmod.current())
				INT=int(self.combobox_fbint.current())
				FRAC=DIV_VAL

		if (self.INTMOD_EN.get()):
			self.combobox_fbfrac.config(state='disabled')
		else:
			self.combobox_fbfrac.config(state='enabled')

		
		self.FFMOD=2.0**FFMOD
		NDIV=INT+FRAC*1.0/2.0**20*(1.0-int(self.INTMOD_EN.get()))
		
		self.pll.def_div(divname='FB-DIV', NDIV=NDIV, PDIV2=int(self.PDIV2_EN.get()), auto_calc=False)

		self.check_pll_status()

		#print self.FFMOD
		#print self.pll.div

	def optim_LPF(self):
		try:
			fc_Hz=float(self.entry_lpf_fc.get())*1.0e3
			PM_deg=float(self.entry_PM.get())
		except:
			tkMessageBox.showinfo('Error! Targeted Loop Dynamics Definition', 'Loop Crossover frequency and phase margin should be POSITIVE REAL numbers')
			return None
		target_lpf=self.pll.calcLPF(fc=fc_Hz, PM_deg=PM_deg)
		print ""
		print ""
		print "Loop-Filter Optimization"
		print "------------------------------"
		print "Targeted Open-Loop Crossover Frequency: %.2f [kHz]" %(fc_Hz/1.0e3)
		print "Targeted Phase Margin: %.2f [deg]" %(PM_deg)
		print "------------------------------"
		print "CP Current: %.2f [uA]" %(self.pll.cp.getI()/1.0e-6)
		print "VCO Frequency: %.2f [GHz]" %(self.pll.vco.getF()/1.0e9)
		print "VCO Gain: %.2f [MHz/V]" %(self.pll.vco.getKVCO()/1.0e6)
		print "FBDIV Modulus: %.2f" %(self.pll.div.getN())
		print "Reference Freq.: %.2f [MHz]" %(self.pll.Fref/1.0e6)
		print "------------------------------"		
		print "Ideal Loop-Filter Values"
		print "------------------------------"
		print "C1= %.2f [pF]" %(target_lpf['C1']/1.0e-12)
		print "C2= %.2f [pF]" %(target_lpf['C2']/1.0e-12)
		print "R2= %.2f [kOhm]" %(target_lpf['R2']/1.0e3)
		print "C3= %.2f pF" %(target_lpf['C3']/1.0e-12)
		print "R3= %.2f [kOhm]" %(target_lpf['R3']/1.0e3)
		print "------------------------------"
		print ""
		
		LPF_CONFIG=self.pll.get_LPF_OptConfig(target_lpf)
		LPF_CONFIG['lpfname']='LPF'
		self.pll.def_lpf(**LPF_CONFIG)

		self.combobox_C1.current(LPF_CONFIG['C1_CODE'])		
		self.combobox_C2.current(LPF_CONFIG['C2_CODE'])	
		self.combobox_C3.current(LPF_CONFIG['C3_CODE'])
		self.combobox_R2.current(LPF_CONFIG['R2_CODE'])
		self.combobox_R3.current(LPF_CONFIG['R3_CODE'])	
		#print self.pll.lpf
		#print self.pll.vco

	def optim_CPLPF(self):
		#fc_Hz=float(self.entry_lpf_fc.get())*1.0e3
		#PM_deg=float(self.entry_PM.get())

		try:
			fc_Hz=float(self.entry_lpf_fc.get())*1.0e3
			PM_deg=float(self.entry_PM.get())
		except:
			tkMessageBox.showinfo('Error! Targeted Loop Dynamics Definition', 'Loop Crossover frequency and phase margin should be POSITIVE REAL numbers')
			return None

		status=self.pll.optim_PLL_LoopBW(PM_deg=PM_deg, fc=fc_Hz)

		if (status):
			# If optimization passed successfuly
			# Read CP Pulse Current and LPF Comp. Values

			PULSE=self.pll.cp.PULSE
			C1_CODE=self.pll.lpf.C1_CTRL
			C2_CODE=self.pll.lpf.C2_CTRL	
			C3_CODE=self.pll.lpf.C3_CTRL
			R2_CODE=self.pll.lpf.R2_CTRL
			R3_CODE=self.pll.lpf.R3_CTRL
			
			# Set corresponding comboboxes
			self.combobox_cp_pulse.current(int(PULSE))

			self.combobox_C1.current(int(C1_CODE))
			self.combobox_C2.current(int(C2_CODE))
			self.combobox_C3.current(int(C3_CODE))
			self.combobox_R2.current(int(R2_CODE))
			self.combobox_R3.current(int(R3_CODE))
			
			# Update ALL
			self.def_ALL()

	def vco_CTUNE(self):
		# Calculation of VCO target-frequency
		# Round to closest integer multiple of reference frequency if INT-N mode is checked

		FVCO_TARGET=float(self.entry_fvco.get())*1.0e9
		INTMOD_EN=self.INTMOD_EN.get()
		PDIV2=int(self.PDIV2_EN.get())

		NDIV=FVCO_TARGET*1.0/((2**PDIV2)*self.pll.Fref)
		
		if (INTMOD_EN):
			NINT=int(round(NDIV))
			NFRAC=0
		else:
			
			NINT=int(floor(NDIV))
			NFRAC=int((NDIV-NINT)*(2**20))
		

		#print NINT
		#print NFRAC

		self.combobox_fbint.current(NINT)
		self.combobox_fbfrac.current(NFRAC)
		self.def_div()
		#print self.pll.div

		FVCO_TARGET=self.pll.div.getN()*self.pll.Fref
		self.entry_fvco.delete(0, 'end')
		self.entry_fvco.insert('end', '%.3f' %(FVCO_TARGET/1.0e9))


		
		VCO_CONFIG=self.pll.VCO_CTUNE(FVCO_TARGET, SEL_FORCE=self.SEL_FORCE.get(), SEL_INIT=int(self.SEL_INIT.get()), FREQ_FORCE=int(self.FREQ_FORCE.get()), FREQ_INIT_POS=int(self.FREQ_INIT_POS.get()), FREQ_MIN=int(self.SEL_FREQ_MIN.get()), FREQ_MAX=int(self.SEL_FREQ_MAX.get()), VTUNE_STEP=1.0e-3, VTUNE_FIX=float(self.VTUNE_FIX.get()), LMS8001_INTERNAL=bool(self.CTUNE_INTERNAL.get()))
		VCO_CONFIG['vconame']='VCO'
		#print VCO_CONFIG
		self.pll.def_vco(**VCO_CONFIG)
		
		self.combobox_vcosel.current(VCO_CONFIG['SEL'])
		self.combobox_vcofreq.current(VCO_CONFIG['FREQ'])
		self.combobox_vcovtune.current(int(VCO_CONFIG['VTUNE']/1.0e-3))

		self.check_pll_status()


	def check_pll_status(self):
		if (float(self.combobox_vcovtune.get())>VTH_HIGH):
			self.vtunehigh.set(True)
		else:
		#	print "VTUNE is not HIGH"
			self.vtunehigh.set(False)

		if (float(self.combobox_vcovtune.get())<VTH_LOW):
			self.vtunelow.set(True)
		else:
			self.vtunelow.set(False)

		ffmod=float(self.combobox_ffmod.get())
		FVCO=self.pll.vco.getF()
		FVCO_FBDIV=self.pll.div.getN()*self.pll.Fref
		FPLL=FVCO/ffmod
		
		FERR=abs(FVCO-FVCO_FBDIV)
		#print FERR
		#print FERR<10.0e3
		self.pll_lock.set(bool(FERR/FVCO<5.0e-6))
		#self.pll_lock.set(True)

		self.label_lofreq.configure(text=('PLL Output Freq= %.3f GHz' %(FPLL/1.0e9)))
		self.label_vcofreq.configure(text=('VCO Freq= %.3f GHz') %(FVCO/1.0e9))


	def update_FVCO_TARGET(self):
		self.def_div()
		FVCO_TARGET=self.pll.div.getN()*self.pll.Fref

		self.entry_fvco.delete(0, 'end')
		self.entry_fvco.insert('end', '%.3f' %(FVCO_TARGET/1.0e9))

		print "Info: You may need to retune the VCO frequency for new feedback-divider settings.\nCheck PLL_LOCK indicator in lower left corner."


	

	def update_pnoise(self):
		if (self.radio_pnoise.get()==1):
			self.entry_ref_foff.configure(state='enabled')
			self.entry_ref_pn.configure(state='enabled')
			self.entry_ref_floor.configure(state='enabled')

			self.entry_fbdiv_foff.configure(state='disabled')
			self.entry_fbdiv_pn.configure(state='disabled')
			self.entry_fbdiv_floor.configure(state='disabled')

			self.entry_vco_foff.configure(state='disabled')
			self.entry_vco_pn.configure(state='disabled')
			self.entry_vco_fc.configure(state='disabled')
		else:
			self.entry_ref_foff.configure(state='disabled')
			self.entry_ref_pn.configure(state='disabled')
			self.entry_ref_floor.configure(state='disabled')

			self.entry_fbdiv_foff.configure(state='disabled')
			self.entry_fbdiv_pn.configure(state='disabled')
			self.entry_fbdiv_floor.configure(state='disabled')

			self.entry_vco_foff.configure(state='disabled')
			self.entry_vco_pn.configure(state='disabled')
			self.entry_vco_fc.configure(state='disabled')

			if (self.radio_pnoise.get()==2):
				self.fbdiv_fpn=fpn_fbdiv_sim_noLDO
				self.fbdiv_pn=pn_fbdiv_sim_noLDO
				self.fbdiv_noise_floor=noise_floor_fbdiv_sim_noLDO

				self.vco_fc=fc_vco_sim_noLDO
				self.vco_fpn=fpn_vco_sim_noLDO
				self.vco_pn=pn_vco_sim_noLDO
				self.vco_noise_floor=noise_floor_vco_sim_noLDO
				
				self.xbuf=ref(Fref=self.pll.Fref)
				self.xbuf.setNoise(fpn=fpn_xbuf_sim_noLDO, pn=pn_xbuf_sim_noLDO, noise_floor=noise_floor_xbuf_sim_noLDO)

				self.cp_In_floor=In_cp_white_sim_noLDO

			elif (self.radio_pnoise.get()==3):
				self.fbdiv_fpn=fpn_fbdiv_sim_mic37122
				self.fbdiv_pn=pn_fbdiv_sim_mic37122
				self.fbdiv_noise_floor=noise_floor_fbdiv_sim_mic37122

				self.vco_fc=fc_vco_sim_mic37122
				self.vco_fpn=fpn_vco_sim_mic37122
				self.vco_pn=pn_vco_sim_mic37122
				self.vco_noise_floor=noise_floor_vco_sim_mic37122
				
				self.xbuf=ref(Fref=self.pll.Fref)
				self.xbuf.setNoise(fpn=fpn_xbuf_sim_mic37122, pn=pn_xbuf_sim_mic37122, noise_floor=noise_floor_xbuf_sim_mic37122)

				self.cp_In_floor=In_cp_white_sim_mic37122
				
			elif (self.radio_pnoise.get()==4):
				self.fbdiv_fpn=fpn_fbdiv_sim_adm7155
				self.fbdiv_pn=pn_fbdiv_sim_adm7155
				self.fbdiv_noise_floor=noise_floor_fbdiv_sim_adm7155

				self.vco_fc=fc_vco_sim_adm7155
				self.vco_fpn=fpn_vco_sim_adm7155
				self.vco_pn=pn_vco_sim_adm7155
				self.vco_noise_floor=noise_floor_vco_sim_adm7155
				
				self.xbuf=ref(Fref=self.pll.Fref)
				self.xbuf.setNoise(fpn=fpn_xbuf_sim_adm7155, pn=pn_xbuf_sim_adm7155, noise_floor=noise_floor_xbuf_sim_adm7155)

				self.cp_In_floor=In_cp_white_sim_adm7155

		self.def_vco_pnoise()
		self.def_ref_pnoise()
		self.def_fbdiv_pnoise()

			
		return None

	#def update_pll_status_frame(self):
	#	fvco=float(self.entry_fvco.get())*1.0e9
	#	ffmod=float(self.combobox_ffmod.get())
	#	fpll=fvco/ffmod
	#	vtune=float(self.combobox_vcovtune.get())
	#	if (vtune>0.9):
	#		self.vtunehigh.set(True)
	#	else:
	#		self.vtunehigh.set(False)
	#	if (vtune<0.3):
	#		self.vtunelow.set(True)
	#	else:
	#		self.vtunelow.set(False)
		
		
	#	self.label_lofreq.configure(text=('PLL Output Freq= %.2f GHz' %(fpll/1.0e9)))
	#	self.label_vcofreq.configure(text=('VCO Freq= %.2f GHz') %(fvco/1.0e9))
		

	#def def_ref_pnoise(self):
	#	self.ref.setNoise(fpn=fpn_ref, pn=pn_ref, noise_floor=noise_floor_ref)

	#def plot_ref_pnoise(self):
		
		
	#	self.def_ref_pnoise()
	#	pn_xbuf=self.ref.calc_pnoise(f=self.flog)

	
	#	plotpnoise(self.flog, pn_xbuf, 1, title='Reference Source Phase Noise Profile')
	#	show_plots()

	def def_ref_pnoise(self, plot_pn=False):
		if not self.def_ref():
			return None
		
		if (self.radio_pnoise.get()>1):
			if (self.ref.getFref()==30.72e6):
				fpn_ref=fpn_ref_e6245lf
				pn_ref=pn_ref_e6245lf
				noise_floor_ref=noise_floor_ref_e6245lf
			elif (self.ref.getFref()==40.0e6):
				fpn_ref=fpn_ref_rtx5032a
				pn_ref=pn_ref_rtx5032a
				noise_floor_ref=noise_floor_ref_rtx5032a
			else:
				fpn_ref=fpn_ref_e6245lf
				pn_ref=pn_ref_e6245lf
				noise_floor_ref=noise_floor_ref_e6245lf
			
			self.entry_ref_foff.config(state='enabled')
			self.entry_ref_pn.config(state='enabled')
			self.entry_ref_floor.config(state='enabled')
			
			self.entry_ref_foff.delete(0,'end')
			self.entry_ref_pn.delete(0,'end')
			self.entry_ref_floor.delete(0,'end')

			
			
			self.entry_ref_foff.insert('end',' '.join(str('%.2e' %(e)) for e in fpn_ref))
			self.entry_ref_pn.insert('end',' '.join(str('%.2f' %(e)) for e in pn_ref))
			self.entry_ref_floor.insert('end',str('%.2f' %(noise_floor_ref)))

			self.entry_ref_foff.config(state='disabled')
			self.entry_ref_pn.config(state='disabled')
			self.entry_ref_floor.config(state='disabled')
			
			self.ref.setNoise(fpn=fpn_ref, pn=pn_ref, noise_floor=noise_floor_ref)
			pn_refonly=self.ref.calc_pnoise(f=self.flog)
			pn_xbuf=self.xbuf.calc_pnoise(f=self.flog)
			pn_ref_xbuf=10.0*np.log10(np.power(10.0, pn_refonly/10.0)+np.power(10.0, pn_xbuf/10.0))
		else:
			fpn_str=self.entry_ref_foff.get()
			pn_str=self.entry_ref_pn.get()
			noise_floor_str=self.entry_ref_floor.get()

			fpn_str_list=fpn_str.split()
			pn_str_list=pn_str.split()
			try:
				noise_floor=float(noise_floor_str)
			except:
				tkMessageBox.showinfo('Error! Reference PN GUI Input', 'Wrong Input for reference NOISE FLOOR, please enter REAL number value')
				return None

			fpn=[]
			pn=[]

			if (len(fpn_str_list)==len(pn_str_list)):
				for i in range(0, len(fpn_str_list)):
					try:
						fpn.append(float(fpn_str_list[i]))
						pn.append(float(pn_str_list[i]))
					except:
						tkMessageBox.showinfo('Error! Reference PN GUI Input', 'Wrong Input for offset frequency or phase noise value, please enter REAL number values')
						return None
				self.ref.setNoise(fpn=fpn, pn=pn, noise_floor=noise_floor)
				pn_refonly=self.ref.calc_pnoise(f=self.flog)
				pn_ref_xbuf=pn_refonly
			else:
				#print "Correct the code! Should display message box!!!!"
				tkMessageBox.showinfo('Error! Reference PN GUI Input', 'List of offset frequencies and phase noise values should have the same length.')
				print "List of offset frequencies and phase noise values should have the same length."
				return None
			
		if (plot_pn):
			plotpnoise(self.flog, pn_ref_xbuf, 1, title='Reference Source + XBUF Phase Noise Profile', line_color=self.line_color, font_name=self.font_name)			
			show_plots()

	def plot_cp_In(self):
		In_CP=self.pll.cp.In(self.pll.flog, self.pll.pfd.get_rst_del()*self.pll.Fref)
		plotlogx(self.flog, In_CP/1.0e-12, 2, xlabel='Frequency [Hz]', ylabel='$I_{n,CP}$ [pA/sqrt(Hz)]', title='Charge-Pump Output Current Noise Density', line_color=self.line_color, font_name=self.font_name)
		show_plots()

	def optimize_Iofs(self):
		# Get indexes of Combos that define CP current settings	
		cp_pulse_ind=self.combobox_cp_pulse.current()
		cp_offset_ind=self.combobox_cp_offset.current()
		ict_cp_ind=self.combobox_cp_ict.current()
		# Calculate Unit current values of CP pulse and offset current
		Ipulse_0=25.0*ict_cp_ind*1.0/16.0
		Iofs_0=Ipulse_0/4.0
		# Get list of possible offset current values
		Iofs_values=self.combobox_cp_offset['values']
		
		if not (self.INTMOD_EN.get()):
			# Targeted offset current value is 3% of Pulse current value - in FranN mode of operation
			Iofs_target=0.03*float(self.combobox_cp_pulse.get())
			ofs_ind=max(1, int(round(Iofs_target/float(Iofs_values[1]))))
			self.combobox_cp_offset.current(ofs_ind)
			
		
		else:
			# In integer-N mode, no need to use offset current value
			self.combobox_cp_offset.current(0)
			
		self.def_cp()


	def plot_lpf_Z(self):
		Z_LPF=self.pll.lpf.tfunc(self.pll.flog)
		Z_LPF=np.abs(Z_LPF)

		plotlogx(self.flog, Z_LPF/1.0e3, 3, xlabel='Frequency [Hz]', ylabel='$Z_{LPF}$ [kOhm]', title='Loop-Filter Impedance Vs. Frequency', line_color=self.line_color, font_name=self.font_name)
		show_plots()

	def plot_lpf_Vn(self):
		Vn_LPF=self.pll.lpf.Vn(self.pll.flog)
		Vn_LPF=np.abs(Vn_LPF)
		plotlogx(self.flog, Vn_LPF/1.0e-9, 4, xlabel='Frequency [Hz]', ylabel='$V_n$ [nV/sqrt(Hz)]', title='Loop-Filter Output Voltage Noise Density', line_color=self.line_color, font_name=self.font_name)
		show_plots()

	def plot_vco_tcurve(self):
		vco_sel=self.pll.vco.SEL
		vco_freq=self.pll.vco.FREQ
		vco_vtune=self.pll.vco.VTUNE

		(vtune_x, vco_freqs_y)=self.pll.vco.get_TCURVE(vco_sel, vco_freq, VTUNE_STEP=1.0e-3)

		plotsig(vtune_x, vco_freqs_y/1.0e9, 5, xlabel='$V_{TUNE}$ [V]', ylabel='$F_{VCO}$ [GHz]', title='VCO Frequency Tuning Curve', line_color=self.line_color, font_name=self.font_name)
		setmarkers(5, [vco_vtune], vtune_x, vco_freqs_y/1.0e9, 'V', 'GHz', fxy=(0.05, -0.05), text_format=('%.3f', '%.3f'), font_name=self.font_name) 
		show_plots()
	
	def def_vco_pnoise(self, plot_pn=False):
		#self.pll.def_vcoPNoise(fc=fc_vco_sim_noLDO, pn=pn_vco_sim_noLDO, fpn=fpn_vco_sim_noLDO)
		#pn_vco=self.pll.vco.calc_pnoise(self.flog)
		
		if (self.radio_pnoise.get()>0):
			vco_pn=[]
			for i in range(0, len(self.vco_pn)):
				vco_pn.append(self.vco_pn[i]+20.0*math.log10(self.pll.vco.getF()/4.0e9))
			
			self.pll.def_vcoPNoise(fc=self.vco_fc, pn=vco_pn, fpn=self.vco_fpn, noise_floor=self.vco_noise_floor)
			#pn_vco=self.pll.vco.calc_pnoise(self.flog)+20.0*math.log10(self.pll.vco.getF()/4.0e9)
			pn_vco=self.pll.vco.calc_pnoise(self.flog)

			find_1MHz=searchF(self.flog, 1.0e6, mode='lower-equal', order='last')
			
			self.entry_vco_foff.config(state='enabled')
			self.entry_vco_foff.delete(0, 'end')
			self.entry_vco_foff.insert('end', '%.2e' %(self.flog[find_1MHz]))
			self.entry_vco_foff.config(state='disabled')

			self.entry_vco_pn.config(state='enabled')
			self.entry_vco_pn.delete(0, 'end')
			self.entry_vco_pn.insert('end', '%.2f' %(pn_vco[find_1MHz]))
			self.entry_vco_pn.config(state='disabled')
			
		else:
			fpn_str=self.entry_vco_foff.get()
			pn_str=self.entry_vco_pn.get()
			fc_str=self.entry_vco_fc.get()

			fpn_str_list=fpn_str.split()
			pn_str_list=pn_str.split()

			fc=float(fc_str)

			fpn=[]
			pn=[]

			if (len(fpn_str_list)==len(pn_str_list)):
				for i in range(0, len(fpn_str_list)):
					fpn.append(float(fpn_str_list[i]))
					pn.append(float(pn_str_list[i]))
			
				self.pll.def_vcoPNoise(fpn=fpn, pn=pn, fc=fc, noise_floor=noise_floor_vco_sim_noLDO)
				pn_vco=self.pll.vco.calc_pnoise(self.flog)
			else:
				print "Correct the code! Should display message box!!!!"
				print "List of offset frequencies and phase noise values should have the same length."
				return None

			
		if (plot_pn):
			plotpnoise(self.flog, pn_vco, 6, title='VCO Phase Noise Profile', line_color=self.line_color, font_name=self.font_name)
			show_plots()
		
		#return None

	def def_fbdiv_pnoise(self, plot_pn=False):
		
		#self.pll.def_divPNoise(fpn=fpn_fbdiv_sim_noLDO, pn=pn_fbdiv_sim_noLDO, noise_floor=noise_floor_fbdiv_sim_noLDO)
		#pn_fbdiv=self.pll.div.calc_pnoise(self.flog)*sqrt(self.pll.calc_REF_MULT())
		
		if (self.radio_pnoise.get()>0):
			self.pll.def_divPNoise(fpn=self.fbdiv_fpn, pn=self.fbdiv_pn, noise_floor=self.fbdiv_noise_floor)
			pn_fbdiv=self.pll.div.calc_pnoise(self.flog)*sqrt(self.pll.calc_REF_MULT())

			find_10kHz=searchF(self.flog, 1.0e4, mode='lower-equal', order='last')
			find_1MHz=searchF(self.flog, 1.0e6, mode='lower-equal', order='last')

			self.entry_fbdiv_foff.config(state='enabled')
			self.entry_fbdiv_pn.config(state='enabled')
			self.entry_fbdiv_floor.config(state='enabled')
			
			self.entry_fbdiv_foff.delete(0, 'end')
			self.entry_fbdiv_foff.insert('end', '%.2e\t' %(self.flog[find_10kHz]))
			self.entry_fbdiv_foff.insert('end', '%.2e' %(self.flog[find_1MHz]))

			self.entry_fbdiv_pn.delete(0, 'end')
			self.entry_fbdiv_pn.insert('end', '%.2f\t' %(pn_fbdiv[find_10kHz]))
			self.entry_fbdiv_pn.insert('end', '%.2f' %(pn_fbdiv[find_1MHz]))

			self.entry_fbdiv_floor.delete(0, 'end')
			self.entry_fbdiv_floor.insert('end', '%.2f\t' %(self.fbdiv_noise_floor))
			
			
			self.entry_fbdiv_foff.config(state='disabled')
			self.entry_fbdiv_pn.config(state='disabled')
			self.entry_fbdiv_floor.config(state='disabled')
		else:
			fpn_str=self.entry_fbdiv_foff.get()
			pn_str=self.entry_fbdiv_pn.get()
			noise_floor_str=self.entry_fbdiv_floor.get()

			fpn_str_list=fpn_str.split()
			pn_str_list=pn_str.split()

			noise_floor=float(noise_floor_str)

			fpn=[]
			pn=[]

			if (len(fpn_str_list)==len(pn_str_list)):
				for i in range(0, len(fpn_str_list)):
					fpn.append(float(fpn_str_list[i]))
					pn.append(float(pn_str_list[i]))
			
				self.pll.def_divPNoise(fpn=fpn, pn=pn, noise_floor=noise_floor)
				pn_fbdiv=self.pll.div.calc_pnoise(self.flog)*sqrt(self.pll.calc_REF_MULT())
			else:
				print "Correct the code! Should display message box!!!!"
				print "List of offset frequencies and phase noise values should have the same length."
				return None

		if (plot_pn):
			plotpnoise(self.flog, pn_fbdiv, 7, title='Feedback-Divider Phase Noise Profile At the PFD Input', line_color=self.line_color, font_name=self.font_name)
			show_plots()
		
		#return None

	def oloop_sim(self):
		(f, open_loop)=self.pll.op_loop_tfunc()
		open_loop_phase=np.rad2deg(unwrap_phase(np.angle(open_loop)))+180
		
		plotlogx2(self.flog, 20*np.log10(np.abs(open_loop)), open_loop_phase, 8, 'Frequency [Hz]', 'Gain [dB]', 'Phase [deg]', 'PLL Open Loop Transfer Function - Mag & Phase', font_name=self.font_name)
		show_plots()

	def cloop_sim(self):
		plt_list=[]
		legend_list=[]
		ffdiv_corr=-6.0*float(self.combobox_ffmod.current())
		if (self.cloop_ref.get()):
			(f, close_loop_tf_REF)=self.pll.cl_loop_tfunc(block='REF')
			plt_cl_ref,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_REF))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', font_name=self.font_name)
			plt_list.append(plt_cl_ref)
			legend_list.append('REF+XBUF')
		if (self.cloop_vco.get()):
			(f, close_loop_tf_VCO)=self.pll.cl_loop_tfunc(block='VCO')
			plt_cl_vco,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_VCO))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', line_color='red', font_name=self.font_name)
			plt_list.append(plt_cl_vco)
			legend_list.append('VCO')
		if (self.cloop_fbdiv.get()):
			(f, close_loop_tf_DIV)=self.pll.cl_loop_tfunc(block='DIV')
			plt_cl_fbdiv,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_DIV))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', line_color='blue', font_name=self.font_name)
			plt_list.append(plt_cl_fbdiv)
			legend_list.append('FB-DIV')
		if (self.cloop_cp.get()):
			(f, close_loop_tf_CP)=self.pll.cl_loop_tfunc(block='CP')
			plt_cl_cp,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_CP))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', line_color='green', font_name=self.font_name)
			plt_list.append(plt_cl_cp)
			legend_list.append('PFD-CP')
		if (self.cloop_lpf.get()):
			(f, close_loop_tf_LPF)=self.pll.cl_loop_tfunc(block='LPF')
			plt_cl_lpf,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_LPF))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', line_color='pink', font_name=self.font_name)
			plt_list.append(plt_cl_lpf)
			legend_list.append('LPF')
		if (self.cloop_sdm.get()):
			(f, close_loop_tf_SDM)=self.pll.cl_loop_tfunc(block='SDM')
			plt_cl_sdm,=plotlogx(self.flog, 20*np.log10(np.abs(close_loop_tf_SDM))+ffdiv_corr, 9, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function - Mag. Response', line_color='orange', font_name=self.font_name)
			plt_list.append(plt_cl_sdm)
			legend_list.append('SDM-MOD')
		
		self.pll.dynamics_summary()
		if (len(plt_list)>0):
			setlegend(9, plt_list, legend_list, font_name=self.font_name)
			show_plots()

		

	def tran_sim(self):
		try:
			FSTEP_MHz=float(self.entry_fstep.get())
		except:
			tkMessageBox.showinfo('Error! Freq. Step at PLL Output Definition', 'Frequency Step at PLL output for transient analysis should be POSITIVE REAL number.')
			return None
		
		fstep_response=self.pll.fstep_response(Ts=1/200.0e6, Tstop=50.0e-6, FSTEP_OUT=FSTEP_MHz*1.0e6)
		t=fstep_response['TIME']
		if (self.tran_pherr.get()):
			phe=fstep_response['PHE_OUT']
			plotsig(t/1.0e-6, phe, 10, 'time [$\mu$s]', 'Phase [rad]', 'Phase Error vs. Time - PLL Frequency Step Response', line_color=self.line_color, font_name=self.font_name)
		if (self.tran_vtune.get()):
			vtune=fstep_response['VTUNE']
			plotsig(t/1.0e-6, vtune, 11, 'time [$\mu$s]', 'Voltage [V]', 'VCO Tuning Voltage vs. Time - PLL Frequency Step Response', line_color=self.line_color, font_name=self.font_name)
	
		plt_list=[]
		legend_list=[]
		if (self.tran_fvco.get()):
			fvco=fstep_response['FOUT']
			plt_tran_fvco,=plotsig(t/1.0e-6, fvco/1.0e9, 12, 'time [$\mu$s]', 'F [GHz]', 'Frequency vs. Time - PLL Frequency Step Response', line_color='black', font_name=self.font_name)
			plt_list.append(plt_tran_fvco)
			legend_list.append('$F_{VCO}$')
		if (self.tran_fpll.get()):
			fout=fstep_response['FOUT']/(2**float(self.combobox_ffmod.current()))
			plt_tran_fout,=plotsig(t/1.0e-6, fout/1.0e9, 12, 'time [$\mu$s]', 'F [GHz]', 'Frequency vs. Time - PLL Frequency Step Response', line_color='blue', font_name=self.font_name)
			plt_list.append(plt_tran_fout)
			legend_list.append('$F_{OUT}$')
		if (self.tran_ferr.get()):
			ferr=fstep_response['FERR']
			plotsig(t/1.0e-6, ferr/1.0e6, 13, 'time [$\mu$s]', '$F_{ERR}$ [MHz]', 'Frequency Error vs. Time - PLL Frequency Step Response', line_color=self.line_color, font_name=self.font_name)


		if (self.tran_fvco.get() or self.tran_fpll.get()):
			setlegend(12, plt_list, legend_list, font_name=self.font_name)
		
		if (self.tran_pherr.get() or self.tran_fvco.get() or self.tran_fpll.get() or self.tran_vtune.get() or self.tran_ferr.get()):
			show_plots()
		
		
	def pnoise_sim(self):
		self.update_pnoise()
		
		if (self.radio_pnoise.get()>1):
			#self.ref.setNoise(fpn=fpn_ref, pn=pn_ref, noise_floor=noise_floor_ref)
			pn_refonly=self.ref.calc_pnoise(f=self.flog)
			pn_xbuf=self.xbuf.calc_pnoise(f=self.flog)
			pn_ref=10.0*np.log10(np.power(10.0, pn_refonly/10.0)+np.power(10.0, pn_xbuf/10.0))
		else:
			pn_ref=self.ref.calc_pnoise(f=self.flog)
		
		(fpn, pn_PLL)=self.pll.pnoise(pn_ref=pn_ref, SDM_NOISE=(not bool(self.INTMOD_EN.get())))
		ffdiv_corr=-6.0*float(self.combobox_ffmod.current())
		
		print self.pll
		
		plt_list=[]
		legend_list=[]
		PH_ERR_RMS=calc_PH_ERR_RMS(fpn, np.array(pn_PLL['TOTAL'])+ffdiv_corr, min(fpn), max(fpn))
		plt_pn_PLL,=plotpnoise(fpn, np.array(pn_PLL['TOTAL'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='black', font_name=self.font_name)
		plt_list.append(plt_pn_PLL)
		legend_list.append('OUT\nInt Ph.Err(rms)=%.3f deg' %(PH_ERR_RMS))
		if (self.cont_vco.get()):
			plt_pn_VCO,=plotpnoise(fpn, np.array(pn_PLL['VCO'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='red', font_name=self.font_name)
			plt_list.append(plt_pn_VCO)
			legend_list.append('VCO')
		if (self.cont_ref.get()):
			plt_pn_REF,=plotpnoise(fpn, np.array(pn_PLL['REF'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='grey', font_name=self.font_name)
			plt_list.append(plt_pn_REF)
			legend_list.append('REF+XBUF')
		if (self.cont_pfdcp.get()):
			plt_pn_CP,=plotpnoise(fpn, np.array(pn_PLL['CP'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='green', font_name=self.font_name)
			plt_list.append(plt_pn_CP)
			legend_list.append('PFD-CP')
		if (self.cont_lpf.get()):
			plt_pn_LPF,=plotpnoise(fpn, np.array(pn_PLL['LPF'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='pink', font_name=self.font_name)
			plt_list.append(plt_pn_LPF)
			legend_list.append('LPF')
		if (self.cont_sdm.get()):
			plt_pn_SDM,=plotpnoise(fpn, np.array(pn_PLL['SDM'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='orange', font_name=self.font_name)
			plt_list.append(plt_pn_SDM)
			legend_list.append('SDM')
		if (self.cont_fbdiv.get()):
			plt_pn_DIV,=plotpnoise(fpn, np.array(pn_PLL['DIV'])+ffdiv_corr, 14, title='LMS 8001 PLL - Phase Noise Analysis - %.3f GHz carrier' %(self.pll.vco.getF()/(2**(-ffdiv_corr/6.0)*1.0e9)), line_color='blue', font_name=self.font_name)
			plt_list.append(plt_pn_DIV)
			legend_list.append('FB-DIV')
		setlegend(14, plt_list, legend_list, font_name=self.font_name)
		setaxis(14, min(self.flog), max(self.flog), -160, -70)

		self.pll.noise_spurs_summary(fmin=min(self.flog), fmax=max(self.flog), pn_ref=pn_ref, SDM_NOISE=(not bool(self.INTMOD_EN.get())))
		
		show_plots()

	
	

	def initUI(self):
		self.parent.title("Lime-Micro LMS8001 PLL-Sim")
		self.style=Style()
		self.style.theme_use("default")

		self.columnconfigure(0, pad=1, weight=1)
		self.columnconfigure(1, pad=1, weight=1)
		self.columnconfigure(2, pad=1, weight=1)
		self.columnconfigure(3, pad=1, weight=1)


		self.rowconfigure(0, pad=10)
		self.rowconfigure(1, pad=1, weight=1)
		self.rowconfigure(2, pad=10, weight=1)
		self.rowconfigure(3, pad=1, weight=1)
		self.rowconfigure(4, pad=1, weight=1)
		self.rowconfigure(5, pad=1, weight=1)

		# Drop-down menu definition

		menubar=Menu(self.parent)
		self.parent.config(menu=menubar)
		
		fileMenu=Menu(menubar)
		
		fileMenu.add_command(label="Save Config", command=self.on_save_Config)
		fileMenu.add_command(label="Open Config", command=self.on_open_Config)
		fileMenu.add_command(label="Save PLL Summary", command=self.on_save_PLL_summary)
		
		fileMenu.add_separator()
		fileMenu.add_command(label="Exit", underline=0, command=self.onExit)
		menubar.add_cascade(label="File", underline=0, menu=fileMenu)

		editMenu=Menu(menubar)
		
		#editMenu.add_command(label='Configure')
		
		editConfigMenu=Menu(editMenu)
		#editConfigMenu.add_command(label='VCO')
		editConfigVCOMenu=Menu(editConfigMenu)
		editConfigVCOMenu.add_command(label='Model', command=self.on_VCO_model)
		editConfigVCOMenu.add_command(label='Coarse Tune Algo.', command=self.on_VCO_ctune)
		editConfigMenu.add_cascade(label='VCO', underline=0, menu=editConfigVCOMenu)
		
		editConfigMenu.add_command(label='CP', command=self.on_config_CP)
		
		editMenu.add_cascade(label='Configure', underline=0, menu=editConfigMenu)
		editMenu.add_command(label='Save/Open INI Files for LMS8001 PLL', command=self.on_gen_INI_Files)
		editMenu.add_command(label='Print PLL Summary', command=self.on_print_PLL_summary)
		editMenu.add_command(label='Reset', command=self.on_Reset)
		self.parent.bind('<F5>', self.on_Reset)
		editMenu.add_separator()		

		editMenu.add_command(label="Preferences", command=self.on_Pref)
		menubar.add_cascade(label="Edit", underline=0, menu=editMenu)
		
		helpMenu=Menu(menubar)

		helpMenu.add_command(label="Handbook", command=self.onHowTo)
		helpMenu.add_separator()
		helpMenu.add_command(label="About", command=self.onAbout)

		menubar.add_cascade(label="Help", underline=0, menu=helpMenu)

		# Toolbar definition
		toolbar=Frame(self.parent, borderwidth=0, relief=RAISED)
		script_dir=os.path.dirname(__file__)
				

		self.IconSave = Image.open(os.path.join(script_dir, "Icons/Save.png"))
		phIm_IconSave = ImageTk.PhotoImage(self.IconSave)

		tbSave=Button(toolbar, width=130, text='Save Config', relief=FLAT, image=phIm_IconSave, command=self.on_save_Config, compound="top")
		tbSave.image = phIm_IconSave
		tbSave.pack(side=LEFT, padx=0.1, pady=1)
			
		self.IconOpen = Image.open(os.path.join(script_dir, "Icons/Open.png"))
		phIm_IconOpen = ImageTk.PhotoImage(self.IconOpen)		

		tbOpen=Button(toolbar, width=130,  text='Open Config', relief=FLAT, image=phIm_IconOpen, command=self.on_open_Config, compound="top")
		tbOpen.image = phIm_IconOpen
		tbOpen.pack(side=LEFT, padx=0.1, pady=1)

		self.IconSaveSummary = Image.open(os.path.join(script_dir, "Icons/SaveSummary.png"))
		phIm_IconSaveSummary = ImageTk.PhotoImage(self.IconSaveSummary)

		tbSaveSummary=Button(toolbar, width=130,  text='Save PLL Summary', image=phIm_IconSaveSummary, relief=FLAT, command=self.on_save_PLL_summary, compound="top")
		tbSaveSummary.image = phIm_IconSaveSummary
		tbSaveSummary.pack(side=LEFT, padx=0.1, pady=1)

		self.IconPrintSummary = Image.open(os.path.join(script_dir, "Icons/PrintSummary.png"))
		phIm_IconPrintSummary = ImageTk.PhotoImage(self.IconPrintSummary)

		tbPrintSummary=Button(toolbar, width=130,  text='Save/Open INI Files', image=phIm_IconPrintSummary, relief=FLAT, command=self.on_gen_INI_Files,  compound="top")
		tbPrintSummary.image = phIm_IconPrintSummary
		tbPrintSummary.pack(side=LEFT, padx=0.1, pady=1)

		self.IconReset = Image.open(os.path.join(script_dir, "Icons/Reset.png"))
		phIm_IconReset = ImageTk.PhotoImage(self.IconReset)

		tbReset=Button(toolbar, width=130,  text='Reset Form (Ctrl+F5)', image=phIm_IconReset, relief=FLAT, command=self.on_Reset, compound="top")
		tbReset.image = phIm_IconReset
		tbReset.pack(side=LEFT, padx=0.1, pady=1)

		self.IconQuit = Image.open(os.path.join(script_dir, "Icons/Quit.png"))
		phIm_IconQuit = ImageTk.PhotoImage(self.IconQuit)

		tbQuit=Button(toolbar, width=130,  text='Exit', image=phIm_IconQuit, relief=FLAT, command=self.onExit, compound="top")
		tbQuit.image=phIm_IconQuit
		tbQuit.pack(side=LEFT, padx=0.1, pady=1)
		
		toolbar.pack(side=TOP, anchor=W, padx=2, pady=0.5)
		
		# Frame for Reference Frequency Definition
		self.ref_frame=LabelFrame(self, text='REFIN DEFINITION', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), relief=RAISED, borderwidth=0)
		self.ref_frame.columnconfigure(0, pad=10)
		self.ref_frame.columnconfigure(1, pad=1)
#		self.ref_frame.columnconfigure(2, pad=1)
#		self.ref_frame.columnconfigure(3, pad=3)

		self.ref_frame.rowconfigure(0, pad=1)
		self.ref_frame.rowconfigure(1, pad=1)
		self.ref_frame.rowconfigure(2, pad=1)
		self.ref_frame.rowconfigure(3, pad=1)
		self.ref_frame.rowconfigure(4, pad=1)
		
		label_ref=Label(self.ref_frame, text='REF Freq. [MHz]')
		label_ref.grid(row=0, column=0, sticky=W)
		self.entry_ref=Entry(self.ref_frame, width=16)
		#self.entry_ref.insert(END,"30.72")
		self.entry_ref.insert(END,"40.0")
		self.entry_ref.grid(row=0, column=1, sticky=W)
		self.entry_ref.bind("<Return>", self.def_ref)
		self.entry_ref.bind("<FocusOut>", self.def_ref)
		

		label_ref_foff=Label(self.ref_frame, text='REF FOFF Values [Hz]')
		label_ref_foff.grid(row=1, column=0, sticky=W)
		self.entry_ref_foff=Entry(self.ref_frame)
		#self.entry_ref_foff.insert(END)
		self.entry_ref_foff.grid(row=1, column=1, sticky=W+N)
		
		label_ref_pn=Label(self.ref_frame, text='REF Ph.Noise Values [dBc/Hz]')
		label_ref_pn.grid(row=2, column=0, sticky=W+N)
		self.entry_ref_pn=Entry(self.ref_frame)
		#self.entry_ref_foff.insert(END)
		self.entry_ref_pn.grid(row=2, column=1, sticky=W)

		label_ref_floor=Label(self.ref_frame, text='REF Noise-Floor [dBc/Hz]')
		label_ref_floor.grid(row=3, column=0, sticky=W+N)
		self.entry_ref_floor=Entry(self.ref_frame)
		#self.entry_ref_floor.insert(END)
		self.entry_ref_floor.grid(row=3, column=1, sticky=W+N)
		
		self.button_ref_pnoise=Button(self.ref_frame, text='Update&Plot REF Phase Noise', command=lambda:self.def_ref_pnoise(plot_pn=True))
		self.button_ref_pnoise.grid(row=4, column=0, columnspan=2, sticky=W+N+E)
		self.ref_frame.grid(row=0, column=0, columnspan=2, sticky=W+E)

		# Frame for PLL Analysis Frequnency Sweep Definition
		self.fsweep_frame=LabelFrame(self, text='FREQ-SWEEP DEFINITION', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')),'bold'), relief=RAISED, borderwidth=0)
		self.fsweep_frame.columnconfigure(0, pad=10)
		self.fsweep_frame.columnconfigure(1, pad=1)

		self.fsweep_frame.rowconfigure(0, pad=1)
		self.fsweep_frame.rowconfigure(1, pad=1)
		self.fsweep_frame.rowconfigure(2, pad=1)
		self.fsweep_frame.rowconfigure(3, pad=1)
		self.fsweep_frame.rowconfigure(4, pad=0)		

		label_fsweep_fmin=Label(self.fsweep_frame, text='PLL Analysis Frequency Sweep Start [Hz]')
		label_fsweep_fmin.grid(row=0, column=0, sticky=W+N)
		self.combobox_fsweep_fmin=Combobox(self.fsweep_frame, values=flog_vals, width=5)
		self.combobox_fsweep_fmin.current(1)
		self.combobox_fsweep_fmin.grid(row=0, column=1, sticky=W+N)
		#self.combobox_fsweep_fmin.bind("<<ComboboxSelected>>", self.def_fsweep)
		

		label_fsweep_fmax=Label(self.fsweep_frame, text='PLL Analysis Frequency Sweep Stop [Hz]')
		label_fsweep_fmax.grid(row=1, column=0, sticky=W+N)
		self.combobox_fsweep_fmax=Combobox(self.fsweep_frame, values=flog_vals, width=5)
		self.combobox_fsweep_fmax.current(6)
		self.combobox_fsweep_fmax.grid(row=1, column=1, sticky=W+N)

		label_fsweep_nstep=Label(self.fsweep_frame, text='PLL Analysis Frequency Sweep Steps/Dec.')
		label_fsweep_nstep.grid(row=2, column=0, sticky=W+N)
		self.entry_fsweep_nstep=Entry(self.fsweep_frame, width=5)
		self.entry_fsweep_nstep.insert(END, 40)
		self.entry_fsweep_nstep.grid(row=2, column=1, sticky=W+N)


		self.button_def_flog=Button(self.fsweep_frame, text='Set PLL Frequency Sweep', width=40, height=2, command=self.def_fsweep)
		self.button_def_flog.grid(row=3, column=0, columnspan=2, sticky=W+S)

		self.fsweep_frame.grid(row=0, column=2, columnspan=2, sticky=W, padx=20)
		

		# Frame for PFD-CP Configuration
		vals_pfd_del=range(0,4)
		inds_cp_current=range(0,64)
		vals_cp_pulse=[]
		vals_cp_offset=[]
		for i in inds_cp_current:
			vals_cp_pulse.append(str(25.0*i))
			vals_cp_offset.append(str(25.0/4*i))
		vals_cp_ict=range(0,32)
		
		self.pfdcp_frame=LabelFrame(self, text='PFD-CP CONFIG', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')),'bold'), relief=RAISED, borderwidth=0)
		self.pfdcp_frame.columnconfigure(0, pad=1)
		self.pfdcp_frame.columnconfigure(1, pad=1)
		self.pfdcp_frame.rowconfigure(0, pad=1)
		self.pfdcp_frame.rowconfigure(1, pad=1)
		self.pfdcp_frame.rowconfigure(2, pad=1)
		self.pfdcp_frame.rowconfigure(3, pad=1)
		self.pfdcp_frame.rowconfigure(4, pad=1)
		
		label_pfddel=Label(self.pfdcp_frame, text='PFD_DEL')
		label_pfddel.grid(row=0, column=0, sticky=W)
		self.combobox_pfddel=Combobox(self.pfdcp_frame, width=3, values=vals_pfd_del)
		self.combobox_pfddel.current(0)
		self.combobox_pfddel.grid(row=0, column=1, sticky=E)
		self.combobox_pfddel.bind("<<ComboboxSelected>>", self.def_pfd)
		self.combobox_pfddel.bind("<Return>", self.def_pfd)
		self.combobox_pfddel.bind("<FocusOut>", self.def_pfd)

		label_cp_pulse=Label(self.pfdcp_frame, text='ICP_PULSE [uA]')
		label_cp_pulse.grid(row=1, column=0, sticky=W)
		self.combobox_cp_pulse=Combobox(self.pfdcp_frame, width=6, values=vals_cp_pulse)
		self.combobox_cp_pulse.current(4)
		self.combobox_cp_pulse.grid(row=1, column=1, sticky=E)
		self.combobox_cp_pulse.bind("<<ComboboxSelected>>", self.def_cp)
		self.combobox_cp_pulse.bind("<Return>", self.def_cp)
		self.combobox_cp_pulse.bind("<FocusOut>", self.def_cp)	

		label_cp_offset=Label(self.pfdcp_frame, text='ICP_OFS [uA]')
		label_cp_offset.grid(row=2, column=0, sticky=W)
		self.combobox_cp_offset=Combobox(self.pfdcp_frame, width=6, values=vals_cp_offset)
		self.combobox_cp_offset.current(0)
		self.combobox_cp_offset.grid(row=2, column=1, sticky=E)
		self.combobox_cp_offset.bind("<<ComboboxSelected>>", self.def_cp)
		self.combobox_cp_offset.bind("<Return>", self.def_cp)
		self.combobox_cp_offset.bind("<FocusOut>", self.def_cp)
		

		label_cp_ict=Label(self.pfdcp_frame, text='ICP_CT')
		label_cp_ict.grid(row=3, column=0, sticky=W)
		self.combobox_cp_ict=Combobox(self.pfdcp_frame, width=3, values=vals_cp_ict)
		self.combobox_cp_ict.grid(row=3, column=1, sticky=E)
		self.combobox_cp_ict.current(16)
		#self.combobox_cp_ict.bind("<<ComboboxSelected>>", self.update_cp_vals)
		self.combobox_cp_ict.bind("<<ComboboxSelected>>", self.def_cp)
		self.combobox_cp_ict.bind("<Return>", self.def_cp)
		self.combobox_cp_ict.bind("<FocusOut>", self.def_cp)
		

		dummy_label1=Label(self.pfdcp_frame)
		dummy_label1.grid(row=4, column=0)
		dummy_label2=Label(self.pfdcp_frame)
		dummy_label2=Label(self.pfdcp_frame)
		dummy_label2.grid(row=4, column=1)
		self.pfdcp_frame.grid(row=1, column=0, sticky=W+E)
		


		
		# Frame for Loop-FLT Configuration
		inds_lpf_comp=range(0,16)
		C1_vals=[]
		C2_vals=[]
		C3_vals=[]
		R2_vals=[]
		R3_vals=[]
		for i in inds_lpf_comp:
			C1_vals.append(str(i*1.2))
			C2_vals.append(str(150.0+i*10))
			C3_vals.append(str(5+i*1.2))
			if (i==0):
				R2_vals.append('Open')
				R3_vals.append('Open')
			else:
				R2_vals.append(str(24.6/i))
				R3_vals.append(str(14.9/i))

		
			
		
		self.lpf_frame=LabelFrame(self, text='LOOP-FILTER CONFIG', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')),'bold'), relief=RAISED, borderwidth=0)
		self.lpf_frame.columnconfigure(0, pad=1)
		self.lpf_frame.columnconfigure(1, pad=1)

		self.lpf_frame.rowconfigure(0, pad=1)
		self.lpf_frame.rowconfigure(1, pad=1)
		self.lpf_frame.rowconfigure(2, pad=1)
		self.lpf_frame.rowconfigure(3, pad=1)
		self.lpf_frame.rowconfigure(4, pad=1)
		
		label_C1=Label(self.lpf_frame, text='C1 [pF]')
		label_C1.grid(row=0, column=0, sticky=W)
		self.combobox_C1=Combobox(self.lpf_frame, values=C1_vals, width=6)
		self.combobox_C1.current(C1_def)
#		self.spinbox_C1.icursor(15)
		self.combobox_C1.grid(row=0, column=1, sticky=E)
		self.combobox_C1.bind("<<ComboboxSelected>>", self.def_lpf)
		self.combobox_C1.bind("<Return>", self.def_lpf)
		self.combobox_C1.bind("<FocusOut>", self.def_lpf)
		
		label_C2=Label(self.lpf_frame, text='C2 [pF]')
		label_C2.grid(row=1, column=0, sticky=W)
		self.combobox_C2=Combobox(self.lpf_frame, values=C2_vals, width=6)
		self.combobox_C2.current(C2_def)
		self.combobox_C2.grid(row=1, column=1, sticky=E)
		self.combobox_C2.bind("<<ComboboxSelected>>", self.def_lpf)
		self.combobox_C2.bind("<Return>", self.def_lpf)
		self.combobox_C2.bind("<FocusOut>", self.def_lpf)
		
		label_C3=Label(self.lpf_frame, text='C3 [pF]')
		label_C3.grid(row=2, column=0, sticky=W)
		self.combobox_C3=Combobox(self.lpf_frame, values=C3_vals, width=6)
		self.combobox_C3.current(C3_def)
		self.combobox_C3.grid(row=2, column=1, sticky=E)
		self.combobox_C3.bind("<<ComboboxSelected>>", self.def_lpf)
		self.combobox_C3.bind("<Return>", self.def_lpf)
		self.combobox_C3.bind("<FocusOut>", self.def_lpf)
		
		label_R2=Label(self.lpf_frame, text='R2 [kOhm]')
		label_R2.grid(row=3, column=0, sticky=W)
		self.combobox_R2=Combobox(self.lpf_frame, values=R2_vals, width=6)
		self.combobox_R2.current(R2_def)
		self.combobox_R2.grid(row=3, column=1, sticky=E)
		self.combobox_R2.bind("<<ComboboxSelected>>", self.def_lpf)
		self.combobox_R2.bind("<Return>", self.def_lpf)
		self.combobox_R2.bind("<FocusOut>", self.def_lpf)

		label_R3=Label(self.lpf_frame, text='R3 [kOhm]')
		label_R3.grid(row=4, column=0, sticky=W)
		self.combobox_R3=Combobox(self.lpf_frame, values=R3_vals, width=6)
		self.combobox_R3.current(R3_def)
		self.combobox_R3.grid(row=4, column=1, sticky=E)
		self.combobox_R3.bind("<<ComboboxSelected>>", self.def_lpf)
		self.combobox_R3.bind("<Return>", self.def_lpf)
		self.combobox_R3.bind("<FocusOut>", self.def_lpf)
		

		self.lpf_frame.grid(row=1, column=1, sticky=W+E)


		# Frame for VCO Configuration

		self.vco_frame=LabelFrame(self, text='VCO CONFIG', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')),'bold'), relief=RAISED, borderwidth=0)
		self.vco_frame.columnconfigure(0, pad=1)
		self.vco_frame.columnconfigure(1, pad=1)

		self.vco_frame.rowconfigure(0, pad=1)
		self.vco_frame.rowconfigure(1, pad=1)
		self.vco_frame.rowconfigure(2, pad=1)
		self.vco_frame.rowconfigure(3, pad=1)
		self.vco_frame.rowconfigure(4, pad=1)

		#vco_sel_vals=range(0,4)
		vco_sel_vals=['EXT-LO', '1', '2', '3']
		vco_freq_vals=range(0,256)
		vco_vtune_inds=range(0,1201)
		vco_vtune_vals=[]
		for i in vco_vtune_inds:
			vco_vtune_vals.append(str(i*1.0/1000))
		
		label_fvco=Label(self.vco_frame, text='Target VCO Freq [GHz]')
		label_fvco.grid(row=0, column=0, sticky=W)
		self.entry_fvco=Entry(self.vco_frame, width=5)
		self.entry_fvco.insert(END, 8.3)
		self.entry_fvco.grid(row=0, column=1, sticky=E)
		
		self.CTUNE_INTERNAL=BooleanVar()
		self.CTUNE_INTERNAL.set(True)
		#SEL_FORCE=False, SEL_INIT=2, FREQ_FORCE=False, FREQ_INIT=128, FREQ_INIT_POS=7, FREQ_MIN=5, FREQ_MAX=250, VTUNE_FIX=0.6, VTUNE_STEP=0.01
		self.SEL_FORCE=BooleanVar()
		self.SEL_FORCE.set(False)
		self.SEL_INIT=IntVar()
		self.SEL_INIT.set(2)
		self.FREQ_FORCE=BooleanVar()
		self.FREQ_FORCE.set(False)
		self.FREQ_INIT=IntVar()
		self.FREQ_INIT.set(128)
		self.FREQ_INIT_POS=IntVar()
		self.FREQ_INIT_POS.set(7)
		self.SEL_FREQ_MIN=IntVar()
		self.SEL_FREQ_MIN.set(5)
		self.SEL_FREQ_MAX=IntVar()
		self.SEL_FREQ_MAX.set(250)
		self.VTUNE_FIX=DoubleVar()
		self.VTUNE_FIX.set(0.6)
		
		self.button_vco_ctune=Button(self.vco_frame, text='VCO COARSE TUNE', command=self.vco_CTUNE)
		self.button_vco_ctune.grid(row=1, column=0, columnspan=2, sticky=N+W+E+S)

		label_vcosel=Label(self.vco_frame, text='VCO SEL')
		label_vcosel.grid(row=2, column=0, sticky=W)
		self.combobox_vcosel=Combobox(self.vco_frame, values=vco_sel_vals, width=5)
		self.combobox_vcosel.current(vco_sel_def)
		self.combobox_vcosel.grid(row=2, column=1, sticky=W)
		self.combobox_vcosel.bind("<<ComboboxSelected>>", self.def_vco)
		self.combobox_vcosel.bind("<Return>", self.def_vco)
		self.combobox_vcosel.bind("<FocusOut>", self.def_vco)
		
		label_vcofreq=Label(self.vco_frame, text='VCO FREQ')
		label_vcofreq.grid(row=3, column=0, sticky=W)
		self.combobox_vcofreq=Combobox(self.vco_frame, values=vco_freq_vals, width=5)
		self.combobox_vcofreq.current(128)
		self.combobox_vcofreq.grid(row=3, column=1, sticky=W)
		self.combobox_vcofreq.bind("<<ComboboxSelected>>", self.def_vco)
		self.combobox_vcofreq.bind("<Return>", self.def_vco)
		self.combobox_vcofreq.bind("<FocusOut>", self.def_vco)
		
		label_vcovtune=Label(self.vco_frame, text='VCO VTUNE [V]')
		label_vcovtune.grid(row=4, column=0, sticky=W)
		self.combobox_vcovtune=Combobox(self.vco_frame, values=vco_vtune_vals, width=5)
		self.combobox_vcovtune.set(vco_vtune_def)
		self.combobox_vcovtune.grid(row=4, column=1, sticky=W)
		self.combobox_vcovtune.bind("<<ComboboxSelected>>", self.def_vco)
		self.combobox_vcovtune.bind("<Return>", self.def_vco)
		self.combobox_vcovtune.bind("<FocusOut>", self.def_vco)

		self.vco_frame.grid(row=1, column=2, sticky=W+E, padx=20)
		
		# Frame for FF-DIV, FB-DIV and SDM Configuration
		self.divsdm_frame=LabelFrame(self, text='DIVIDERS-SDM CONFIG', font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')),'bold'), relief=RAISED, borderwidth=0)
		self.divsdm_frame.columnconfigure(0, pad=1)
		self.divsdm_frame.columnconfigure(1, pad=1)

		self.divsdm_frame.rowconfigure(0, pad=1)
		self.divsdm_frame.rowconfigure(1, pad=1)
		self.divsdm_frame.rowconfigure(2, pad=1)
		self.divsdm_frame.rowconfigure(3, pad=1)
		self.divsdm_frame.rowconfigure(4, pad=1)

		fbdiv_nint_vals=range(0, 2**10)
		fbdiv_nfrac_vals=range(0, 2**20)
		ffdiv_mod_codes=range(0,4)
		ffdiv_mod_vals=[]
		for i in ffdiv_mod_codes:
			ffdiv_mod_vals.append(str(2**i))
		
		
		label_ffdiv=Label(self.divsdm_frame, text='FFDIV-MOD')
		label_ffdiv.grid(row=0, column=0, sticky=W+N)
		self.combobox_ffmod=Combobox(self.divsdm_frame, values=ffdiv_mod_vals, width=5)
		self.combobox_ffmod.set(ffdiv_mod_def)
		self.combobox_ffmod.grid(row=0, column=1, sticky=E+N)
		self.FFMOD=1
		self.combobox_ffmod.bind("<<ComboboxSelected>>", self.def_div)
		self.combobox_ffmod.bind("<Return>", self.def_div)
		self.combobox_ffmod.bind("<FocusOut>", self.def_div)
		
		label_fbint=Label(self.divsdm_frame, text='FBDIV-NINT')
		label_fbint.grid(row=1, column=0, sticky=W+N)
		self.combobox_fbint=Combobox(self.divsdm_frame, values=fbdiv_nint_vals, width=5)
		self.combobox_fbint.set(fbdiv_nint_def)
		self.combobox_fbint.grid(row=1, column=1, sticky=E+N)
		self.combobox_fbint.bind("<<ComboboxSelected>>", self.def_div)
		self.combobox_fbint.bind("<Return>", self.def_div)
		self.combobox_fbint.bind("<FocusOut>", self.def_div)


		label_fbfrac=Label(self.divsdm_frame, text='FBDIV-NFRAC')
		label_fbfrac.grid(row=2, column=0, sticky=W+N)
		self.combobox_fbfrac=Combobox(self.divsdm_frame, values=fbdiv_nfrac_vals, width=8)
		self.combobox_fbfrac.set(fbdiv_nfrac_def)
		self.combobox_fbfrac.grid(row=2, column=1, sticky=E+N)
		self.combobox_fbfrac.bind("<<ComboboxSelected>>", self.def_div)
		self.combobox_fbfrac.bind("<Return>", self.def_div)
		self.combobox_fbfrac.bind("<FocusOut>", self.def_div)
		
		self.INTMOD_EN=IntVar()
		self.cbox_intmod=Checkbutton(self.divsdm_frame, text='INT-N MODE', variable=self.INTMOD_EN, onvalue=1, offvalue=0, command=self.def_div)
		self.cbox_intmod.grid(row=3, column=0, sticky=W+N)
		self.PDIV2_EN=IntVar()
		self.cbox_pdiv2=Checkbutton(self.divsdm_frame, text='PDIV2_EN', variable=self.PDIV2_EN, onvalue=1, offvalue=0, command=self.def_div)
		self.cbox_pdiv2.grid(row=4, column=0, sticky=W+N)

		self.divsdm_frame.grid(row=1, column=3, sticky=W+N+E)

		# PFD-CP Specific Options and Plots
		
		self.cp_fc=DoubleVar()
		self.cp_fc.set(cp_fc_def)
		self.cp_slope=DoubleVar()
		self.cp_slope.set(cp_slope_def)
		self.pll.cp=lms8001_cp(fc=float(self.cp_fc.get()), slope=float(self.cp_slope.get()))
		
		self.buttons_cp_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.button_Incp=Button(self.buttons_cp_frame, text='Plot CP Noise Current', width=19, command=self.plot_cp_In)
		self.button_Incp.grid(row=0, column=0, sticky=W+N)

		self.button_optIofs=Button(self.buttons_cp_frame, text='Optimize ICP_OFS value', width=19, command=self.optimize_Iofs)
		self.button_optIofs.grid(row=1, column=0, sticky=W+N)
		self.buttons_cp_frame.grid(row=2, column=0, sticky=W+N)
		
		# Loop-FLT Specfic-Options and Plots
		self.lpfopt_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.lpfopt_frame.columnconfigure(0, pad=1)
		self.lpfopt_frame.columnconfigure(1, pad=1)
		self.lpfopt_frame.rowconfigure(0, pad=1)
		self.lpfopt_frame.rowconfigure(1, pad=1)
		self.lpfopt_frame.rowconfigure(2, pad=1)
		self.lpfopt_frame.rowconfigure(3, pad=1)
		self.lpfopt_frame.rowconfigure(4, pad=1)
		self.lpfopt_frame.rowconfigure(5, pad=1)
		
		self.button_ZLPF=Button(self.lpfopt_frame, text='Plot LPF Impedance', command=self.plot_lpf_Z)
		self.button_ZLPF.grid(row=0, columnspan=2, sticky=E+W+N)

		self.button_LPF_Vn=Button(self.lpfopt_frame, text='Plot LPF Noise Voltage', command=self.plot_lpf_Vn)
		self.button_LPF_Vn.grid(row=1, columnspan=2, sticky=E+W+N)
		
		label_LoopFLT_Fc=Label(self.lpfopt_frame, text="Target Fc [kHz]")
		label_LoopFLT_Fc.grid(row=2, column=0, sticky=W)
		self.entry_lpf_fc=Entry(self.lpfopt_frame, width=6)
		self.entry_lpf_fc.insert(END, 180.0)
		self.entry_lpf_fc.grid(row=2, column=1, sticky=W)
		

		label_LoopFLT_PM=Label(self.lpfopt_frame, text='Ph. Margin [deg]')
		label_LoopFLT_PM.grid(row=3, column=0, sticky=W)
		self.entry_PM=Entry(self.lpfopt_frame, width=6)
		self.entry_PM.insert(END, 49.8)
		self.entry_PM.grid(row=3, column=1, sticky=W)
		
		self.button_OptLPF=Button(self.lpfopt_frame, text='Optimize/Update LPF', command=self.optim_LPF)
		self.button_OptLPF.grid(row=4, columnspan=2, sticky=E+W)
		
		self.button_OptLPF=Button(self.lpfopt_frame, text='Optimize/Update CP-LPF', command=self.optim_CPLPF)
		self.button_OptLPF.grid(row=5, columnspan=2, sticky=E+W)		

		self.lpfopt_frame.grid(row=2, column=1, sticky=W+N)

		# VCO Specfic-Options and Plots
		self.vcoopt_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.vcoopt_frame.columnconfigure(0, pad=1)
		self.vcoopt_frame.columnconfigure(1, pad=1)
		self.vcoopt_frame.rowconfigure(0, pad=1)
		self.vcoopt_frame.rowconfigure(1, pad=1)
		self.vcoopt_frame.rowconfigure(2, pad=1)
		self.vcoopt_frame.rowconfigure(3, pad=1)
		self.vcoopt_frame.rowconfigure(4, pad=1)
		self.vcoopt_frame.rowconfigure(5, pad=1)
		self.vcoopt_frame.rowconfigure(6, pad=1)

		self.button_VCOTUNE=Button(self.vcoopt_frame, text='Plot VCO Tuning Curve', width=23, command=self.plot_vco_tcurve)
		self.button_VCOTUNE.grid(row=0, column=0, columnspan=2, sticky=W+E+N+S)
	
		label_vcopn_foff=Label(self.vcoopt_frame, text='VCO Ph.Noise FOFF Values [Hz]')
		label_vcopn_foff.grid(row=1, column=0, columnspan=2, sticky=W+E+N+S)
		self.entry_vco_foff=Entry(self.vcoopt_frame, width=23)
		self.entry_vco_foff.grid(row=2, column=0, columnspan=2, sticky=W+E+N+S)
		
		label_vcopn=Label(self.vcoopt_frame, text='VCO Ph.Noise Values [dBc/Hz]')
		label_vcopn.grid(row=3, column=0, columnspan=2, sticky=W+E+N+S)
		self.entry_vco_pn=Entry(self.vcoopt_frame, width=23)
		self.entry_vco_pn.grid(row=4, column=0, columnspan=2, sticky=W+E+N+S)
		
		label_vcofc=Label(self.vcoopt_frame, text='VCO Corner Freq. [kHz]', width=20)
		label_vcofc.grid(row=5, column=0, sticky=W)
		self.entry_vco_fc=Entry(self.vcoopt_frame, width=5)
		self.entry_vco_fc.insert(END, 200.0)
		self.entry_vco_fc.grid(row=5, column=1, sticky=E)

		self.button_vcopn=Button(self.vcoopt_frame, text='Update&Plot VCO Phase Noise', command=lambda:self.def_vco_pnoise(plot_pn=True))
		self.button_vcopn.grid(row=6, column=0, columnspan=2, sticky=E+W+N+S)
		

		self.vcoopt_frame.grid(row=2, column=2, sticky=W+N+E, padx=20)

		# DIVs Specfic-Options and Plots
		self.div_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.div_frame.columnconfigure(0, pad=1)
		self.div_frame.columnconfigure(1, pad=1)
		self.div_frame.rowconfigure(0, pad=1)
		self.div_frame.rowconfigure(1, pad=1)
		self.div_frame.rowconfigure(2, pad=1)
		self.div_frame.rowconfigure(3, pad=1)
		self.div_frame.rowconfigure(4, pad=1)
		self.div_frame.rowconfigure(5, pad=1)
		self.div_frame.rowconfigure(6, pad=1)


		self.button_update_vcofreq=Button(self.div_frame, text='Calculate/Update VCO Freq', command=self.update_FVCO_TARGET)
		self.button_update_vcofreq.grid(row=0, column=0, columnspan=2, sticky=W+E+N+S)
		
		label_fbdiv_foff=Label(self.div_frame, text='FB-DIV Ph.Noise FOFF [Hz]')
		label_fbdiv_foff.grid(row=1, column=0, columnspan=2, sticky=W+E+N+S)
		self.entry_fbdiv_foff=Entry(self.div_frame, width=23)
		self.entry_fbdiv_foff.grid(row=2, column=0, columnspan=2, sticky=W+E+N+S)

		label_fbdiv_pn=Label(self.div_frame, text='FB-DIV Ph.Noise Values [dBc/Hz]')
		label_fbdiv_pn.grid(row=3, column=0, columnspan=2, sticky=W+E+N+S)
		self.entry_fbdiv_pn=Entry(self.div_frame, width=23)
		self.entry_fbdiv_pn.grid(row=4, column=0, columnspan=2, sticky=W+E+N+S)

		Label(self.div_frame, text='FB-DIV Ph.Noise Floor [dBc/Hz]').grid(row=5, column=0, sticky=W+E+N+S)
		self.entry_fbdiv_floor=Entry(self.div_frame, width=6)
		self.entry_fbdiv_floor.grid(row=5, column=1, sticky=W+E+N+S)

		self.button_fbdiv_pn=Button(self.div_frame, text='Update&Plot FB-DIV Phase Noise', width=23, command=lambda:self.def_fbdiv_pnoise(plot_pn=True))
		self.button_fbdiv_pn.grid(row=6, column=0, columnspan=2, sticky=W+E+N+S)

	
		self.div_frame.grid(row=2, column=3, sticky=W+N+E)

		# PLL Status Info.
		self.pll_status_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.pll_status_frame.columnconfigure(0, pad=1)
		self.pll_status_frame.rowconfigure(0, pad=1)
		self.pll_status_frame.rowconfigure(1, pad=1)
		self.pll_status_frame.rowconfigure(2, pad=1)
		self.pll_status_frame.rowconfigure(3, pad=1)
		self.pll_status_frame.rowconfigure(4, pad=1)
		self.pll_status_frame.rowconfigure(5, pad=1)
		
		
		self.label_lofreq=Label(self.pll_status_frame)
		self.label_vcofreq=Label(self.pll_status_frame)
		self.vtunehigh=BooleanVar()		
		self.cbox_vtunehigh=Checkbutton(self.pll_status_frame, state='disabled', text='VTUNE_HIGH', onvalue=1, offvalue=0, variable=self.vtunehigh)
		self.vtunelow=BooleanVar()
		self.cbox_vtunelow=Checkbutton(self.pll_status_frame, state='disabled', text='VTUNE_LOW', onvalue=1, offvalue=0, variable=self.vtunelow)
		self.pll_lock=BooleanVar()
		self.cbox_pll_lock=Checkbutton(self.pll_status_frame, state='disabled', text='PLL_LOCK', onvalue=1, offvalue=0, variable=self.pll_lock)

		Label(self.pll_status_frame, text="PLL STATUS", font=(None, 9, 'bold')).grid(row=0, column=0, sticky=W+N)
		self.label_lofreq.grid(row=1, column=0, sticky=W+N)
		self.label_vcofreq.grid(row=2, column=0, sticky=W+N)
		self.cbox_vtunehigh.grid(row=3, column=0, sticky=W+N)
		self.cbox_vtunelow.grid(row=4, column=0, sticky=W+N)
		self.cbox_pll_lock.grid(row=5, column=0, sticky=W+N)
		
		self.pll_status_frame.grid(row=3, column=0, sticky=W+N+E)

		#self.update_pll_status_frame()

		# PLL Closed-Loop Analysis Setup

		self.cloop_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.cloop_frame.columnconfigure(0, pad=1)
		self.cloop_frame.rowconfigure(0, pad=1)
		self.cloop_frame.rowconfigure(1, pad=1)
		self.cloop_frame.rowconfigure(1, pad=1)
		self.cloop_frame.rowconfigure(2, pad=1)
		self.cloop_frame.rowconfigure(3, pad=1)
		self.cloop_frame.rowconfigure(4, pad=1)
		


		Label(self.cloop_frame, text='CLOSED-LOOP ANALYSIS SETUP', font=(None, 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky=W+N)
		Label(self.cloop_frame, text='Choose Transfer Functions to Plot').grid(row=1, column=0, columnspan=2, sticky=W+N)

		self.cloop_ref=BooleanVar()
		self.cloop_ref.set(True)
		self.cbox_cloop_ref=Checkbutton(self.cloop_frame, text='REF-OUT', onvalue=1, offvalue=0, variable=self.cloop_ref)
		self.cbox_cloop_ref.grid(row=2, column=0, sticky=W+N)

		self.cloop_cp=BooleanVar()
		self.cloop_cp.set(False)
		self.cbox_cloop_cp=Checkbutton(self.cloop_frame, text='CP-OUT', onvalue=1, offvalue=0, variable=self.cloop_cp)
		self.cbox_cloop_cp.grid(row=3, column=0, sticky=W+N)

		self.cloop_lpf=BooleanVar()
		self.cloop_lpf.set(False)
		self.cbox_cloop_lpf=Checkbutton(self.cloop_frame, text='LPF-OUT', onvalue=1, offvalue=0, variable=self.cloop_lpf)
		self.cbox_cloop_lpf.grid(row=4, column=0, sticky=W+N)

		self.cloop_vco=BooleanVar()
		self.cloop_vco.set(True)
		self.cbox_cloop_cp=Checkbutton(self.cloop_frame, text='VCO-OUT', onvalue=1, offvalue=0, variable=self.cloop_vco)
		self.cbox_cloop_cp.grid(row=2, column=1, sticky=W+N)

		self.cloop_fbdiv=BooleanVar()
		self.cloop_fbdiv.set(False)
		self.cbox_cloop_fbdiv=Checkbutton(self.cloop_frame, text='FBDIV-OUT', onvalue=1, offvalue=0, variable=self.cloop_fbdiv)
		self.cbox_cloop_fbdiv.grid(row=3, column=1, sticky=W+N)

		self.cloop_sdm=BooleanVar()
		self.cloop_sdm.set(False)
		self.cbox_cloop_sdm=Checkbutton(self.cloop_frame, text='SDM-OUT', onvalue=1, offvalue=0, variable=self.cloop_sdm)
		self.cbox_cloop_sdm.grid(row=4, column=1, sticky=W+N)

		self.cloop_frame.grid(row=3, column=1, sticky=W+N+E)

		# PLL Transient Analysis Setup
		self.tran_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.tran_frame.columnconfigure(0, pad=1)
		self.tran_frame.columnconfigure(1, pad=1)
		self.tran_frame.rowconfigure(0, pad=1)
		self.tran_frame.rowconfigure(1, pad=1)
		self.tran_frame.rowconfigure(2, pad=1)
		self.tran_frame.rowconfigure(3, pad=1)
		self.tran_frame.rowconfigure(4, pad=1)
		Label(self.tran_frame, text='TRANSIENT ANALYSIS SETUP', font=(None, 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky=W+N)
		Label(self.tran_frame, text='Freq. Step @ OUT [MHz]').grid(row=1, column=0, sticky=W+N)
		self.entry_fstep=Entry(self.tran_frame, width=5)
		self.entry_fstep.insert(END, '10.0')
		self.entry_fstep.grid(row=1, column=1, sticky=W+N)

		Label(self.tran_frame, text='Choose Signals to Plot').grid(row=2, column=0, columnspan=2, sticky=W+N)
		
		self.tran_vtune=BooleanVar()
		self.tran_vtune.set(True)
		self.cbox_tran_vtune=Checkbutton(self.tran_frame, text='VCO VTUNE', onvalue=1, offvalue=0, variable=self.tran_vtune)
		self.cbox_tran_vtune.grid(row=3, column=0, sticky=W+N)
		
		self.tran_ferr=BooleanVar()
		self.tran_ferr.set(False)
		self.cbox_tran_ferr=Checkbutton(self.tran_frame, text='FERR', onvalue=1, offvalue=0, variable=self.tran_ferr)
		self.cbox_tran_ferr.grid(row=4, column=0, sticky=W+N)

		self.tran_pherr=BooleanVar()
		self.tran_pherr.set(False)
		self.cbox_tran_pherr=Checkbutton(self.tran_frame, text='Ph.ERR', onvalue=1, offvalue=0, variable=self.tran_pherr)
		self.cbox_tran_pherr.grid(row=5, column=0, sticky=W+N)	

		self.tran_fvco=BooleanVar()
		self.tran_fvco.set(True)
		self.cbox_tran_fvco=Checkbutton(self.tran_frame, text='FVCO', onvalue=1, offvalue=0, variable=self.tran_fvco)
		self.cbox_tran_fvco.grid(row=3, column=1, sticky=W+N)

		self.tran_fpll=BooleanVar()
		self.tran_fpll.set(False)
		self.cbox_tran_fpll=Checkbutton(self.tran_frame, text='FPLL', onvalue=1, offvalue=0, variable=self.tran_fpll)
		self.cbox_tran_fpll.grid(row=4, column=1, sticky=W+N)	


		self.tran_frame.grid(row=3, column=2, sticky=W+N+E, padx=20)
		
		# Phase-Noise Analysis Setup
		self.pnoise_frame=Frame(self, relief=RAISED, borderwidth=0)
		self.pnoise_frame.columnconfigure(0, pad=1)
		self.pnoise_frame.columnconfigure(1, pad=1)
		self.pnoise_frame.rowconfigure(0, pad=1)
		self.pnoise_frame.rowconfigure(1, pad=1)
		self.pnoise_frame.rowconfigure(2, pad=1)
		self.pnoise_frame.rowconfigure(3, pad=1)
		self.pnoise_frame.rowconfigure(4, pad=1)
		self.pnoise_frame.rowconfigure(5, pad=1)
		self.pnoise_frame.rowconfigure(6, pad=1)
		self.pnoise_frame.rowconfigure(7, pad=1)
		self.pnoise_frame.rowconfigure(8, pad=1)
		
		Label(self.pnoise_frame, text='PNOISE ANALYSIS SETUP', font=(None, 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky=W+N)
		self.radio_pnoise=IntVar()
		self.radio_pnoise.set(2)
		Radiobutton(self.pnoise_frame, text="GUI Values, for REF PN only", variable=self.radio_pnoise, value=1, command=self.update_pnoise).grid(row=1, column=0, columnspan=2, sticky=W+N)
		Radiobutton(self.pnoise_frame, text="Simulated", variable=self.radio_pnoise, value=2, command=self.update_pnoise).grid(row=2, column=0, columnspan=2, sticky=W+N)
		#Radiobutton(self.pnoise_frame, text="Simulated, MIC31722 LDO", variable=self.radio_pnoise, value=3, command=self.update_pnoise).grid(row=3, column=0, columnspan=2, sticky=W+N)
		#Radiobutton(self.pnoise_frame, text="Simulated, ADM7155 LDO", variable=self.radio_pnoise, value=4, command=self.update_pnoise).grid(row=4, column=0, columnspan=2, sticky=W+N)

		Label(self.pnoise_frame, text='Plot contributions from:').grid(row=5, column=0, columnspan=2, sticky=W+N)
		
		self.cont_vco=BooleanVar()
		Checkbutton(self.pnoise_frame, text="VCO", onvalue=1, offvalue=0, variable=self.cont_vco).grid(row=6, column=0, sticky=W+N)
		
		self.cont_lpf=BooleanVar()
		Checkbutton(self.pnoise_frame, text="LPF", onvalue=1, offvalue=0, variable=self.cont_lpf).grid(row=7, column=0, sticky=W+N)

		self.cont_pfdcp=BooleanVar()
		Checkbutton(self.pnoise_frame, text="PFD-CP", onvalue=1, offvalue=0, variable=self.cont_pfdcp).grid(row=8, column=0, sticky=W+N)

		
		self.cont_ref=BooleanVar()
		Checkbutton(self.pnoise_frame, text="REF", onvalue=1, offvalue=0, variable=self.cont_ref).grid(row=6, column=1, sticky=W+N)

		self.cont_fbdiv=BooleanVar()
		Checkbutton(self.pnoise_frame, text="FB-DIV", onvalue=1, offvalue=0, variable=self.cont_fbdiv).grid(row=7, column=1, sticky=W+N)

		self.cont_sdm=BooleanVar()
		Checkbutton(self.pnoise_frame, text="SDM", onvalue=1, offvalue=0, variable=self.cont_sdm).grid(row=8, column=1, sticky=W+N)

		self.pnoise_frame.grid(row=3, column=3, sticky=W+N+E)

		

		# PLL Analysis Buttons
		#sh = self.parent.winfo_screenheight()
		#if (sys.platform=='win32' and sh<950):
		#	self.oLoopTFButton=Button(self, text='Open-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), 11, 'bold'), command=self.oloop_sim)
		#	self.oLoopTFButton.grid(row=4, column=0, sticky=W+N+E)
		#	self.cLoopTFButton=Button(self, text='Close-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), 11, 'bold'), command=self.cloop_sim)
		#	self.cLoopTFButton.grid(row=4, column=1, sticky=W+N+E)
		#	self.trRespButton=Button(self, text='PLL Transient Response',  height=3, font=(self.GUI_font.cget('family'), 11, 'bold'), command=self.tran_sim)
		#	self.trRespButton.grid(row=4, column=2, padx=0, sticky=W+N+E)
		#	self.phNoiseButton=Button(self, text='PLL Phase Noise Analysis',  height=3, font=(self.GUI_font.cget('family'), 11, 'bold'), command=self.pnoise_sim)
		#	self.phNoiseButton.grid(row=4, column=3, sticky=W+N+E)
		#else:
		#	self.oLoopTFButton=Button(self, text='Open-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.oloop_sim)
		#	self.oLoopTFButton.grid(row=4, column=0, sticky=W+N+E)
		#	self.cLoopTFButton=Button(self, text='Close-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.cloop_sim)
		#	self.cLoopTFButton.grid(row=4, column=1, sticky=W+N+E)
		#	self.trRespButton=Button(self, text='PLL Transient Response',  height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.tran_sim)
		#	self.trRespButton.grid(row=4, column=2, padx=0, sticky=W+N+E)
		#	self.phNoiseButton=Button(self, text='PLL Phase Noise Analysis',  height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.pnoise_sim)
		#	self.phNoiseButton.grid(row=4, column=3, sticky=W+N+E)
		self.oLoopTFButton=Button(self, text='Open-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.oloop_sim)
		self.oLoopTFButton.grid(row=4, column=0, sticky=W+N+E)
		self.cLoopTFButton=Button(self, text='Close-Loop PLL Analysis', height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.cloop_sim)
		self.cLoopTFButton.grid(row=4, column=1, sticky=W+N+E)
		self.trRespButton=Button(self, text='PLL Transient Response',  height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.tran_sim)
		self.trRespButton.grid(row=4, column=2, padx=0, sticky=W+N+E)
		self.phNoiseButton=Button(self, text='PLL Phase Noise Analysis',  height=3, font=(self.GUI_font.cget('family'), int(self.GUI_font.cget('size')), 'bold'), command=self.pnoise_sim)
		self.phNoiseButton.grid(row=4, column=3, sticky=W+N+E)

		self.def_fsweep(None)

		self.def_ALL()
		self.update_pnoise()
		
		# Make Object Containg References to all GUI widgets and variables defining the state of LMS8001_PLLSim
		self.GUI_ElemList=GUI_ElemList()
		self.make_GUI_ElemList()		

		#print dir(self)
		
		#self.pack(fill=BOTH, expand=True)
		#self.parent.update()



	


		
