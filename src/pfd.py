from header import *

class pfd(object):

	def __init__(self, name='PFD', pfdtype='tristate', rst_del=400.0e-12):
		self.name=name		
		if pfdtype in valid_pfd_types:
			self.pfdtype=pfdtype
		else:
			print "Wrong (Unsupported) PFD type."
			print "List of supported PFD types: "
			for s in valid_pfd_types:
				print ' '*10 + s
			print "PFD not created. Returning None."
			return None

		if (rst_del>0):
			self.rst_del=rst_del
		else:
			print "PFD reset path delay should be positive real number."
			print "PFD not created. Returning None"
			return None

	def __str__(self):
		return ("PFD class instance\n\tInst.Name= %s\n\tPFD type=%s\n\tReset Path Delay= %.2e s" % (self.name, self.pfdtype, self.rst_del))

	def setName(self, name):
		self.name=name

	def set_rst_del(self, rst_del):
		if (rst_del>0):
			self.rst_del=rst_del
		else:
			print "PFD reset path delay should be positive real number."
			print "PFD reset path delay not changed."


	def set_pfd_type(self, pfdtype):
		if pfdtype in valid_pfd_types:
			self.pfdtype=pfdtype
		else:
			print "Wrong (Unsupported) PFD type."
			print "List of supported PFD types: "
			for s in valid_pfd_types:
				print ' '*10 + s
			print "PFD type not changed."
			

	def get_rst_del(self):
		return self.rst_del

	def pfd_type(self):
		return self.pfdtype
	
	def tfunc_scalar(self):
		if (self.pfdtype=='tristate' or self.pfdtype=='tristate_dual_edge'):
			return 1.0/(2*math.pi)
		return None

	def tfunc(self,f):
		return 1.0/(2*math.pi)*np.ones((len(f),1))*np.complex(1,0)

class lms8001_pfd(pfd):
	
	def __init__(self, name='PFD_LMS8001IC', PFD_DEL=0, PFD_FLIP=0):
		self.name=name

		
		
		PFD_DEL=lms8001_pfd.checkCTRL(PFD_DEL, 'PFD_DEL', 0, 3)
		PFD_FLIP=lms8001_pfd.checkCTRL(PFD_FLIP, 'PFD_FLIP', 0, 3)
		
		self.PFD_DEL=PFD_DEL
		self.rst_del=400.0e-12+PFD_DEL*150e-12

		self.PFD_FLIP=PFD_FLIP
		self.pfdtype='tristate'


		
	@staticmethod
	def checkCTRL(val, valname, val_min, val_max):
		val=floor(val)
		if (val<val_min):
			print "Warning: PFD control word %s cannot be lower than %d. %s set to %d." % (valname, val_min,  valname, val_min)
			val=val_min
		elif (val>val_max):
			print "Warning: PFD control word %s cannot be higher than %d. %s set to %d." % (valname, val_max,  val_name, val_max)
			val=val_max
		return val

	def __str__(self):
		return ("PFD class instance\n\tInst.Name= %s\n\tPFD type=%s\n\tReset Path Delay= %.2e s\n\tPFD_DEL= %d\n\tPFD_FLIP= %d" % (self.name, self.pfdtype, self.rst_del, self.PFD_DEL, self.PFD_FLIP))
		
	
	def set_rst_del(self, PFD_DEL):
		PFD_DEL=lms8001_pfd.checkCTRL(PFD_DEL, 'PFD_DEL', 0, 3)
		self.PFD_DEL=PFD_DEL
		#self.rst_del=400.0e-12+PFD_DEL*150.0e-12
		self.rst_del=440.0e-12+PFD_DEL*50.0e-12
	
	def set_pfd_flip(self, PFD_FLIP):
		PFD_FLIP=lms8001_pfd.checkCTRL(PFD_FLIP, 'PFD_FLIP', 0, 3)
		self.PFD_FLIP=PFD_FLIP
	
	def tfunc_scalar(self):
		if (self.pfdtype=='tristate' or self.pfdtype=='tristate_dual_edge'):
			pfd_dir=-(2.0*self.PFD_FLIP-1.0)
			return pfd_dir/(2*math.pi)
		return None
	
	def tfunc(self,f):
		pfd_dir=-(2.0*self.PFD_FLIP-1.0)
		return pfd_dir/(2*math.pi)*np.ones((len(f),1))*np.complex(1,0)

	def set_pfd_type(self, pfdtype):
		print "LMS8001 IC has PLL with TRISTATE PFD. Object attribute WILL NOT be changed to %s." % (pfdtype)
		self.pfdtype='tristate'

