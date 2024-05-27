#!/bin/bash

job_id_7937=$(sbatch --parsable 7937_import_log.sh running-example.xes)
job_id_1882=$(sbatch --parsable --dependency=afterok:$job_id_7937 1882_discovery.sh 0.2)
