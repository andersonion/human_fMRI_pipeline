#! /bin/env bash

mother_script=$1
oms=${mother_script}
if [[ "x${mother_script}x" != "xx" && ! -e ${mother_script} ]];then
	mother_script=${PWD}/${mother_script};
	if [[ ! -e ${mother_script} ]];then
		echo "A mother script was specified but could not be found;";
		echo "no script will be ran after the environment is activated."
		echo "Locations searched:"
		echo "    ${oms}"
		echo " 	  ${mother_script}"
		mother_script="";
	fi	
fi

if [[ ${mother_script} ]];then
	if [[ ${mother_script##*.} != 'py' ]];then
		echo "Mother script does not appear to be a python script."
		echo "An attempt to run ${mother_script} with a python interpreter will be made, but expect it to fail."
	fi
fi

conda_test=$(conda info --envs | grep '/fmri_connectomes' 2>/dev/null | wc -l);
if ((! ${conda_test} ));then
	echo "Conda env 'fmri_connectomes' does not appear to exist; configuring now..."
	conda env create -p ./fmri_connectomes --file environment.yml;
fi

active_conda_env_test=$(conda info --envs | grep '*' | grep 'fmri_connectomes ' 2>/dev/null | wc -l);

if ((! ${active_conda_env_test} ));then
	echo "Conda env 'fmri_connectomes' does not appear to be activated; activating now..."
	conda init;
	conda activate fmri_connectomes;
fi

conda_test=$(conda info --envs | grep '/fmri_connectomes' 2>/dev/null | wc -l);
active_conda_env_test=$(conda info --envs | grep '*' | grep 'fmri_connectomes ' 2>/dev/null | wc -l);

if (( ${conda_test} && ${active_conda_env_test} ));then
	echo "Conda environment 'fmri_connectomes' successfully installed and activated."
	if [[ ${mother_script} ]];then
		echo "Restarting mother script: ${mother_script}..."
		python3 ${mother_script};
	fi
else
	echo "ERROR: Conda environment 'fmri_connectomes' unsuccessfully created and/or loaded."
	if [[ ${mother_script} ]];then
		echo "WILL NOT rerun mother script: ${mother_script}..."
	fi
	exit 1
fi