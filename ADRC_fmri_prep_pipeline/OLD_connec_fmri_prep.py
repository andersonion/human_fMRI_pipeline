#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:54:06 2023

@author: ali
"""


import nibabel as nib
import numpy as np
from scipy.ndimage import morphology
from nibabel import load, save, Nifti1Image, squeeze_image
import os
import sys, string, os
import pandas as pd
import os, socket
import numpy as np
import nibabel as nib
import pandas as pd
from nibabel.processing import resample_to_output


  
    
    
#subj = (sys.argv[1])
subj = 'ADRC0002'


    

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





#time_ser_path= '/mnt/munin2/Badea/Lab/human/ADRC/time_ser/'
time_ser_path= '/Volumes/Data/Badea/Lab/human/ADRC/time_ser/'
if not os.path.isdir(time_ser_path) : os.mkdir(time_ser_path)







#atlas_index_path  = '/mnt/munin2/Badea/Lab/atlases/IITmean_RPI/IITmean_RPI_index.xlsx'
atlas_index_path  = '/Volumes/Data/Badea/Lab/atlases/IITmean_RPI/IITmean_RPI_index.xlsx'
legend  = pd.read_excel(atlas_index_path)

#label_path  = '/mnt/munin2/Badea/Lab/mouse/VBM_23ADRC_IITmean_RPI-results/connectomics/' + subj +'/' + subj+'_IITmean_RPI_labels.nii.gz'
label_path  = '/Volumes/Data/Badea/Lab/mouse/VBM_23ADRC_IITmean_RPI-results/connectomics/' + subj +'/' + subj+'_IITmean_RPI_labels.nii.gz'




label_nii=nib.load(label_path)
label_nii.shape
data_label=label_nii.get_fdata()
roi_list=np.unique(data_label)
roi_list = roi_list[1:]
#atlas_idx = data_label


#new_label = os.path.join(  '/mnt/munin2/Badea/Lab/human/ADRC/new_labels/' ,  subj +  ' .nii.gz')
new_label = os.path.join(  '/Volumes/Data/Badea/Lab/human/ADRC/new_labels/' ,  subj +  '.nii.gz')

if not os.path.exists(new_label):

    labels_data = data_label
    labels = np.unique(labels_data)
    labels = np.delete(labels, 0)
    label_nii_order = labels_data * 0.0
    for i in labels:
        leg_index = np.where(legend['index2'] == i)
        leg_index = leg_index[0][0]
        ordered_num = legend['index'][leg_index]
        label3d_index = np.where(labels_data == i)
        label_nii_order[label3d_index] = ordered_num

    file_result = nib.Nifti1Image(label_nii_order, label_nii.affine, label_nii.header)
    new_label = new_label
    nib.save(file_result, new_label)
        
label_nii=nib.load(new_label)
label_nii.shape
data_label=label_nii.get_fdata()
roi_list=np.unique(data_label)
roi_list = roi_list[1:]



#errts_nii_gz = '/mnt/munin2/Badea/Lab/human/ADRC/fmriprep_output/sub-' + subj+'/func/sub-' + subj + '_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz'
errts_nii_gz = '/Volumes/Data/Badea/Lab/human/ADRC/fmriprep_output/sub-' + subj+'/func/sub-' + subj + '_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz'

file_data=nib.load(errts_nii_gz)

resampled_source_image = resample_to_output(label_nii, np.diagonal(file_data.affine)[:3])

resampled_source_image.shape
file_data.shape










sub_timeseries=file_data.get_fdata()
result=parcellated_matrix(sub_timeseries, data_label, roi_list)
if os.path.isfile(time_ser_path + 'ts_' + subj +  '.csv'): os.remove(time_ser_path + 'ts_' + subj +  '.csv')
np.savetxt( time_ser_path + 'ts_' + subj +  '.csv'  , result, delimiter=',', fmt='%s')





# FCs


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

# if more than 298 time series limit the time series to 299 tp 
if sub_timeseries.shape[3] >298 : sub_timeseries = sub_timeseries[:,:,:,:299]
#
resultFC=parcellated_FC_matrix(sub_timeseries, data_label, roi_list)
if os.path.isfile(time_ser_path + 'FC_' + subj +  '.csv'): os.remove(time_ser_path + 'FC_' + subj +  '.csv')
np.savetxt( time_ser_path + 'FC_' + subj +  '.csv'  , resultFC, delimiter=',', fmt='%s')    