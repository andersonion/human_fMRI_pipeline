# This code is imported from Jacques Stout's parallel repository
import os, socket, sys, glob, subprocess

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))

import shutil;
print(shutil.which("python"))
print(subprocess.getoutput("python -m pip list | grep nilearn"))

# Change as needed:
default_project = "ADNI"

subj = ''
if len(sys.argv) > 1:
	subj = (sys.argv[1])
if subj == '':
	raise ValueError(f"No subject specified; no work will be done. Quitting now...")

project = ''
if len(sys.argv) > 2:
	project = (sys.argv[2])
	
if project == '':
	print(f"No project specified; using default project: {default_project}")
	project = default_project

env_path = subprocess.check_output(
    "conda info --envs | grep fmri_connectomes | head -1 | tr -d '*' | tr -s ' '",
    shell=True,
    text=True
).strip()
conda_env = os.environ.get("CONDA_DEFAULT_ENV")
run_code = True
if conda_env != env_path:
	print(f"Conda environment 'fmri_connectomes' not activated; running setup/activate script now...")
	run_code = False
	setup_cmd = f"bash {script_dir}/setup_fmri_connectomes_conda_env.bash {script_path} {subj} {project}"
	subprocess.run(setup_cmd, shell=True, check=True)

import numpy as np
import nibabel as nib
import pandas as pd
from nibabel.processing import resample_to_output
from nilearn.input_data import NiftiLabelsMasker
from nilearn.interfaces.fmriprep import load_confounds
from nilearn.connectome import ConnectivityMeasure


def mkcdir(folderpaths, sftp=None):
    # creates new folder only if it doesnt already exists

    if sftp is None:
        if np.size(folderpaths) == 1:
            if not os.path.exists(folderpaths):
                os.mkdir(folderpaths)
        else:
            for folderpath in folderpaths:
                if not os.path.exists(folderpath):
                    os.mkdir(folderpath)
    else:
        if np.size(folderpaths) == 1:
            try:
                sftp.chdir(folderpaths)
            except:
                sftp.mkdir(folderpaths)
        else:
            for folderpath in folderpaths:
                try:
                    sftp.chdir(folderpath)
                except:
                    sftp.mkdir(folderpath)


def label_mask_inplace(label_nii,target_nii):
    label_aff = label_nii.affine
    target_aff = target_nii.affine
    new_shape = target_nii.shape

    label_data = label_nii.get_fdata()
    new_label_mat = np.zeros(new_shape[:3])

    x_coord = target_aff[0, 3]
    y_coord = target_aff[1, 3]
    z_coord = target_aff[2, 3]

    x_label = np.round((x_coord - label_aff[0, 3]) / label_aff[0, 0])
    y_label = np.round((y_coord - label_aff[1, 3]) / label_aff[1, 1])
    z_label = np.round((z_coord - label_aff[2, 3]) / label_aff[2, 2])

    for x in np.arange(new_shape[0]):
        y_coord = target_aff[1, 3]
        for y in np.arange(new_shape[1]):
            z_coord = target_aff[2, 3]
            for z in np.arange(new_shape[2]):

                """
                x_coord = x * target_aff[0, 0] + target_aff[0, 3]
                y_coord = y * target_aff[1, 1] + target_aff[1, 3]
                z_coord = z * target_aff[2, 2] + target_aff[2, 3]

                x_label = (x_coord-label_aff[0, 3])/label_aff[0, 0]
                y_label = (y_coord-label_aff[1, 3])/label_aff[1, 1]
                z_label = (z_coord-label_aff[2, 3])/label_aff[2, 2]
                """

                if x_label>=0 and y_label>=0 and z_label>=0:
                    new_label_mat[x,y,z] = int(np.round(label_data[int(x_label),int(y_label),int(z_label)]))

                z_coord += target_aff[2, 2]
                z_label = np.round((z_coord - label_aff[2, 3]) / label_aff[2, 2])

            y_coord += target_aff[1, 1]
            y_label = np.round((y_coord - label_aff[1, 3]) / label_aff[1, 1])

        x_coord+= target_aff[0,0]
        x_label = np.round((x_coord - label_aff[0, 3]) / label_aff[0, 0])

    return(new_label_mat)


