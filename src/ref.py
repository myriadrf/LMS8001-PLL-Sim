from header import *
from plot_funcs import searchF

class ref(object):
	"""Defines the reference frequency source"""

	def __init__(self, name='REF_SRC', Fref=40.0e6, output='square', fpn=[1.0e3, 10.0e3], pn=[-130, -140], noise_floor=-152.00):
		self.name=name
		if (Fref<=0):
			print "ERROR while creating Reference Source Object!!!!"
			print "Reference frequency should be real positive number."
			print "Reference source instance not generated. Returning None."
			return None
		else:
			self.Fref=Fref
		if output not in valid_ref_outputs:
			print "ERROR while creating Reference Source Object!!!!"
			print "Not valud reference output signaling type. Valid types are: ", valid_ref_outputs
			print "Reference source instance not generated. Returning None."
			return None

		else:
			self.output=output

		if (sorted(fpn)==fpn and len(fpn)==len(pn)):
			self.fpn=fpn
			self.pn=pn
			self.noise_floor=noise_floor
		else:
			print "ERROR while creating Reference Source Object!!!!"
			print "List of offset frequencies need to be sorted from the lower to higher values."
			print "Lists of offset frequencies and corresponding phase noise values should have the same length."
			print "Reference source instance not generated. Returning None."
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

		return 'Refence Source Class Instance\n\tInst.Name= %s\n\tFref=%.2f MHz\n\t%s wave output\n\tPhase Noise vs. Freq= %s\n\tNoise Floor= %.2f dBc/Hz' % (self.name, self.Fref/1.0e6, self.output, pn_str, self.noise_floor)

	def setNoise(self, fpn, pn, noise_floor):
		if (sorted(fpn)==fpn and len(fpn)==len(pn)):
			self.fpn=fpn
			self.pn=pn
			self.noise_floor=noise_floor
		else:
			print "ERROR while defining the phase noise profile of Reference Source."
			print "List of fc frequencies need to be sorted from lower to higher values."
			print "Reference source noise parameters not changed!!!"


	def setName(self,name):
		self.name=name
	
	def setFref(self, Fref):
		if (Fref<=0):
			print "Reference frequency should be real positive number."
			print "Reference source instance not updated"
		else:
			self.Fref=Fref

	def setOutput(self, output):
		if output not in valid_ref_outputs:
			print "Not valud reference output signaling type. Valid types are: ", valid_ref_outputs
			print "Reference source instance not updated."

		else:
			self.output=output

	def getFref(self):
		return self.Fref

	def getName(self):
		return self.name

	def getOutput(self):
		return self.output




	def calc_pnoise(self, f):
		"""Calculates phase noise characteristic of reference source. fc-corner frequencies, ascending order, slope - phase noise slopes bellow fc-s, between flicker (-10 dB/dec) and thermal noise_floor [dBc/Hz]"""

		pn_vals=[]
		pn=self.pn
		fpn=self.fpn


		ind_fst=searchF(fpn, f[0], 'greater-equal', 'first')
		ind_lst=searchF(fpn, f[len(f)-1],  'lower-equal', 'last')
		
		if (ind_lst<ind_fst):
			print "ERROR while calculating Phase Noise of Reference  Source."
			print "Unordered list of offset frequencies. Returning None."
			return None



		if (ind_fst>0 and ind_fst<len(fpn)):
			slope_fst=(pn[ind_fst]-pn[ind_fst-1])/log10(fpn[ind_fst]/fpn[ind_fst-1])
			pn_fst=pn[ind_fst-1]+slope_fst*log10(f[0]/fpn[ind_fst-1])
		else:
			if (ind_fst==0):
				slope_fst=-30.0
				pn_fst=pn[0]+slope_fst*log10(f[0]/fpn[0])
			else:
				print "ERROR while calculating Phase Noise of Reference  Source."
				print "List of spot frequency not inside the desired span of offset frequencies for phase noise."
				print "Returning None."
				return None			
			
		if (ind_lst>0 and ind_lst<len(fpn)):
			slope_lst=(pn[ind_lst]-pn[ind_lst-1])/log10(fpn[ind_lst]/fpn[ind_lst-1])
		else:
			print "ERROR while calculating Phase Noise of Reference  Source Object."
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
