from header import *

class lpf(object):
	def __init__(self, name='LPF', order=3):
		self.name=name
		if (order<4 and order>1):
			self.order=order
			self.C1=0
			self.C2=0
			self.C3=0
			self.R2=0
			self.R3=0
		else:
			print "Passive Loop Filter topologies with order 2 or 3 are only supported."
			print "LPF instance not created. Returning None."
			return None

	def __str__(self):
		return ("LPF class instance\n\tInst.Name= %s\n\torder=%d\n\tC1=%.2f [pF]\n\tC2=%.2f [pF]\n\tR2=%.2f [kOhm]\n\tC3=%.2f [pF]\n\tR3=%.2f [kOhm]" %(self.name, self.order, self.C1/1.0e-12, self.C2/1.0e-12, self.R2/1.0e3, self.C3/1.0e-12, self.R3/1.0e3)) 

	def negVal(self,s,val):
		print "LPF instance(Error):"
		print "\tTrying to set attribute %s to negative value %.2f" % (s,val)
		print "\tAction will not take place."

	def setName(self, name):
		self.name=name

	def getLPF_vals(self):
		d_LPF={'C1':self.C1, 'C2':self.C2, 'R2':self.R2, 'C3':self.C3, 'R3':self.R3, 'order':self.order}
		return d_LPF
	
			

	def setC1(self,C1):
		if (C1>0):
			self.C1=C1
		else:
			self.negVal('C1', C1)
	
	def setC2(self,C2):
		if (C2>0):
			self.C2=C2
		else:
			self.negVal('C2', C2)
		

	def setC3(self,C3):
		if (C3>=0):
			self.C3=C3
		else:
			self.negVal('C3', C3)
	
	def setR2(self,R2):
		if (R2>=0):
			self.R2=R2
		else:
			self.negVal('R2', R2)
	
	def setR3(self,R3):
		if (R3>=0):
			self.R3=R3
		else:
			self.negVal('R3',R3)

	def setLPF(self, C1, C2, R2, C3, R3, order=3):
		self.setC1(C1)
		self.setC2(C2)
		self.setC3(C3)
		self.setR2(R2)
		self.setR3(R3)
		self.setLPForder(order)

	def setLPForder(self,order):
		if (order>1 and order<4):
			self.order=order
		elif (order==1):
			print "Trying to set LPF order to 1. Only orders 2 and 3 are supported."
			print "Setting order to 2"
			self.order=2
		elif (order>3):
			print "Trying to set LPF order to value greater than 3. Only orders 2 and 3 are supported."
			print "Setting order to 3"
			self.order=3
		else:
			self.negVal('order', order)

	def tfunc_ADF4002_PCB(self,f):
		j=np.complex(0,1)
		w=2*math.pi*f
		s=j*w
		
		#R4=10.0e6		
		R4=5.0e100
		Z3=R4/(1.0+s*self.C3*R4)
		
		if (self.order==3):
			#Flp=(1+s*self.C2*self.R2)/((s**3)*self.C1*self.C2*Z3*self.R2*self.R3 + (s**2)*(self.C1*self.C2*self.R2+self.C1*Z3*self.R3+self.C2*Z3*self.R3+self.C2*Z3*self.R2)+s*(self.C1+self.C2+Z3))
			Flp=(1.0/(s*self.C1)*(self.R2+1.0/(s*self.C2))*(self.R3+Z3))/(1.0/(s*self.C1)*(self.R2+1.0/(s*self.C2)) + 1.0/(s*self.C1)*(self.R3+Z3) + (self.R2+1.0/(s*self.C2))*(self.R3+Z3))*Z3/(self.R3+Z3)
		elif (self.order==2):
			Flp=(1.0/(s*self.C1)*(self.R2+1.0/(s*self.C2))*(self.R3+Z3))/(1.0/(s*self.C1)*(self.R2+1.0/(s*self.C2)) + 1.0/(s*self.C1)*(self.R3+Z3) + (self.R2+1.0/(s*self.C2))*(self.R3+Z3))*Z3/(self.R3+Z3)
		else:
			Flp=np.ones((len(f),1))

		return Flp


	def tfunc(self,f):
		j=np.complex(0,1)
		w=2*math.pi*f
		s=j*w

		
		if (self.order==3 or self.order==2):
			Flp=(1+s*self.C2*self.R2)/((s**3)*self.C1*self.C2*self.C3*self.R2*self.R3 + (s**2)*(self.C1*self.C2*self.R2+self.C1*self.C3*self.R3+self.C2*self.C3*self.R3+self.C2*self.C3*self.R2)+s*(self.C1+self.C2+self.C3))
		else:
			Flp=np.ones((len(f),1))

		return Flp
		#return self.tfunc_ADF4002_PCB(f)

	def Vn(self, f, T=25):
		"""This method calculates thermal noise voltage density of PLL loop filter reffered to the output port. T is temperature in Celsius degrees."""
		j=np.complex(0,1)
		w=2*math.pi*f
		s=j*w
		
		kB=1.38e-23 # Boltzmann constant
		TEMP=273.15+T
		
		if (self.order==2):
    			vn_lpf_out=sqrt(4*kB*TEMP*self.R2)/(1+self.C1/self.C2+s*self.C1*self.R2);
		elif (self.order==3):
    			vr2n=sqrt(4*kB*TEMP*self.R2)*( (self.R3+1./(s*self.C3))*(1./(s*self.C1))/(self.R3+1./(s*self.C3)+1./(s*self.C1)) )/(self.R2+1./(s*self.C2)+(self.R3+1./(s*self.C3))*(1./(s*self.C1))/(self.R3+1./(s*self.C3)+1./(s*self.C1)))*(1./(s*self.C3))/(self.R3+1./(s*self.C3));
   			vr3n=sqrt(4*kB*TEMP*self.R3)*(1./(s*self.C3))/(self.R3+1./(s*self.C1)*(self.R2+1./(s*self.C2))/(self.R2+1./(s*self.C2)+1./(s*self.C1))+1./(s*self.C3));
    			vn_lpf_out=sqrt(abs(vr2n)**2+abs(vr3n)**2);  
		else:
			return None

		return vn_lpf_out


