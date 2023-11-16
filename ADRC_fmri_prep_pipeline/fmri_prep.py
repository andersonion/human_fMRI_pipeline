#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:54:06 2023

@author: ali
"""


import os, sys, glob

root = '/mnt/munin2/Badea/Lab/'
root_proj = '/mnt/munin2/Badea/Lab/human/ADRC/'

fmri_command = 'singularity exec /usr/local/packages/singularity/images/fmriprep-v23.0.1.sif fmriprep'

subj = (sys.argv[1])
output_BIDS = os.path.join(root_proj,'ADRC_BIDS')
fmriprep_output = os.path.join(root_proj,'fmriprep_output')

work_dir = os.path.join(root_proj,'work_dir')

command = f' {fmri_command} {output_BIDS} {fmriprep_output} ' \
    f'participant --participant-label {subj} -w {work_dir} --nthreads 20 ' \
    f'--output-spaces T1w'
os.system(command)
#print(command)
try:
    work_subj_dir = os.path.join(glob.glob(os.path.join(work_dir,'fmriprep*'))[0],f'*{subj}')
except IndexError:
    print(f'Could not find work subject directory for ')
