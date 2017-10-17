from header import *
from plot_funcs import searchF

class div(object):
	def __init__(self, name='FB-DIV', N=200.0, fpn=[1.0e3, 1.0e4, 1.0e5], pn=[-130.0, -140.0, -150.0], noise_floor=-165.0):
		self.name=name		
		if (N>0):
			self.N=N
		else:
			print "Division Modulus should be positive real number."
			print "Feedback divider instance not created. Returning none."
			return None

		if (sorted(fpn)==fpn and len(fpn)==len(pn)):
			self.fpn=fpn
			self.pn=pn
			self.noise_floor=noise_floor
		else:
			print "ERROR while creating the Feedback Divider Object."
			print "Feedback divider phase noise offset frequency list should contain only positive real numbers."
			print "List with offset frequency values and list with corresponding spot phase noise values should have equal length."
			print "Feedback divider instance not created. Returning None."
			return None

	def __str__(self):
		pn_str=''
		pn_str+='['
		for i in range(0, len(self.fpn)):
			pn_str+='(%.2f dBc/Hz @ %.2e Hz)' % (self.pn[i], self.fpn[i])
			if (i<len(self.fpn)-1):
				pn_str+=', '
			else:
				pn_str+=']'

		
		return ("FB Divider class instance\n\tInst.Name= %s\n\tN=%.2f\n\tPhase Noise vs. Freq= %s\n\tNoise Floor=%.2f dBc/Hz" % (self.name, self.N, pn_str, self.noise_floor))

	def setNoise(self, fpn, pn, noise_floor):
		if (sorted(fpn)==fpn and len(fpn)==len(pn)):
			self.fpn=fpn
			self.pn=pn
			self.noise_floor=noise_floor
		else:
			print "ERROR while defining Phase Noise performance of the Feedback Divider Object."
			print "Feedback divider phase noise offset frequency list should contain only positive real numbers."
			print "List with offset frequency values and list with corresponding spot phase noise values should have equal length."
			print "Feedback divider instance not created. Returning None."
			return None

	
	def setN(self, N):
		self.N=N

	def getN(self):
		return self.N

	def setName(self, name):
		self.name=name

	def tfunc(self, f):
		return 1.0/self.N*np.ones((len(f),1))
	
#	def calc_pnoise(self, f):
#		
#		fc=self.fc
#		slope=self.slope
#		noise_floor=self.noise_floor
#		
#		pn_vals=[]
#		for fval in f:
#			if (fval<=fc):
#				pn_vals.append(noise_floor+slope*log10(fval/fc))
#			else:
#				pn_vals.append(noise_floor)
#		return np.array(pn_vals)

	def calc_pnoise(self, f):
		"""Calculates phase noise characteristic of reference source. fpn-offset frequencies, ascending order, pn - phase noise values in dBc/Hz, noise_floor - Noise floor in dBc/Hz"""

		pn_vals=[]
		pn=self.pn
		fpn=self.fpn


		ind_fst=searchF(fpn, f[0], 'greater-equal', 'first')
		ind_lst=searchF(fpn, f[len(f)-1],  'lower-equal', 'last')
		
		if (ind_lst<ind_fst):
			print "ERROR while calculating Phase Noise of Feedback-Divider Object."
			print "Unordered list of offset frequencies. Returning None."
			return None



		if (ind_fst>0 and ind_fst<len(fpn)):
			slope_fst=(pn[ind_fst]-pn[ind_fst-1])/log10(fpn[ind_fst]/fpn[ind_fst-1])
			pn_fst=pn[ind_fst-1]+slope_fst*log10(f[0]/fpn[ind_fst-1])
		else:
			if (ind_fst==0):
				slope_fst=-10.0
				pn_fst=pn[0]+slope_fst*log10(f[0]/fpn[0])
			else:
				print "ERROR while calculating Phase Noise of Feedback-Divider."
				print "List of spot frequency not inside the desired span of offset frequencies for phase noise."
				print "Returning None."
				return None			
			
		if (ind_lst>0 and ind_lst<len(fpn)):
			slope_lst=(pn[ind_lst]-pn[ind_lst-1])/log10(fpn[ind_lst]/fpn[ind_lst-1])
		else:
			print "ERROR while calculating Phase Noise of Feedback-Divider."
			print "List of spot frequency not inside the desired span of offset frequencies for phase noise."
			print "Returning None."
			return None	

		
		
		
		
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





