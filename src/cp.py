from header import *

class cp(object):
	def __init__(self, name='CP', i=100.0e-6, fc=1.0e6, iup_noise=12.0e-12, idn_noise=6.6e-12, slope=-10):
		self.name=name
		if (i>=0):
			self.i=i;
		else:
			print "CP currentb must be positive real number."
			print "CP not created. Returning None."
			return None

		if (fc>0):
			self.fc=fc
			self.iup_noise=iup_noise
			self.idn_noise=idn_noise
			self.slope=slope
		else:
			print "CP noise corner frequency should be positive real number."
			print "CP not created. Returning None."
			return None

	
	def __str__(self):
		return ("CP class instance\n\tInst.Name= %s\n\tIcp= %.2f [uA]\n\tfc=%.2e\n\tIup_n=%.2e A/sqrt(Hz), Idn_n=%.2e A/sqrt(Hz)\n\tNoise slope vs. freq = %.2f dB/dec" % (self.name, self.i/1.0e-6, self.fc, self.iup_noise, self.idn_noise, self.slope))
	
	def setNoise(self, fc, iup_noise, idn_noise, slope):
		if (fc>0):
			self.fc=fc
			self.iup_noise=iup_noise
			self.idn_noise=idn_noise
			self.slope=slope
		else:
			print "CP noise corner frequency should be positive real number."
			print "CP noise parameters not changed."
			

	def setName(self, name):
		self.name=name

	def setI(self,i):
		if (i>=0):
			self.i=i;
		else:
			print "CP currentb must be positive real number."
			print "CP not created. Returning None."
			return None

	def getI(self):
		return self.i

	def tfunc(self,f):
		return self.i*np.ones((len(f),1))*np.complex(1,0)

	def In_floor(self, ks):
		iup_noise=self.iup_noise
		idn_noise=self.idn_noise
		return math.sqrt(iup_noise**2+idn_noise**2)*ks

	def In(self, f, ks):
		"""This method calculates pss current noise spectrum in A/sqrt(Hz) at CP output port. ks is multiplication constant due to sampling nature of PFD driving CP. ks=PFD.rst_del/Fref"""
		fc=self.fc
		slope=self.slope
		iup_noise=self.iup_noise
		idn_noise=self.idn_noise
		
		#in_floor=math.sqrt(iup_noise**2+idn_noise**2)*ks
		in_floor=self.In_floor(ks)
	
		In_cp=[]
		for fval in f:
			if fval<fc:
				In_val_log=20*log10(in_floor)+slope*log10(fval/fc)
				In_cp.append(10**(In_val_log/20.0))
			else:
				In_cp.append(in_floor)


		for i in range(0,len(In_cp)):
			In_cp[i]=math.sqrt(In_cp[i]**2+(self.In_white)**2)
			#In_val_log=20*log10(in_floor)+slope*log10(fval/fc)
		#	if (In_cp[i]<=4.4e-12):
		#		In_cp[i]=4.4e-12
		#	

		return np.array(In_cp)

		#return np.array(In_cp)+1.4e-12*2.6 # default
		# return np.array(In_cp)+2.4e-12 # this is simulation result without taking the supply noise from MIC37122 LDO taken into account

		#return np.array(In_cp)+4.424e-12 # with supply noise profile of MIC37122 LDO taken from datasheet, almost 6dB increase in CP noise-floor

		#return np.array(In_cp)*1

