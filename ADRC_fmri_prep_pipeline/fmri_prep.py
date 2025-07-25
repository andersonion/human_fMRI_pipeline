#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:54:06 2023

@author: ali
"""
# Generalizing for any human project
# Change as needed:
default_project = "HABS"

import os, sys, glob, pathlib

subj = (sys.argv[1])
clean_subj = subj.replace('_',"")

project = ''
if len(sys.argv) > 2:
	project = (sys.argv[2])


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


root = os.path.dirname(BD)
#root = '/mnt/munin2/Badea/Lab/'
root_proj = f'{BD}/{project}/'

print(f'root_proj = {root_proj} ')

if os.path.exists(root_proj):
	pass
else:
	raise FileNotFoundError(f'root_proj (value: {root_proj} ) is either not set or does not exist.')


SID=os.environ['SINGULARITY_IMAGE_DIR']
FREESURFER_HOME=os.environ['FREESURFER_HOME']

if os.path.exists(SID):
	pass
else:
	raise FileNotFoundError(f'SINGULARITY_IMAGE_DIR (value: {SID} ) is either not set or does not exist.')

# Command used on BIAC cluster
#fmri_command = f'singularity exec {SID}/fmriprep-v23.0.1.sif fmriprep'

# First installation on QIAL cluster, not used as of yet
#fmri_command = f'singularity exec {SID}/fmriprep-v23.0.1.simg fmriprep'

# Upgraded version on QIAL cluster singularity run --bind /mnt/newStor:/mnt/newStor fmriprep.simg ...
#singularity run --bind /mnt/newStor:/mnt/newStor fmriprep.simg ...

#fmri_command = f'singularity exec --bind /mnt/newStor:/mnt/newStor --bind /home/apps:/home/apps {SID}/fmriprep-v25.0.0.sif fmriprep'
## It seems that it was a mistake to include '--bind /home/apps:/home/apps'...that would then call our messed up fsl/python configurations
## instead of the containerized versions; removing that option	
fmri_command = f'singularity exec --cleanenv -B /mnt/newStor:/mnt/newStor -B {FREESURFER_HOME}/license.txt:/opt/freesurfer/license.txt {SID}/fmriprep-v25.0.0.sif fmriprep'
# May need this: ANACONDA_HOME = "/home/apps//ubuntu-22.04/anaconda3/ssl/"; and this in the singularity call: -B {ANACONDA_HOME}:{ANACONDA_HOME} (working fine without it for now)

output_BIDS = os.path.join(root_proj,f"{project}_BIDS/")
fmriprep_output = os.path.join(root_proj,'fmriprep_output')

work_dir = os.path.join(root_proj,'work_dir')

print(f'output_BIDS = {output_BIDS} ')
print(f'fmriprep_output = {fmriprep_output} ')
no_recon = "";
if "Flair" in subj.lower():
	no_recon = '--fs-no-reconall '
	
command = f' {fmri_command} {output_BIDS} {fmriprep_output} ' \
	f'{no_recon}' \
    f'participant --participant-label {clean_subj} -w {work_dir} --nthreads 20 ' \
    f'--output-spaces T1w  --fs-license-file /opt/freesurfer/license.txt'
os.system(command)
print(command)
try:
    work_subj_dir = os.path.join(glob.glob(os.path.join(work_dir,'fmriprep*'))[0],f'*{subj}')
except IndexError:
    print(f'Could not find work subject directory for {clean_subj}')
