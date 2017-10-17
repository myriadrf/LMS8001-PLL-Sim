from header import *

from ref import *
from pfd import *
from cp import *
from LoopFLT import *
from vco import *
from div import *
from sdm import *
#from plot_funcs import searchF

def calc_PH_ERR_RMS(f, pn, fmin, fmax):
	ind_list=range(0,len(f))
	
	# Code for finding index nummbers of fmin and fmax values inside the array f
	ind_min=pll.searchF(f, fmin, 'lower-equal', 'last')
	ind_max=pll.searchF(f, fmax, 'greater-equal', 'first')
	

	if (ind_min>ind_max):
		print "calc_rmsPhErr Function: Bad Settings for fmin and fmax."
		print "calc_rmsPhErr Function: Phase Noise and Spurs Performance Summary will not be plotted.\n\n"
		return None

	if (ind_min==-1):
		print "calc_rmsPhErr Function: Too low fmin. Setting fmin to min(f)\n\n"
		fmin=min(f)
		ind_min=0
	if (ind_max==len(f)):
		print "calc_rmsPhErr Function: Too high fmax value. Setting fmax to max(f)\n\n"
		fmax=max(f)
		ind_max=len(f)-1
		
	# Calculate integrated RMS phase error from fmin to fmax
	
	pnoise_int=np.array(pn[ind_min:ind_max:1])
	pnoise_int=pnoise_int.reshape(1,len(pnoise_int))

	f_int=np.array(f[ind_min:ind_max:1])
	f_int=f_int.reshape(1,len(f_int))
		
	integral=np.trapz(10.0**(pnoise_int/10.0), x=f_int)	
	PH_ERR_RMS=180.0/math.pi*math.sqrt(2.0*integral)
	return PH_ERR_RMS

def unwrap_phase(ph, deg_unit=False):
	ph_prev=ph[0]
	if (deg_unit):
		ph_th=180
	else:
		ph_th=np.pi

	for i in range(1,len(ph)):
		diff_ph=ph[i]-ph_prev
		if (diff_ph>ph_th):
			dph=-2*ph_th
		elif (diff_ph<-ph_th):
			dph=2*ph_th
		else:
			dph=0

		for j in range(i,len(ph)):
			ph[j]+=dph
	return ph

