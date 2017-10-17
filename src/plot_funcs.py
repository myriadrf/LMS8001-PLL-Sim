import matplotlib
matplotlib.use("TkAgg")
import sys
import os
#from cppsimdata import *

from pylab import *
import matplotlib.pyplot as plt

# Setup for TEX
#rc('text', usetex=True)

#fig_width_pt = 550  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0/72.27               # Convert pt to inch
#golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
#fig_width = fig_width_pt*inches_per_pt  # width in inches
#fig_height = fig_width*golden_mean      # height in inches
#fig_size =  [fig_width,fig_height]
#params = {'backend': 'ps',
#            'axes.labelsize': 12,
#            'text.fontsize': 12,
#            'legend.fontsize': 12,
#            'xtick.labelsize': 12,
#            'ytick.labelsize': 12,
#            'text.usetex': True,
#            'figure.figsize': fig_size}
fig_width_pt = 550  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean      # height in inches
fig_size =  [fig_width,fig_height]
params = {'figure.figsize': fig_size}
rcParams.update(params)



#from matplotlib import style
#print style.available
#[u'seaborn-darkgrid', u'seaborn-notebook', u'classic', u'seaborn-ticks', u'grayscale', u'bmh', u'seaborn-talk', u'dark_background', u'ggplot', u'fivethirtyeight', u'seaborn-colorblind', u'seaborn-deep', u'seaborn-whitegrid', u'seaborn-bright', u'seaborn-poster', u'seaborn-muted', u'seaborn-paper', u'seaborn-white', u'seaborn-pastel', u'seaborn-dark', u'seaborn-dark-palette']

#style.use("seaborn-dark")
from scipy.signal import lfilter, welch



#default_fontname='Linux Biolinum O'
#default_fontname='Times New Roman'
if (sys.platform=='win32'):
	default_fontname='Segoe UI'
else:
	default_fontname='CMU Serif'


#font = {'family' : 'normal',
#        'weight' : 'bold',
#        'size'   : 22}

font = {'family' : default_fontname}

matplotlib.rc('font', **font)

# calculate phase noise: returns frequency (Hz) and specral density (dBc/Hz)
def phasenoise(noiseout, Ts, fft_len):
   Kv = 1.0
   phase = lfilter([Ts*2*np.pi*Kv],[1,-1],noiseout-np.mean(noiseout))
   f, Pxx = welch(phase,1/Ts,'hanning',fft_len, None, None, 'constant', False, 'density',-1)
   Pxx_db = 10.0*np.log10(Pxx)
   return f, Pxx_db


def searchF(f, fval, mode='lower-equal', order='first'):
	"""Mode='lower-equal' - Method finds 'first' or 'last' (dep. on order arg.) element that is lower or equal to fval
	   Mode='greater-equal' - Method finds 'first' or 'last' (dep. on order arg.) element that is greater or equal to fval	"""

	ind_list=range(0, len(f))
	ind_list_rev=ind_list[:]	
	ind_list_rev.reverse()
		
	if (order not in ['first', 'last']):
		print "Bad order argument. Supported values are 'first' and 'last' for this argument."
		print "Returning -1."
		return -1

	if (mode not in ['lower-equal', 'greater-equal']):
		print "Bad mode argument. Supported values are 'lower-equal' and 'greater-equal' for this argument."
		print "Returning -1."
		return -1

	if (order=='first'):
		for ind_val in ind_list:
			if (mode=='lower-equal'):
				if (f[ind_val]<=fval):
					return ind_val
			else:
				if (f[ind_val]>=fval):
					return ind_val
		return len(f)

	else:
		for ind_val in ind_list_rev:
			if (mode=='lower-equal'):
				if (f[ind_val]<=fval):
					return ind_val
			else:
				if (f[ind_val]>=fval):
					return ind_val
		return -1


def find_1st_xind(elem, l):
	"""Finds the index of first element that is lower or equal then the targeted value. List needs to be sorted-ascending order."""
	i=0
	for u in l:
		if u>elem:
			if (i>0):
				return i-1
			else:
				return 0
		i+=1
	return -1
 


def setaxis(fignum, xmin, xmax, ymin, ymax):
	figure(fignum)
	plt.axis([xmin, xmax, ymin, ymax])


def setmarkers(fignum, xvals, x, y, xunit, yunit, text_format=('%.2e', '%.2e'),mstyle='o', fxy=(0.01, 0.05), fcolor='red', ecolor='black', arrowcolor='black', anncolor='black', msize=50, font_name=default_fontname, font_size='small'):
	xind=[]	
	for xelem in xvals:
		ind=find_1st_xind(xelem, x)
		if (ind>=0):
			xind.append(ind)

	figure(fignum)
	scatter(x[xind], y[xind], s=msize, marker=mstyle, facecolor=fcolor, edgecolor=ecolor)
	dx=fxy[0]*(max(x)-min(x))

	dy=fxy[1]*(max(y)-min(y))	

	for i in xind:
		marker_text='('+ text_format[0] % x[i]+ ' ' + xunit + ', ' + text_format[1] % y[i] + ' ' + yunit +')'
		plt.annotate(marker_text, xy=(x[i],y[i]), xytext=(x[i]+dx,y[i]+dy), xycoords='data', arrowprops=dict(arrowstyle='->', color=arrowcolor), family=font_name, fontsize=font_size, color=anncolor)


