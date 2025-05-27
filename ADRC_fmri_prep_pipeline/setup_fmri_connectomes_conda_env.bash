#! /bin/env bash

conda_test=$(conda info --envs | grep 'fmri_connectomes ' 2>/dev/null | wc -l);
if ((! ${conda_test} ));then
	conda env create -p ./fmri_connectomes --file environment.yml;
fi

active_conda_env_test=$(conda info --envs | grep '*' | grep 'fmri_connectomes ' 2>/dev/null | wc -l);

if ((! ${active_conda_env_test} ));then
	conda activate fmri_connectomes;
fi