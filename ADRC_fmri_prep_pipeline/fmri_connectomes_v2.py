# This code is imported from Jacques Stout's parallel repository
import os, socket, sys, glob, subprocess

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))

conda_env = os.environ.get("CONDA_DEFAULT_ENV")
run_code = True
if conda_env != "fmri_connectomes":
	print(f"Conda environment 'fmri_connectomes' not activated; running setup/activate script now...")
	run_code = False
	setup_cmd = f"bash {script_dir}/setup_fmri_connectomes_conda_env.bash {script_path}"
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

# Change as needed:
project = 'ADNI'
if run_code:
	