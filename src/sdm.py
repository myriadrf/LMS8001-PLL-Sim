from header import *

class sdm(object):
	"""Represents sigma-delta modulator, MASH topology."""
	def __init__(self, name='SDM', order=3, Nbit=20):
		self.name=name
		if (order<0):
			print "SDM order should be positive integer."
			print "SDM instance not created. Returning None."
			return None
		else:
			self.order=order
			self.zrepr='OUT(z)=IN(z)+(1-z^-1)^%d x Eq(z), Eq - quant. noise' %( self.order )


		if (Nbit<=0):
			print "SDM bit lenght should be positive real number."
			print "SDM instcance not created. Returning None."
			return None
		else:
			self.Nbit=Nbit

	def __str__(self):
		return "SDM Class Instance, MASH Topology\n\tInst.Name= %s\n\torder= %d\n\tNbit= %d\n\tZ-Domain TFunc, %s" % (self.name, self.order, self.Nbit, self.zrepr)

	def calc_inps(self, N):
		if (N>0):
			Nint=floor(N)
			Nfrac=(N-Nint)*(2**self.Nbit)
		else:
			return (0,0)
		
		return {'INT':Nint, 'FRAC':Nfrac}

	def setName(self, name):
		self.name=name

	def getName(self):
		return self.name
	
	def setOrder(self, order):
		if (order>0):
			self.order=order
			self.zrepr='OUT(z)=IN(z)+(1-z^-1)^%d x Eq(z), Eq - quant. noise' %( self.order )
		else:
			print "SDM order should be postive integer."
			print "SDM order will not be changed."

	def getOrder(self):
		return self.order

	def setNbit(self, Nbit):
		if (Nbit>0):
			self.Nbit=Nbit
		else:
			print "SDM bit length should be postive real number."
			print "SDM bit length will not be changded"

	def getNbit(self):
		return self.Nbit()

	
	def calc_pnoise(self, f, Fref):
		j=np.complex(0,1)
		He_mash111=np.abs((1-np.exp(-j*2*np.pi*f/Fref)))**(2*(self.order-1)); 
		phi_SD=np.sqrt(2*(2*np.pi)**2/(24*Fref)*He_mash111);
		pn_SD=[]
		for val in phi_SD:
			pn_SD.append(20*math.log10(val/sqrt(2)))
		return np.array(pn_SD)
