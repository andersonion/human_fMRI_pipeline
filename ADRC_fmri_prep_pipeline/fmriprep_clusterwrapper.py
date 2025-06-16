#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 13:17:57 2023

@author: ali
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 13:30:59 2023

@author: ali
"""

import os , glob
import sys
#import nibabel as nib

# Generalizing for any human project
# Change as needed:
default_project = "HABS"

import os, sys, glob, pathlib

project = ''
if len(sys.argv) > 1:
	project = (sys.argv[1])


if project == '':
	print(f"No project specified; using default project: {default_project}")
	project = default_project


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



current_file_path = os.path.abspath(__file__)
code_folder = os.path.dirname(current_file_path)

#create sbatch folder
job_descrp =  "fmri_coreg"
sbatch_folder_path = f"{BD}/{project}/"+job_descrp + '_sbatch/'

if not os.path.exists(sbatch_folder_path):
    os.system(f"mkdir -p {sbatch_folder_path}" )



data_path = f"{BD}/{project}/{project}_BIDS"

checker=True
## For some reason, the outputs are going somewhere different compared to the original script.
#outpathfolder = f"{BD}/{project}_prep/fmriprep_output"
outpathfolder = f"{BD}/{project}/fmriprep_output"

list_folders_path = os.listdir(data_path)
#list_of_subjs_long = [i for i in list_folders_path if project in i and not '.' in i]
list_of_subjs_long = [i for i in list_folders_path if "sub-" in i and not '.' in i]
subjects = sorted(list_of_subjs_long)
list_of_subjs = [i.replace('sub-','') for i in list_of_subjs_long]

for subj in list_of_subjs:
    
    #fmri_file = list_fmir_folders_path +subj + "/ses-1/func/" + subj +"_ses-1_bold.nii.gz" 
    #nib.load(fmri_file)
    if checker:
        ## My results have a slightly different naming convention for some reason...maybe it's
        ## on account of using a later version of fmriprep...no longer have 'ingstate_run-01'
        ## as part of the file name.
        #output_file_name = os.path.join(outpathfolder,f'sub-{subj}','func',f'sub-{subj}_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz')
        output_file_name_1 = os.path.join(outpathfolder,f'sub-{subj}','func',f'sub-{subj}_task-rest_space-T1w_desc-preproc_bold.nii.gz')
        # We found out that it can produce the above results, even with critical failures...check for confounds as well:
        output_file_name_2 = os.path.join(outpathfolder,f'sub-{subj}','func',f'sub-{subj}_task-rest_desc-confounds_timeseries.tsv')
        
        T1_file_name = os.path.join(data_path,f'sub-{subj}','anat',f'sub-{subj}_T1w.nii.gz')
       
        if os.path.exists(output_file_name_1) and os.path.exists(output_file_name_2):
            print(f'Already did subject {subj}')
            continue
        
        if not os.path.exists(T1_file_name):
            print(f'Skipping: T1w missing for subject: {subj}')
            continue
            
    python_command = "python3 " + code_folder + "/fmri_prep.py " + subj
    job_name = job_descrp + "_"+ subj
    
    # If the gunnies folder is up to date, either the sge or slurm submit script can be used,
    # regardless of which cluster you be on.
    command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"   
    os.system(command)
    print(f'Launched subject {subj}')
    #os.system(python_command)
