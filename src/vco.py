from header import *
from plot_funcs import searchF
import pandas as pnd

class vco(object):
	"""Represents ideal VCO. F is frequency of oscillation in Hz, and KVCO is tuning sensistivity in Hz/V"""
	def __init__(self, name='VCO', F=1.0e9, KVCO=20.0e6,  fc=200.0e3, (pn,fpn)=(-121, 1.0e6), noise_floor=-165.0):
		self.name=name		
		if (F<=0):
			print "VCO oscillation frequency should be positive real number."
			print "VCO object not created. Returning None."
			return None
		else:
			self.F=F
			self.KVCO=KVCO

		if (fc>0 and fpn>0):
			self.fc=fc
			self.pn=pn
			self.fpn=fpn
			self.noise_floor=noise_floor

		else:
			print "Corner frequency and phase noise frequency should be positive real number."
			print "VCO object not created. Returning None."
			return None
	
	def setNoise(self, fc, (pn, fpn)=(-121, 1.0e6), noise_floor=-165.0):
		if (fc>0 and fpn>0):
			self.fc=fc
			self.pn=pn
			self.fpn

		else:
			print "Corner frequnecy and phase noise frequency should be positive real number."
			print "VCO Noise parameters not changed."


	def __str__(self):
		return ("VCO class instance\n\tInst.Name= %s\n\tF=%.2f GHZ\n\tKVCO=%.2f MHz/V\n\tfc=%.2e Hz\n\tPhase Noise-Freq Pair=(%.2f dBc/Hz, %.2eHz)\n\tNoise Floor=%.2f dBc/Hz" %(self.name, self.F/1.0e9, self.KVCO/1.0e6, self.fc, self.pn, self.fpn, self.noise_floor))

	def tfunc(self,f):
		j=np.complex(0,1)
		w=2*math.pi*f
		s=j*w

		Kvco=2*math.pi*self.KVCO
		return Kvco/(j*w)

	def setName(self, name):
		self.name=name


	def setF(self,F):
		if (F<0):
			print "VCO oscillation frequency should be positive real number."
			print "VCO oscillation frequency will not be changed."
		else:
			self.F=F

	def setKVCO(self,KVCO):
		self.KVCO=KVCO

	def getF(self):
		return self.F

	def getKVCO(self):
		return self.KVCO

	def calc_pnoise_pwl(self, f):
		
		pn_vals=[]
		
		fc=self.fc
		pn=self.pn
		fpn=self.fpn


		ind_fst=searchF(fpn, f[0], 'greater-equal', 'first')
		ind_lst=searchF(fpn, f[len(f)-1],  'lower-equal', 'last')
		
		if (ind_lst<ind_fst):
			print "Error: VCO Calculate Phase Noise Method, PieceWise Approx."
			print "Unordered list of offset frequencies. Returning None."
			return None



		if (ind_fst>0 and ind_fst<len(fpn)):
			slope_fst=(pn[ind_fst]-pn[ind_fst-1])/log10(fpn[ind_fst]/fpn[ind_fst-1])
			pn_fst=pn[ind_fst-1]+slope_fst*log10(f[0]/fpn[ind_fst-1])
		else:
			if (fpn[ind_fst]<fc):
				slope_fst=-30.0
			else:
				slope_fst=-20.0
			if (ind_fst==0):
				pn_fst=pn[0]-slope_fst*log10(fpn[0]/f[0])
			else:
				pn_fst=pn[len(fpn)-1]+slope_fst*log10(f[0]/fpn[len(fpn)-1])				
			
		if (ind_lst>0 and ind_lst<len(fpn)-1):
			slope_lst=(pn[ind_lst]-pn[ind_lst-1])/log10(fpn[ind_lst]/fpn[ind_lst-1])
			#if (fpn[ind_lst]<fc):
			#	slope_lst=max(-30.0, slope_lst)
			#else:
			#	slope_lst=max(-20.0, slope_lst)

		else:
			if (fpn[ind_lst]<fc):
				slope_lst=-30.0
			else:
				slope_lst=-20.0

		
		
		
		
		fpn_ind=ind_fst
		pn_sec=pn_fst
		f_ind_sec=0
		slope=slope_fst


		f_ind=0
		while (f_ind<len(f)):
			if (f[f_ind]>fpn[fpn_ind]):
				pn_sec=pn_last
				f_ind_sec=f_ind-1
				
				if (fpn_ind==ind_lst):
					slope=slope_lst
				else:
					fpn_ind+=1
					slope=(pn[fpn_ind]-pn[fpn_ind-1])/log10(fpn[fpn_ind]/fpn[fpn_ind-1])

			pn_last=pn_sec+slope*log10(f[f_ind]/f[f_ind_sec])
			pn_vals.append(pn_last)
			f_ind+=1

		pn_vco=np.array(pn_vals)
		pn_vco=np.power(10.0, pn_vco/10.0)+np.power(10.0, self.noise_floor/10.0)
		pn_vco=10.0*np.log10(pn_vco)

		return pn_vco	
						
			
			

	def calc_pnoise_1p(self, f):
		"""fc - VCO pnoise corner frequency, where slope changes from -30 dB/dec(upconv. flicker noise) to -20 dB/dec (upconv. thermal noise), (pn, fpn) - tuple which defines one (pnoise[dBc/Hz], foffset[Hz]) known pair."""

		fc=self.fc
		pn=self.pn
		fpn=self.fpn
		
		
		if (fpn<fc):
			slope=-30
		else:
			slope=-20

		pn_fc=pn-slope*log10(fpn/fc)
		
		pn_vals=[]
		for fval in f:
			if (fval<fc):
				slope=-30
			else:
				slope=-20
			pn_vals.append(pn_fc+slope*log10(fval/fc))

		pn_vco=np.array(pn_vals)
		pn_vco=np.power(10.0, pn_vco/10.0)+np.power(10.0, self.noise_floor/10.0)
		pn_vco=10.0*np.log10(pn_vco)

		return pn_vco	

	def calc_pnoise(self,f):
		if (type(self.fpn) is list) and (type(self.pn) is list):
			return self.calc_pnoise_pwl(f)
		else:
			return self.calc_pnoise_1p(f)

