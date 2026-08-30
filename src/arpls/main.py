import fitsio
import numpy as np
from copy import copy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mitigation import arpls_mask, st_mask, get_sm_kwargs, get_di_kwargs

def plot_subint(image, h, title, cmap):
	m,n = image.data.shape
	plt.figure()
	plt.imshow(image, aspect='auto', cmap=cmap)
	plt.xticks(np.arange(0, n, n//5), np.round(np.arange(0, h['TBIN']*(n+1), h['TBIN']*n/5), decimals=2))
	plt.yticks(np.arange(0, m, m//5), np.arange(0, 1600, 100)[::-1])
	plt.title(title)
	plt.xlabel('Time (s)')
	plt.ylabel('Frequency (MHz)')

if __name__ == '__main__':
	# read a 4096×1024 image from fits file
	fname = '../data/G69.04+0.00_tracking-M14_0040.fits'
	sub = 0
	hdu, h= fitsio.read(fname, header=True, rows=sub, ext=-1)
	data = hdu[0]['DATA'][:, 0, :, 0]
	data = data.T[::-1]

	plot_subint(data, h, 'Original image', 'hot')
	
	print('RFI flagging based on ArPLS-ST...')
	mask1 = arpls_mask(data)
	palette = copy(plt.cm.hot)
	palette.set_bad('cyan', 1.0)
	plot_subint(np.ma.array(data, mask=mask1), h, 'ArPLS-ST', palette)
	
	print('RFI flagging based on SumThreshold...')
	mask2 = st_mask(data, chi_1=20, sm_kwargs=get_sm_kwargs(80, 50, 10, 30), di_kwargs=get_di_kwargs(3, 3))
	plot_subint(np.ma.array(data, mask=mask2), h, 'SumThreshold', palette)