class lms8001_div(div):
	def __init__(self, name='FB-DIV_LMS8001IC', NDIV=200.0, PDIV2=0, fpn=[1.0e3, 1.0e4, 1.0e5], pn=[-130.0, -140.0, -150.0], noise_floor=-170):
		self.name=name	
		NDIV=lms8001_div.checkCTRL(NDIV, 'NDIV', 0, 1023)
		if (NDIV<56):
			print "Warning: Minimum Value of NDIV due to Pulse-Swallow Feedback Divider Architecture is 56."
			print "Warning: Results will not be valid."

		PDIV2=lms8001_div.checkCTRL(PDIV2, 'PDIV2', 0, 1, 1)
		
		self.PDIV2=PDIV2
		self.NDIV=NDIV		

		self.setN()		

		if (sorted(fpn)==fpn and len(fpn)==len(pn)):
			self.fpn=fpn
			self.pn=pn
			self.noise_floor=noise_floor
		else:
			print "ERROR while creating the Feedback Divider Object."
			print "Feedback divider phase noise offset frequency list should contain only positive real numbers."
			print "List with offset frequency values and list with corresponding spot phase noise values should have equal length."
			print "Feedback divider instance not created. Returning None."
			return None	

	@staticmethod
	def checkCTRL(val, valname, val_min, val_max, en_floor=0):
		if (en_floor):		
			val=floor(val)
		if (val<val_min):
			print "Warning: FB-DIV digital control %s is considered as %d bit positive integer. Minimum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_min)
			val=val_min
		elif (val>val_max):
			print "Warning: FB-DIV digital control %s is considered as %d bit positive integer. Maximum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_max)
			val=val_max

		return val

	def setN(self):
		self.N=self.NDIV*(2.0**self.PDIV2)

	def setNDIV(self,NDIV):
		NDIV=lms8001_div.checkCTRL(NDIV, 'NDIV', 0, 1023)
		if (NDIV<56):
			print "Warning: Minimum Value of NDIV due to Pulse-Swallow Feedback Divider Architecture is 56."
			print "Warning: Results will not be valid."
		self.NDIV=NDIV
		self.setN()

	def getNDIV(self):
		return self.NDIV

	def setPDIV2(self, PDIV2):
		PDIV2=lms8001_div.checkCTRL(PDIV2, 'PDIV2', 0, 1, 1)
		self.PDIV2=PDIV2
		self.setN()
	
	def getPDIV2(self):
		return self.PDIV2

	def getConfig(self):
		config=dict()
		config['PDIV2']=self.PDIV2
		NINT=floor(self.NDIV)
		NFRAC=(self.NDIV-NINT)*(2**20)
		P=floor(self.NDIV/8)
		S=self.NDIV-8*P
		if (NFRAC>0):
			SDM_MODE='ON'
		else:
			SDM_MODE='OFF'
		
		config['P']=P
		config['S']=S
		config['INT']=NINT
		config['FRAC']=NFRAC
		config['SDM_MODE']=SDM_MODE
		return config

	def __str__(self):
		CFG=self.getConfig()

		pn_str=''
		pn_str+='['
		for i in range(0, len(self.fpn)):
			pn_str+='(%.2f dBc/Hz @ %.2e Hz)' % (self.pn[i], self.fpn[i])
			if (i<len(self.fpn)-1):
				pn_str+=', '
			else:
				pn_str+=']'

		return ("FB Divider class instance\n\tInst.Name= %s\n\tN=%.2f (NDIV=%.2f, PDIV2=%d, INT=%d, FRAC=%d)\n\tP=%d, S=%d, SDM_MODE=%s\n\tPhase Noise vs. Freq= %s\n\tPhase Noise Floor=%.2f dBc/Hz" % (self.name, self.N, self.NDIV, self.PDIV2, CFG['INT'], CFG['FRAC'], CFG['P'], CFG['S'],  CFG['SDM_MODE'], pn_str, self.noise_floor))

