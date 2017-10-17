from limemicro_pllsim2 import *

from Tkinter import Tk, Toplevel, Menu, LabelFrame, Frame, Label, RIGHT, LEFT, TOP, BOTTOM, BOTH, RAISED, W, E, END, N, S, IntVar, Spinbox, BooleanVar, Button, Event, CENTER, FLAT
from ttk import Style, Entry, Combobox, Checkbutton, Radiobutton
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk
import webbrowser
import matplotlib.font_manager
import tkFont
import time

# Copied from Python module LMS8001_EVB for LMS8001-IC configuration
from LMS8001_REGDESC import *
from LMS8001_regDataStructs import *




class gen_INI_win(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self)
		
		img = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'Icons/LMS8001_PLLSim.png'))
		self.tk.call('wm', 'iconphoto', self._w, img)
		self.resizable(0,0)
		self.parent=parent
		
		self.initUI()
		self.center_Window()
		
		# Update Config
		self.updateConfig()
		# Write Configuration to PLL Profile 0 REGBANK and PLL_CFG Register
		self.update_PLL_CFG_Reg()
		self.update_PLL_Profile_Regs()
		self.updateWindow()
		self.protocol("WM_DELETE_WINDOW", self.onQuit)

	def updateWindow(self):
		PLL_prof=self.combo_PLL_Profile.get()
		
		# PLL_VCO_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_VCO_CFG_'+PLL_prof)
		if not int(PLL_prof) in self.configuredPLLProfs:
			self.VCO_AAC_EN.set(1)
			self.update_VCO_AMP()
			self.combo_VCO_AMP.current(3)
		else:
			self.VCO_AAC_EN.set(reg['VCO_AAC_EN_'+PLL_prof])
			self.combo_VCO_AMP.current(reg['VCO_AMP_'+PLL_prof+'<6:0>'])
			self.update_VCO_AMP()
		self.combo_VCO_SWVDD.current(reg['VDIV_SWVDD_'+PLL_prof+'<1:0>'])	

		# PLL_FLOCK_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG1_'+PLL_prof)
		self.combo_R3_FLOCK.current(reg['FLOCK_R3_'+PLL_prof+'<3:0>'])
		self.combo_R2_FLOCK.current(reg['FLOCK_R2_'+PLL_prof+'<3:0>'])
		self.combo_C2_FLOCK.current(reg['FLOCK_C2_'+PLL_prof+'<3:0>'])
		self.combo_C1_FLOCK.current(reg['FLOCK_C1_'+PLL_prof+'<3:0>'])

		# PLL_FLOCK_CFG2_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG2_'+PLL_prof)
		self.combo_C3_FLOCK.current(reg['FLOCK_C3_'+PLL_prof+'<3:0>'])
		self.combo_PULSE_FLOCK.current(reg['FLOCK_PULSE_'+PLL_prof+'<5:0>'])
		self.combo_OFS_FLOCK.current(reg['FLOCK_OFS_'+PLL_prof+'<5:0>'])
		

		# PLL_FLOCK_CFG3 register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG3_'+PLL_prof)
		self.FLOCK_EN_D.set((reg['FLOCK_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&8)>>3)
		self.FLOCK_EN_C.set((reg['FLOCK_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&4)>>2)
		self.FLOCK_EN_B.set((reg['FLOCK_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&2)>>1)
		self.FLOCK_EN_A.set((reg['FLOCK_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&1))	
		self.combo_FLOCK_N.current(reg['FLOCK_N_'+PLL_prof+'<9:0>'])
		
		# Try to determine BWEF value for PLL profile if possible
		if not int(PLL_prof) in self.configuredPLLProfs:	
			self.combo_FLOCK_BWEF.current(1)
		else:
			if (self.parent.combobox_C1.current()==self.combo_C1_FLOCK.current() and self.parent.combobox_C2.current()==self.combo_C2_FLOCK.current() and self.parent.combobox_C3.current()==self.combo_C3_FLOCK.current()):
				self.combo_FLOCK_BWEF.current(0)
				if int(1.0*self.combo_R2_FLOCK.current()/self.parent.combobox_R2.current())==int(1.0*self.combo_R3_FLOCK.current()/self.parent.combobox_R3.current()):
					BWEF_VAL=int(1.0*self.combo_R2_FLOCK.current()/self.parent.combobox_R2.current())
					if (str(BWEF_VAL) in self.combo_FLOCK_BWEF.cget('values')):
						self.combo_FLOCK_BWEF.set(BWEF_VAL)
			else:
				self.combo_FLOCK_BWEF.current(0)
		
		

		# PLL_SDM_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_SDM_CFG_'+PLL_prof)
		self.DITHER_EN.set(reg['DITHER_EN_'+PLL_prof])
		self.SEL_SDMCLK.set(reg['SEL_SDMCLK_'+PLL_prof])
		self.REV_SDMCLK.set(reg['REV_SDMCLK_'+PLL_prof])
		


		# PLL_LODIST_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LODIST_CFG_'+PLL_prof)
		self.EN_D.set(reg['PLL_LODIST_EN_OUT_'+PLL_prof+'<3:0>']>>3)
		self.EN_C.set((reg['PLL_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&4)>>2)
		self.EN_B.set((reg['PLL_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&2)>>1)
		self.EN_A.set(reg['PLL_LODIST_EN_OUT_'+PLL_prof+'<3:0>']&1)
		
		#print reg['PLL_LODIST_FSP_OUT0_'+PLL_prof+'<2:0>']
		self.IQ_D.set(not (reg['PLL_LODIST_FSP_OUT3_'+PLL_prof+'<2:0>']>>2))
		self.IQ_C.set(not (reg['PLL_LODIST_FSP_OUT2_'+PLL_prof+'<2:0>']>>2))
		self.IQ_B.set(not (reg['PLL_LODIST_FSP_OUT1_'+PLL_prof+'<2:0>']>>2))
		self.IQ_A.set(not (reg['PLL_LODIST_FSP_OUT0_'+PLL_prof+'<2:0>']>>2))

		#self.on_IQ_A()
		#self.on_IQ_B()
		#self.on_IQ_C()
		#self.on_IQ_D()

		self.update_PH_A()
		self.update_PH_B()
		self.update_PH_C()
		self.update_PH_D()

		self.combo_PH_D.set((reg['PLL_LODIST_FSP_OUT3_'+PLL_prof+'<2:0>']&3)*90)
		self.combo_PH_C.set((reg['PLL_LODIST_FSP_OUT2_'+PLL_prof+'<2:0>']&3)*90)
		self.combo_PH_B.set((reg['PLL_LODIST_FSP_OUT1_'+PLL_prof+'<2:0>']&3)*90)
		self.combo_PH_A.set((reg['PLL_LODIST_FSP_OUT0_'+PLL_prof+'<2:0>']&3)*90)
		

		self.updateLOFreqs()		
		

	def on_PLL_Profile(self, e=None):
		PLL_prof=self.combo_PLL_Profile.current()
		if (PLL_prof not in self.configuredPLLProfs):
			self.Button_Write.configure(state='disabled')
		else:
			self.Button_Write.configure(state='active')
			# ovde je problem
			self.updateMainWindow()
		self.updatePLL()
		self.updateWindow()
		
		

	def updateConfig(self):
		if (not self.parent.pll_lock.get()):
			tkMessageBox.showinfo('Warning: PLL-Core Config', 'PLL-Core Configuration in Main-Window seems not valid as PLL_LOCK indicator is not HIGH. It is recommended to save PLL Profiles Settings with PLL_FLOCK=1. Please make changes in Main-Window and click on \'Update Config from Main Window\' - Button.')
		
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof not in self.configuredPLLProfs):
			self.configuredPLLProfs.append(active_prof)
			self.Button_Write.configure(state='active')

		# Update Widget Values
		self.update_VCO_AMP()
		self.update_VDD_VCOREG()
		self.update_FLOCK_N()
		self.update_PH_A()
		self.update_PH_B()
		self.update_PH_C()
		self.update_PH_D()
		self.updateLOFreqs()
		self.update_FLOCK_LPF()
		self.update_FLOCK_CP()

		# Update PLL Config from main window
		self.updatePLL()

		# Write to PLL Profile Registers
		self.update_PLL_Profile_Regs()
		
		
		

	def updateMainWindow(self):
		# Read from GUI which PLL profile user selected to configure
		PLL_prof=self.combo_PLL_Profile.get()

		# PLL_CP_CFG0_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_CP_CFG0_'+PLL_prof)
		self.parent.combobox_pfddel.current(reg['DEL_'+PLL_prof+'<1:0>'])
		self.parent.combobox_cp_pulse.current(reg['PULSE_'+PLL_prof+'<5:0>'])
		self.parent.combobox_cp_offset.current(reg['OFS_'+PLL_prof+'<5:0>'])

		# PLL_CP_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_CP_CFG1_'+PLL_prof)
		self.parent.combobox_cp_ict.current(reg['ICT_CP_'+PLL_prof+'<4:0>'])
		
		# PLL_LPF_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LPF_CFG1_'+PLL_prof)
		self.parent.combobox_R3.current(reg['R3_'+PLL_prof+'<3:0>'])
		self.parent.combobox_R2.current(reg['R2_'+PLL_prof+'<3:0>'])
		self.parent.combobox_C2.current(reg['C2_'+PLL_prof+'<3:0>'])
		self.parent.combobox_C1.current(reg['C1_'+PLL_prof+'<3:0>'])
		
		# PLL_LPF_CFG2_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LPF_CFG2_'+PLL_prof)
		self.parent.combobox_C3.current(reg['C3_'+PLL_prof+'<3:0>'])

		# PLL_VCO_FREQ_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_VCO_FREQ_'+PLL_prof)
		self.parent.combobox_vcofreq.current(reg['VCO_FREQ_'+PLL_prof+'<7:0>'])

		# PLL_VCO_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_VCO_CFG_'+PLL_prof)
		self.parent.combobox_vcosel.current(reg['VCO_SEL_'+PLL_prof+'<1:0>'])
		
		# PLL_FF_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FF_CFG_'+PLL_prof)
		self.parent.combobox_ffmod.current(reg['FF_MOD_'+PLL_prof+'<1:0>'])
		
		
		# PLL_SDM_CFG_n
		reg=self.lms8001_regs.getRegisterByName('PLL_SDM_CFG_'+PLL_prof)
		self.parent.INTMOD_EN.set(reg['INTMOD_EN_'+PLL_prof])
		self.parent.combobox_fbint.set(reg['INTMOD_'+PLL_prof+'<9:0>'])
		
		# PLL_FRACMODL_n register
		regL=self.lms8001_regs.getRegisterByName('PLL_FRACMODL_'+PLL_prof)
		

		# PLL_FRACMODH_n register
		regH=self.lms8001_regs.getRegisterByName('PLL_FRACMODH_'+PLL_prof)
		self.parent.combobox_fbfrac.set(regH['FRACMODH_'+PLL_prof+'<3:0>']*2**16+regL['FRACMODL_'+PLL_prof+'<15:0>'])

		# PLL_ENABLE_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_ENABLE_'+PLL_prof)
		self.parent.PDIV2_EN.set(reg['PLL_EN_FB_PDIV2_'+PLL_prof])
		
		
		self.parent.def_ALL()
		self.parent.update_FVCO_TARGET()
		self.parent.vco_CTUNE()
		#self.updatePLL()
		#return None
	
	


	def save_INI(self):
		self.updatePLL()

		predef_fname='LMS8001_PLL_%s%s%s_%sh%sm.ini' %(time.strftime("%y"), time.strftime("%m"), time.strftime("%d"), time.strftime("%H"), time.strftime("%M"))
		f_ini = tkFileDialog.asksaveasfile(mode='w', defaultextension=".ini", filetypes=[("Ini files", "*.ini")], initialfile=predef_fname)
		
		
		
		if (not f_ini):
			return None
		 	
		
		header="[file_info]\ntype=lms8001_minimal_config\nversion=1\n[lms8001_registers]\n"
		self.updateRegs()
		f_ini.write(header)
		
		reg_list=self.lms8001_regs.getRegistersByName(regList="ALL")
		for reg in reg_list:
			#print reg.getName()
			#print ''
			#print reg
			#print '%04x %04x' %(reg.getAddress, reg.getValue())
			f_ini.write('0x%04x=0x%04x\n' %(reg.getAddress(), reg.getValue()))
		
		
		f_ini.write('[reference_clock]\n')
		f_ini.write('ref_clk_mhz=%.2f\n' %(float(self.parent.entry_ref.get())))
		
		f_ini.write('[temp_sens_coeff]\n')
		f_ini.write('T0=-105.45\n')
		
		f_ini.close()
	
	def update_PLL_CFG_Reg(self, e=None):
		# PLL_VREG Register
		reg=self.lms8001_regs.getRegisterByName('PLL_VREG')
		reg['EN_VCOBIAS']=1
		reg['BYP_VCOREG']=int(self.BYP_VCOREG.get())
		reg['VDIV_VCOREG<7:0>']=int(self.combo_VDD_VCOREG.current())
		# PLL_CFG_XBUF Register
		reg=self.lms8001_regs.getRegisterByName('PLL_CFG_XBUF')
		reg['PLL_XBUF_SLFBEN']=int(self.XBUF_SLFBEN.get())
		reg['PLL_XBUF_BYPEN']=int(self.XBUF_BYPEN.get())
		reg['PLL_XBUF_EN']=1
		# PLL_CFG Register
		reg=self.lms8001_regs.getRegisterByName('PLL_CFG')
		# Activate PLL Core		
		reg['PLL_RSTN']=1

	def update_PLL_Profile_Regs(self, e=None):
		# Read from GUI which PLL profile user selected to configure
		PLL_prof=self.combo_PLL_Profile.get()
		if (int(PLL_prof) not in self.configuredPLLProfs):
			tkMessageBox.showinfo('Error: PLL Profile '+PLL_prof+' configuration', 'For configuring new PLL profile please load first PLL-Core configuration from main window by clicking on \'Update Config from Main Window\' - Button.')
			self.lift()
			
			return None
		# Define Registers in selected PLL Profile REGBANK
		# PLL_ENABLE_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_ENABLE_'+PLL_prof)
		reg['PLL_LODIST_EN_BIAS_'+PLL_prof]=1
		if (self.IQ_A.get() or self.IQ_B.get() or self.IQ_C.get() or self.IQ_D.get()):
			reg['PLL_LODIST_EN_DIV2IQ_'+PLL_prof]=1
		else:
			reg['PLL_LODIST_EN_DIV2IQ_'+PLL_prof]=0

		
				
		reg['PLL_EN_VTUNE_COMP_'+PLL_prof]=1
		reg['PLL_EN_LD_'+PLL_prof]=1
		reg['PLL_EN_PFD_'+PLL_prof]=1
		reg['PLL_EN_CP_'+PLL_prof]=1
		if (self.parent.combobox_cp_offset.current()>0):
			reg['PLL_EN_CPOFS_'+PLL_prof]=1
		else:
			reg['PLL_EN_CPOFS_'+PLL_prof]=0
		reg['PLL_EN_VCO_'+PLL_prof]=1
		reg['PLL_EN_FFDIV_'+PLL_prof]=1
		if (self.parent.PDIV2_EN.get()):
			reg['PLL_EN_FB_PDIV2_'+PLL_prof]=1
		else:
			reg['PLL_EN_FB_PDIV2_'+PLL_prof]=0
		
		if (self.parent.combobox_ffmod.current()>0):
			reg['PLL_EN_FFCORE_'+PLL_prof]=1
		else:
			reg['PLL_EN_FFCORE_'+PLL_prof]=0

		reg['PLL_EN_FBDIV_'+PLL_prof]=1
		reg['PLL_SDM_CLK_EN_'+PLL_prof]=int(not self.parent.INTMOD_EN.get())
		
		# PLL_LPF_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LPF_CFG1_'+PLL_prof)
		reg['R3_'+PLL_prof+'<3:0>']=self.parent.combobox_R3.current()
		reg['R2_'+PLL_prof+'<3:0>']=self.parent.combobox_R2.current()
		reg['C2_'+PLL_prof+'<3:0>']=self.parent.combobox_C2.current()
		reg['C1_'+PLL_prof+'<3:0>']=self.parent.combobox_C1.current()
		
		# PLL_LPF_CFG2_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LPF_CFG2_'+PLL_prof)
		reg['C3_'+PLL_prof+'<3:0>']=self.parent.combobox_C3.current()

		# PLL_CP_CFG0_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_CP_CFG0_'+PLL_prof)
		reg['DEL_'+PLL_prof+'<1:0>']=self.parent.combobox_pfddel.current()
		reg['PULSE_'+PLL_prof+'<5:0>']=self.parent.combobox_cp_pulse.current()
		reg['OFS_'+PLL_prof+'<5:0>']=self.parent.combobox_cp_offset.current()

		# PLL_CP_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_CP_CFG1_'+PLL_prof)
		reg['ICT_CP_'+PLL_prof+'<4:0>']=self.parent.combobox_cp_ict.current()
		if (self.parent.INTMOD_EN.get()):
			reg['LD_VCT_'+PLL_prof+'<1:0>']=2
		else:
			reg['LD_VCT_'+PLL_prof+'<1:0>']=0
		

		# PLL_VCO_FREQ_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_VCO_FREQ_'+PLL_prof)
		reg['VCO_FREQ_'+PLL_prof+'<7:0>']=self.parent.combobox_vcofreq.current()

		# PLL_VCO_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_VCO_CFG_'+PLL_prof)
		reg['VCO_AAC_EN_'+PLL_prof]=int(self.VCO_AAC_EN.get())
		if (self.parent.combobox_vcosel.current()):
			reg['VCO_SEL_'+PLL_prof+'<1:0>']=int(self.parent.combobox_vcosel.get())
		else:
			reg['VCO_SEL_'+PLL_prof+'<1:0>']=self.parent.combobox_vcosel.current()
		reg['VCO_AMP_'+PLL_prof+'<6:0>']=int(self.combo_VCO_AMP.get())
		reg['VDIV_SWVDD_'+PLL_prof+'<1:0>']=self.combo_VCO_SWVDD.current()
		
		# PLL_FF_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FF_CFG_'+PLL_prof)
		reg['FFDIV_SEL_'+PLL_prof]=int(self.parent.combobox_ffmod.current()>0)
		reg['FFCORE_MOD_'+PLL_prof+'<1:0>']=int(self.parent.combobox_ffmod.current())
		reg['FF_MOD_'+PLL_prof+'<1:0>']=int(self.parent.combobox_ffmod.current())
		
		# PLL_SDM_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_SDM_CFG_'+PLL_prof)
		reg['DITHER_EN_'+PLL_prof]=int(self.DITHER_EN.get())
		reg['SEL_SDMCLK_'+PLL_prof]=int(self.SEL_SDMCLK.get())
		reg['REV_SDMCLK_'+PLL_prof]=int(self.REV_SDMCLK.get())
		reg['INTMOD_EN_'+PLL_prof]=int(self.parent.INTMOD_EN.get())
		reg['INTMOD_'+PLL_prof+'<9:0>']=int(self.parent.combobox_fbint.get())
		
		# PLL_FRACMODL_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FRACMODL_'+PLL_prof)
		reg['FRACMODL_'+PLL_prof+'<15:0>']=int(self.parent.combobox_fbfrac.get())&int(2**16-1)

		# PLL_FRACMODH_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FRACMODH_'+PLL_prof)
		reg['FRACMODH_'+PLL_prof+'<3:0>']=int(int(self.parent.combobox_fbfrac.get())/(2**16))&int(2**4-1)

		# PLL_LODIST_CFG_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_LODIST_CFG_'+PLL_prof)
		reg['PLL_LODIST_EN_OUT_'+PLL_prof+'<3:0>']=8*int(self.EN_D.get())+4*int(self.EN_C.get())+2*int(self.EN_B.get())+1*int(self.EN_A.get())
		reg['PLL_LODIST_FSP_OUT3_'+PLL_prof+'<2:0>']=4*(1-int(self.IQ_D.get()))+int(float(self.combo_PH_D.get())/90.0)
		reg['PLL_LODIST_FSP_OUT2_'+PLL_prof+'<2:0>']=4*(1-int(self.IQ_C.get()))+int(float(self.combo_PH_C.get())/90.0)
		reg['PLL_LODIST_FSP_OUT1_'+PLL_prof+'<2:0>']=4*(1-int(self.IQ_B.get()))+int(float(self.combo_PH_B.get())/90.0)
		reg['PLL_LODIST_FSP_OUT0_'+PLL_prof+'<2:0>']=4*(1-int(self.IQ_A.get()))+int(float(self.combo_PH_A.get())/90.0)
		
		# Configuring Fast-Lock Mode Registers
		# PLL_FLOCK_CFG1_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG1_'+PLL_prof)
		reg['FLOCK_R3_'+PLL_prof+'<3:0>']=self.combo_R3_FLOCK.current()
		reg['FLOCK_R2_'+PLL_prof+'<3:0>']=self.combo_R2_FLOCK.current()
		reg['FLOCK_C2_'+PLL_prof+'<3:0>']=self.combo_C2_FLOCK.current()
		reg['FLOCK_C1_'+PLL_prof+'<3:0>']=self.combo_C1_FLOCK.current()

		# PLL_FLOCK_CFG2_n register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG2_'+PLL_prof)
		reg['FLOCK_C3_'+PLL_prof+'<3:0>']=self.combo_C3_FLOCK.current()
		reg['FLOCK_PULSE_'+PLL_prof+'<5:0>']=self.combo_PULSE_FLOCK.current()
		reg['FLOCK_OFS_'+PLL_prof+'<5:0>']=self.combo_OFS_FLOCK.current()
		

		# PLL_FLOCK_CFG3 register
		reg=self.lms8001_regs.getRegisterByName('PLL_FLOCK_CFG3_'+PLL_prof)
		reg['FLOCK_LODIST_EN_OUT_'+PLL_prof+'<3:0>']=8*int(self.FLOCK_EN_D.get())+4*int(self.FLOCK_EN_C.get())+2*int(self.FLOCK_EN_B.get())+1*int(self.FLOCK_EN_A.get())	
		reg['FLOCK_N_'+PLL_prof+'<9:0>']=self.combo_FLOCK_N.current()
		

	def updateRegs(self):
		#self.lms8001_regParser=regDescParser(LMS8001_REGDESC.split('\n'))
		#self.lms8001_regs=lms8001_regParser.getRegisterDefinition()	


		#try:
		#	f_ini=open(file_path_name, 'w')
		#except:
		#	print 'Error while creating the .ini file.'
		#	tkMessageBox.showinfo('Error', 'Error while creating the .ini file')
		 		
		
		#header="""
		#[file_info]
		#type=lms8001_minimal_config
		#version=1
		#[lms8001_registers]
		#"""
		
		self.update_PLL_CFG_Reg()
		self.update_PLL_Profile_Regs()
				
	def center_Window(self):
		sw = self.winfo_screenwidth()
		sh = self.winfo_screenheight()
		self.update()
		winW=self.winfo_width()
		winH=self.winfo_height()
		
		#x=int(round((sw-winW)/4.0))
		#y=int(round((sh-winH)/4.0))

		MainWin_Pos=self.parent.parent.geometry()
		#print MainWin_Pos
		#print MainWin_Pos.split('x')
		x=int(MainWin_Pos.split('x')[1].split('+')[1])
		y=int(MainWin_Pos.split('x')[1].split('+')[2])
		self.geometry('%dx%d+%d+%d' % (winW, winH, x+self.parent.winW+7, y))
		#print type(self.parent.parent.geometry())

	def on_IQ(self, IQ_val):
		self.updateLOFreqs()
		if (IQ_val):
			return [0, 90, 180, 270]
		else:
			return [0,180]
	
	def on_IQ_A(self):
		self.update_PH_A()
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()

	def update_PH_A(self):
		i=int(self.combo_PH_A.current())
		if (i>=0):
			ph_old=self.phases_A[i]
		else:
			ph_old=0
		phases=self.on_IQ(self.IQ_A.get())
		self.phases_A=phases
		self.combo_PH_A.config(values=phases)
		if (ph_old in phases):
			self.combo_PH_A.set(ph_old)
		elif (ph_old<180):
			self.combo_PH_A.set(0)
		else:
			self.combo_PH_A.set(180)
		#self.update_PLL_Profile_Regs()
	
	def on_IQ_B(self):
		self.update_PH_B()
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()

	def update_PH_B(self):
		i=int(self.combo_PH_B.current())
		if (i>=0):
			ph_old=self.phases_B[i]
		else:
			ph_old=0
		phases=self.on_IQ(self.IQ_B.get())
		self.phases_B=phases
		self.combo_PH_B.config(values=phases)
		if (ph_old in phases):
			self.combo_PH_B.set(ph_old)
		elif (ph_old<180):
			self.combo_PH_B.set(0)
		else:
			self.combo_PH_B.set(180)
		#self.update_PLL_Profile_Regs()
	
	def on_IQ_C(self):
		self.update_PH_C()
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()

	def update_PH_C(self):
		i=int(self.combo_PH_C.current())
		if (i>=0):
			ph_old=self.phases_C[i]
		else:
			ph_old=0
		phases=self.on_IQ(self.IQ_C.get())
		self.phases_C=phases
		self.combo_PH_C.config(values=phases)
		if (ph_old in phases):
			self.combo_PH_C.set(ph_old)
		elif (ph_old<180):
			self.combo_PH_C.set(0)
		else:
			self.combo_PH_C.set(180)
		#self.update_PLL_Profile_Regs()
	
	def on_IQ_D(self):
		self.update_PH_D()
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()
	
	def update_PH_D(self):
		i=int(self.combo_PH_D.current())
		if (i>=0):
			ph_old=self.phases_C[i]
		else:
			ph_old=0
		phases=self.on_IQ(self.IQ_D.get())
		self.phases_D=phases
		self.combo_PH_D.config(values=phases)
		if (ph_old in phases):
			self.combo_PH_D.set(ph_old)
		elif (ph_old<180):
			self.combo_PH_D.set(0)
		else:
			self.combo_PH_D.set(180)
		#self.update_PLL_Profile_Regs()

	def updatePLLFreqs(self):
		self.FVCO=self.parent.pll.vco.getF()
		self.FPLL=self.FVCO/float(self.parent.combobox_ffmod.get())
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof not in self.configuredPLLProfs):
			self.lbl_VCO_FREQ.config(text=('VCO Freq=X (Update)'))
			self.lbl_PLL_FREQ.config(text=('PLL Freq=X GHz (Update)'))
			return
		if (self.parent.combobox_vcosel.current()>0):
			self.lbl_VCO_FREQ.config(text=('VCO Freq=%.3f GHz' %(self.FVCO/1.0e9)))
			self.lbl_PLL_FREQ.config(text=('PLL Freq=%.3f GHz' %(self.FPLL/1.0e9)))
		else:
			self.lbl_VCO_FREQ.config(text=('VCO Freq=X (EXT-LO)'))
			self.lbl_PLL_FREQ.config(text=('PLL Freq=X (EXT-LO)'))

	def on_LO_EN(self):
		self.updateLOFreqs()
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()

	def on_combo_PH(self, e=None):
		if (self.combo_PLL_Profile.current() in self.configuredPLLProfs):
			self.update_PLL_Profile_Regs()

	def updateLOFreqs(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof not in self.configuredPLLProfs):
			self.Freq_A.config(text=('X (Update or FastSetup)'))
			self.Freq_B.config(text=('X (Update or FastSetup)'))
			self.Freq_C.config(text=('X (Update or FastSetup)'))
			self.Freq_D.config(text=('X (Update or FastSetup)'))
			self.button_PN_A.config(state='disabled')
			self.button_PN_B.config(state='disabled')
			self.button_PN_C.config(state='disabled')
			self.button_PN_D.config(state='disabled')
			return None
		if (self.parent.combobox_vcosel.current()>0):
			self.Freq_A.config(text=('%.3f GHz' %(self.FPLL*int(self.EN_A.get())/1.0e9/2.0**int(self.IQ_A.get()))))
			self.Freq_B.config(text=('%.3f GHz' %(self.FPLL*int(self.EN_B.get())/1.0e9/2.0**int(self.IQ_B.get()))))
			self.Freq_C.config(text=('%.3f GHz' %(self.FPLL*int(self.EN_C.get())/1.0e9/2.0**int(self.IQ_C.get()))))
			self.Freq_D.config(text=('%.3f GHz' %(self.FPLL*int(self.EN_D.get())/1.0e9/2.0**int(self.IQ_D.get()))))
			self.button_PN_A.config(state='active') if self.EN_A.get() else self.button_PN_A.config(state='disabled')
			self.button_PN_B.config(state='active') if self.EN_B.get() else self.button_PN_B.config(state='disabled')
			self.button_PN_C.config(state='active') if self.EN_C.get() else self.button_PN_C.config(state='disabled')
			self.button_PN_D.config(state='active') if self.EN_D.get() else self.button_PN_D.config(state='disabled')
		else:
			self.Freq_A.config(text=('X (EXT-LO)'))
			self.Freq_B.config(text=('X (EXT-LO)'))
			self.Freq_C.config(text=('X (EXT-LO)'))
			self.Freq_D.config(text=('X (EXT-LO)'))
			self.button_PN_A.config(state='disabled')
			self.button_PN_B.config(state='disabled')
			self.button_PN_C.config(state='disabled')
			self.button_PN_D.config(state='disabled')
		#self.update_PLL_Profile_Regs()

	def updatePLLDyn(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof not in self.configuredPLLProfs):
			self.lbl_PLL_DYN.config(text=('3dB BW=X, PM=X (Update)'))
			return None
		if (self.parent.combobox_vcosel.current()>0):
			stat, res_dict=self.parent.pll.dynamics_summary()
			self.PLL_F3dB=res_dict['F3dB']
			self.PLL_PM=res_dict['PM']
			self.lbl_PLL_DYN.config(text=('3dB BW=%.0f kHz, PM=%.1f deg' %(self.PLL_F3dB/1.0e3, self.PLL_PM)))
		else:
			self.lbl_PLL_DYN.config(text=('3dB BW=X, PM=X (EXT-LO)'))
	
		
	def updatePLLPN(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof not in self.configuredPLLProfs):
			self.lbl_IntPN.config(text=('Int_PN @ PLL_OUT= X (Update)'))
			return None
		if (self.parent.combobox_vcosel.current()>0):		
			if (self.parent.radio_pnoise.get()>1):
				pn_refonly=self.parent.ref.calc_pnoise(f=self.parent.flog)
				pn_xbuf=self.parent.xbuf.calc_pnoise(f=self.parent.flog)
				pn_ref=10.0*np.log10(np.power(10.0, pn_refonly/10.0)+np.power(10.0, pn_xbuf/10.0))
			else:
				pn_ref=self.parent.ref.calc_pnoise(f=self.parent.flog)
		
			(fpn, pn_PLL)=self.parent.pll.pnoise(pn_ref=pn_ref, SDM_NOISE=(not bool(self.parent.INTMOD_EN.get())))
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())
			pn_PLL_FREQ=np.array(pn_PLL['TOTAL'])+ffdiv_corr
			self.Int_PN=calc_PH_ERR_RMS(fpn, pn_PLL_FREQ, min(fpn), max(fpn))
			self.lbl_IntPN.config(text=('Int_PN @ PLL_OUT= %.2f deg' %(self.Int_PN)))
		else:
			self.lbl_IntPN.config(text=('Int_PN @ PLL_OUT= X (EXT-LO)'))
	
	def updatePLL(self):
		self.updatePLLFreqs()
		self.updateLOFreqs()
		self.updatePLLDyn()
		self.updatePLLPN()
		self.update_FLOCK_N()
	
	def on_VCO_AAC_EN(self):
		self.update_VCO_AMP()
		self.update_PLL_Profile_Regs()

	def update_VCO_AMP(self):
		ind=self.combo_VCO_AMP.current()
		if (ind<0):
			ind=3
		if (self.VCO_AAC_EN.get()):
			ind=ind&3
			self.combo_VCO_AMP.config(values=range(0,4))
		else:
			self.combo_VCO_AMP.config(values=range(0,128))
		self.combo_VCO_AMP.current(ind)
		#self.update_PLL_Profile_Regs()
		#self.update_PLL_CFG_Reg()

	def on_FLOCK_N(self, e=None):
		self.update_FLOCK_N()
		self.update_PLL_Profile_Regs()
	
	def update_FLOCK_N(self):
		ind=self.combo_FLOCK_N.current()
		if (ind<0):
			ind=400
		
		cycles=range(0,1024)
		flock_N_values=[]
		for c in cycles:
			flock_N_values.append(str('%.2f' %(c*1.0/self.parent.pll.Fref*1.0e6)))
		self.combo_FLOCK_N.config(values=flock_N_values)
		self.combo_FLOCK_N.current(ind)
		#self.update_PLL_Profile_Regs()
		
	def reset(self):
		self.initUI()
		# Update Config
		self.updateConfig()
		# Write Configuration to PLL Profile 0 REGBANK and PLL_CFG Register
		self.update_PLL_CFG_Reg()
		self.update_PLL_Profile_Regs()
		
		#self.center_Window()

	def on_BYP_VCOREG(self):
		self.update_VDD_VCOREG()
		self.update_PLL_CFG_Reg()

	def update_VDD_VCOREG(self):
		ind=self.combo_VDD_VCOREG.current()
		if (ind<0):
			ind=32
			vdd_vals=[]
			for i in range(0,256):
				vdd_vals.append(str('%.3f'%(1.80*(257.0-i)/(265-i))))
				self.combo_VDD_VCOREG.config(state='enabled', values=vdd_vals)
			self.combo_VDD_VCOREG.current(ind)
			self.combo_VDD_VCOREG.config(state='disabled')
		if (self.BYP_VCOREG.get()):
			self.combo_VDD_VCOREG.config(state='disabled')
		else:
			self.combo_VDD_VCOREG.config(state='enabled')
		#self.update_PLL_CFG_Reg()

	def update_FLOCK_LPF(self):
		ind_C1=self.combo_C1_FLOCK.current()
		ind_C2=self.combo_C2_FLOCK.current()
		ind_C3=self.combo_C3_FLOCK.current()
		ind_R2=self.combo_R2_FLOCK.current()
		ind_R3=self.combo_R3_FLOCK.current()
		self.combo_C1_FLOCK.config(values=self.parent.combobox_C1.cget('values'))
		self.combo_C2_FLOCK.config(values=self.parent.combobox_C2.cget('values'))
		self.combo_C3_FLOCK.config(values=self.parent.combobox_C3.cget('values'))
		self.combo_R2_FLOCK.config(values=self.parent.combobox_R2.cget('values'))
		self.combo_R3_FLOCK.config(values=self.parent.combobox_R3.cget('values'))
		if (ind_C1<0):
			ind_C1=8
		self.combo_C1_FLOCK.current(ind_C1)
		if (ind_C2<0):
			ind_C2=8
		self.combo_C2_FLOCK.current(ind_C2)
		if (ind_C3<0):
			ind_C3=8
		self.combo_C3_FLOCK.current(ind_C3)
		if (ind_R2<0):
			ind_R2=4
		self.combo_R2_FLOCK.current(ind_R2)
		if (ind_R3<0):
			ind_R3=4
		self.combo_R3_FLOCK.current(ind_R3)
		

	def update_FLOCK_CP(self):
		ind_PULSE=self.combo_PULSE_FLOCK.current()
		ind_OFS=self.combo_OFS_FLOCK.current()
		self.combo_PULSE_FLOCK.config(values=self.parent.combobox_cp_pulse.cget('values'))
		self.combo_OFS_FLOCK.config(values=self.parent.combobox_cp_offset.cget('values'))
		
		if (ind_PULSE<0):
			ind_PULSE=63
		self.combo_PULSE_FLOCK.current(ind_PULSE)

		if (ind_OFS<0):
			ind_OFS=0
		self.combo_OFS_FLOCK.current(ind_OFS)

	def on_FLOCK_BWEF(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof in self.configuredPLLProfs):
			# Calculate Loop-Filter Fast-Lock Configuration
			self.combo_C1_FLOCK.current(self.parent.combobox_C1.current())
			self.combo_C2_FLOCK.current(self.parent.combobox_C2.current())
			self.combo_C3_FLOCK.current(self.parent.combobox_C3.current())
			self.combo_R2_FLOCK.current(min(self.parent.combobox_R2.current()*int(self.combo_FLOCK_BWEF.get()), 15))
			self.combo_R3_FLOCK.current(min(self.parent.combobox_R3.current()*int(self.combo_FLOCK_BWEF.get()), 15))

			# Calculate CP Fast-Lock Configuration
			self.combo_PULSE_FLOCK.current(min(self.parent.combobox_cp_pulse.current()*int(self.combo_FLOCK_BWEF.get())**2, 63))
			self.combo_OFS_FLOCK.current(min(self.parent.combobox_cp_offset.current()*int(self.combo_FLOCK_BWEF.get())**2, 63))
		
			# Write to dedicated PLL Profile Registers
			self.update_PLL_Profile_Regs()
		

		else:
			tkMessageBox.showinfo('Error: Fast-Lock Config', 'PLL Profile '+str(active_prof) +' not configured yet. First, please update PLL-Core settings from Main Window by clicking on \'Update Config from Main Window\' - Button.')
	
	def on_FLOCK_Fc_PM(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof in self.configuredPLLProfs):
			try:
				fc_Hz=float(self.entry_FLOCK_Fc.get())*1.0e3
				PM_deg=float(self.entry_FLOCK_PM.get())
			except:
				tkMessageBox.showinfo('Error! Fast-Lock Loop Dynamics Definition', 'Loop Crossover frequency and phase margin should be POSITIVE REAL numbers')
				return None

			PULSE_NORM_MODE=self.parent.pll.cp.PULSE
			OFS_NORM_MODE=self.parent.pll.cp.OFS
			C1_CODE_NORM_MODE=self.parent.pll.lpf.C1_CTRL
			C2_CODE_NORM_MODE=self.parent.pll.lpf.C2_CTRL	
			C3_CODE_NORM_MODE=self.parent.pll.lpf.C3_CTRL
			R2_CODE_NORM_MODE=self.parent.pll.lpf.R2_CTRL
			R3_CODE_NORM_MODE=self.parent.pll.lpf.R3_CTRL
		

			status=self.parent.pll.optim_PLL_LoopBW(PM_deg=PM_deg, fc=fc_Hz)
	
			if (status):
				# If optimization passed successfuly
				# Read CP Pulse Current and LPF Comp. Values
	
				PULSE_FLOCK_MODE=self.parent.pll.cp.PULSE
				OFS_FLOCK_MODE=min(int((PULSE_FLOCK_MODE*1.0/PULSE_NORM_MODE)*OFS_NORM_MODE), 63)			

				C1_CODE_FLOCK_MODE=self.parent.pll.lpf.C1_CTRL
				C2_CODE_FLOCK_MODE=self.parent.pll.lpf.C2_CTRL	
				C3_CODE_FLOCK_MODE=self.parent.pll.lpf.C3_CTRL
				R2_CODE_FLOCK_MODE=self.parent.pll.lpf.R2_CTRL
				R3_CODE_FLOCK_MODE=self.parent.pll.lpf.R3_CTRL
			
				# Set corresponding comboboxes for FAST-LOCK Config.
				self.combo_PULSE_FLOCK.current(int(PULSE_FLOCK_MODE))
				self.combo_OFS_FLOCK.current(int(OFS_FLOCK_MODE))
				self.combo_C1_FLOCK.current(int(C1_CODE_FLOCK_MODE))
				self.combo_C2_FLOCK.current(int(C2_CODE_FLOCK_MODE))
				self.combo_C3_FLOCK.current(int(C3_CODE_FLOCK_MODE))
				self.combo_R2_FLOCK.current(int(R2_CODE_FLOCK_MODE))
				self.combo_R3_FLOCK.current(int(R3_CODE_FLOCK_MODE))
	
				# Set-Back corresponding comboboxes for NORMAL-LOCK MODE Config.
				self.parent.combobox_cp_pulse.current(int(PULSE_NORM_MODE))

				self.parent.combobox_C1.current(int(C1_CODE_NORM_MODE))
				self.parent.combobox_C2.current(int(C2_CODE_NORM_MODE))
				self.parent.combobox_C3.current(int(C3_CODE_NORM_MODE))
				self.parent.combobox_R2.current(int(R2_CODE_NORM_MODE))
				self.parent.combobox_R3.current(int(R3_CODE_NORM_MODE))			


				# Update ALL
				self.parent.def_ALL()
				# Write to dedicated PLL Profile Registers
				self.update_PLL_Profile_Regs()
			else:
				tkMessageBox.showinfo('Error: Fast-Lock Config', 'PLL Profile '+str(active_prof) +' Loop BW Optimization for Fast-Lock Mode Failed. Try some other values for Fc-PM input pair.')
		else:
			tkMessageBox.showinfo('Error: Fast-Lock Config', 'PLL Profile '+str(active_prof) +' not configured yet. First, please update PLL-Core settings from Main Window by clicking on \'Update Config from Main Window\' - Button.')	

	def on_CHECK_FLOCK(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof in self.configuredPLLProfs):
			plt_list=[]
			plt_vtune_list=[]
			legend_list=[]

			self.updateMainWindow()
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())

			try:
				FSTEP_MHz=float(self.parent.entry_fstep.get())
			except:
				tkMessageBox.showinfo('Error! Freq. Step at PLL Output Definition-Main Window', 'Frequency Step at PLL output for transient analysis should be POSITIVE REAL number.')
				return None
		
			PULSE_NORM_MODE=self.parent.combobox_cp_pulse.current()
			OFS_NORM_MODE=self.parent.combobox_cp_offset.current()
			C1_CODE_NORM_MODE=self.parent.combobox_C1.current()
			C2_CODE_NORM_MODE=self.parent.combobox_C2.current()	
			C3_CODE_NORM_MODE=self.parent.combobox_C3.current()
			R2_CODE_NORM_MODE=self.parent.combobox_R2.current()
			R3_CODE_NORM_MODE=self.parent.combobox_R3.current()

			PULSE_FLOCK_MODE=self.combo_PULSE_FLOCK.current()
			OFS_FLOCK_MODE=self.combo_OFS_FLOCK.current()			
			C1_CODE_FLOCK_MODE=self.combo_C1_FLOCK.current()
			C2_CODE_FLOCK_MODE=self.combo_C2_FLOCK.current()
			C3_CODE_FLOCK_MODE=self.combo_C3_FLOCK.current()
			R2_CODE_FLOCK_MODE=self.combo_R2_FLOCK.current()
			R3_CODE_FLOCK_MODE=self.combo_R3_FLOCK.current()
	
			(f, close_loop_tf_REF)=self.parent.pll.cl_loop_tfunc(block='REF')

			fstep_response=self.parent.pll.fstep_response(Ts=1/200.0e6, Tstop=50.0e-6, FSTEP_OUT=FSTEP_MHz*1.0e6)
			t=fstep_response['TIME']
		
			plt_cl_ref_NORM,=plotlogx(self.parent.flog, 20*np.log10(np.abs(close_loop_tf_REF))+ffdiv_corr, 20, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function, REFIN to PLLOUT - Mag. Response', font_name=self.parent.font_name)
			plt_list.append(plt_cl_ref_NORM)
			legend_list.append('STEADY-STATE MODE')

			vtune=fstep_response['VTUNE']
			plt_vtune_NORM,=plotsig(t/1.0e-6, vtune, 21, 'time [$\mu$s]', 'Voltage [V]', 'VCO Tuning Voltage vs. Time - PLL Frequency Step Response', font_name=self.parent.font_name)
			plt_vtune_list.append(plt_vtune_NORM)
		
			self.parent.combobox_cp_pulse.current(int(PULSE_FLOCK_MODE))
			self.parent.combobox_cp_offset.current(int(OFS_FLOCK_MODE))
			self.parent.combobox_C1.current(int(C1_CODE_FLOCK_MODE))
			self.parent.combobox_C2.current(int(C2_CODE_FLOCK_MODE))
			self.parent.combobox_C3.current(int(C3_CODE_FLOCK_MODE))
			self.parent.combobox_R2.current(int(R2_CODE_FLOCK_MODE))
			self.parent.combobox_R3.current(int(R3_CODE_FLOCK_MODE))	
			self.parent.def_ALL()

			(f, close_loop_tf_REF)=self.parent.pll.cl_loop_tfunc(block='REF')
			
			fstep_response=self.parent.pll.fstep_response(Ts=1/200.0e6, Tstop=50.0e-6, FSTEP_OUT=FSTEP_MHz*1.0e6)
			t=fstep_response['TIME']

			plt_cl_ref_FLOCK,=plotlogx(self.parent.flog, 20*np.log10(np.abs(close_loop_tf_REF))+ffdiv_corr, 20, 'Frequency [Hz]', 'Gain [dB]', 'PLL Close Loop Transfer Function, REFIN to PLLOUT - Mag. Response', font_name=self.parent.font_name, line_color='red')
			plt_list.append(plt_cl_ref_FLOCK)
			legend_list.append('FAST-LOCK MODE')

			vtune=fstep_response['VTUNE']
			plt_vtune_NORM,=plotsig(t/1.0e-6, vtune, 21, 'time [$\mu$s]', 'Voltage [V]', 'VCO Tuning Voltage vs. Time - PLL Frequency Step Response', line_color='red', font_name=self.parent.font_name)
			plt_vtune_list.append(plt_vtune_NORM)
	
			self.parent.combobox_cp_pulse.current(int(PULSE_NORM_MODE))
			self.parent.combobox_cp_offset.current(int(OFS_NORM_MODE))
			self.parent.combobox_C1.current(int(C1_CODE_NORM_MODE))
			self.parent.combobox_C2.current(int(C2_CODE_NORM_MODE))
			self.parent.combobox_C3.current(int(C3_CODE_NORM_MODE))
			self.parent.combobox_R2.current(int(R2_CODE_NORM_MODE))
			self.parent.combobox_R3.current(int(R3_CODE_NORM_MODE))	
			self.parent.def_ALL()

			setlegend(20, plt_list, legend_list, font_name=self.parent.font_name)
			setlegend(21, plt_vtune_list, legend_list, font_name=self.parent.font_name)
			show_plots()
		else:
			tkMessageBox.showinfo('Error: Checking Fast-Lock Config', 'PLL Profile '+str(active_prof) +' not configured yet. First, please update PLL-Core settings from Main Window by clicking on \'Update Config from Main Window\' - Button.')
			
	def on_copy_EN_FLOCK(self):
		active_prof=int(self.combo_PLL_Profile.current())
		if (active_prof in self.configuredPLLProfs):
			# Calculate Loop-Filter Fast-Lock Configuration
			self.FLOCK_EN_A.set(self.EN_A.get())
			self.FLOCK_EN_B.set(self.EN_B.get())
			self.FLOCK_EN_C.set(self.EN_C.get())
			self.FLOCK_EN_D.set(self.EN_D.get())
		
			# Write to dedicated PLL Profile Registers
			self.update_PLL_Profile_Regs()
		

		else:
			tkMessageBox.showinfo('Error: Fast-Lock Config', 'PLL Profile '+str(active_prof) +' not configured yet. First, please update PLL-Core settings from Main Window by clicking on \'Update Config from Main Window\' - Button.')

	def onQuit(self):
		self.parent.gen_INI_win=None
		self.destroy()

	def FastSetup(self):
		status_1stStep=self.config_PLL_Loop()
		if not status_1stStep:
			return None
		self.on_FLOCK_BWEF()
		self.updateRegs()
		self.updateConfig()

	def open_INI(self):
		self.lms8001_regParser=regDescParser(LMS8001_REGDESC.split('\n'))
		self.lms8001_regs=self.lms8001_regParser.getRegisterDefinition()

		ftypes = [('Ini files', '*.ini'), ('All files', '*')]
	

		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fname=dlg.show()

		try:
			f=open(fname, 'r')
		except:
			tkMessageBox.showinfo('Error: Open Ini File', 'Error while opening ini file')
			return None
		FREF_MHZ=self.parent.pll.Fref/1.0e6
		

		ini_lines=f.readlines()
		i=0
		# Find line with [lms8001_registers]
		while(i<len(ini_lines)):
			if (ini_lines[i].strip()=='[lms8001_registers]'):
				break
			i+=1
		if (i>=len(ini_lines)):
			tkMessageBox.showinfo('Error: Open Ini File', 'Not valid ini file or not supported format of ini file')
			return None
		i+=1
		while (i<len(ini_lines)):
			if (ini_lines[i].strip().startswith('[')):
				break
			line_elements=ini_lines[i].strip().split('=')
			addr=int(line_elements[0],0)
			val=int(line_elements[1],0)
			#print addr,'=',val
			reg=self.lms8001_regs.getRegisterByAddress(addr)
			reg.setValue(val)
			i+=1
		while (i<len(ini_lines)):
			if (ini_lines[i].strip()=='[reference_clock]'):
				FREF_MHZ=float(ini_lines[i+1].strip().split('=')[1])
			i+=1
		self.parent.entry_ref.delete(0, 'end')
		self.parent.entry_ref.insert('end', FREF_MHZ)
		self.configuredPLLProfs=range(0,8)
		self.combo_PLL_Profile.current(0)
		# Update Everything
		self.updateMainWindow()
		self.updateWindow()
		self.updateConfig()
		return None

	def config_PLL_Loop(self):
		try:
			FLO_FastSetup=float(self.entry_LOFreq_FastSetup.get())
		except:
			tkMessageBox.showinfo('Error: PLL Profile FastSetup', 'Desired LO Frequency should be positive real number.')
		if (FLO_FastSetup<0):
			tkMessageBox.showinfo('Error: PLL Profile FastSetup', 'Desired LO Frequency should be positive real number.')
		
		IQ_FastSetup=self.useIQ.get()
		IntN_FastSetup=self.INT_N.get()
		
		if (IQ_FastSetup):
			if not (self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9<=FLO_FastSetup<=self.parent.pll.vco.calcF(3,255,0.6)/2.0e9):
				tkMessageBox.showinfo("Error: PLL Profile FastSetup", "F_LO should be between %.2f MHz and %.2f GHz, when IQ=True. Failed to set LO Freq." %(self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9*1000, self.parent.pll.vco.calcF(3,255,0.6)/2.0e9))
				return False
		else:
			if not (self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9<=FLO_FastSetup<=self.parent.pll.vco.calcF(3,255,0.6)/1.0e9):
				tkMessageBox.showinfo("Error: PLL Profile FastSetup", ("F_LO should be between %.2f MHz and %.2f GHz, when IQ=True. Failed to set LO Freq." %(self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9*1000, self.parent.pll.vco.calcF(3,255,0.6)/1.0e9)))
				return False
			if (self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9<=FLO_FastSetup<=self.parent.pll.vco.calcF(3,255,0.6)/2.0/8.0e9):
				tkMessageBox.showinfo("Error: PLL Profile FastSetup", ("F_LO values between %.2f MHz and %.2f MHz can only be generated when using IQ DIV-BY-2 in LO-DIST. Setting use of IQ Phases." %(self.parent.pll.vco.calcF(1,0,0.6)/2.0/8.0e9*1000, self.parent.pll.vco.calcF(3,255,0.6)/2.0/8.0e9*1000)))
				self.useIQ.set(True)

		FFMOD=0
		F_VCO=(2.0**int(IQ_FastSetup))*(2.0**FFMOD)*FLO_FastSetup
		while not (self.parent.pll.vco.calcF(1,0,0.6)/1.0e9<=F_VCO<=self.parent.pll.vco.calcF(3,255,0.6)/1.0e9):
			FFMOD+=1
			F_VCO=(2.0**int(IQ_FastSetup))*(2.0**FFMOD)*FLO_FastSetup

		# Define Target FVCO in Main Window
		self.parent.entry_fvco.delete(0, 'end')
		self.parent.entry_fvco.insert('end', str(F_VCO))
		# Define Int-N Mode checkbox in Main Window
		self.parent.INTMOD_EN.set(IntN_FastSetup)
		# Define FF-MOD Combobox
		self.parent.combobox_ffmod.current(FFMOD)
		
		# Perform sequqence of calibration and optimization of PLL Loop Core
		self.parent.vco_CTUNE()
		self.parent.optim_CPLPF()
		self.parent.optimize_Iofs()

		# Determine the value of IQ checkboxes in LO-DIST Config frame 
		if not (self.EN_A.get() or self.EN_B.get() or self.EN_C.get() or self.EN_D.get()):
			self.IQ_A.set(IQ_FastSetup)
			self.IQ_B.set(IQ_FastSetup)
			self.IQ_C.set(IQ_FastSetup)
			self.IQ_D.set(IQ_FastSetup)
		else:
			if (self.EN_A.get()):
				self.IQ_A.set(IQ_FastSetup)
			if (self.EN_B.get()):
				self.IQ_B.set(IQ_FastSetup)
			if (self.EN_C.get()):
				self.IQ_C.set(IQ_FastSetup)
			if (self.EN_D.get()):
				self.IQ_D.set(IQ_FastSetup)

		
		# If everything is OK, update Config, write to registers and return True		
		self.updateConfig()
		return True

	def plot_PN(self, channel):
		active_prof=int(self.combo_PLL_Profile.current())
		#if (active_prof not in self.configuredPLLProfs):
		#	self.lbl_IntPN.config(text=('Int_PN @ PLL_OUT= X (Update)'))
		#	return None
		if (self.parent.combobox_vcosel.current()>0):		
			if (self.parent.radio_pnoise.get()>1):
				pn_refonly=self.parent.ref.calc_pnoise(f=self.parent.flog)
				pn_xbuf=self.parent.xbuf.calc_pnoise(f=self.parent.flog)
				pn_ref=10.0*np.log10(np.power(10.0, pn_refonly/10.0)+np.power(10.0, pn_xbuf/10.0))
			else:
				pn_ref=self.parent.ref.calc_pnoise(f=self.parent.flog)
		(fpn, pn_PLL)=self.parent.pll.pnoise(pn_ref=pn_ref, SDM_NOISE=(not bool(self.parent.INTMOD_EN.get())))
		if (channel=='A'):
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())-6.0*int(self.IQ_A.get())
			IQ_val=int(self.IQ_A.get())
		elif (channel=='B'):
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())-6.0*int(self.IQ_B.get())
			IQ_val=int(self.IQ_B.get())
		elif (channel=='C'):
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())-6.0*int(self.IQ_C.get())
			IQ_val=int(self.IQ_C.get())
			
		else:
			ffdiv_corr=-6.0*float(self.parent.combobox_ffmod.current())-6.0*int(self.IQ_D.get())
			IQ_val=int(self.IQ_D.get())
		pn_LO=np.array(pn_PLL['TOTAL'])+ffdiv_corr
		PH_ERR_RMS=calc_PH_ERR_RMS(fpn, pn_LO, min(fpn), max(fpn))
		plotpnoise(fpn, pn_LO, 22+ord(channel)-ord('A'), title=('LO Ch. '+channel+' Phase Noise @ %.3f GHz carrier, Int Ph.Err(rms)=%.3f deg' %(self.FPLL/1.0e9/2.0**(IQ_val), PH_ERR_RMS) ))
		show_plots()

	def plot_PN_A(self):
		self.plot_PN('A')
		
	def plot_PN_B(self):
		self.plot_PN('B')

	def plot_PN_C(self):
		self.plot_PN('C')

	def plot_PN_D(self):
		self.plot_PN('D')

	def initUI(self):
		self.title('Generate INI File')
		
		self.lms8001_regParser=regDescParser(LMS8001_REGDESC.split('\n'))
		self.lms8001_regs=self.lms8001_regParser.getRegisterDefinition()

		self.configuredPLLProfs=[0]

		self.FVCO=0
		self.FPLL=0
	
		self.PLL_F3dB=0
		self.PLL_PM=0

		self.Int_PN=0

		self.rowconfigure(0, pad=1)
		self.rowconfigure(1, pad=10)
		self.rowconfigure(2, pad=1)
		self.rowconfigure(3, pad=1)
		self.rowconfigure(4, pad=1)
		#self.rowconfigure(5, pad=40)
		#self.rowconfigure(6, pad=1)
		self.columnconfigure(0, pad=10)
		self.columnconfigure(1, pad=10)
		self.columnconfigure(2, pad=15)
		#self.columnconfigure(3, pad=1)
		#self.columnconfigure(4, pad=1)
		#self.columnconfigure(5, pad=1)
		#self.columnconfigure(6, pad=1)
		#self.columnconfigure(7, pad=1)


		# XBUF Settings
		#self=Frame(self, borderwidth=0, relief=RAISED)
		#self.columnconfigure(0, pad=95)
		#self.columnconfigure(1, pad=42)
		#self.columnconfigure(2, pad=20)
		frame_XBUF=Frame(self, borderwidth=0, relief=RAISED)
		lbl_XBUF_TITLE=Label(frame_XBUF, text='REFCLK BUFFER', width=15, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_XBUF_TITLE.grid(row=0, column=0, sticky=W)
		self.XBUF_SLFBEN=BooleanVar()
		cbox_XBUF_SLFBEN=Checkbutton(frame_XBUF, text='Self-Bias Mode', onvalue=1, offvalue=0, variable=self.XBUF_SLFBEN, command=self.update_PLL_CFG_Reg)
		cbox_XBUF_SLFBEN.grid(row=1, column=0, sticky=W)
		self.XBUF_BYPEN=BooleanVar()
		cbox_XBUF_BYPEN=Checkbutton(frame_XBUF, text='Bypass 1st Stage', onvalue=1, offvalue=0, variable=self.XBUF_BYPEN, command=self.update_PLL_CFG_Reg)
		cbox_XBUF_BYPEN.grid(row=2, column=0, sticky=W)
		#Label(frame_XBUF).grid(row=3, column=0, sticky=W)
		#Label(frame_XBUF).grid(row=4, column=0, sticky=W)
		frame_XBUF.grid(row=0, column=1, sticky=W+N)
		
		# VCO-BIAS Settings
		frame_VCO_BIAS=Frame(self, borderwidth=0, relief=RAISED)
		lbl_VCO_TITLE=Label(frame_VCO_BIAS, text='VCO-BIAS', width=16, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_VCO_TITLE.grid(row=0, column=0, sticky=W)
		self.BYP_VCOREG=BooleanVar()
		self.BYP_VCOREG.set(1)
		cbox_BYP_VCOREG=Checkbutton(frame_VCO_BIAS, text='Bypass VCO Reg.', onvalue=1, offvalue=0, variable=self.BYP_VCOREG, command=self.on_BYP_VCOREG)
		cbox_BYP_VCOREG.grid(row=1, column=0, sticky=W)
		frame_VCO_REG=Frame(frame_VCO_BIAS, borderwidth=0, relief=RAISED)
		frame_VCO_REG.columnconfigure(0, pad=0)
		lbl_VDD_VCOREG=Label(frame_VCO_REG, text='VDD_VCOREG [V]')
		lbl_VDD_VCOREG.grid(row=0, column=0, sticky=W)
		self.combo_VDD_VCOREG=Combobox(frame_VCO_REG, values=[], width=5)
		self.combo_VDD_VCOREG.grid(row=0, column=1, sticky=W)	
		frame_VCO_REG.grid(row=2, column=0, sticky=W+E)
		#Label(frame_VCO_REG).grid(row=3, column=0, sticky=W)
		#Label(frame_VCO_REG).grid(row=4, column=0, sticky=W)
		frame_VCO_BIAS.grid(row=0, column=2, sticky=W+N)
		
		# Fast Setup Button 
		frame_FastSetup=Frame(self, borderwidth=0, relief=RAISED)
		lbl_frame_FastSetup_TITLE=Label(frame_FastSetup, text='FAST SETUP', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_frame_FastSetup_TITLE.grid(row=0, column=0, sticky=W)
		Label(frame_FastSetup, text='Things to do before FastSetup:', anchor=W).grid(row=1, column=0, sticky=W)
		#Label(frame_FastSetup, text='1. Define PLL-Core In Main Window', anchor=W).grid(row=2, column=0, sticky=W)
		
		Label(frame_FastSetup, text='1. Choose PLL Profile to Configure', anchor=W).grid(row=2, column=0, sticky=W)
		frame_LOFreq_FastSetup=Frame(frame_FastSetup, borderwidth=0, relief=RAISED)
		Label(frame_LOFreq_FastSetup, text='2. LO Freq [GHz]', anchor=W).grid(row=0, column=0, sticky=W)
		self.entry_LOFreq_FastSetup=Entry(frame_LOFreq_FastSetup, width=5)
		self.entry_LOFreq_FastSetup.insert('end', '4.15')
		self.entry_LOFreq_FastSetup.grid(row=0, column=1, padx=1, sticky=W)
		self.INT_N=BooleanVar()
		cbox_INT_N=Checkbutton(frame_LOFreq_FastSetup, text='INT-N', onvalue=1, offvalue=0, variable=self.INT_N)
		cbox_INT_N.grid(row=0, column=2, padx=3, sticky=W)
		self.useIQ=BooleanVar()
		self.useIQ.set(1)
		cbox_useIQ=Checkbutton(frame_LOFreq_FastSetup, text='IQ-GEN', onvalue=1, offvalue=0, variable=self.useIQ)
		cbox_useIQ.grid(row=1, column=2, padx=3, sticky=W)
		Button(frame_LOFreq_FastSetup, text='Configure PLL Loop', command=self.config_PLL_Loop).grid(row=1, column=0, columnspan=2)
		frame_LOFreq_FastSetup.grid(row=3, column=0, sticky=W)
		
		Label(frame_FastSetup, text='3. Configure LO-DIST Network', anchor=W).grid(row=4, column=0, sticky=W)
		Button_FastSetupProfile=Button(frame_FastSetup, text='FastSetup of PLL Profile', command=self.FastSetup, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		Button_FastSetupProfile.grid(row=5, column=0, sticky=W+N+E)
		frame_FastSetup.grid(row=1, column=0, sticky=W+N)
		#self.grid(row=0, column=0, columnspan=1, sticky=W+E)
		
		

		# PLL Profile Index Frame
		#self=Frame(self, borderwidth=0, relief=RAISED)
		#self.columnconfigure(0, pad=42)
		#self.columnconfigure(1, pad=20)
		#self.columnconfigure(2, pad=1)
		frame_PLL_Profile=Frame(self,  borderwidth=0, relief=RAISED)
		frame_PLL_Profile.columnconfigure(0, pad=1)
		frame_PLL_Profile.columnconfigure(1, pad=1)
		lbl_PLL_Profile=Label(frame_PLL_Profile, text='PLL PROFILE CONFIG', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold') )
		lbl_PLL_Profile.grid(row=0, column=0, columnspan=2, sticky=W)
		lbl_PLL_Prof_Num=Label(frame_PLL_Profile, text='Configure PLL Profile', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))) )
		lbl_PLL_Prof_Num.grid(row=1, column=0, sticky=W)
		self.combo_PLL_Profile=Combobox(frame_PLL_Profile, values=range(0,8), width=3)
		self.combo_PLL_Profile.current(0)
		self.combo_PLL_Profile.grid(row=1, column=1, sticky=W+N)
		# Bindings
		self.combo_PLL_Profile.bind("<<ComboboxSelected>>", self.on_PLL_Profile)
		#self.combo_PLL_Profile.bind("<Return>", self.on_PLL_Profile)
		#self.combo_PLL_Profile.bind("<FocusOut>", self.on_PLL_Profile)
		Button_Update=Button(frame_PLL_Profile, text='Update Config from\nMain Window', fg='dark blue', command=self.updateConfig)		
		Button_Update.grid(row=3, column=0, columnspan=2, sticky=W+E)
		self.Button_Write=Button(frame_PLL_Profile, text='Load Config to\nMain Window', fg='dark blue', command=self.updateMainWindow)
		self.Button_Write.grid(row=4, column=0, columnspan=2, sticky=W+E)
		#Label(frame_PLL_Profile).grid(row=3, column=0, columnspan=2, sticky=W)
		#Label(frame_PLL_Profile).grid(row=4, column=0, columnspan=2, sticky=W)
		Label(frame_PLL_Profile).grid(row=5, column=0, columnspan=2, sticky=W)
		#Label(frame_PLL_Profile).grid(row=6, column=0, columnspan=2, sticky=W)
		frame_PLL_Profile.grid(row=0, column=0, sticky=W+N)

		

		frame_PLL_Core=Frame(self, borderwidth=0, relief=RAISED)
		lbl_PLL_TITLE=Label(frame_PLL_Core, text='PLL-CORE SUMMARY', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'), fg='dark blue')
		lbl_PLL_TITLE.grid(row=0, column=0, sticky=W)
		self.VCO_AAC_EN=BooleanVar()
		self.VCO_AAC_EN.set(True)
		cbox_VCO_AAC_EN=Checkbutton(frame_PLL_Core, text='VCO_AAC_EN', onvalue=1, offvalue=0, variable=self.VCO_AAC_EN, command=self.on_VCO_AAC_EN)
		cbox_VCO_AAC_EN.grid(row=1, column=0, sticky=W)
		frame_VCO_AMP=Frame(frame_PLL_Core, borderwidth=0, relief=RAISED)
		lbl_VCO_AMP=Label(frame_VCO_AMP, text='VCO_AMP', width=9, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_VCO_AMP.grid(row=0, column=0, sticky=W)
		self.combo_VCO_AMP=Combobox(frame_VCO_AMP, values=[], width=5)
		self.combo_VCO_AMP.grid(row=0, column=1, sticky=W)
		lbl_VCO_SWVDD=Label(frame_VCO_AMP, text='SWVDD [mV]', width=11, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_VCO_SWVDD.grid(row=1, column=0, sticky=W)
		self.combo_VCO_SWVDD=Combobox(frame_VCO_AMP, values=[600, 800, 1000, 1200], width=5)
		self.combo_VCO_SWVDD.grid(row=1, column=1, sticky=W)
		self.combo_VCO_SWVDD.current(2)
		frame_VCO_AMP.grid(row=2, column=0, sticky=W)
		
		self.lbl_VCO_FREQ=Label(frame_PLL_Core, text=('VCO Freq=%.3f GHz' %(self.FVCO/1.0e9)), width=20, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))), fg='dark blue')
		self.lbl_VCO_FREQ.grid(row=3, column=0, sticky=W)
		self.lbl_PLL_FREQ=Label(frame_PLL_Core, text=('PLL Freq=%.3f GHz' %(self.FPLL/1.0e9)), width=20, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))), fg='dark blue')
		self.lbl_PLL_FREQ.grid(row=4, column=0, sticky=W)
		self.lbl_PLL_DYN=Label(frame_PLL_Core, text=('3dB BW=%.1f kHz, PM=%.1f deg' %(self.PLL_F3dB/1.0e3, self.PLL_PM)), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))), fg='dark blue')
		self.lbl_PLL_DYN.grid(row=5, column=0, sticky=W)
		#Label(frame_PLL_Core).grid(row=6, column=0, sticky=W)
		self.lbl_IntPN=Label(frame_PLL_Core, text=('Int_PN @ PLL_OUT= %.2f deg' %(self.Int_PN)), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))), fg='dark blue')
		self.lbl_IntPN.grid(row=7, column=0, sticky=W)
		frame_PLL_Core.grid(row=1, column=1, sticky=W+N)
		
		# Bindings
		#cbox_BYP_VCOREG.config(command=self.config_VDD_VCOREG)
		#cbox_VCO_AAC_EN.config(command=self.on_VCO_AAC_EN)
		self.combo_VCO_AMP.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_VCO_AMP.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_VCO_AMP.bind("<FocusOut>", self.update_PLL_Profile_Regs)
		self.combo_VCO_SWVDD.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_VCO_SWVDD.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_VCO_SWVDD.bind("<FocusOut>", self.update_PLL_Profile_Regs)	
		self.combo_VDD_VCOREG.bind("<<ComboboxSelected>>", self.update_PLL_CFG_Reg)
		self.combo_VDD_VCOREG.bind("<Return>", self.update_PLL_CFG_Reg)
		self.combo_VDD_VCOREG.bind("<FocusOut>", self.update_PLL_CFG_Reg)

		# SDM-Settings Frame
		frame_SDM=Frame(self, borderwidth=0, relief=RAISED)
		lbl_frame_SDM_TITLE=Label(frame_SDM, text='SDM CONFIG', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_frame_SDM_TITLE.grid(row=0, column=0, sticky=W)
		self.DITHER_EN=BooleanVar()
		self.cbox_DITHER_EN=Checkbutton(frame_SDM, text='Enable SDM Dithering', variable=self.DITHER_EN, onvalue=1, offvalue=0, command=self.update_PLL_Profile_Regs)
		self.cbox_DITHER_EN.grid(row=1, column=0, sticky=W)
		self.SEL_SDMCLK=BooleanVar()
		self.cbox_SEL_SDMCLK=Checkbutton(frame_SDM, text='SDM Clock: 0(FB-DIV) or 1(REFCLK)', variable=self.SEL_SDMCLK, onvalue=1, offvalue=0, command=self.update_PLL_Profile_Regs)
		self.cbox_SEL_SDMCLK.grid(row=2, column=0, sticky=W)
		self.REV_SDMCLK=BooleanVar()
		self.cbox_REV_SDMCLK=Checkbutton(frame_SDM, text='Reverse SDM Clock', variable=self.REV_SDMCLK, onvalue=1, offvalue=0, command=self.update_PLL_Profile_Regs)
		self.cbox_REV_SDMCLK.grid(row=3, column=0, sticky=W)
		frame_SDM.grid(row=1, column=2, sticky=W+N)
		#self.grid(row=1, column=0, columnspan=3, sticky=W+E)
		
		# Fast-Lock Mode Frame
		#frame_FLOCK=Frame(self, borderwidth=0, relief=RAISED)
		#frame_FLOCK.columnconfigure(0, pad=25)
		#frame_FLOCK.columnconfigure(1, pad=35)
		#frame_FLOCK.columnconfigure(2, pad=1)
		frame_Fast_Lock=Frame(self, borderwidth=0, relief=RAISED)
		frame_Fast_Lock.columnconfigure(0, pad=1)
		frame_Fast_Lock.columnconfigure(1, pad=1)
		lbl_Fast_Lock_TITLE=Label(frame_Fast_Lock, text='FAST-LOCK MODE', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_Fast_Lock_TITLE.grid(row=0, column=0, columnspan=2, sticky=W)
		lbl_FLOCK_N=Label(frame_Fast_Lock, text='Duration [us]', anchor=W)
		lbl_FLOCK_N.grid(row=1, column=0, sticky=W)
		self.combo_FLOCK_N=Combobox(frame_Fast_Lock, values=[], width=5)
		self.combo_FLOCK_N.grid(row=1, column=1, sticky=W)
		
		Label(frame_Fast_Lock, text='Enable LO Channels', anchor=W).grid(row=2, column=0, columnspan=2, sticky=W)
		Label(frame_Fast_Lock, text='during Fast-Lock Mode', anchor=W).grid(row=3, column=0, columnspan=2, sticky=W)
		self.FLOCK_EN_A=BooleanVar()
		self.cbox_FLOCK_EN_A=Checkbutton(frame_Fast_Lock, text='EN_ChA', onvalue=1, offvalue=0, variable=self.FLOCK_EN_A, command=self.update_PLL_Profile_Regs)
		self.cbox_FLOCK_EN_A.grid(row=4, column=0, padx=10, sticky=W)
		self.FLOCK_EN_B=BooleanVar()
		self.cbox_FLOCK_EN_B=Checkbutton(frame_Fast_Lock, text='EN_ChB', onvalue=1, offvalue=0, variable=self.FLOCK_EN_B, command=self.update_PLL_Profile_Regs)
		self.cbox_FLOCK_EN_B.grid(row=5, column=0, padx=10, sticky=W)
		self.FLOCK_EN_C=BooleanVar()
		self.cbox_FLOCK_EN_C=Checkbutton(frame_Fast_Lock, text='EN_ChC', onvalue=1, offvalue=0, variable=self.FLOCK_EN_C, command=self.update_PLL_Profile_Regs)
		self.cbox_FLOCK_EN_C.grid(row=6, column=0, padx=10, sticky=W)
		self.FLOCK_EN_D=BooleanVar()
		self.cbox_FLOCK_EN_D=Checkbutton(frame_Fast_Lock, text='EN_ChD', onvalue=1, offvalue=0, variable=self.FLOCK_EN_D, command=self.update_PLL_Profile_Regs)
		self.cbox_FLOCK_EN_D.grid(row=7, column=0, padx=10, sticky=W)
		Button_Copy_EN_FLOCK=Button(frame_Fast_Lock, text='Same ENs as in LO-DIST Cfg', command=self.on_copy_EN_FLOCK)
		Button_Copy_EN_FLOCK.grid(row=8, column=0, columnspan=2, sticky=W)
		#self.FLOCK_EN=BooleanVar()
		#cbox_FLOCK_EN=Checkbutton(frame_Fast_Lock, text='Enable Used LO Channels', onvalue=1, offvalue=0, variable=self.FLOCK_EN, command=self.update_PLL_Profile_Regs)
		#cbox_FLOCK_EN.grid(row=3, column=0, columnspan=2, sticky=W)
		

		# Bindings
		self.combo_FLOCK_N.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_FLOCK_N.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_FLOCK_N.bind("<FocusOut>", self.update_PLL_Profile_Regs)	
				

		Label(frame_Fast_Lock).grid(row=4, column=0, columnspan=2, sticky=W)
		Label(frame_Fast_Lock).grid(row=5, column=0, columnspan=2, sticky=W)
		frame_Fast_Lock.grid(row=2, column=0, sticky=W+N)

		# FLOCK Loop-Filter Config
		frame_FLOCK_LPF_CP=Frame(self, relief=RAISED, borderwidth=0)
		lbl_frame_FLOCK_LPF_CP_TITLE=Label(frame_FLOCK_LPF_CP, text='FAST-LOCK LPF CONFIG', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_frame_FLOCK_LPF_CP_TITLE.grid(row=0, column=0, columnspan=2, sticky=W)
		lbl_C1_FLOCK=Label(frame_FLOCK_LPF_CP, text='C1 [pF]', anchor=W)
		lbl_C1_FLOCK.grid(row=1, column=0, sticky=W)
		self.combo_C1_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_C1_FLOCK.grid(row=1, column=1, sticky=W)
		lbl_C2_FLOCK=Label(frame_FLOCK_LPF_CP, text='C2 [pF]', anchor=W)
		lbl_C2_FLOCK.grid(row=2, column=0, sticky=W)
		self.combo_C2_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_C2_FLOCK.grid(row=2, column=1, sticky=W)
		lbl_C3_FLOCK=Label(frame_FLOCK_LPF_CP, text='C3 [pF]', anchor=W)
		lbl_C3_FLOCK.grid(row=3, column=0, sticky=W)
		self.combo_C3_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_C3_FLOCK.grid(row=3, column=1, sticky=W)
		lbl_R2_FLOCK=Label(frame_FLOCK_LPF_CP, text='R2 [kOhm]', anchor=W)
		lbl_R2_FLOCK.grid(row=4, column=0, sticky=W)
		self.combo_R2_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_R2_FLOCK.grid(row=4, column=1, sticky=W)
		lbl_R3_FLOCK=Label(frame_FLOCK_LPF_CP, text='R3 [kOhm]', anchor=W)
		lbl_R3_FLOCK.grid(row=5, column=0, sticky=W)
		self.combo_R3_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_R3_FLOCK.grid(row=5, column=1, sticky=W)

		# Bindings
		self.combo_C1_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_C1_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_C1_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)
		self.combo_C2_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_C2_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_C2_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)
		self.combo_C3_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_C3_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_C3_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)			
		self.combo_R2_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_R2_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_R2_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)	
		self.combo_R3_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_R3_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_R3_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)

		# FLOCK CP Config
		Label(frame_FLOCK_LPF_CP).grid(row=6, column=0, columnspan=2, sticky=W)
		lbl_frame_FLOCK_LPF_CP_TITLE=Label(frame_FLOCK_LPF_CP, text='FAST-LOCK CP CONFIG', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_frame_FLOCK_LPF_CP_TITLE.grid(row=7, column=0, columnspan=2, sticky=W)
		lbl_PULSE_FLOCK=Label(frame_FLOCK_LPF_CP, text='ICP_PULSE [uA]', anchor=W)
		lbl_PULSE_FLOCK.grid(row=8, column=0, sticky=W)
		self.combo_PULSE_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_PULSE_FLOCK.grid(row=8, column=1, sticky=W)
		lbl_OFS_FLOCK=Label(frame_FLOCK_LPF_CP, text='ICP_OFS [uA]', anchor=W)
		lbl_OFS_FLOCK.grid(row=9, column=0, sticky=W)
		self.combo_OFS_FLOCK=Combobox(frame_FLOCK_LPF_CP, values=[], width=6)
		self.combo_OFS_FLOCK.grid(row=9, column=1, sticky=W)
		Button_FLOCK=Button(frame_FLOCK_LPF_CP, text='Check FAST-LOCK Config', command=self.on_CHECK_FLOCK)
		Button_FLOCK.grid(row=10, column=0, columnspan=2, sticky=W)
		frame_FLOCK_LPF_CP.grid(row=2, column=1, sticky=W+N)
	
		# Bindings
		self.combo_PULSE_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_PULSE_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_PULSE_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)	
		self.combo_OFS_FLOCK.bind("<<ComboboxSelected>>", self.update_PLL_Profile_Regs)
		self.combo_OFS_FLOCK.bind("<Return>", self.update_PLL_Profile_Regs)
		self.combo_OFS_FLOCK.bind("<FocusOut>", self.update_PLL_Profile_Regs)
		
		# FLOCK DEFINITION
		frame_FLOCK_DEF=Frame(self, relief=RAISED, borderwidth=0)
		lbl_FLOCK_DEF_TITLE=Label(frame_FLOCK_DEF, text='FAST-LOCK MODE OPTIMIZATION', anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_FLOCK_DEF_TITLE.grid(row=0, column=0, columnspan=2, sticky=W)
		lbl_FLOCK_OPTIM1=Label(frame_FLOCK_DEF, text='Opt. Method 1\nBWEF-Bandwidth Extension Factor', anchor=W)
		lbl_FLOCK_OPTIM1.grid(row=1, column=0, columnspan=2, sticky=W)		
		lbl_FLOCK_BWEF=Label(frame_FLOCK_DEF, text='BWEF in Fast-Lock', anchor=W)
		lbl_FLOCK_BWEF.grid(row=2, column=0, sticky=W)
		self.combo_FLOCK_BWEF=Combobox(frame_FLOCK_DEF, values=range(1,5), width=3)
		self.combo_FLOCK_BWEF.current(0)
		self.combo_FLOCK_BWEF.grid(row=2, column=1, sticky=W)
		button_FLOCK_BWEF=Button(frame_FLOCK_DEF, text='Set Fast-Lock Config with BWEF', command=self.on_FLOCK_BWEF)
		button_FLOCK_BWEF.grid(row=3, column=0, columnspan=2, sticky=W+E)

		Label(frame_FLOCK_DEF).grid(row=4, column=0, columnspan=2, sticky=W)
		lbl_FLOCK_OPTIM2=Label(frame_FLOCK_DEF, text='Opt. Method 2\nPLL Loop Dynamics in Fast-Lock Mode', anchor=W)
		lbl_FLOCK_OPTIM2.grid(row=5, column=0, columnspan=2, sticky=W)
		lbl_FLOCK_Fc=Label(frame_FLOCK_DEF, text='Fast-Lock Fc [kHz]', anchor=W)
		lbl_FLOCK_Fc.grid(row=6, column=0, sticky=W)
		
		self.entry_FLOCK_Fc=Entry(frame_FLOCK_DEF, width=5)
		self.entry_FLOCK_Fc.insert('end', 360)
		self.entry_FLOCK_Fc.grid(row=6, column=1, sticky=W)
		 

		lbl_FLOCK_PM=Label(frame_FLOCK_DEF, text='Fast-Lock Ph.Margin [deg]', anchor=W)
		lbl_FLOCK_PM.grid(row=7, column=0, sticky=W)
		
		self.entry_FLOCK_PM=Entry(frame_FLOCK_DEF, width=5)
		self.entry_FLOCK_PM.insert('end', 49.8)
		self.entry_FLOCK_PM.grid(row=7, column=1, sticky=W)
		button_FLOCK_Fc_PM=Button(frame_FLOCK_DEF, text='Set Fast-Lock Config for Fc-Ph.Mar.', command=self.on_FLOCK_Fc_PM)
		button_FLOCK_Fc_PM.grid(row=8, column=0, columnspan=2, sticky=W+E)
		
		frame_FLOCK_DEF.grid(row=2, column=2, sticky=W+N)
		
		
		
		#frame_FLOCK.grid(row=2, column=0, columnspan=3, sticky=W+E)
		
		# LO-DIST
		frame_LO_DIST=LabelFrame(self, text='LO-DISTRIBUTION', font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'), borderwidth=0, relief=RAISED)

		lbl_ch=Label(frame_LO_DIST, text='LO Channel', width=12, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_ch.grid(row=0, column=0, sticky=W)
		#lbl_IQ=Label(frame_LO_DIST, text='IQ-GEN EN', width=15, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		#lbl_IQ.grid(row=0, column=1, sticky=W)
		lbl_IQ=Label(frame_LO_DIST, text='IQ-GEN EN', width=12, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_IQ.grid(row=0, column=1, sticky=W)
		lbl_PH=Label(frame_LO_DIST, text='Phase [deg]', width=12, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_PH.grid(row=0, column=2, sticky=W)
		lbl_EN=Label(frame_LO_DIST, text='EN', width=10, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_EN.grid(row=0, column=3, sticky=W)
		lbl_PhNoise=Label(frame_LO_DIST, text='Ph. Noise', width=10, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_PhNoise.grid(row=0, column=4, sticky=W)

				
		# LO-DIST Config for ChannelA
		lbl_chA=Label(frame_LO_DIST, text='Channel A', font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_chA.grid(row=1, column=0, sticky=W)
		self.IQ_A=BooleanVar()
		self.IQ_A.set(True)
		cbox_IQ_A=Checkbutton(frame_LO_DIST, text='IQ', onvalue=1, offvalue=0, variable=self.IQ_A, command=self.on_IQ_A)
		cbox_IQ_A.grid(row=1, column=1, sticky=W)
		self.phases_A=[0, 90, 180, 270]
		self.combo_PH_A=Combobox(frame_LO_DIST, width=8, values=self.phases_A)
		self.combo_PH_A.grid(row=1, column=2, sticky=W)
		self.combo_PH_A.current(0)
		self.EN_A=BooleanVar()
		cbox_EN_A=Checkbutton(frame_LO_DIST, text='EN_ChA', onvalue=1, offvalue=0, variable=self.EN_A, command=self.on_LO_EN)
		cbox_EN_A.grid(row=1, column=3, sticky=W)
		self.button_PN_A=Button(frame_LO_DIST, text='Plot', height=1, command=self.plot_PN_A)
		self.button_PN_A.grid(row=1, column=4, sticky=W)
		# LO-DIST Config for ChannelB
		lbl_chB=Label(frame_LO_DIST, text='Channel B', font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_chB.grid(row=2, column=0, sticky=W)
		self.IQ_B=BooleanVar()
		self.IQ_B.set(True)
		cbox_IQ_B=Checkbutton(frame_LO_DIST, text='IQ', onvalue=1, offvalue=0, variable=self.IQ_B, command=self.on_IQ_B)
		cbox_IQ_B.grid(row=2, column=1, sticky=W)
		self.phases_B=[0, 90, 180, 270]
		self.combo_PH_B=Combobox(frame_LO_DIST, width=8, values=self.phases_B)
		self.combo_PH_B.grid(row=2, column=2, sticky=W)
		self.combo_PH_B.current(0)
		self.EN_B=BooleanVar()
		cbox_EN_B=Checkbutton(frame_LO_DIST, text='EN_ChB', onvalue=1, offvalue=0, variable=self.EN_B, command=self.on_LO_EN)
		cbox_EN_B.grid(row=2, column=3, sticky=W)
		self.button_PN_B=Button(frame_LO_DIST, text='Plot', height=1, command=self.plot_PN_B)
		self.button_PN_B.grid(row=2, column=4, sticky=W)
		
		# LO-DIST Config for ChannelC
		lbl_chC=Label(frame_LO_DIST, text='Channel C', font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_chC.grid(row=3, column=0, sticky=W)
		self.IQ_C=BooleanVar()
		self.IQ_C.set(True)
		cbox_IQ_C=Checkbutton(frame_LO_DIST, text='IQ', onvalue=1, offvalue=0, variable=self.IQ_C, command=self.on_IQ_C)
		cbox_IQ_C.grid(row=3, column=1, sticky=W)
		self.phases_C=[0, 90, 180, 270]
		self.combo_PH_C=Combobox(frame_LO_DIST, width=8, values=self.phases_C)
		self.combo_PH_C.grid(row=3, column=2, sticky=W)
		self.combo_PH_C.current(0)
		self.EN_C=BooleanVar()
		cbox_EN_C=Checkbutton(frame_LO_DIST, text='EN_ChC', onvalue=1, offvalue=0, variable=self.EN_C, command=self.on_LO_EN)
		cbox_EN_C.grid(row=3, column=3, sticky=W)
		self.button_PN_C=Button(frame_LO_DIST, text='Plot', height=1, command=self.plot_PN_C)
		self.button_PN_C.grid(row=3, column=4, sticky=W)

		# LO-DIST Config for ChannelD
		lbl_chD=Label(frame_LO_DIST, text='Channel D', font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		lbl_chD.grid(row=4, column=0, sticky=W)
		self.IQ_D=BooleanVar()
		self.IQ_D.set(True)
		cbox_IQ_D=Checkbutton(frame_LO_DIST, text='IQ', onvalue=1, offvalue=0, variable=self.IQ_D, command=self.on_IQ_D)
		cbox_IQ_D.grid(row=4, column=1, sticky=W)
		self.phases_D=[0, 90, 180, 270]
		self.combo_PH_D=Combobox(frame_LO_DIST, width=8, values=self.phases_D)
		self.combo_PH_D.grid(row=4, column=2, sticky=W)
		self.combo_PH_D.current(0)		
		self.EN_D=BooleanVar()
		cbox_EN_D=Checkbutton(frame_LO_DIST, text='EN_ChD', onvalue=1, offvalue=0, variable=self.EN_D, command=self.on_LO_EN)
		cbox_EN_D.grid(row=4, column=3, sticky=W)
		self.button_PN_D=Button(frame_LO_DIST, text='Plot', height=1, command=self.plot_PN_D)
		self.button_PN_D.grid(row=4, column=4, sticky=W)
		
		# Bindings
		self.combo_PH_A.bind("<<ComboboxSelected>>", self.on_combo_PH)
		self.combo_PH_A.bind("<Return>", self.on_combo_PH)
		self.combo_PH_A.bind("<FocusOut>", self.on_combo_PH)
		self.combo_PH_B.bind("<<ComboboxSelected>>", self.on_combo_PH)
		self.combo_PH_B.bind("<Return>", self.on_combo_PH)
		self.combo_PH_B.bind("<FocusOut>", self.on_combo_PH)
		self.combo_PH_C.bind("<<ComboboxSelected>>", self.on_combo_PH)
		self.combo_PH_C.bind("<Return>", self.on_combo_PH)
		self.combo_PH_C.bind("<FocusOut>", self.on_combo_PH)
		self.combo_PH_D.bind("<<ComboboxSelected>>", self.on_combo_PH)
		self.combo_PH_D.bind("<Return>", self.on_combo_PH)
		self.combo_PH_D.bind("<FocusOut>", self.on_combo_PH)	

		# PLL-Core Summary from Main-Window
		# Remainder
		#FVCO=self.pll.vco.getF()
		#FVCO_FBDIV=self.pll.div.getN()*self.pll.Fref
		#FPLL=FVCO/ffmod
		
		
		
		# LO Output Frequencies
		lbl_LO_FREQ_TITLE=Label(frame_LO_DIST, text='LO Output Freq.', width=15, anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		lbl_LO_FREQ_TITLE.grid(row=0, column=5, sticky=W)
		self.Freq_A=Label(frame_LO_DIST, text=('%.3f GHz' %(self.FPLL/1.0e9/2.0**int(self.IQ_A.get()))), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		self.Freq_A.grid(row=1, column=5, sticky=W)
		self.Freq_B=Label(frame_LO_DIST, text=('%.3f GHz' %(self.FPLL/1.0e9/2.0**int(self.IQ_B.get()))), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		self.Freq_B.grid(row=2, column=5, sticky=W)
		self.Freq_C=Label(frame_LO_DIST, text=('%.3f GHz' %(self.FPLL/1.0e9/2.0**int(self.IQ_C.get()))), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		self.Freq_C.grid(row=3, column=5, sticky=W)
		self.Freq_D=Label(frame_LO_DIST, text=('%.3f GHz' %(self.FPLL/1.0e9/2.0**int(self.IQ_D.get()))), anchor=W, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size'))))
		self.Freq_D.grid(row=4, column=5, sticky=W)
		frame_LO_DIST.grid(row=3, column=0, columnspan=3, sticky=W+N+E)

	
		frame_Buttons=Frame(self, borderwidth=0, relief=RAISED)
		frame_Buttons.grid_rowconfigure(0, weight=1)
		frame_Buttons.grid_columnconfigure(0, weight=1)
		frame_Buttons.grid_columnconfigure(1, weight=1)
		frame_Buttons.grid_columnconfigure(2, weight=1)
		frame_Buttons.grid_columnconfigure(3, weight=1)
		Button_Save=Button(frame_Buttons, text='Save Ini File', height=2, command=self.save_INI, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		Button_Save.grid(row=0, column=0, sticky=W+E)
		Button_Open=Button(frame_Buttons, text='Open Ini File', height=2, command=self.open_INI, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'))
		Button_Open.grid(row=0, column=1, sticky=W+E)
		Button_Reset=Button(frame_Buttons, text='Reset Form', height=2, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'), command=self.reset)
		Button_Reset.grid(row=0, column=2, sticky=W+E)
		Button_Quit=Button(frame_Buttons, text='Quit', height=2, font=(self.parent.GUI_font.cget('family'), int(self.parent.GUI_font.cget('size')), 'bold'), command=self.onQuit)
		Button_Quit.grid(row=0, column=3, sticky=W+E)
		frame_Buttons.grid(row=4, column=0, columnspan=3, sticky=W+E)
		

		

		# Update Widget Values
		#self.update_VCO_AMP()
		#self.update_VDD_VCOREG()
		#self.update_FLOCK_N()
		#self.update_PH_A()
		#self.update_PH_B()
		#self.update_PH_C()
		#self.update_PH_D()
		#self.updateLOFreqs()
		#self.update_FLOCK_LPF()
		#self.update_FLOCK_CP()

		# Update PLL Config from main window
		#self.updatePLL()

		
		
		
		
		
