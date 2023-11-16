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

try :
    BD = os.environ['BIGGUS_DISKUS']
#os.environ['GIT_PAGER']
except KeyError:  
    print('BD not found locally')
    BD = '***/mouse'    
    #BD ='***/example'
else:
    print("BD is found locally.")
#create sbatch folder
job_descrp =  "fmri_coreg"
sbatch_folder_path = "/mnt/munin2/Badea/Lab/human/ADRC/fmri_pipeline_batch/"+job_descrp + '_sbatch/'

if not os.path.exists(sbatch_folder_path):
    os.system(f"mkdir -p {sbatch_folder_path}" )
    #os.makedirs(sbatch_folder_path)
GD = '/mnt/clustertmp/common/rja20_dev/gunnies/'

data_path = '/mnt/munin2/Badea/Lab/human/ADRC/ADRC_BIDS'

list_folders_path = os.listdir(data_path)
list_of_subjs_long = [i for i in list_folders_path if 'ADRC' in i and not '.' in i]
subjects = sorted(list_of_subjs_long)
list_of_subjs = [i.replace('sub-','') for i in list_of_subjs_long]
list_of_subjs = ['ADRC0001']
for subj in list_of_subjs:
    #print(subj)
    #fmri_file = list_fmir_folders_path +subj + "/ses-1/func/" + subj +"_ses-1_bold.nii.gz" 
    #nib.load(fmri_file)
    python_command = "python3 /mnt/munin2/Badea/Lab/human/ADRC/ADRC_fmri_prep_pipeline/fmri_prep.py "+subj
    job_name = job_descrp + "_"+ subj
    command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"   
    os.system(command)