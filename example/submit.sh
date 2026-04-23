#!/bin/bash
#SBATCH --job-name=dock
#SBATCH --output=logs/out_%A_%a.txt
#SBATCH --cpus-per-task=1
#SBATCH --array=1-100
#SBATCH --partition=low
#SBATCH --time=30:00:00
#SBATCH --mem=10G

/quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease -database /quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/database @flags -user_tag $SLURM_ARRAY_TASK_ID -out:suffix $SLURM_ARRAY_TASK_ID -out:path:all ./results
