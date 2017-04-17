"""
Module for retrieving Az, El, data from dirfile
"""
import re
import os
import glob
import subprocess as sp
import numpy as np
import pygetdata as gd


# Someday fill this out better
dtypes = {
	gd.INT16: np.int16,
	gd.INT32: np.int32,
	gd.UINT32: np.uint32,
	gd.FLOAT32: np.float32,
	gd.FLOAT64: np.float64,
}

az_encoder = 'az_encoder_counts'
az_entry = 'AZ_DEGREES'
el_entry = 'EL_DEGREES'
hwp_encoder = 'hwp_encoder_counts'
fp_temp = 'FOCAL_PLANE'

def hk_frag_kludge(dirfile_path):
	"""
	Not proud of this.
	For some reason, cannot get nframes of dirfile
	while fragment is hanging around?
	Temporarily move dirfile's format file...
	"""
	sp.check_call(["cp", os.path.join(dirfile_path, "format"), os.path.join(dirfile_path, ".format")])
	orig_format_file = file(os.path.join(dirfile_path, '.format'), 'r')
	orig_format_lines = orig_format_file.readlines()
	orig_format_file.close()
	format_file = file(os.path.join(dirfile_path, 'format'), 'w')
	new_format_lines = filter(lambda L: not L.startswith("/INCLUDE"), orig_format_lines)
	format_file.writelines(new_format_lines)
	format_file.close()

def undo_hk_frag_kludge(dirfile_path):
	sp.check_call(["mv", os.path.join(dirfile_path, ".format"), os.path.join(dirfile_path, "format")])


def getdata_az_el(dirfile_path):
	"""
	Returns numpy array of shape
	(n_samples)
	of Az in degrees from dirfile_path.
	Az data is assumed to be of the
	form 
	"""
	hk_frag_kludge(dirfile_path)
	dirfile = gd.dirfile(dirfile_path, gd.RDONLY)
	gd_data_type = gd.FLOAT32
	gd_hwp_data_type = gd.UINT32
#	gd_fp_data_type = gd.UINT16
#	print dirfile.nframes
#	num_samples = dirfile.nframes * 400 #dirfile.entry(az_encoder).spf
#	print num_samples
#	print dirfile.entry(az_encoder).spf
#	print len(dirfile.getdata(az_entry, gd_data_type, num_frames=dirfile.nframes))
	num_samples=len(dirfile.getdata(az_entry, gd_data_type, num_frames=dirfile.nframes))
	
	data = np.zeros((4, num_samples), dtype=dtypes[gd_data_type])
#	try:
	data[0,:] = dirfile.getdata(az_entry, gd_data_type, num_frames=dirfile.nframes)
	data[1,:] = dirfile.getdata(el_entry, gd_data_type, num_frames=dirfile.nframes)
	data[2,:] = dirfile.getdata(hwp_encoder, gd_hwp_data_type, num_frames=dirfile.nframes)
	fp_temp_len=len(dirfile.getdata(fp_temp, gd_data_type, num_frames=dirfile.nframes))
	data[3,0:fp_temp_len] = dirfile.getdata(fp_temp, gd_data_type, num_frames=dirfile.nframes)
#	data[3,:] = dirfile.getdata(fp_temp, gd_data_type, num_frames=dirfile.nframes+1)
#		except IndexError:
#			print 'shape: ', np.shape(data)
#			print '(r,c) = (%i,%i)' % (r, c,)
#			raise IndexError
	undo_hk_frag_kludge(dirfile_path)
	return data


