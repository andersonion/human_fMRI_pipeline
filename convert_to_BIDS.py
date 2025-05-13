# Originally written by Jacques Stout for converting ARDC subjects to BIDS format.
# Adapted for more general use on 27 March 2025 (Thursday), by Robert "BJ" Anderson/

# First argument is the original path of the input data.
# Second argument is the output path.
# There is some code that will need to be modified for your specific data structure

import json, os, shutil, sys
import SimpleITK as sitk

orig_path = sys.argv[1]
output_path = sys.argv[2]
subj = sys.argv[3]

#orig_path = '/Volumes/Data/Badea/Lab/ADRC-20230511/'
#output_path = '/Users/jas/jacques/ADRC/ADRC_Dataset/'

#from DTC.file_manager.file_tools import buildlink, mkcdir, getfromfile

def mkcdir(folderpaths, sftp=None):
    #creates new folder only if it doesnt already exists
    import numpy as np
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

# Is this a test subject for debugging?
#subj = 'ADRC0001'



subj_folder = os.path.join(output_path,f'sub-{subj}')
anat_folder = os.path.join(output_path,f'sub-{subj}/anat')
func_folder = os.path.join(output_path,f'sub-{subj}/func')

mkcdir([subj_folder,anat_folder,func_folder],None)

# Hey you! Change this as needed for your data.
t1_path_orig = os.path.join(orig_path,f'{subj}_T1.nii.gz')  # change this with your file

t1_nii_path = os.path.join(anat_folder,f'sub-{subj}_T1w.nii.gz')
t1_json_path = os.path.join(anat_folder,f'sub-{subj}_T1w.json')

if not os.path.exists(t1_nii_path):
    shutil.copy(t1_path_orig,t1_nii_path)

# save dict in 'header.json'
if not os.path.exists(t1_json_path):
    # read image
    itk_image = sitk.ReadImage(t1_nii_path)

    # get metadata dict
    header = {k: itk_image.GetMetaData(k) for k in itk_image.GetMetaDataKeys()}
    with open(t1_json_path, "w") as outfile:
        json.dump(header, outfile, indent=4)


func_path_orig = os.path.join(orig_path,f'{subj}_fMRI_nii4D.nii.gz')  # change this with your file

func_nii_path = os.path.join(func_folder,f'sub-{subj}_task-restingstate_run-01_bold.nii.gz')
func_json_path = os.path.join(func_folder,f'sub-{subj}_task-restingstate_run-01_bold.json')

if not os.path.exists(func_nii_path):
    shutil.copy(func_path_orig,func_nii_path)

# save dict in 'header.json'
if not os.path.exists(func_json_path):
    # read image
    itk_image = sitk.ReadImage(func_nii_path)

    # get metadata dict
    header = {k: itk_image.GetMetaData(k) for k in itk_image.GetMetaDataKeys()}
    with open(func_json_path, "w") as outfile:
        json.dump(header, outfile, indent=4)

