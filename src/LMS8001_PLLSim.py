from limepllconf_BASIC import *

def main():
	rootWindow=Tk()
			
	app=limepllconf(rootWindow)	
	rootWindow.resizable(0,0) # This removes maimize button from the main window	
	rootWindow.mainloop()


if (__name__=='__main__'):
	main()
