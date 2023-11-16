#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 13:30:59 2023

@author: ali
"""

import os , glob, shutil
import sys, subprocess, copy
#import nibabel as nib

try :
    BD = os.environ['BIGGUS_DISKUS']
#os.environ['GIT_PAGER']
except KeyError:  
    print('BD not found locally')
    BD = '/mnt/munin2/Badea/Lab/mouse'    
    #BD ='/Volumes/Data/Badea/Lab/mouse'
else:
    print("BD is found locally.")
#create sbatch folder
job_descrp =  "mrtrix"
sbatch_folder_path = BD+"/ADRC_jacques_pipeline/"+job_descrp + '_sbatch/'

if not os.path.exists(sbatch_folder_path):
    os.system(f"mkdir -p {sbatch_folder_path}" )
    #os.makedirs(sbatch_folder_path)
GD = '/mnt/clustertmp/common/rja20_dev/gunnies/'
#GD = '/mnt/munin2/Badea/Lab/mouse/mrtrix_pipeline/'


data_folder_path ='/mnt/munin2/Badea/Lab/ADRC-20230511/'
#list_folders_path = '/Volumes/Data/Badea/Lab/ADRC-20230511/'
list_folders_path = os.listdir(data_folder_path)
directories = [item for item in list_folders_path if os.path.isdir(os.path.join(data_folder_path, item))]
list_of_subjs_long = [i for i in directories if 'ADRC' in i]
list_of_subjs = list_of_subjs_long


completion_checker=True
cleanup = False
test= True

list_of_subjs.sort()
list_of_subjs_true = copy.deepcopy(list_of_subjs)

if completion_checker:
    perm_folder = os.path.join(BD,'ADRC_jacques_pipeline','perm_files')
    for subj in list_of_subjs:
        fa_path = os.path.join(perm_folder, f'{subj}_fa.nii.gz')
        tck_path = os.path.join(perm_folder, f'{subj}_smallerTracks2mill.tck')
        subj_out_folder = os.path.join(BD, 'ADRC_jacques_pipeline','temp',subj)

        if os.path.exists(fa_path) and os.path.exists(tck_path):
            list_of_subjs_true.remove(subj)
        elif cleanup and os.path.exists(subj_out_folder):
            print(f'deleting {subj_out_folder}')
            shutil.rmtree(subj_out_folder)

if test:
    print(list_of_subjs_true)

#list_of_subjs[90]
#list_of_subjs = [i.partition('_subjspace_dwi.nii.gz')[0] for i in list_of_subjs_long]

''' 
conn_path = '/mnt/munin2/Badea/Lab/mouse/ADRC_mrtrix_dwifsl/connectome/'
#conn_path = '/Volumes/Data/Badea/Lab/mouse/mrtrix_ad_decode/connectome/'
if os.path.isdir(conn_path):
    done_subj = os.listdir(conn_path)
    done_subj = [i for i in done_subj if 'conn_plain' in i]
    done_subj = [i.partition('_conn_plain.csv')[0] for i in done_subj]
    list_of_subjs = set(list_of_subjs) - set(done_subj)
  

trac_path = '/mnt/munin2/Badea/Lab/mouse/ADRC_mrtrix_dwifsl/perm_files/'
#trac_path = '/Volumes/Data/Badea/Lab/mouse/ADRC_mrtrix_dwifsl/perm_files/'
if os.path.isdir(trac_path):
    done_subj = os.listdir(trac_path)
    done_subj = [i for i in done_subj if 'smallerTracks2mill' in i]
    done_subj = [i.partition('_smallerTracks2mill')[0] for i in done_subj]
    list_of_subjs = set(list_of_subjs) - set(done_subj)   
        
#list_fmri_folders.remove(".DS_Store")

'''


#list_of_subjs_true = ['ADRC0017', 'ADRC0025', 'ADRC0026', 'ADRC0028', 'ADRC0033', 'ADRC0040', 'ADRC0043', 'ADRC0047', 'ADRC0084', 'ADRC0085', 'ADRC0101', 'ADRC0102', 'ADRC0111']

#list_of_subjs_true = ['ADRC0028']
list_of_subjs_true = ['ADRC0091', 'ADRC0080', 'ADRC0086', 'ADRC0082', 'ADRC0070', 'ADRC0064', 'ADRC0065', 'ADRC0063', 'ADRC0079', 'ADRC0048', 'ADRC0066', 'ADRC0095', 'ADRC0071', 'ADRC0076', 'ADRC0050', 'ADRC0087', 'ADRC0099', 'ADRC0100', 'ADRC0078', 'ADRC0083', 'ADRC0062', 'ADRC0096', 'ADRC0097']

if not test:
    for subj in list_of_subjs_true:
        #print(subj)
        #fmri_file = list_fmir_folders_path +subj + "/ses-1/func/" + subj +"_ses-1_bold.nii.gz" 
        #nib.load(fmri_file)
        python_command = "python /mnt/munin2/Badea/Lab/human/ADRC/ADRC_fmri_prep_pipeline/.py "+subj
        #python_command = "python /mnt/munin2/Badea/Lab/mouse/mrtrix_pipeline/main_trc_conn.py "+subj
        job_name = job_descrp + "_"+ subj
        command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"   
        os.system(command)
    #    subprocess.call(command, shell=True)
    #    os.system('qsub -S '+python_command  )


'''


subj = "ADRC0001"

 #print(subj)
python_command = "python /mnt/munin2/Badea/Lab/mouse/ADRC_jacques_pipeline/ADRC_preprocessing_pipeline.py "+subj
 #python_command = "python /mnt/munin2/Badea/Lab/mouse/mrtrix_pipeline/main_trc_conn.py "+subj
job_name = job_descrp + "_"+ subj
command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"   
os.system(command)

'''

