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
    
# Make this code reusable for other projects    
project = "ADNI"

#create sbatch folder
job_descrp =  "fmri_coreg"
sbatch_folder_path = f"{BD}/{project}_prep/"+job_descrp + '_sbatch/'

if not os.path.exists(sbatch_folder_path):
    os.system(f"mkdir -p {sbatch_folder_path}" )



data_path = f"{BD}/{project}/{project}_BIDS"

checker=True
outpathfolder = f"{BD}/{project}_prep/fmriprep_output"

list_folders_path = os.listdir(data_path)
list_of_subjs_long = [i for i in list_folders_path if project in i and not '.' in i]
subjects = sorted(list_of_subjs_long)
list_of_subjs = [i.replace('sub-','') for i in list_of_subjs_long]
#list_of_subjs = ['ADRC0001']
print(list_of_subjs_long)
print(subjects)
for subj in list_of_subjs:
    print(subj)
    #fmri_file = list_fmir_folders_path +subj + "/ses-1/func/" + subj +"_ses-1_bold.nii.gz" 
    #nib.load(fmri_file)
    if checker:
        output_file_name = os.path.join(outpathfolder,f'sub-{subj}','func',f'sub-{subj}_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz')
        #print(output_file_name)
        if os.path.exists(output_file_name):
            #print(f'Already did subject {subj}')
            continue
    python_command = "python3 " + code_folder + "/fmri_prep.py " + subj
    job_name = job_descrp + "_"+ subj
    
    # If the gunnies folder is up to date, either the sge or slurm submit script can be used,
    # regardless of which cluster you be on.
    command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"   
    os.system(command)
    print(f'Launched subject {subj}')
    #os.system(python_command)