class pll(object):
	def __init__(self, name='PLL', IC_name='GENERAL', Fref=40.0e6, VCO_EM_MODEL=False, VCO_MEAS_FREQ=True):
		if (IC_name not in valid_IC_names):
			print "Not a VALID IC_name argument."
			print "VALID IC_name(s) are:"
			for validIC in valid_IC_names:
				print '\t', validIC

			print "PLL Object not Initialized. Exiting. Returning None."

		self.IC_name=IC_name
		self.Fref=Fref
		self.flog=pll.gen_flog(2, 8, 40)
		self.name=name
		if (IC_name=='GENERAL' or IC_name=='GEN'):
			self.pfd=pfd()
			self.cp=cp()
			self.lpf=lpf()
			self.vco=vco()
			self.div=div()
		elif (IC_name=='LMS8001'):
			self.pfd=lms8001_pfd()
			self.cp=lms8001_cp()
			self.lpf=lms8001_lpf()
			self.vco=lms8001_vco(EM_MODEL=VCO_EM_MODEL, MEAS_FREQ=VCO_MEAS_FREQ)
			self.div=lms8001_div()
		self.sdm=sdm()

	def setFref(self, Fref):
		if (Fref>0):
			self.Fref=Fref
		else:
			print "Error: Defining PLL Reference Frequency: PLL Reference Frequnecy should be positive real value."
						

	
	def calc_REF_MULT(self):
		pfdtype=self.pfd.pfd_type()
		if (pfdtype=='tristate'):
			REF_MULT=1.0
		elif (pfdtype=='tristate_dual_edge'):
			REF_MULT=2.0
		return REF_MULT

	@staticmethod
	def gen_flog(exp_min, exp_max, pt_per_dec=40):
		exps=np.array(np.arange(exp_min, exp_max+1.0/pt_per_dec, 1.0/pt_per_dec))
		exps=exps.reshape((len(exps),1))
		flog=10.0**exps
		return flog

	@staticmethod
	def PM_difference_LPF3(T1, wc, gamma, T31, PM_rad):
		return np.arctan2(gamma/(wc*T1*(1+T31)),1.0)-np.arctan2(wc*T1,1.0)-np.arctan2(wc*T1*T31,1.0)-PM_rad

	@staticmethod
	def calc_T1_LPF3ord(fname, wc, gamma, T31, PM_rad, approx=False, eps=1.0e-12):
		t1_estim=(1.0/math.cos(PM_rad)-math.tan(PM_rad))/(wc*(1+T31))

		if (approx):
			return t1_estim
		else:
			t1_old=0.001*t1_estim
			t1=1000*t1_estim
			
			while not (abs(f(t1, wc, gamma, T31, PM_rad))<eps):
				t1_new=t1-fname(t1, wc, gamma, T31, PM_rad)*(t1-t1_old)/(fname(t1, wc, gamma, T31, PM_rad)-fname(t1_old, wc, gamma, T31, PM_rad))
				t1_old=max(t1, 0.001*t1_estim)
				t1=max(t1_new, 0.001*t1_estim)

			return t1

	@staticmethod
	def searchF(f, fval, mode='lower-equal', order='first'):
		"""Mode='lower-equal' - Method finds 'first' or 'last' (dep. on order arg.) element that is lower or equal to fval
		   Mode='greater-equal' - Method finds 'first' or 'last' (dep. on order arg.) element that is greater or equal to fval	"""

		ind_list=range(0, len(f))
		ind_list_rev=ind_list[:]	
		ind_list_rev.reverse()
		
		if (order not in ['first', 'last']):
			print "Bad order argument. Supported values are 'first' and 'last' for this argument."
			print "Returning -1."
			return -1

		if (mode not in ['lower-equal', 'greater-equal']):
			print "Bad mode argument. Supported values are 'lower-equal' and 'greater-equal' for this argument."
			print "Returning -1."
			return -1

		if (order=='first'):
			for ind_val in ind_list:
				if (mode=='lower-equal'):
					if (f[ind_val]<=fval):
						return ind_val
				else:
					if (f[ind_val]>=fval):
						return ind_val
			return len(f)

		else:
			for ind_val in ind_list_rev:
				if (mode=='lower-equal'):
					if (f[ind_val]<=fval):
						return ind_val
				else:
					if (f[ind_val]>=fval):
						return ind_val

			return -1


	
	def def_pfd(self, **pfdargs):
		try:
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				self.pfd.setName(pfdargs['pfdname'])
				self.pfd.set_pfd_type(pfdargs['pfdtype'])
				self.pfd.set_rst_del(float(pfdargs['pfdrstdel']))

			elif (self.IC_name=='LMS8001'):
				self.pfd.setName(pfdargs['pfdname'])
				self.pfd.set_rst_del(int(pfdargs['PFD_DEL']))
				self.pfd.set_pfd_flip(int(pfdargs['PFD_FLIP']))
		except:
			print "Error: Possible Argument Mismatch while defining PFD attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_pfd(pfdname=, pfdtype=, pfdrstdel=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_pfd(pfdname=, PFD_DEL=, PFD_FLIP=)' % (self.IC_name)
		

	def def_cp(self, **cpargs):
		try:
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				self.cp.setName(cpargs['cpname'])
				self.cp.setI(float(cpargs['i']))

			elif (self.IC_name=='LMS8001'):
				self.cp.setName(cpargs['cpname'])
				self.cp.setI(int(cpargs['PULSE']))
				self.cp.setIOFS(int(cpargs['OFS']))
				self.cp.setIBIAS(int(cpargs['ICT']))
		except:
			print "Error: Possible Argument Mismatch while defining CP attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_cp(cpname=, i=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_cp(cpname=, PULSE=, OFS=, ICT=)' % (self.IC_name)

	def def_cpNoise(self, **cpargs):
		try:
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				self.cp.setNoise(float(cpargs['fc']), float(cpargs['iup_noise']), float(cpargs['idn_noise']), float(cpargs['slope']))

			elif (self.IC_name=='LMS8001'):
				self.cp.setNoise(float(cpargs['fc']), float(cpargs['slope']), float(cpargs['In_white']))
		except:
			print "Error: Possible Argument Mismatch while defining CP Noise attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_cpNoise(fc=, iup_noise=, idn_noise=, slope=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_cpNoise(fc=, slope=, In_white=)' % (self.IC_name)

	def def_lpf(self, **lpfargs):
		try:
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				self.lpf.setName(lpfargs['lpfname'])
				self.lpf.setLPF(float(lpfargs['C1']), float(lpfargs['C2']), float(lpfargs['R2']), float(lpfargs['C3']), float(lpfargs['R3']), int(lpfargs['order']))
			elif (self.IC_name=='LMS8001'):
				self.lpf.setName(lpfargs['lpfname'])
				self.lpf.setLPF(int(lpfargs['C1_CODE']), int(lpfargs['C2_CODE']), int(lpfargs['R2_CODE']), int(lpfargs['C3_CODE']), int(lpfargs['R3_CODE']), 3)
		except:
			print "Error: Possible Argument Mismatch while defining LPF attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_lpf(lpfname=, C1=, C2=, R2=, C3=, R3=, order=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_lpf(lpfname=, C1_CODE=, C2_CODE=, R2_CODE=, C3_CODE=, R3_CODE=)' % (self.IC_name)
				
	def def_vco(self, **vcoargs):
		try:
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				self.vco.setName(vcoargs['vconame'])
				self.vco.setF(float(vcoargs['F']))
				self.vco.setKVCO(float(vcoargs['KVCO']))
			elif (self.IC_name=='LMS8001'):
				self.vco.setName(vcoargs['vconame'])
				self.vco.setF(int(vcoargs['SEL']), int(vcoargs['FREQ']), float(vcoargs['VTUNE']))
		except:
			print "Error: Possible Argument Mismatch while defining VCO attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_vco(vconame=, F=, KVCO=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_vco(vconame=, SEL=, FREQ=, VTUNE=)' % (self.IC_name)

			
		
	def def_vcoPNoise(self, **vcoargs):
		try:
			if (len(vcoargs.keys())==1):
				self.vco.setNoise((vcoargs['fc']))
			else:
				self.vco.setNoise((vcoargs['fc']), ((vcoargs['pn']), (vcoargs['fpn'])))
		except:
			print "Error: Possible Argument Mismatch while defining VCO PNoise attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN' or self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_vcoPNoise(fc=) or .def_vcoPNoise(fc=, (pn, fpn)=)' % (self.IC_name)
				
	


	def def_div(self, auto_calc=False, **divargs):
		try:
			REF_MULT=self.calc_REF_MULT()		
			self.div.setName(divargs['divname'])
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				if (auto_calc):
					self.div.setN(self.vco.getF()/(self.Fref*REF_MULT))
				else:
					self.div.setN(float(divargs['N']))
			elif (self.IC_name=='LMS8001'):
				if (auto_calc):
					if ('PDIV2' in divargs.keys()):
						expn=int(divargs['PDIV2'])
					else:	
						expn=0.0
					expn=max(expn, 0.0)
					expn=min(expn, 1.0)
					denum=2.0**expn
					self.div.setPDIV2(expn)

					self.div.setNDIV(1.0/denum*self.vco.getF()/(self.Fref*REF_MULT))
				else:
					self.div.setNDIV(float(divargs['NDIV']))
					self.div.setPDIV2(int(divargs['PDIV2']))
		except:
			print "Error: Possible Argument Mismatch while defining DIV attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN'):
				print 'For IC_name=%s syntax is .def_div(divname=, N=, auto_calc=)' % (self.IC_name)
			elif (self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_div(divname=, NDIV=, PDIV2=, auto_calc=)' % (self.IC_name)

	def def_divPNoise(self, **divargs):
		try:
			self.div.setNoise(divargs['fpn'], divargs['pn'], divargs['noise_floor'])
		except:
			print "Error: Possible Argument Mismatch while defining DIV PNoise attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN' or self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_divPNoise(fpn=[...], pn=[...], noise_floor=)' % (self.IC_name)
	def div_Config(self):
		if (self.IC_name=='LMS8001'):
			return self.div.getConfig()
		else:
			return dict()
	
	def def_sdm(self, **sdmargs):
		try:
			self.sdm.setName(sdmargs['sdmname'])
			self.sdm.setOrder(sdmargs['sdmorder'])
			self.sdm.setNbit(sdmargs['sdmNbit'])
		except:
			print "Error: Possible Argument Mismatch while defining SDM attributes."
			print "       Argument Names in method call are mandatory."
			if (self.IC_name=='GENERAL' or self.IC_name=='GEN' or self.IC_name=='LMS8001'):
				print 'For IC_name=%s syntax is .def_sdm(sdmname=, sdmorder=, sdmNbit=)' % (self.IC_name)

	def getSDM_inps(self):
		return self.sdm.get_inps(self.div.getNDIV())

	def set_flog(self, exp_min, exp_max, pt_per_dec):
		self.flog=pll.gen_flog(exp_min, exp_max, pt_per_dec)
		return self.flog

	def __str__(self):
		fmin=min(self.flog)
		fmax=max(self.flog)
		n_dec=math.log10(fmax/fmin)
		pt_per_dec=floor(len(self.flog)/n_dec)
		SDM_INPUTS=self.sdm.calc_inps(self.div.getNDIV())

		title='PLL Class Instance\n'
		line_Fref='Reference Frequency= %.2f MHz\n' %(self.Fref/1.0e6)
		line_Flog='PLL Frequency Analysis, from fmin=%.2e Hz to fmax=%.2e Hz, with %d points/decade\n' % (fmin, fmax, pt_per_dec)
		line1='Inst.Name = ' + self.name + '\n'
		line2='List of Subblocks:\n' + '-'*25 + '\n'
		line_sdm_inputs='\n\tNINT= %d, NFRAC= %d' % (SDM_INPUTS['INT'], SDM_INPUTS['FRAC'])
		line_sub_blocks=str(self.pfd) + '\n' + str(self.cp) + '\n' + str(self.lpf) + '\n' + str(self.vco) + '\n' + str(self.div) +'\n' + str(self.sdm) + line_sdm_inputs + '\n'

		
		return (title+line_Fref+line_Flog+line1+line2+line_sub_blocks)

	
	def calcLPF(self, PM_deg=49.8, fc=80e3, gamma=1.045, T31=0.1, order=3, approx='False', eps=1.0e-12):
		PM_rad=PM_deg*math.pi/180
		wc=2*math.pi*fc

		REF_MULT=self.calc_REF_MULT()
		
		Kphase=self.cp.getI()/(2*math.pi)

		Kvco=2*math.pi*self.vco.getKVCO()
		
		N=self.div.getN()/REF_MULT

		if (order<2 or order>3):
			print "Unsupported PLL Loop-Filer order.\nOnly Passive Loop-Filter topologies, of order 2 or 3, are supported."
			return {'C1':0, 'C2':0, 'R2':0, 'C3':0, 'R3':0, 'KMAX':0}
		
		if (order==2):	
			T1=(math.sqrt(((1+gamma)**2)*((math.tan(PM_rad))**2)+4*gamma)-(1+gamma)*math.tan(PM_rad))/(2*wc);
   			T2=gamma/((wc**2)*T1);
    			A0=Kphase*Kvco/(N*(wc**2))*sqrt((1+(wc**2)*(T2**2))/(1+(wc**2)*(T1**2)));

			C1=A0*T1/T2;
  			C2=A0-C1;
    			R2=T2/C2;
    			C3=0;
    			R3=0;
    			KMAX=0;

		elif (order==3):
			T1=pll.calc_T1_LPF3ord(pll.PM_difference_LPF3, wc, gamma, T31, PM_rad, approx, eps)
			T3=T1*T31;
    			T2=gamma/((wc**2)*(T1+T3));

			A0=(Kphase*Kvco)/((wc**2)*N)*math.sqrt((1+(wc**2)*(T2**2))/((1+(wc**2)*(T1**2))*(1+(wc**2)*(T3**2))));
    			A2=A0*T1*T3;
    			A1=A0*(T1+T3);

			C1=A2/(T2**2)*(1+math.sqrt(1+T2/A2*(T2*A0-A1)));
    			C3=(-(T2**2)*(C1**2)+T2*A1*C1-A2*A0)/((T2**2)*C1-A2);
    			C2=A0-C1-C3;
    			R2=T2/C2;
    			R3=A2/(C1*C3*T2);
    			KMAX=(T2-(T1+T3))*A0*(T1+T3)/((T2**2)*T1*T3);

		return {'C1':C1, 'C2':C2, 'R2':R2, 'C3':C3, 'R3':R3, 'KMAX':KMAX}

	def get_LPF_OptConfig(self, TARGET_VALS):
		if (self.IC_name=='LMS8001'):
			return self.lpf.optim(TARGET_VALS['C1'], TARGET_VALS['C2'], TARGET_VALS['R2'], TARGET_VALS['C3'], TARGET_VALS['R3'])
		else:
			return dict()

	def optim_PLL_LoopBW(self, PM_deg=49.8, fc=80.0e3):
		"""
		This method finds optimal PLL configuration, CP pulse current and LPF element values.
		Optimization finds maximal CP current which can results with targeted PLL Loop BW using Loop-Filter elements which can be implemented in LMS8001 IC.
		Result should be PLL configuration with best phase noise performance for targeted loop bandwidth.
		"""

		# Calculate Phase Margin in radians
		# Calculate angle frequency for fc
		PM_rad=PM_deg*math.pi/180
		wc=2*math.pi*fc		

		# Get initial CP current settings
		CP_NAME=self.cp.name
		PULSE_INIT=self.cp.PULSE
		OFS_INIT=self.cp.OFS
		ICT_CP_INIT=self.cp.ICT

		# Pulse control word of CP inside LMS8001 will be swept from 63 to 4.
		# First value that gives implementable PLL configuration will be used.	
		cp_pulse_vals=range(4,64)
		cp_pulse_vals.reverse()
	

		for cp_pulse in cp_pulse_vals:
			self.def_cp(cpname=CP_NAME, PULSE=cp_pulse, OFS=OFS_INIT, ICT=ICT_CP_INIT)
		

			LPF_IDEAL_VALUES=self.calcLPF(PM_deg=PM_deg, fc=fc, gamma=1.045, T31=0.1, order=3, approx='False', eps=1.0e-12)


			C1=LPF_IDEAL_VALUES['C1']
			C2=LPF_IDEAL_VALUES['C2']
			C3=LPF_IDEAL_VALUES['C3']
			R2=LPF_IDEAL_VALUES['R2']
			R3=LPF_IDEAL_VALUES['R3']
		
		

			C1_cond=(LMS8001_C1_STEP<=C1<=15*LMS8001_C1_STEP)
			C2_cond=(LMS8001_C2_FIX<=C2<=LMS8001_C2_FIX+15*LMS8001_C2_STEP)
			C3_cond=(LMS8001_C3_FIX+LMS8001_C3_STEP<=C3<=LMS8001_C3_FIX+15*LMS8001_C3_STEP)
			R2_cond=(LMS8001_R2_0/15.0<=R2<=LMS8001_R2_0)
			R3_cond=(LMS8001_R3_0/15.0<=R3<=LMS8001_R3_0)
		
			if (C1_cond and C2_cond and C3_cond and R2_cond and R3_cond):

				LPF_REAL_VALUES=self.get_LPF_OptConfig(LPF_IDEAL_VALUES)
			

				self.def_lpf(lpfname='LoopFLT_LMS8001', C1_CODE=LPF_REAL_VALUES['C1_CODE'], C2_CODE=LPF_REAL_VALUES['C2_CODE'], R2_CODE=LPF_REAL_VALUES['R2_CODE'], C3_CODE=LPF_REAL_VALUES['C3_CODE'], R3_CODE=LPF_REAL_VALUES['R3_CODE'])
				print 'PLL LoopBW Optimization finished successfuly.'
				print '-'*45
				print ''
				return True
	
		print 'PLL LoopBW Optimization failed.'
		print 'Some of the LPF component(s) out of implementable range.'
		# Set back to initial settings of CP
		self.def_cp(cpname=CP_NAME, PULSE=PULSE_INIT, OFS=OFS_INIT, ICT=ICT_CP_INIT)
		return False
	

	def op_loop_tfunc(self, f=np.empty(shape=(0, 0))):
		if (f.size==0):
			f=self.flog
		return (f, self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f))
	
	def cl_loop_tfunc(self, block='REF', f=np.empty(shape=(0, 0))):
		if (f.size==0):
			f=self.flog
		
		if (block=='REF' or block=='DIV'):
			FG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		elif (block=='VCO'):
			FG=1.0
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		elif (block=='LPF'):
			FG=self.vco.tfunc(f)
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		elif (block=='CP'):
			FG=self.lpf.tfunc(f)*self.vco.tfunc(f)
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		elif (block=='PFD'):
			FG=self.cp.tfunc(f)*self.lpf.tfunc(f)*self.self.vco.tfunc(f)
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		elif (block=='SDM'):
			FG=self.div.tfunc(f)*self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)
			LG=self.pfd.tfunc(f)*self.cp.tfunc(f)*self.lpf.tfunc(f)*self.vco.tfunc(f)*self.div.tfunc(f)
		else:
			print "Unsupported name of the PLL sub-block. Returning None"
			return (None, None)

		return (f, FG/(1+LG))

