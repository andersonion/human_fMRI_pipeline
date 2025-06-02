#! /bin/env bash
#conda init;
mother_script=$1
oms=${mother_script}
ms_prefix='';
all_args=@;

if [[ "x${mother_script}x" != "xx" && ! -e ${mother_script} ]];then
	mother_script=${PWD}/${mother_script};
	ms_prefix="${PWD}/";
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

# Whitelist the vars you want to retain
WHITELIST_VARS=(
  HOME
  USER
  LOGNAME
  TERM
  TMPDIR
  SLURM_JOB_ID
  SLURM_JOB_NODELIST
  SLURM_TMPDIR
  WORK
  GUNNIES
  BIGGUS_DISKUS
  PATH
)

# Build a clean environment declaration
ENV_DECL=""
for var in "${WHITELIST_VARS[@]}"; do
    val="${!var}"
    if [[ -n "$val" ]]; then
        ENV_DECL+=" $var=\"$val\""
    fi
done

# Prepend a safe base PATH
p_test=$(printf "%s\n" "${WHITELIST_VARS[@]}" | grep -Fxq "PATH")
echo "p_test = ${p_test}"
if [[ ! ${p_test} ]];then
	ENV_DECL+=" PATH=/usr/bin:/bin"
fi
# Run the command in a clean shell
eval env -i $ENV_DECL bash --noprofile --norc <<'EOF'
echo "DEBUG TESTING:"
echo $PATH
conda info --envs | grep '/fmri_connectomes' 2>/dev/null | wc -l
conda_test=$(conda info --envs | grep '/fmri_connectomes' 2>/dev/null | wc -l);
if ((! ${conda_test} ));then
	echo "Conda environment 'fmri_connectomes' does not appear to exist; configuring now..."
	conda env create -p ./fmri_connectomes --file environment.yml;
fi

active_conda_env_test=$(conda info --envs | grep '*' | grep '/fmri_connectomes' 2>/dev/null | wc -l);

if ((! ${active_conda_env_test} ));then
	echo "Conda environment 'fmri_connectomes' does not appear to be activated; activating now..."
	if command -v conda >/dev/null 2>&1; then
		# Use conda.sh dynamically if conda is found
		__conda_setup="$($(command -v conda) shell.bash hook 2> /dev/null)"
		if [ $? -eq 0 ]; then
			eval "$__conda_setup"
		else
			echo "Failed to initialize conda shell hook"
			exit 1
		fi
	else
		echo "conda not found in PATH"
		exit 1
	fi
	env_path=$(conda info --envs | grep fmri_connectomes | head -1 | tr -d '*' | tr -d [:space:]);
	conda activate ${env_path};
fi

# Its critical to find and source the conda.sh file (from ChatGPT):

if [ -n "$CONDA_EXE" ]; then
	echo "CONDA_EXE = ${CONDA_EXE}"
	conda_sh_path="$(dirname "$CONDA_EXE")/../etc/profile.d/conda.sh"
	conda_sh_path="$(realpath "$conda_sh_path")"
    if [ -e ${conda_sh_path} ];then
    	echo "conda.sh is located at: $conda_sh_path"
    	source "$conda_sh_path"
	else
		echo "conda.sh was assumed to be at: $conda_sh_path"
		echo "But that appears not to exist."
		echo "conda.sh not found and CANNOT be sourced; EXPECT DUMB FAILURES"
	fi
else
    echo "CONDA_EXE not found. Thusly..."
    echo "conda.sh not found and CANNOT be sourced; EXPECT DUMB FAILURES"
fi

# Test and run mother script if needed:

conda_test=$(conda info --envs | grep '/fmri_connectomes' 2>/dev/null | wc -l);
active_conda_env_test=$(conda info --envs | grep '*' | grep '/fmri_connectomes' 2>/dev/null | wc -l);

if (( ${conda_test} && ${active_conda_env_test} ));then
	echo "Conda environment 'fmri_connectomes' successfully installed and activated."
	if [[ ${mother_script} ]];then
		echo "Restarting mother script,"
		echo "Full command:"
		env_path=$(conda info --envs | grep fmri_connectomes | head -1 | tr -d '*' | tr -s [:space:]);
		shift
		full_cmd="conda run -p ${env_path} python3 ${mother_script} ${all_args}"
		echo "${full_cmd}"
		${full_cmd};
	fi
else
	echo "ERROR: Conda environment 'fmri_connectomes' unsuccessfully created and/or loaded."
	if [[ ${mother_script} ]];then
		echo "WILL NOT rerun mother script: ${mother_script}..."
	fi
	exit 1
fi
EOF