def parcellated_matrix(sub_timeseries, atlas_idx, roi_list):
    timeseries_dict = {}
    for i in roi_list:
        roi_mask = np.asarray(atlas_idx == i, dtype=bool)
        timeseries_dict[i] = sub_timeseries[roi_mask].mean(axis=0)
        #print (i)
    roi_labels = list(timeseries_dict.keys())
    sub_timeseries_mean = []
    for roi in roi_labels:
        sub_timeseries_mean.append(timeseries_dict[roi])
        #print(sum(sub_timeseries_mean[int(roi)]==0))
    #corr_matrix = np.corrcoef(sub_timeseries_mean)
    return sub_timeseries_mean


def parcellated_FC_matrix(sub_timeseries, atlas_idx, roi_list):
    timeseries_dict = {}
    for i in roi_list:
        roi_mask = np.asarray(atlas_idx == i, dtype=bool)
        timeseries_dict[i] = sub_timeseries[roi_mask].mean(axis=0)
        #print (i)
    roi_labels = list(timeseries_dict.keys())
    sub_timeseries_mean = []
    for roi in roi_labels:
        sub_timeseries_mean.append(timeseries_dict[roi])
        #print(sum(sub_timeseries_mean[int(roi)]==0))
    corr_matrix = np.corrcoef(sub_timeseries_mean)
    return corr_matrix


def round_label(label_path,label_outpath=None):
    if isinstance(label_path,str):
        label_nii = nib.load(label_path)
    else:
        label_nii = label_path

    label_val = label_nii.get_fdata()

    label_val_round = np.array([
        [
            [int(round(item)) if isinstance(item, float) else item for item in row]
            for row in plane
        ]
        for plane in label_val
    ])

    if label_outpath is None:
        if isinstance(label_path,str):
            label_outpath = label_path
        else:
            raise Exception('Need a nifti path')

    img_nii_new = nib.Nifti1Image(label_val_round, label_nii.affine, label_nii.header)
    nib.save(img_nii_new,label_outpath)


def all_integers(lst):
    return all(isinstance(x, int) or (isinstance(x, float) and x.is_integer()) for x in lst)