class lms8001_vco(vco):
	def __init__(self, name='VCO_LMS8001IC', EM_MODEL=False, MEAS_FREQ=True, SEL=3, FREQ=128, VTUNE=0.6,  fc=200.0e3, (pn,fpn)=(-121, 1.0e6), noise_floor=-165.0):
		self.name=name
		SEL=lms8001_vco.checkCTRL(SEL, 'SEL', 0, 3)
		FREQ=lms8001_vco.checkCTRL(FREQ, 'FREQ', 0, 255)
		VTUNE=lms8001_vco.checkVTUNE(VTUNE, 'VTUNE', LMS8001_VTUNE_MIN, LMS8001_VTUNE_MAX)

		self.SEL=SEL
		self.FREQ=FREQ
		self.VTUNE=VTUNE

		script_dir=os.path.dirname(__file__)
		

		if not(EM_MODEL):
			VCOL_FILEPATH=os.path.join(script_dir, 'Data/VCOL_RCEXT.csv')
			VCOM_FILEPATH=os.path.join(script_dir, 'Data/VCOM_RCEXT.csv')
			VCOH_FILEPATH=os.path.join(script_dir, 'Data/VCOH_RCEXT.csv')
		else:
			if (MEAS_FREQ):
				VCOL_FILEPATH=os.path.join(script_dir, 'Data/VCOL_MEAS.csv')
				VCOM_FILEPATH=os.path.join(script_dir, 'Data/VCOM_MEAS.csv')
				VCOH_FILEPATH=os.path.join(script_dir, 'Data/VCOH_MEAS.csv')
			else:
				VCOL_FILEPATH=os.path.join(script_dir, 'Data/VCOL_RLCKEXT.csv')
				VCOM_FILEPATH=os.path.join(script_dir, 'Data/VCOM_RLCKEXT.csv')
				VCOH_FILEPATH=os.path.join(script_dir, 'Data/VCOH_RLCKEXT.csv')
		
		
		self.VCOL_DATA=(pnd.read_csv(VCOL_FILEPATH)).values
		self.VCOM_DATA=(pnd.read_csv(VCOM_FILEPATH)).values
		self.VCOH_DATA=(pnd.read_csv(VCOH_FILEPATH)).values
		
		self.setF(SEL, FREQ, VTUNE)

		
		if ((type(fc) is float) and (type(fpn) is float)) and (fc>0 and fpn>0):
			self.fc=fc
			self.pn=pn
			self.fpn=fpn

		elif (type(fc) is float) and ((type(fpn) is list) and (type(pn) is list)):
			print "Warning: List of offset frequencies should contain only positive real numbers."
			self.fc=fc
			self.pn=pn
			self.fpn=fpn

		else:
			print "Offset frequency and phase noise frequency should be positive real number(s) (scalar or list)."
			print "If a list of offset frequencies and corresponding phase noise values is used, they should have the same length."
			print "VCO object not created. Returning None."
			return None

		self.noise_floor=noise_floor

	@staticmethod
	def checkVTUNE(val, valname, val_min, val_max):
		if (val<val_min):
			print "Warning: VCO %s cannot go lower then %d. Minimum value will be used." % (valname, val_min)
			val=val_min
		elif (val>val_max):
			print "Warning: VCO %s cannot go higher then %d. Maximum value will be used." % (valname, val_max)
			val=val_max

		return val

	@staticmethod
	def checkCTRL(val, valname, val_min, val_max):
		val=floor(val)
		if (val<val_min):
			print "Warning: VCO digital control %s is considered as %d bit positive integer. Minimum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_min)
			val=val_min
		elif (val>val_max):
			print "Warning: VCO digital control %s is considered as %d bit positive integer. Maximum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_max)
			val=val_max

		return val
	
	def setNoise(self, fc, (pn, fpn), noise_floor=-165.0):
		if ((type(fc) is float) and (type(fpn) is float)) and (fc>0 and fpn>0):
			self.fc=fc
			self.pn=pn
			self.fpn=fpn
		elif (type(fc) is float) and ((type(fpn) is list) and (type(pn) is list)) and (len(pn)==len(fpn)) and (len(pn)==len(fpn)):
			print "Warning: List of offset frequencies should contain only positive real numbers."
			self.fc=fc
			self.pn=pn
			self.fpn=fpn
		else:
			print "Offset frequency and phase noise frequency should be positive real number(s) (scalar or list)."
			print "If a list of offset frequencies and corresponding phase noise values is used, they should have the same length."
			print "VCO object not created. Returning None."
			return None

		self.noise_floor=noise_floor

	def getVars(self, SEL,FREQ):
		if (SEL==0):
			self.F=0
			print "Warning: External LO Mode Configured. SEL of %s set to 0." % (self.name)
			return (0.0, 0.0, 0.0, 0.0, 0.0)

		else:
			
			if (SEL==1):
				VCO_DATA=self.VCOL_DATA	
			elif (SEL==2):
				VCO_DATA=self.VCOM_DATA
			else:
				VCO_DATA=self.VCOH_DATA
			F0=VCO_DATA[FREQ,1]
			P3=VCO_DATA[FREQ,2]
			P2=VCO_DATA[FREQ,3]
			P1=VCO_DATA[FREQ,4]
			P0=VCO_DATA[FREQ,5]
			return (F0,P3,P2,P1,P0)

	def calcF(self,SEL,FREQ,VTUNE):
		(F0,P3,P2,P1,P0)=self.getVars(SEL,FREQ)
		return F0*(P3*(VTUNE**3)+P2*(VTUNE**2)+P1*VTUNE+P0)

	def calcKVCO(self, SEL, FREQ, VTUNE):
		(F0,P3,P2,P1,P0)=self.getVars(SEL,FREQ)
		return F0*(3*P3*(VTUNE**2)+2*P2*VTUNE+P1)

	

	def setF(self, SEL, FREQ, VTUNE):
		SEL=lms8001_vco.checkCTRL(SEL, 'SEL', 0, 3)
		FREQ=lms8001_vco.checkCTRL(FREQ, 'FREQ', 0, 255)
		VTUNE=lms8001_vco.checkVTUNE(VTUNE, 'VTUNE', 0.0, 1.2)

		self.SEL=SEL
		self.FREQ=FREQ
		self.VTUNE=VTUNE
	
		
		self.F=self.calcF(SEL,FREQ,VTUNE)
		self.KVCO=self.calcKVCO(SEL,FREQ,VTUNE)

	def setKVCO(self, KVCO=0):
		print "Warning: %s Tuning Sensitivity is automatically calculated when defining (SEL,FREQ,VTUNE) parameters." % (self.name)
		print "Warning: KVCO attribute of %s will not be changed." % (self.name)

	def AUTO_CAL(self, F_TARGET, VTUNE_FIX=0.6, VTUNE_STEP=0.01, SEL_INIT=0):
		"""This method is used to find optimal VCO digital configuration (SEL and FREQ) and to estimate approx. VTUNE value for targeted VCO frequency of F_TARGET"""

		DF_BEST=100.0e9
		if (SEL_INIT==0):
			SEL_OPT=0
			SEL_LIST=range(1,4)
		else:
			SEL_INIT=lms8001_vco.checkCTRL(SEL_INIT, 'VCO_AUTO_CAL:SEL_INIT', 1, 3)
			SEL_OPT=SEL_INIT
			SEL_LIST=range(int(SEL_OPT),int(SEL_OPT)+1)
		FREQ_OPT=0
		VTUNE_OPT=VTUNE_FIX

		VTUNE_N=int(floor((LMS8001_VTUNE_MAX-LMS8001_VTUNE_MIN)*1.0/VTUNE_STEP))

		for SEL in SEL_LIST:
			for FREQ in range(0,256):
				F_ESTIM=self.calcF(SEL,FREQ,VTUNE_FIX)
				
				
				DF=abs(F_ESTIM-F_TARGET)

				if (DF<DF_BEST):
					DF_BEST=DF
					SEL_OPT=SEL
					FREQ_OPT=FREQ

		DF_BEST=100.0e9
		if (SEL_OPT>0):
			
			for i in range(0,VTUNE_N):
				VTUNE_VAL=LMS8001_VTUNE_MIN+i*VTUNE_STEP
				F_ESTIM=self.calcF(SEL_OPT,FREQ_OPT,VTUNE_VAL)
				DF=abs(F_ESTIM-F_TARGET)

				if (DF<DF_BEST):
					DF_BEST=DF
					VTUNE_OPT=VTUNE_VAL
		
		VCO_CONFIG={'SEL':SEL_OPT, 'FREQ':FREQ_OPT, 'VTUNE':VTUNE_OPT}
		return VCO_CONFIG

	def get_TCURVE(self, SEL, FREQ, VTUNE_STEP=0.05):
		SEL=lms8001_vco.checkCTRL(SEL, 'SEL', 0, 3)
		FREQ=lms8001_vco.checkCTRL(FREQ, 'FREQ', 0, 255)

		VTUNE_N=int(floor((LMS8001_VTUNE_MAX-LMS8001_VTUNE_MIN)*1.0/VTUNE_STEP))
		VTUNE_SWEEP=[]
		F_SWEEP=[]
		for i in range(0,VTUNE_N):
			VTUNE_VAL=LMS8001_VTUNE_MIN+i*VTUNE_STEP
			F_ESTIM=self.calcF(SEL,FREQ,VTUNE_VAL)
			VTUNE_SWEEP.append(VTUNE_VAL)
			F_SWEEP.append(F_ESTIM)

		return (np.array(VTUNE_SWEEP),np.array(F_SWEEP))

		
	
	def CTUNE_SEL(self, F_TARGET, SEL_FORCE=False, SEL_INIT=2, FREQ_MIN=5, FREQ_MAX=250, VTUNE_FIX=0.6):
		if (SEL_FORCE):
			return SEL_INIT
		else:
			if (self.calcF(2, FREQ_MIN, VTUNE_FIX)>F_TARGET):
				return 1
			elif (self.calcF(2, FREQ_MAX, VTUNE_FIX)<F_TARGET):
				return 3
			else:
				return 2


	def CTUNE_FREQ(self, F_TARGET, SEL, FREQ_FORCE=0, FREQ_INIT=128, FREQ_INIT_POS=7, VTUNE_FIX=0.6, VTUNE_STEP=0.01):
		SEL=lms8001_vco.checkCTRL(SEL, 'SEL', 1, 3)
		FREQ_INIT=lms8001_vco.checkCTRL(FREQ_INIT, 'FREQ_INIT', 0, 255)
		FREQ_INIT_POS=lms8001_vco.checkCTRL(FREQ_INIT_POS, 'FREQ_INIT_POS', 0, 7)
		VTUNE_FIX=lms8001_vco.checkVTUNE(VTUNE_FIX, 'VTUNE_FIX', LMS8001_VTUNE_MIN, LMS8001_VTUNE_MAX)
		VTUNE_N=int(floor((LMS8001_VTUNE_MAX-LMS8001_VTUNE_MIN)*1.0/VTUNE_STEP))

		if not (FREQ_FORCE):
			FREQ_INIT_POS=7
			FREQ_POS=FREQ_INIT_POS
			FREQ_CURRENT=int(pow(2,FREQ_INIT_POS))			
					
		else:
			FREQ_POS=FREQ_INIT_POS
			i=7
			FREQ_MASK=0
			while (i>=FREQ_POS):
				FREQ_MASK+=int(pow(2,i))
			FREQ_CURRENT=FREQ_INIT&FREQ_MASK

		while (FREQ_POS>=0):
			F_VAL=self.calcF(SEL, FREQ_CURRENT, VTUNE_FIX)

			FREQ_HIGH=(F_VAL>F_TARGET)
			#print 'FREQ_CURRENT= %d , FREQ_HIGH= %d' % (FREQ_CURRENT, FREQ_HIGH)
			FREQ_EQUAL=(F_VAL==F_TARGET)
			FREQ_LOW=(F_VAL<F_TARGET)
				
			FREQ_MASK=0
			i=7
			while (i>FREQ_POS):
				FREQ_MASK+=int(pow(2,i))
				i=i-1
			if not (FREQ_HIGH):
				FREQ_MASK+=int(pow(2,FREQ_POS))
				
			FREQ_CURRENT=FREQ_CURRENT&FREQ_MASK
			FREQ_POS-=1
			if (FREQ_POS>=0):
				FREQ_CURRENT+=int(pow(2,FREQ_POS))
			

		FREQ_OPT=FREQ_CURRENT
		DF_BEST=100.0e9
			
		for i in range(0,VTUNE_N):
			VTUNE_VAL=LMS8001_VTUNE_MIN+i*VTUNE_STEP
			F_ESTIM=self.calcF(SEL,FREQ_OPT,VTUNE_VAL)
			DF=abs(F_ESTIM-F_TARGET)

			if (DF<DF_BEST):
				DF_BEST=DF
				VTUNE_OPT=VTUNE_VAL

		return (FREQ_OPT, VTUNE_OPT)

	def CTUNE(self, F_TARGET, SEL_FORCE=False, SEL_INIT=2, FREQ_FORCE=False, FREQ_INIT=128, FREQ_INIT_POS=7, FREQ_MIN=5, FREQ_MAX=250, VTUNE_FIX=0.6, VTUNE_STEP=0.01):
		SEL_OPT=self.CTUNE_SEL(F_TARGET, SEL_FORCE, SEL_INIT, FREQ_MIN, FREQ_MAX, VTUNE_FIX)
		(FREQ_OPT, VTUNE_OPT)=self.CTUNE_FREQ(F_TARGET, SEL_OPT, FREQ_FORCE, FREQ_INIT, FREQ_INIT_POS, VTUNE_FIX, VTUNE_STEP)
		VCO_CONFIG={'SEL':SEL_OPT, 'FREQ':FREQ_OPT, 'VTUNE':VTUNE_OPT}
		return VCO_CONFIG

		
		


	def __str__(self):
		
		pn_str='['

		if ((type(self.fpn) is list) and (type(self.pn) is list)):
			for i in range(0,len(self.fpn)-1):
				pn_str+='(%.2f dBc/Hz, %.2eHz), ' % (self.pn[i], self.fpn[i])
			pn_str+='(%.2f dBc/Hz, %.2eHz)' % (self.pn[len(self.fpn)-1], self.fpn[len(self.fpn)-1])
		else:
			pn_str='(%.2f dBc/Hz, %.2eHz)]' % (self.pn, self.fpn)

		#return ("VCO class instance\n\tInst.Name= %s\n\tF=%.4f GHZ (SEL= %d, FREQ= %d, VTUNE= %.2f V)\n\tKVCO=%.2f MHz/V\n\tfc=%.2e Hz\n\tPhase Noise-Freq Pair=(%.2f dBc/Hz, %.2eHz)" %(self.name, self.F/1.0e9, self.SEL, self.FREQ, self.VTUNE, self.KVCO/1.0e6, self.fc, self.pn, self.fpn))

		return ("VCO class instance\n\tInst.Name= %s\n\tF=%.4f GHZ (SEL= %d, FREQ= %d, VTUNE= %.3f V)\n\tKVCO=%.2f MHz/V\n\tfc=%.2e Hz\n\tPhase Noise vs. Freq=%s\n\tNoise Floor=%.2f dBc/Hz" %(self.name, self.F/1.0e9, self.SEL, self.FREQ, self.VTUNE, self.KVCO/1.0e6, self.fc, pn_str, self.noise_floor))

	
		