class lms8001_lpf(lpf):

	def __init__(self, name='LPF_LMS8001IC', C1_CTRL=8, C2_CTRL=8, R2_CTRL=1, C3_CTRL=8, R3_CTRL=1):
		self.name=name
		
		C1_CTRL=lms8001_lpf.checkCTRL(C1_CTRL, 'C1_CTRL')
		C2_CTRL=lms8001_lpf.checkCTRL(C2_CTRL, 'C2_CTRL')
		R2_CTRL=lms8001_lpf.checkCTRL(R2_CTRL, 'R2_CTRL')
		C3_CTRL=lms8001_lpf.checkCTRL(C3_CTRL, 'C3_CTRL')
		R3_CTRL=lms8001_lpf.checkCTRL(R3_CTRL, 'R3_CTRL')
		

		self.order=3
		self.C1_CTRL=C1_CTRL
		self.C2_CTRL=C2_CTRL
		self.C3_CTRL=C3_CTRL
		self.R2_CTRL=R2_CTRL
		self.R3_CTRL=R3_CTRL

		self.setLPF(C1_CTRL, C2_CTRL, R2_CTRL, C3_CTRL, R3_CTRL)

	def __str__(self):
		return ("LPF class instance\n\tInst.Name= %s\n\torder=%d\n\tC1=%.2f [pF] (%d)\n\tC2=%.2f [pF] (%d)\n\tR2=%.2f [kOhm] (%d)\n\tC3=%.2f [pF] (%d)\n\tR3=%.2f [kOhm] (%d)" %(self.name, self.order, self.C1/1.0e-12, self.C1_CTRL, self.C2/1.0e-12, self.C2_CTRL, self.R2/1.0e3, self.R2_CTRL, self.C3/1.0e-12, self.C3_CTRL, self.R3/1.0e3, self.R3_CTRL)) 

	@staticmethod
	def checkCTRL(val, valname):
		val=floor(val)
		if (val<0):
			print "Warning: LPF Digital Control is considered as 4b positive integer. Minumum value is 0." % (valname)
			val=0
		elif (val>15):
			print "Warning: LPF Digital Control is considered as 4b positive integer. Maximum value is 15." % (valname)
			val=15
		return val

	
	
	def setLPForder(self, order):
		self.order=3

	def calcC1(self,C1_CTRL):
		return LMS8001_C1_STEP*C1_CTRL
		
	def setC1(self, C1_CTRL):
		C1_CTRL=lms8001_lpf.checkCTRL(C1_CTRL, 'C1_CTRL')
		self.C1_CTRL=C1_CTRL
		self.C1=self.calcC1(C1_CTRL)

	def calcC2(self, C2_CTRL):
		return LMS8001_C2_FIX+LMS8001_C2_STEP*C2_CTRL

	def setC2(self, C2_CTRL):
		C2_CTRL=lms8001_lpf.checkCTRL(C2_CTRL, 'C2_CTRL')
		self.C2_CTRL=C2_CTRL
		self.C2=self.calcC2(C2_CTRL)

	def calcR2(self, R2_CTRL):
		if (R2_CTRL):
			return LMS8001_R2_0/R2_CTRL
		else:
			return 10.0e6

	def setR2(self, R2_CTRL):
		R2_CTRL=lms8001_lpf.checkCTRL(R2_CTRL, 'R2_CTRL')
		self.R2_CTRL=R2_CTRL
		self.R2=self.calcR2(R2_CTRL)
	
	def calcC3(self, C3_CTRL):
		return LMS8001_C3_FIX+LMS8001_C3_STEP*C3_CTRL
	
	def setC3(self, C3_CTRL):
		C3_CTRL=lms8001_lpf.checkCTRL(C3_CTRL, 'C3_CTRL')
		self.C3_CTRL=C3_CTRL
		self.C3=self.calcC3(C3_CTRL)

	def calcR3(self, R3_CTRL):
		if (R3_CTRL):
			return LMS8001_R3_0/R3_CTRL
		else:
			return 10.0e6

	def setR3(self, R3_CTRL):
		R3_CTRL=lms8001_lpf.checkCTRL(R3_CTRL, 'R3_CTRL')
		self.R3_CTRL=R3_CTRL
		self.R3=self.calcR3(R3_CTRL)

	def findCode(self, COMP_NAME, TARGET):
		"""Finds the optimum value of COMPONENT 'COMP_NAME' DIGITAL CODE for closest match to the targeted value 'TARGET' """ 
		MIN_ERR=1.0e20
		BEST_CODE=-1
		
		if (COMP_NAME=='C1'):
			m=self.calcC1
		elif (COMP_NAME=='C2'):
			m=self.calcC2
		elif (COMP_NAME=='R2'):
			m=self.calcR2
		elif (COMP_NAME=='C3'):
			m=self.calcC3
		elif (COMP_NAME=='R3'):
			m=self.calcR3
		else:
			print "Error: Wrong Name of the LMS8001 IC Loop Filter Component. Exiting. Returning -1."
			return BEST_CODE
		
		for CODE in range(0,16):
			ABS_ERR=abs(m(CODE)-TARGET)
			if (ABS_ERR<MIN_ERR):
				MIN_ERR=ABS_ERR
				BEST_CODE=CODE

		return BEST_CODE

	

	def optim(self, C1_TARGET, C2_TARGET, R2_TARGET, C3_TARGET, R3_TARGET):
		"""Finds the optimal configuration of PLL Loop Filter inside the LMS8001 IC, Arguments are targeted values of passive components (C1,C2,R2,C3,R3)""" 
		LPF_CONFIG=dict()		
		LPF_CONFIG['C1_CODE']=self.findCode('C1', C1_TARGET)
		LPF_CONFIG['C2_CODE']=self.findCode('C2', C2_TARGET)
		LPF_CONFIG['R2_CODE']=self.findCode('R2', R2_TARGET)
		LPF_CONFIG['C3_CODE']=self.findCode('C3', C3_TARGET)
		LPF_CONFIG['R3_CODE']=self.findCode('R3', R3_TARGET)
		return LPF_CONFIG

	
	