class lms8001_cp(cp):
	def __init__(self, name='CP_LMS8001IC', PULSE=4, OFS=0, ICT=16, fc=0.6e6, slope=-10, In_white=0.0):
		self.name=name
		PULSE=lms8001_cp.checkCTRL(PULSE, 'PULSE', 0, 63)
		OFS=lms8001_cp.checkCTRL(OFS, 'OFS', 0, 63)
		ICT=lms8001_cp.checkCTRL(ICT, 'ICT', 0, 31)
		
		self.PULSE=PULSE
		self.OFS=OFS
		self.ICT=ICT

		self.setIBIAS(ICT)

		
		

		#self.ibias=self.ICT*20.0e-6*5.0/4.0)
		#self.i=self.ibias*self.PULSE
		#self.iofs=self.ibias*self.OFS
		

		if (fc>0):
			self.fc=fc
			self.slope=slope
			self.In_white=abs(In_white)
		else:
			print "CP noise corner frequency should be positive real number."
			print "CP not created. Returning None."
			return None

	@staticmethod
	def checkCTRL(val, valname, val_min, val_max):
		val=floor(val)
		if (val<val_min):
			print "Warning: CP digital control %s is considered as %d bit positive integer. Minimum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_min)
			val=val_min
		elif (val>val_max):
			print "Warning: CP digital control %s is considered as %d bit positive integer. Maximum value is %d. This value will be used." % (valname, math.log10(val_max-val_min+1)/math.log10(2.0), val_max)
			val=val_max

		return val

	def setIBIAS(self, ICT):
		ICT=lms8001_cp.checkCTRL(ICT, 'ICT', 0, 31)
		self.ICT=ICT
		self.ibias=self.ICT/16.0*20.0e-6*5.0/4.0
		self.setI(self.PULSE)
		self.setIOFS(self.OFS)
		self.setIUP_NOISE()
		self.setIDN_NOISE()
		self.setIOFS_NOISE()
		
		

	def setI(self, PULSE):
		PULSE=lms8001_cp.checkCTRL(PULSE, 'PULSE', 0, 63)
		self.PULSE=PULSE
		self.i=self.ibias*self.PULSE
		self.setIUP_NOISE()
		self.setIDN_NOISE()
		self.setIOFS_NOISE()

	def setIOFS(self, OFS):
		OFS=lms8001_cp.checkCTRL(OFS, 'OFS', 0, 63)
		self.OFS=OFS
		self.iofs=self.ibias/4.0*self.OFS
		self.setIUP_NOISE()
		self.setIDN_NOISE()
		self.setIOFS_NOISE()

	def getIOFS(self):
		return self.iofs

	def setIUP_NOISE(self):
		if (self.PULSE>0):
			self.iup_noise=(-1.6772e-16*(self.PULSE)**3+8.3497e-15*(self.PULSE)**2+2.7810e-12*(self.PULSE)+1.7898e-12)*self.ICT*1.0/16.0
		else:
			self.iup_noise=0.0
		
	def getIUP_NOISE(self):
		return self.iup_noise
	
	def setIDN_NOISE(self):
		if (self.PULSE>0):
			self.idn_noise=(1.151e-17*(self.PULSE)**3-1.4306e-15*(self.PULSE)**2+1.2072e-12*(self.PULSE)+1.7036e-12)*self.ICT*1.0/16.0
		else:
			self.idn_noise=0.0


	def getIDN_NOISE(self):
		return self.idn_noise

	def setIOFS_NOISE(self):
		if (self.OFS>0):
			self.iofs_noise=(1.5238e-17*(self.OFS)**3-1.8788e-15*(self.OFS)**2+3.6971e-13*(self.OFS)+1.1317e-12)*self.ICT*1.0/16.0
		else:
			self.iofs_noise=0.0

	def getIOFS_NOISE(self):
		return self.iofs_noise

	def setNoise(self, fc, slope, In_white):
		if (fc>0):
			self.fc=fc
			self.slope=slope
			self.In_white=abs(In_white)
		else:
			print "CP noise corner frequency should be positive real number."
			print "CP noise parameters not changed."

	def In_floor(self, ks):
		iup_noise=self.iup_noise
		idn_noise=self.idn_noise
		iofs_noise=self.iofs_noise
		
		kup=self.iofs/self.i
		#return 1.0*math.sqrt(iup_noise**2*(1+kup**2)+idn_noise**2+iofs_noise**2)*ks
		return 1.0*math.sqrt(iup_noise**2*(1+kup**2)*ks**2+idn_noise**2*ks**2+iofs_noise**2)
	

	def __str__(self):
		return ("CP class instance\n\tInst.Name= %s\n\tIbias= %.2f uA, ICT=%d\n\tIcp= %.2f uA, PULSE=%d\n\tIofs= %.2f uA, OFS=%d\n\tfc=%.2e\n\tIup_n=%.2e A/sqrt(Hz), Idn_n=%.2e A/sqrt(Hz)\n\tIofs_n= %.2e A/sqrt(Hz)\n\tNoise slope vs. freq = %.2f dB/dec\n\tIn_white= %.2e A/sqrt(Hz)" % (self.name, self.ibias/1.0e-6, self.ICT, self.i/1.0e-6, self.PULSE, self.iofs/1.0e-6, self.OFS, self.fc, self.iup_noise, self.idn_noise, self.iofs_noise, self.slope, self.In_white))


	
	
