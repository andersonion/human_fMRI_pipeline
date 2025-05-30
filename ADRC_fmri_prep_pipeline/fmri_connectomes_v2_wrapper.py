# This code is imported from Jacques Stout's parallel repository
import os, socket, sys, glob, subprocess

# Change as needed:
default_project = "ADNI"
project = ''
if len(sys.argv) > 1:
	project = (sys.argv[1])

if project == '':
	print(f"No project specified; using default project: {default_project}")
	project = default_project

use_cluster = True
if len(sys.argv) > 2:
	if sys.argv[2] == '0':
		use_cluster = False
		print("You have chosen to not take advantage of the power of the HPC resources, running 'locally'...")

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))

conda_env = os.environ.get("CONDA_DEFAULT_ENV")
env_path = subprocess.check_output(
    "conda info --envs | grep fmri_connectomes | head -1 | tr -d '*' | tr -s ' '",
    shell=True,
    text=True
).strip()

run_code = True
if conda_env != env_path:
	print(f"Conda environment 'fmri_connectomes' not activated; running setup/activate script now...")
	run_code = False
	arguments = ""
	if len(sys.argv) > 1:
		arguments = sys.arg[1:]
		print(f"Arguments: {arguments}")
	setup_cmd = f"bash {script_dir}/setup_fmri_connectomes_conda_env.bash {script_path} {arguments}"
	print("Setup command:")
	print(setup_cmd)
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

	
	
if run_code:
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
	
	WORK = os.environ['WORK']
	
	
	qial_hosts = [ 'kea' , 'kos', 'andros' , 'crete', 'kythira', 'patmos']
	host=socket.gethostname().split('.')[0]
	
	
	if host=='santorini':
		root = '/Volumes/Data/Badea/Lab/'
		root_proj = '/Volumes/Data/Badea/Lab/human/ADRC/'
	elif host in qial_hosts: 
		root = f'{WORK}/'
		root_proj = f'{BD}/{project}/'
	else:
		root = '/mnt/munin2/Badea/Lab/'
		root_proj = '/mnt/munin2/Badea/Lab/human/ADRC/'
	
	# I currently do not know what results for which I should be checking...
	checker = True	
	
	current_file_path = os.path.abspath(__file__)
	code_folder = os.path.dirname(current_file_path)

	job_descrp = "fMRI_connectomes"
	sbatch_folder_path = f"{BD}/{project}/"+job_descrp + '_sbatch/'
	if not os.path.exists(sbatch_folder_path):
		os.system(f"mkdir -p {sbatch_folder_path}" )
	
	data_path = f'{BD}/{project}/fmriprep_output'
	SAMBA_path_results_prefix = f'{BD}/diffusion_prep_MRtrix_'
	
	list_folders_path = os.listdir(data_path)
	list_of_subjs_long = [i for i in list_folders_path if 'sub-' in i and not '.' in i and not '.html' in i]
	list_of_subjs = sorted(list_of_subjs_long)
	subjects = list_of_subjs
	
	outpathfolder = f"{BD}/{project}/connectomes/functional_conn"
	
	for subj in subjects:
		subj_strip = subj.replace('sub-',"")
		subj_temp = subj_strip
		if '_' not in subj_temp:
			subj_temp = subj_temp.replace('y','_y')

		if checker:
			## My results have a slightly different naming convention for some reason...maybe it's
			## on account of using a later version of fmriprep...no longer have 'ingstate_run-01'
			## as part of the file name.
			#output_file_name = os.path.join(outpathfolder,f'sub-{subj}','func',f'sub-{subj}_task-restingstate_run-01_space-T1w_desc-preproc_bold.nii.gz')
			output_file_name = os.path.join(outpathfolder,f'func_connectome_corr_{subj_temp}.csv')
			print(output_file_name)
			if os.path.exists(output_file_name):
				print(f'Already did subject {subj_temp}')
				continue
		python_command = "python3 " + code_folder + "/fmri_connectomes_v2.py " + subj + ' ' + project
		job_name = job_descrp + "_"+ subj_temp
		
		# If the gunnies folder is up to date, either the sge or slurm submit script can be used,
		# regardless of which cluster you be on.
		
		if use_cluster:
			command = GD + "submit_sge_cluster_job.bash " + sbatch_folder_path + " "+ job_name + " 0 0 '"+ python_command+"'"
		else:
			command = python_command
			
		os.system(command)
		print(f'Launched subject {subj}')
