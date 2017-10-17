
widget_types=['checkbutton_var', 'radiobutton_var', 'entry', 'combo', 'var']

class GUI_Element(object):

	def __init__(self, e, name, widget):
		
		self.widget_types=widget_types
	
		if not widget in self.widget_types:
			print 'GUI_Element Class: Unsupported type of widget.'
			print 'GUI Element Class: Supported Types: ', widget_types
			
		self.element=e
		self.name=name
		self.wtype=widget
	
		self.widget_types=widget_types
		#self.elem_dict={}
		#for w in widget_types:
		#	self.elem_dict[w]=[]

	def setVal(self, val):
		if self.wtype=='entry':
			state=self.element.cget('state')
			self.element.config(state='enabled')
			self.element.delete(0, 'end')
			self.element.insert('end', str(val).strip())
			self.element.config(state=state)
		elif self.wtype=='combo':
			self.element.current(int(val))
		elif self.wtype=='checkbutton_var':
			self.element.set(int(val))
		elif self.wtype=='radiobutton_var':
			self.element.set(int(val))
		elif self.wtype=='var':
			#print type(self.element)
			self.element.set(val)
	
	def getVal(self):
		if self.wtype=='entry':
			return self.element.get()
		elif self.wtype=='combo':
			return self.element.current()
		elif self.wtype=='checkbutton_var':
			return int(self.element.get())
		elif self.wtype=='radiobutton_var':
			return int(self.element.get())
		elif self.wtype=='var':
			return self.element.get()

class GUI_ElemList(object):
	def __init__(self):

		self.widget_types=widget_types

		self.elem_dict={}
		for w in widget_types:
			self.elem_dict[w]=[]

	def addElem(self, GUI_elem):
		self.elem_dict[GUI_elem.wtype].append(GUI_elem)
	
	def add(self, e, name, widget):
		GUI_elem=GUI_Element(e, name, widget)
		self.addElem(GUI_elem)

	def get_GUIelem_byName(self, name):
		for k in self.elem_dict.keys():
			for e in self.elem_dict[k]:
				if (e.name==name):
					return e
		return None
	
	def get_GUIelem_byNameType(self, name, wtype):
		if not wtype in self.elem_dict.keys():
			return None
		for e in self.elem_dict[wtype]:
			if (e.name==name):
				return e
		return None

	def get_elemList_ofType(self, wtype):
		if not (wtype in self.widget_types):
			return None
		return self.elem_dict[wtype]
		
