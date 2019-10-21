#!/bin/bash

{{ cookiecutter.batch_directives }}

set -e  # abort on first error
set -u  # abort if undefinded variable is encountered

{{ cookiecutter.module_loads }}

WW3_EXE="{{ cookiecutter.wwatch3_exe_dir }}"
MPIRUN="mpirun"
GATHER="{{ cookiecutter.wwatch3_cmd }} gather"

RUN_START_DATES=(
  {{ cookiecutter.run_start_dates_yyyymmdd }}
)

RESULTS_DIRS=(
  {{ cookiecutter.results_dirs }}
)
WORK_DIRS=(
  {{ cookiecutter.work_dirs }}
)

for (( i=0; i<${{ '{#' }}RESULTS_DIRS[@]}; ++i ))
do
  echo "results dir: ${RESULTS_DIRS[i]}"

  cd ${WORK_DIRS[i]}
  echo "working dir: $(pwd)"

  echo "Starting wind.nc file creation at $(date)"
  ln -s ww3_prnc_wind.inp ww3_prnc.inp && \
  ${WW3_EXE}/ww3_prnc && \
  rm -f ww3_prnc.inp
  echo "Ending wind.nc file creation at $(date)"

  echo "Starting current.nc file creation at $(date)"
  ln -s ww3_prnc_current.inp ww3_prnc.inp && \
  ${WW3_EXE}/ww3_prnc && \
  rm -f ww3_prnc.inp
  echo "Ending current.nc file creation at $(date)"

  echo "Starting run at $(date)"
  ${MPIRUN} -np {{ cookiecutter.n_procs }} ${WW3_EXE}/ww3_shel && \
  mv log.ww3 ww3_shel.log && \
  rm current.ww3 wind.ww3 && \
  echo "Ended run at $(date)"

  echo "Starting netCDF4 fields output at $(date)"
  ${WW3_EXE}/ww3_ounf && \
  mv SoG_ww3_fields_${RUN_START_DATES[i]}.nc \
    SoG_ww3_fields_${RUN_START_DATES[i]}_${RUN_START_DATES[i]}.nc && \
  rm out_grd.ww3
  echo "Ending netCDF4 fields output at $(date)"

  echo "Results gathering started at $(date)"
  ${GATHER} ${RESULTS_DIRS[i]} --debug
  echo "Results gathering ended at $(date)"

  echo "Deleting run directory"
  rmdir $(pwd)
  echo "Finished at $(date)"
done