if run_code:

	import shutil;
	print(shutil.which("python"))
	print("nilearn test = " + subprocess.getoutput("python -m pip list | grep nilearn 2>/dev/null | wc -l"))



	# Make sure important paths exist and are set:
	try :
		BD = os.environ['BIGGUS_DISKUS']
			# Force to be human if set to mouse:
		BD = BD.replace('/mouse','/human') 
	#os.environ['GIT_PAGER']
	except KeyError:  
		print('BD not found locally')
		BD = '***/human'    
		#BD ='***/example'
	else:
		print("BD is found locally.")
		BD=os.path.abspath(f"{BD}/../human/")
	
	try :
		GD = os.environ['GUNNIES']   
	
	except KeyError:  
		print('GUNNIES not found locally')   
		GD = '/mnt/clustertmp/common/rja20_dev/gunnies/'
	else:
		print("GUNNIES is found locally.")
	
	WORK = os.environ['WORK']
	
	
	qial_hosts = [ 'kea' , 'kos', 'andros' , 'crete', 'kythira', 'patmos']
	host=socket.gethostname().split('.')[0]
	
	
	if host=='santorini':
		root = '/Volumes/Data/Badea/Lab/'
		root_proj = '/Volumes/Data/Badea/Lab/human/ADRC/'
	elif host in qial_hosts: 
		root = f'{WORK}/'
		root_proj = f'{BD}/{project}/'
	else:
		root = '/mnt/munin2/Badea/Lab/'
		root_proj = '/mnt/munin2/Badea/Lab/human/ADRC/'
	
	data_path = f'{BD}/{project}/fmriprep_output'
	SAMBA_path_results_prefix = f'{BD}/diffusion_prep_MRtrix_'
	

	
	fmriprep_output = os.path.join(root_proj,'fmriprep_output')
	conn_path = os.path.join(root_proj, 'connectomes')
	func_conn_path = os.path.join(conn_path,'functional_conn')
	
	
	slice_func = False #Do you want to split the functionnal time series into just the first three hundred points
	check_label = True
	
	overwrite=False
	
	
	## Begin subject-specific work (previously this was inside a subject loop)
	subj_strip = subj.replace('sub-',"")
	subj_path = os.path.join(fmriprep_output, f'sub-{subj_strip}')
	fmri_path = os.path.join(subj_path,'func',f'sub-{subj_strip}_task-rest_space-T1w_desc-preproc_bold.nii.gz')
	print(fmri_path)
	if not os.path.exists(fmri_path):
		txt = (f'Could not find the fmri for subject {subj_strip}')
		raise FileNotFoundError(txt)
		

	flabel = os.path.join(conn_path, subj + '_new_labels_resampled.nii.gz')
	new_label = os.path.join(conn_path, subj + '_new_labels.nii.gz')
	
	subj_temp = subj_strip
	if '_y' not in subj_temp:
		subj_temp = subj_temp.replace('y','_y')

	mkcdir(func_conn_path)
	fmri_nii=nib.load(fmri_path)

	time_serts_path = os.path.join(func_conn_path, f'time_series_{subj_temp}.csv')
	time_FC_path = os.path.join(func_conn_path,f'func_connectome_corr_{subj_temp}.csv')
	time_FCvar_path = os.path.join(func_conn_path,f'func_connectome_covar_{subj_temp}.csv')

	print(f'Running functional connectomes for subject {subj_strip}')

	if not os.path.exists(flabel) or overwrite:
		if not os.path.exists(new_label) or overwrite:
			label_path = os.path.join(SAMBA_path_results_prefix + subj_temp, subj_temp + '_IITmean_RPI_labels.nii.gz')
			label_nii = nib.load(label_path)
			labels_data = label_nii.get_fdata()
			labels = np.unique(labels_data)
			labels = np.delete(labels, 0)
			label_nii_order = labels_data * 0.0

			path_atlas_legend = os.path.join(root, 'atlases', 'IITmean_RPI', 'IITmean_RPI_index.xlsx')
			legend = pd.read_excel(path_atlas_legend)
			new_label = os.path.join(conn_path, subj + '_new_labels.nii.gz')

			# index_csf = legend [ 'Subdivisions_7' ] == '8_CSF'
			# index_wm = legend [ 'Subdivisions_7' ] == '7_whitematter'
			# vol_index_csf = legend[index_csf]

			for i in labels:
				leg_index = np.where(legend['index2'] == i)
				leg_index = leg_index[0][0]
				ordered_num = legend['index'][leg_index]
				label3d_index = np.where(labels_data == i)
				label_nii_order[label3d_index] = ordered_num

			file_result = nib.Nifti1Image(label_nii_order, label_nii.affine, label_nii.header)
			new_label = os.path.join(conn_path, subj + '_new_labels.nii.gz')
			nib.save(file_result, new_label)

	label_nii=nib.load(new_label)

	if not all_integers(np.unique(label_nii.get_fdata())):
		round_label(new_label)
		label_nii=nib.load(new_label)

	masker = NiftiLabelsMasker(
		labels_img=label_nii,
		standardize="zscore_sample",
		standardize_confounds="zscore_sample",
		memory="nilearn_cache",
		verbose=5,
	)

	# Extract the time series
	confounds, sample_mask = load_confounds(fmri_path, strategy=["motion", "wm_csf"], motion="basic")

	time_series = masker.fit_transform(fmri_nii, confounds=confounds, sample_mask=sample_mask)

	if not os.path.exists(time_serts_path) or overwrite:
		if os.path.exists(time_serts_path):
			os.remove(time_serts_path)
		np.savetxt(time_serts_path, time_series, delimiter=',', fmt='%s')

	correlation_measure = ConnectivityMeasure(
		kind="correlation",
		standardize="zscore_sample",
	)

	covar_measure = ConnectivityMeasure(
		kind="covariance",
		standardize="zscore_sample",
	)

	correlation_matrix = correlation_measure.fit_transform([time_series])[0]
	covar_matrix = covar_measure.fit_transform([time_series])[0]

	np.fill_diagonal(correlation_matrix, 0)

	if not os.path.exists(time_FC_path) or overwrite:
		if os.path.exists(time_FC_path):
			os.remove(time_FC_path)
		np.savetxt(time_FC_path, correlation_matrix, delimiter=',', fmt='%s')

	if not os.path.exists(time_FCvar_path) or overwrite:
		if os.path.exists(time_FCvar_path):
			os.remove(time_FCvar_path)
		np.savetxt(time_FCvar_path, covar_matrix, delimiter=',', fmt='%s')
