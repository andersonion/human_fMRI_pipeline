#! /bin/env bash
runno_prefix_letter='D';
bash human_diffusion_preprocessing_MRtrix.bash D0007 /mnt/newStor/paros/paros_WORK//tmp_ADRC_MUSE/D0007

# Run diffusion prep
sub_script=$GUNNIES/submit_slurm_cluster_job.bash;
tmp_inputs="${WORK}/tmp_ADRC_MUSE/";
cd $tmp_inputs;
sbatch_dir=${tmp_inputs}/sbatch
mkdir -p ${sbatch_dir};

for id in $(ls -d *);do
	raw_nii_folder=${tmp_inputs}/${id};
	cmd="bash ${GUNNIES}/human_diffusion_preprocessing_MRtrix.bash ${id} ${raw_nii_folder}";
	job_name=${id}_diffusion_processing;
	sub_cmd="${sub_script} ${sbatch_dir} ${job_name} 0 0 ${cmd}";
	test_output=${WORK}/human/diffusion_prep_MRtrix_${id}/${id}_sift_mu.txt;
	if [[ ! -f ${test_output} ]];then
		$sub_cmd;
	fi
done
	