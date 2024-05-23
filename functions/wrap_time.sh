#!/usr/local_rwth/bin/bash

mkdir -p times

start=$(date +%s%N | cut -b1-13)

PROG=$1
shift

$PROG "$@"
rc=$?

end=$(date +%s%N | cut -b1-13)

duration=$((end - start))

echo "Start: $start" > times/$SLURM_JOB_ID.time
echo "End: $end" >> times/$SLURM_JOB_ID.time
echo "Duration: $duration" >> times/$SLURM_JOB_ID.time
exit $rc