#	def time_responseFFT(self, fs, T):
#		"""This method calculates LTI time response of the analyzed PLL. fs is for sampling rate, T is the total time duratation."""
		
#		Ts=1.0/fs
#		fmax=fs/2.0
#		fmin=1.0/T
#		N=math.ceil(T/Ts)
#		df=(fmax-fmin)/N
		
		
#		if (fmin>fmax):
#			print "Wrong settings for fs and T. Returning None."
#			return (None, None)

#		flin=np.array(np.arange(fmin, fmax, df))
#		flin=flin.reshape((len(flin),1))
#		wlin=2.0*math.pi*flin
#		slin=np.complex(0,1)*wlin
		
#		inp=2*math.pi*0.05e6/(slin**2)
#		#print 'input shape', inp.shape
#		#print flin.size

#		t=np.array(np.arange(0,(len(flin))*Ts, Ts))
#		t=t.reshape(len(t),1)
		
#		(fjunk, CLoop)=self.cl_loop_tfunc(f=flin, block='REF')
#		TFunc_pos=CLoop/self.vco.tfunc(flin)*inp
#		TFunc_neg=TFunc_pos[1:1:len(TFunc_pos)-1]
#		TFunc_FFT=np.append(TFunc_pos, np.conj(np.flipud(TFunc_neg)))
#		#TFunc_FFT=np.append(np.conj(np.flipud(TFunc)), TFunc)
#		time_resp=np.fft.ifft(TFunc_FFT)
#		time_resp=time_resp.reshape(len(time_resp),1)
#		return (t, time_resp)

	def fstep_response(self, Ts=1/200.0e6, Tstop=50.0e-6, FSTEP_OUT=10.0e6):
		"""Ts is sampling period, Tstop is stop time, FSTEP_OUT value of desired frequency step at VCO output"""

		LPF=self.lpf.getLPF_vals()

		LPFord=LPF['order']
		C1=LPF['C1']
		C2=LPF['C2']
		R2=LPF['R2']
		C3=LPF['C3']
		R3=LPF['R3']


		Icp=self.cp.getI()
		
		N=self.div.getN()
		
		Kvco=2*math.pi*self.vco.getKVCO()
		
		PFD=self.pfd.tfunc_scalar()
		
		
		FSTEP_PFDIN=FSTEP_OUT/N
		
		if (LPFord==3 or LPFord==2):
			NOM_PhE = [(C1*C2*C3*R2*R3), (C1*C2*R2+C1*C3*R3+C2*C3*R3+C2*C3*R2), (C1+C2+C3), 0, 0];
			DENOM_PhE = [(C1*C2*C3*R2*R3), (C1*C2*R2+C1*C3*R3+C2*C3*R3+C2*C3*R2), (C1+C2+C3), Icp*Kvco*PFD/N*C2*R2,  Icp*Kvco*PFD/N];

			
			NOM_Vtune=[Icp*PFD*C2*R2, Icp*PFD, 0];
			DENOM_Vtune=[(C1*C2*C3*R2*R3), (C1*C2*R2+C1*C3*R3+C2*C3*R3+C2*C3*R2), (C1+C2+C3), Icp*Kvco*PFD/N*C2*R2,  Icp*Kvco*PFD/N];

			NOM_Fout=[0, 0, Icp*Kvco*(PFD**2)*C2*R2, Icp*Kvco*(PFD**2), 0];
			DENOM_Fout=[(C1*C2*C3*R2*R3), (C1*C2*R2+C1*C3*R3+C2*C3*R3+C2*C3*R2), (C1+C2+C3), Icp*Kvco*PFD/N*C2*R2,  Icp*Kvco*PFD/N];
		
		t=np.array(np.arange(0, Tstop, Ts))
		
		PH_IN=2*math.pi*FSTEP_PFDIN*t
		

		[tvals, PHE_OUT, state]=scp.signal.lsim((NOM_PhE, DENOM_PhE), PH_IN, t)
		[tvals, VTUNE, state]=scp.signal.lsim((NOM_Vtune, DENOM_Vtune), PH_IN, t)
		[tvals, FOUT, state]=scp.signal.lsim((NOM_Fout, DENOM_Fout), PH_IN, t)
		FOUT+=self.vco.getF()
		VTUNE*=Kvco/(N*2*pi*FSTEP_PFDIN)
		FERR=FOUT-(self.vco.getF()+FSTEP_OUT)
		out_res={'TIME':t, 'PHE_OUT':PHE_OUT, 'VTUNE':VTUNE, 'FOUT':FOUT, 'FERR':FERR}
		
		return out_res

	def setVCO_Noise(self, fc, (pn, fpn)):
		self.vco.setNoise(fc, (pn,fpn))


	def vco_pnoise(self, f=np.empty(shape=(0, 0))):
		if f.size==0:
			f=self.flog

		return (f, self.vco.calc_pnoise(f))

	def VCO_CTUNE(self, F_TARGET, SEL_FORCE=False, SEL_INIT=2, FREQ_FORCE=False, FREQ_INIT=128, FREQ_INIT_POS=7, FREQ_MIN=5, FREQ_MAX=250, VTUNE_FIX=0.6, VTUNE_STEP=0.01, LMS8001_INTERNAL=False):
		if (self.IC_name=='LMS8001'):
			if not (LMS8001_INTERNAL):
				if not (SEL_FORCE):
					SEL_INIT=0
				return self.vco.AUTO_CAL(F_TARGET, VTUNE_FIX=VTUNE_FIX, VTUNE_STEP=VTUNE_STEP, SEL_INIT=SEL_INIT)
			else:
				return self.vco.CTUNE(F_TARGET, SEL_FORCE, SEL_INIT, FREQ_FORCE, FREQ_INIT, FREQ_INIT_POS, FREQ_MIN, FREQ_MAX, VTUNE_FIX, VTUNE_STEP)
		else:
			return dict()


	def setDiv_Noise(self, fc, slope, noise_floor):
		self.div.setNoise(fc, slope, noise_floor)	

	def div_pnoise(self, f=np.empty(shape=(0, 0))):
		if f.size==0:
			f=self.flog

		return (f, self.div.calc_pnoise(f))

	def setCP_Noise(self, fc, iup_noise, idn_noise, slope):
		self.cp.setNoise(fc, iup_noise, idn_noise, slope)

	def cp_pnoise(self, f=np.empty(shape=(0, 0)), ks=0.016):
		if f.size==0:
			f=self.flog

		In_cpout=self.cp.In(f, self.pfd.get_rst_del()*self.Fref)
		pn_vals=In_cpout/(self.cp.getI()*self.pfd.tfunc_scalar())
		for i in range(0,len(pn_vals)):
			pn_vals[i]=20.0*math.log10(abs(pn_vals[i]))
		return (f, pn_vals)

	def lpf_Vn(self, f=np.empty(shape=(0, 0))):
		if f.size==0:
			f=self.flog

		return (f, self.lpf.Vn(f))

	def sdm_pnoise(self, f=np.empty(shape=(0, 0))):
		if f.size==0:
			f=self.flog

		Fref=self.Fref

		return (f, self.sdm.calc_pnoise(f, Fref))

	def pnoise(self, f=np.empty(shape=(0, 0)), pn_ref=np.empty(shape=(0, 0)), outputs=['ALL'], SDM_NOISE=True):
		if f.size==0:
			f=self.flog


		pn_sdm=self.sdm.calc_pnoise(f,self.Fref)
		Vn_lpf=self.lpf.Vn(f)
		In_cp=self.cp.In(f, self.pfd.get_rst_del()*self.Fref)*sqrt(self.calc_REF_MULT())
		

		#plotlogx(f, In_cp,10)
		pn_div=self.div.calc_pnoise(f)*sqrt(self.calc_REF_MULT())
		pn_vco=self.vco.calc_pnoise(f)

		phi_sdm=sqrt(2)*(10**(pn_sdm/20))
		phi_div=sqrt(2)*(10**(pn_div/20))
		phi_vco=sqrt(2)*(10**(pn_vco/20))
		
		phi_sdm=phi_sdm.reshape(len(f),1)
		(fcl, NoiseTF_SDM)=self.cl_loop_tfunc(f=f, block='SDM')
		phi_SDM_OUT=phi_sdm*NoiseTF_SDM
		# If SDM Quant. Noise is not a concern as in Integer-N Operating Mode
		if (SDM_NOISE==False):
			for i in range(0,len(phi_SDM_OUT)):
				phi_SDM_OUT[i]=sqrt(2)*10.0**(-20.0)

		
		phi_vco=phi_vco.reshape(len(f),1)
		(fcl, NoiseTF_VCO)=self.cl_loop_tfunc(f=f, block='VCO')
		phi_VCO_OUT=phi_vco*NoiseTF_VCO
		
		phi_div=phi_div.reshape(len(f),1)
		(fcl, NoiseTF_DIV)=self.cl_loop_tfunc(f=f, block='DIV')
		phi_DIV_OUT=phi_div*NoiseTF_DIV
		
		Vn_lpf=Vn_lpf.reshape(len(f),1)
		(fcl, NoiseTF_LPF)=self.cl_loop_tfunc(f=f, block='LPF')
		phi_LPF_OUT=Vn_lpf*NoiseTF_LPF

		In_cp=In_cp.reshape(len(f),1)
		(fcl, NoiseTF_CP)=self.cl_loop_tfunc(f=f, block='CP')
		#phi_CP_OUT=sqrt(2)*In_cp*NoiseTF_CP
		phi_CP_OUT=In_cp*NoiseTF_CP
		
		if (pn_ref.size==f.size):
			phi_REF=sqrt(2)*(10**(pn_ref/20))
			phi_REF=phi_REF.reshape(len(f),1)

			(fcl, NoiseTF_REF)=self.cl_loop_tfunc(f=f, block='REF')
			phi_REF_OUT=phi_REF*np.abs(NoiseTF_REF)
		else:
			phi_REF_OUT=np.zeros((len(f),1))
		
		
		phi_PLL2=(np.abs(phi_SDM_OUT)**2+np.abs(phi_VCO_OUT)**2+np.abs(phi_DIV_OUT)**2+np.abs(phi_LPF_OUT)**2+np.abs(phi_CP_OUT)**2+np.abs(phi_REF_OUT)**2)
				
		phi_PLL=[]
		for val in phi_PLL2:
			phi_PLL.append(math.sqrt(val))

		pn_PLL=[]
		pn_SDM_OUT=[]
		pn_VCO_OUT=[]
		pn_DIV_OUT=[]
		pn_LPF_OUT=[]
		pn_CP_OUT=[]
		pn_REF_OUT=[]
		
		for find in range(0,len(f)):
			pn_PLL.append(20*math.log10(abs(phi_PLL[find])/sqrt(2)))
			pn_SDM_OUT.append(20*math.log10(abs(phi_SDM_OUT[find])/sqrt(2)))
			pn_VCO_OUT.append(20*math.log10(abs(phi_VCO_OUT[find])/sqrt(2)))
			pn_DIV_OUT.append(20*math.log10(abs(phi_DIV_OUT[find])/sqrt(2)))
			pn_LPF_OUT.append(20*math.log10(abs(phi_LPF_OUT[find])/sqrt(2)))
			pn_CP_OUT.append(20*math.log10(abs(phi_CP_OUT[find])/sqrt(2)))

			if (phi_REF_OUT[find]==0):
				pn_REF_OUT.append(-300.0)
			else:
				pn_REF_OUT.append(20*math.log10(abs(phi_REF_OUT[find])/sqrt(2)))


		pnoise_out={}
		pnoise_out['TOTAL']=pn_PLL
		if ('ALL' in outputs):
			pnoise_out['VCO']=pn_VCO_OUT
			pnoise_out['SDM']=pn_SDM_OUT
			pnoise_out['DIV']=pn_DIV_OUT
			pnoise_out['LPF']=pn_LPF_OUT
			pnoise_out['CP']=pn_CP_OUT
			pnoise_out['REF']=pn_REF_OUT
		else:
			if ('VCO' in outputs):
				pnoise_out['VCO']=pn_VCO_OUT

			if ('DIV' in outputs):
				pnoise_out['DIV']=pn_DIV_OUT

			if ('SDM' in outputs):
				pnoise_out['SDM']=pn_SDM_OUT

			if ('REF' in outputs):
				pnoise_out['REF']=pn_REF_OUT

			if ('CP' in outputs):
				pnoise_out['CP']=pn_CP_OUT

			if ('LPF' in outputs):
				pnoise_out['LPF']=pn_LPF_OUT


		return (f, pnoise_out)

	def noise_spurs_summary(self, f=np.empty(shape=(0, 0)), fmin=100, fmax=100.0e6, fs=[1.0e3, 1.0e4, 1.0e5, 1.0e6, 10.0e6], pn_ref=np.empty(shape=(0, 0)), RefSpurSupp=-70, PN_CLOSE=-100.0, print_to_file=False, file_name='noise_spurs_summary.txt', print_to_cmd=True, SDM_NOISE=True):
		"""This method prints phase-noise and reference spurs performance summary in command line or text file."""

		if (f.size==0):
			f=self.flog

		ind_min=-1
		ind_max=len(f)
		
		summary_text=''
		if (print_to_file):
			summary_file=open(file_name, "w")
		ind_list=range(0,len(f))

		# Code for finding index nummbers of fmin and fmax values inside the array f
		ind_min=pll.searchF(f, fmin, 'lower-equal', 'last')
		ind_max=pll.searchF(f, fmax, 'greater-equal', 'first')
		

		if (ind_min>ind_max):
			print "Bad Settings for fmin and fmax."
			print "Phase Noise and Spurs Performance Summary will not be plotted.\n\n"
			return (False, None)

		if (ind_min==-1):
			print "Too low fmin. Setting fmin to min(f)\n\n"
			fmin=min(f)
			ind_min=0
		if (ind_max==len(f)):
			print "Too high fmax value. Setting fmax to max(f)\n\n"
			fmax=max(f)
			ind_max=len(f)-1
		
		# Calculate integrated RMS phase error from fmin to fmax
		(fx,pnoise_val)=self.pnoise(f=f, pn_ref=pn_ref, outputs=[''], SDM_NOISE=SDM_NOISE)
		pnoise_out=pnoise_val['TOTAL']
		
		pnoise_int=np.array(pnoise_out[ind_min:ind_max:1])
		pnoise_int=pnoise_int.reshape(1,len(pnoise_int))
		# pnoise_int+=2.0 
		f_int=np.array(f[ind_min:ind_max:1])
		f_int=f_int.reshape(1,len(f_int))
		
		integral=np.trapz(10.0**(pnoise_int/10.0), x=f_int)	
		PH_ERR_RMS=180.0/math.pi*math.sqrt(2.0*integral)
		
		# Calculate maximum recommended close-loop 3 dB BW for fractional-PLL mode and close-in PNoise boundary of PN_CLOSE dBc/Hz
		An=10.0**(PN_CLOSE/10.0)		
		Fcomp=self.Fref*self.calc_REF_MULT()
		sdm_ord=self.sdm.getOrder()
		F3dB_MAX=Fcomp/2.0/math.pi*(Fcomp/(8.0*(math.pi)**2)*An*(2*sdm_ord+1))**(1.0/(2*sdm_ord-2))

		# Calculated maximum 1st harmonic current value from CP which leaves refererence spur level bellow RefSpurSupp dBc
		ind_Fcomp=pll.searchF(f, Fcomp, 'lower-equal', 'last')
		(fx, CL_LOOP_REF)=self.cl_loop_tfunc(block='REF', f=f)
		
		if (ind_Fcomp<0 or ind_Fcomp>len(f)-1):
			print "Warning: Reference frequency is not inside the f array."
			print "Max CP Harmonic Current set to 1.0e6 Amps."
			Icp_harm_max=1.0e6
		
		Z_LoopFLT=self.lpf.tfunc(f)
		CL_LOOP_FCOMP_dB=20*math.log10(abs(CL_LOOP_REF[ind_Fcomp]))
		Icph_max1=10.0**((RefSpurSupp-CL_LOOP_FCOMP_dB)/20.0)*self.pfd.tfunc_scalar()*self.cp.getI()
		Icph_max2=10.0**(RefSpurSupp/20.0)*2*Fcomp/(self.vco.getKVCO()*abs(Z_LoopFLT[ind_Fcomp]))
		Icp_harm_max=min(Icph_max1, Icph_max2)

		# Create text for Phase Noise and Ref. Spurs Summary
		Nsep=60
		summary_text+='\n'
		summary_text+='%s, Phase Noise & Spurs Performance Summary\n' % (self.name)
		summary_text+=('-'*Nsep + '\n')
		summary_text+='Charge Pump Current Spurs\n'
		summary_text+=('-'*Nsep + '\n')
		summary_text+='\tTargeted PFD Fcomp Spur Suppression= %.2f dBc\n' % (RefSpurSupp)
		summary_text+='\tMax. Value of CP Harmonic Current= %.2f nA at Fcomp=%.2f MHz\n' % (Icp_harm_max/1.0e-9, Fcomp/1.0e6)
		summary_text+=('-'*Nsep + '\n')
		summary_text+='Maximum PLL Loop Bandwidth in Fractional-N Operating Mode\n'
		summary_text+=('-'*Nsep + '\n')
		summary_text+='\tTargeted Close-In Phase Noise Level=%.2f dBc/Hz\n' % (PN_CLOSE)
		summary_text+='\tMax. PLL 3-dB Close-Loop Bandwidh= %.2f KHz\n' % (F3dB_MAX/1.0e3)
		summary_text+=('-'*Nsep + '\n')
		summary_text+='Phase-Noise Performance @ VCO Output\n'
		summary_text+=('-'*Nsep + '\n')
		summary_text+='\tRMS Phase Error=%.2f, Integrated from %.2e Hz to %.2e Hz\n' %(PH_ERR_RMS, fmin, fmax)
		

		for fval in fs:
			ind_fval=pll.searchF(f, fval, 'lower-equal', 'last')
			res_str='\tPN[%.2f GHz + %.2e Hz]= ' % (Fcomp*self.div.getN()/1.0e9, fval)
			if (ind_fval==-1 or ind_fval==len(f)):
				res_str+='Not.Calc.\n'
			else:
				res_str+='%.2f dBc/Hz\n' % (pnoise_out[ind_fval])
			
			summary_text+=res_str

		summary_text+=('-'*Nsep + '\n')

		summary_dict={'F3dB_MAX':F3dB_MAX, 'PH_ERR_RMS':PH_ERR_RMS, 'ICP_HARM_MAX':Icp_harm_max, 'TEXT':summary_text}

		if (print_to_file):
			summary_file.write(summary_text)
			summary_file.close()
		elif (print_to_cmd):
			print summary_text
		
		return (True, summary_dict)

	def dynamics_summary(self, f=np.empty(shape=(0, 0)), Ts=1/200.0e6, Tstop=50.0e-6, FSTEP_OUT=10.0e6, FERR_HIGH=5.0e3, FERR_LOW=100.0, print_to_file=False, file_name='dynamics_summary.txt', print_to_cmd=True):
		summary_text=''
		if (f.size==0):
			f=self.flog

		if (print_to_file):
			summary_file=open(file_name, 'w')

		if (FERR_HIGH<FERR_LOW):
			print "Error: Settling Frequency Error FERR_HIGH greater then FERR_LOW."
			print "       Exiting. Returning (False, {})\n\n"
			return (False, dict())
		
		PLL_FSTEP=self.fstep_response(Ts, Tstop, FSTEP_OUT)
		(freqOL, PLL_OP_LOOP)=self.op_loop_tfunc(f=f)
		(freqCL, PLL_CL_LOOP)=self.cl_loop_tfunc(f=f)

		TIME=PLL_FSTEP['TIME']
		TIME=TIME.reshape(len(TIME),1)

		FERR=PLL_FSTEP['FERR']
		FERR=FERR.reshape(len(FERR),1)

		
		ind_LOW=len(TIME)
		ind_HIGH=len(TIME)
		for ind in range(0, len(TIME)):
			if (FERR[ind]>FERR_LOW):
				ind_LOW=ind
			if (FERR[ind]>FERR_HIGH):
				ind_HIGH=ind
		ind_HIGH+=1
		ind_LOW+=1
		if (ind_HIGH>=len(TIME)):
			ind_HIGH=len(TIME)-1

		if (ind_LOW>=len(TIME)):
			ind_LOW=len(TIME)-1

		ind_F3dB=len(freqCL)
		PLL_CL_LOOP_DC=PLL_CL_LOOP[0]
		for ind in range(0, len(freqCL)):
			if (20*math.log10(abs(PLL_CL_LOOP[ind]/PLL_CL_LOOP_DC))<=-3):
				ind_F3dB=ind
				break
		if (ind_F3dB==len(freqCL)):
			ind_F3dB-=1

		ind_Fc=len(freqOL)
		for ind in range(0, len(freqOL)):
			if (20*math.log10(abs(PLL_OP_LOOP[ind]))<=0):
				ind_Fc=ind
				break
		if (ind_Fc==len(freqOL)):
			ind_Fc-=1
		
		F3dB=freqCL[ind_F3dB]
		Fc=freqOL[ind_Fc]
		PM=np.rad2deg(unwrap_phase(np.angle(PLL_OP_LOOP[ind_Fc])))+180
		
		Nsep=60
		summary_text+='\n'
		summary_text+='%s, Loop Dynamics Summary\n' % (self.name)
		summary_text+=('-'*Nsep + '\n')
		summary_text+='\tSettling Time= %.3f us for FERR<%.2e Hz\n' % (TIME[ind_HIGH]/1.0e-6, FERR_HIGH)
		summary_text+='\tSettling Time= %.3f us for FERR<%.2e Hz\n' % (TIME[ind_LOW]/1.0e-6, FERR_LOW)
		summary_text+=('-'*Nsep + '\n')
		summary_text+='\tClose Loop BW 3dB=%.2f kHz\n' % (F3dB/1.0e3)
		summary_text+='\tOpen Loop Crossover Frequency=%.2f kHz\n' % (Fc/1.0e3)
		summary_text+='\tPhase Margin= %.2f deg\n' % (PM)
		summary_text+=('-'*Nsep + '\n')
		
		if (print_to_file):
			summary_file.write(summary_text)
			summary_file.close()
		elif (print_to_cmd):
			print summary_text

		DYN_SUMMARY={'TEXT':summary_text, 'THIGH':TIME[ind_HIGH], 'TLOW':TIME[ind_LOW], 'F3dB':F3dB, 'Fc':Fc, 'PM':PM}
		return (True, DYN_SUMMARY)
		
	def gen_summary(self, print_to_file=False, file_name='pll_summary.txt', fmin=100, fmax=100.0e6, pn_ref=np.empty(shape=(0, 0)), SDM_NOISE=True):
		summary_text=''
		summary_text+=str(self)
		(DYN_STATUS, DYN_SUMMARY)=self.dynamics_summary(print_to_cmd=False)
		(PN_STATUS, PN_SUMMARY)=self.noise_spurs_summary(print_to_cmd=False, fmin=fmin, fmax=fmax, pn_ref=pn_ref, SDM_NOISE=SDM_NOISE)
		if (DYN_STATUS):
			DYN_TEXT=DYN_SUMMARY['TEXT']
			summary_text+=DYN_TEXT
		if (PN_STATUS):
			PN_TEXT=PN_SUMMARY['TEXT']
			summary_text+=PN_TEXT

		if not(print_to_file):
			print summary_text
		else:
			summary_file=open(file_name, 'w')
			summary_file.write(summary_text)
			summary_file.close()

		return summary_text
		

		

		
