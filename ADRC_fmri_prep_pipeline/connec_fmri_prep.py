#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 12:29:36 2023

@author: ali
"""

import os, socket, sys
import numpy as np
import nibabel as nib
import pandas as pd
from nibabel.processing import resample_to_output
import os, socket
import numpy as np
import nibabel as nib
from nibabel.processing import resample_to_output




    
subj = (sys.argv[1])
#subj = 'ADRC0001'


#time series
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


flabel = os.path.join('/mnt/munin2/Badea/Lab/human/ADRC/new_labels/', subj + '_new_labels_resampled.nii.gz')
new_label = os.path.join(  '/mnt/munin2//Badea/Lab/human/ADRC/new_labels/' ,  subj +  '.nii.gz')


fmri_path = '/mnt/munin2/Badea/Lab/human/ADRC/fmriprep_output/sub-' + subj+'/func/sub-' + subj + '_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz'
fmri_nii=nib.load(fmri_path)

time_serts_path = os.path.join( '/mnt/munin2//Badea/Lab/human/ADRC/fmri_connectomes/', f'time_serts_{subj}.csv')
time_FC_path = os.path.join('/mnt/munin2/Badea/Lab/human/ADRC/fmri_connectomes/',f'time_serFC_{subj}.csv')

print(f'Running functionnal connectomes for subject {subj}')




label_path = '/mnt/munin2/Badea/Lab/mouse/VBM_23ADRC_IITmean_RPI-results/connectomics/' + subj +'/' + subj+'_IITmean_RPI_labels.nii.gz'



fmrimean = os.path.join('/mnt/munin2/Badea/Lab/human/ADRC/new_labels/', subj + '_meanfmri.nii')

os.system('fslmaths ' + fmri_path+' -Tmean ' +  fmrimean)
os.system('gzip ' + fmrimean)

fmrimean = fmrimean + '.gz'


os.system('antsApplyTransforms -v 1 -d 3  -e 0 -i '+ label_path  +' -r '+ fmrimean   + ' -n GenericLabel  -o '  +flabel )


label_path = flabel



label_nii = nib.load(label_path)
labels_data = label_nii.get_fdata()
labels = np.unique(labels_data)
labels = np.delete(labels, 0)
label_nii_order = labels_data * 0.0

path_atlas_legend = '/mnt/munin2/Badea/Lab/atlases/IITmean_RPI/IITmean_RPI_index.xlsx'
legend = pd.read_excel(path_atlas_legend)
new_label =  os.path.join(  '/mnt/munin2/Badea/Lab/human/ADRC/new_labels/' ,  subj +  '.nii.gz')


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
nib.save(file_result, new_label)

label_new_nii = nib.load(new_label)




    # Run the command
    #ants_apply_transforms = apply_transforms_to_points(ants_apply_transforms_command)

#label_nii.shape
data_label=label_new_nii.get_fdata()

#atlas_idx = data_label

"""
voxel_coords = nib.affines.apply_affine(nib.affines.inv(affine1), [x, y, z])
voxel_coords = [int(round(coord)) for coord in voxel_coords]
label_val = label_nii.get_fdata()[tuple(voxel_coords)]
value_nifti2 = nifti2.get_fdata()[tuple(voxel_coords)]

"""


#Creating a new label matrix that has the exact same dimensions as the fmri image.
#Simple code, assumes that they're already aligned and have same voxel size and that voxel size is a good affine diagonal!!






sub_timeseries=fmri_nii.get_fdata()


###### test:







label_mask_in =   data_label



    

roi_list=np.unique(label_mask_in)
roi_list = roi_list[1:]

result=parcellated_matrix(sub_timeseries, label_mask_in, roi_list)


np.savetxt(time_serts_path, result, delimiter=',', fmt='%s')


# if more than 298 time series limit the time series to 299 tp

#if sub_timeseries.shape[3] >298 : sub_timeseries = sub_timeseries[:,:,:,:299]


resultFC=parcellated_FC_matrix(sub_timeseries, label_mask_in, roi_list)

np.savetxt(time_FC_path, resultFC, delimiter=',', fmt='%s')
