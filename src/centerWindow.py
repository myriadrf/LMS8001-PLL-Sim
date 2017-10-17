def center_Window(win, rootWin=False):
	sw = win.winfo_screenwidth()
	sh = win.winfo_screenheight()
	win.update()
	winW=win.winfo_width()
	winH=win.winfo_height()
		
	#x=int(round((sw-winW)/3.0))
	#y=int(round((sh-winH)/3.0))
	#win.geometry('%dx%d+%d+%d' % (winW, winH, x, y))
	if (rootWin):
		win.geometry('%dx%d+%d+%d' % (winW, winH, 0, 0.05*sh))
	else:
		MainWin_Pos=win.parent.parent.geometry()
		#print MainWin_Pos
		#print MainWin_Pos.split('x')
		x=int(MainWin_Pos.split('x')[1].split('+')[1])
		y=int(MainWin_Pos.split('x')[1].split('+')[2])
		win.geometry('%dx%d+%d+%d' % (winW, winH, x+win.parent.winW-winW, y))
		
	#win.update()