def setmarkers2(fignum, xvals, x, y, xunit, yunit, yaxis='left', text_format=('%.2e', '%.2e'), mstyle='o', fxy=(0.01, 0.05), fcolor='red', ecolor='black', arrowcolor='black', anncolor='black', msize=50, font_name=default_fontname, font_size='small'):
	xind=[]	
	
	for xelem in xvals:
		ind=find_1st_xind(xelem, x)
		if (ind>=0):
			xind.append(ind)

	fig=figure(fignum)
	#ax=fig.add_subplot(111)

	if (yaxis=='right'):
		ax=fig.axes[1]
	else:
		ax=fig.axes[0]
	
	ax.scatter(x[xind], y[xind], s=msize, marker=mstyle, facecolor=fcolor, edgecolor=ecolor)
	dx=fxy[0]*(max(x)-min(x))

	dy=fxy[1]*(max(y)-min(y))	

	for i in xind:
		marker_text='('+ text_format[0] % x[i]+ ' ' + xunit + ', ' + text_format[1] % y[i] + ' ' + yunit +')'
		ax.annotate(marker_text, xy=(x[i],y[i]), xytext=(x[i]+dx,y[i]+dy), xycoords='data', arrowprops=dict(arrowstyle='->', color=arrowcolor), family=font_name, fontsize=font_size, color=anncolor)


def setlegend(fignum, graph, text, loc='upper right', leg_loc='upper right',  font_name=default_fontname, font_size='small'):
	figure(fignum)
	#font_plot={'fontname':font_name}
	#matplotlib.rc('font',family=font_name)
	plt.legend(graph, text, loc=leg_loc, prop={'family':font_name, 'size':font_size}) 


def valid_dir(path):
	if not (os.path.isdir(path)):
		return False
        else:
		return True  

def show_plots():
	#plt.ion()	
	plt.show()
	#plt.show(block=False)
	#plt.ioff()
	#plt.show(0)
	#fig=plt.figure()
	#fig.canvas.manager.show()
	#plt.ioff()
	#plt.draw()
	#plt.show(block=False)
	#plt.ion()
	
def plotsig(x, y, fignum=1, xlabel='x-axis', ylabel='y-axis', title='Graph Title', line_width=2, line_color='black', grid_on=True, font_name=default_fontname):
	figure(fignum)
	font_plot={'fontname':font_name}
	graph=plot(x, y, color=line_color, linewidth=line_width)
	plt.xlabel(xlabel, **font_plot)
	plt.ylabel(ylabel, **font_plot)
	plt.grid(grid_on)
	plt.title(title, **font_plot)
	figure(fignum).canvas.set_window_title(title)
	return graph

def plotpnoise(f, pn, fignum=1, xlabel='Frequency Offset [Hz]', ylabel='Phase Noise [dBc/Hz]', title='Phase Noise - CppSim', line_width=2, line_color='black', grid_on=True, font_name=default_fontname):
	figure(fignum)
	font_plot={'fontname':font_name}
	graph=semilogx(f, pn, color=line_color, linewidth=line_width)
	plt.xlabel(xlabel, **font_plot)
	plt.ylabel(ylabel, **font_plot)
	plt.grid(grid_on)
	plt.title(title, **font_plot)
	figure(fignum).canvas.set_window_title(title)
	return graph

def plotlogx(x, y, fignum=1, xlabel='x-label', ylabel='y-label', title='Graph Title', line_width=2, line_color='black', grid_on=True, font_name=default_fontname):
	figure(fignum)
	font_plot={'fontname':font_name}
	graph=semilogx(x, y, color=line_color, linewidth=line_width)
	plt.xlabel(xlabel, **font_plot)
	plt.ylabel(ylabel, **font_plot)
	plt.grid(grid_on)
	plt.title(title, **font_plot)
	figure(fignum).canvas.set_window_title(title)
	return graph

def plotlogx2(x, y1, y2, fignum=1, xlabel='x-label', y1label='y1-label', y2label='y2-label', title='Graph Title', line_width=2, line1_color='black', line2_color='red', grid1_on=True, grid2_on=False, font_name=default_fontname):
	fig=figure(fignum)
	ax1=fig.add_subplot(111)
	font_plot={'fontname':font_name}
	graph1=ax1.semilogx(x, y1, color=line1_color, linewidth=line_width)
	ax1.set_xlabel(xlabel, **font_plot)
	ax1.set_ylabel(y1label, **font_plot)
	ax1.grid(grid1_on)
	ax1.spines['right'].set_color(line1_color)
	ax1.yaxis.label.set_color(line1_color)
	ax1.tick_params(axis='y', colors=line1_color)
	#ax.title(title, **font_plot)
	ax2=ax1.twinx()
	graph2=ax2.semilogx(x, y2, color=line2_color, linewidth=line_width)
	ax2.set_xlabel(xlabel, **font_plot)
	ax2.set_ylabel(y2label, **font_plot)
	ax2.grid(grid2_on)
	ax2.spines['right'].set_color(line2_color)
	ax2.yaxis.label.set_color(line2_color)
	ax2.tick_params(axis='y', colors=line2_color)
	plt.title(title, **font_plot)
	figure(fignum).canvas.set_window_title(title)
	return [graph1, graph2]


