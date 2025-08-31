#!/bin/bash

#===================================================================#
# CFD-DEM parallel run script for hybrid boundary settling test
# Based on settlingTestMPI but with hybrid boundary approach
# 5-cycle particle filling with CFD-DEM coupling
#===================================================================#

#- source CFDEM env vars
. ~/.bashrc

#- include functions
source $CFDEM_PROJECT_DIR/etc/functions.sh

#--------------------------------------------------------------------------------#
#- define variables
casePath="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"
logpath=$casePath
headerText="run_parallel_cfdemSolverPiso_packingCFDEM_hybridBoundary"
logfileName="log_$headerText"
solverName="cfdemSolverPiso"
nrProcs="8"
machineFileName="none"   # yourMachinefileName | none
debugMode="off"          # on | off| strict
reconstructCase="true"   # true | false
testHarnessPath="$CFDEM_TEST_HARNESS_PATH"
runOctave="false"        # no octave analysis for this case
cleanUp="false"          # keep data for analysis
postproc="false"
#--------------------------------------------------------------------------------#

echo "===================================================================="
echo "CFD-DEM混合边界耦合仿真 - 标准CFDEM运行模式"
echo "案例: $casePath"
echo "处理器数: $nrProcs"
echo "===================================================================="

#- call function to run a parallel CFD-DEM case
parCFDDEMrun $logpath $logfileName $casePath $headerText $solverName $nrProcs $machineFileName $debugMode $reconstructCase

if [ $postproc == "true" ]
  then

    #- keep terminal open (if started in new terminal)
    echo "simulation finished? ...press enter to proceed"
    read

    #- get VTK data from liggghts dump file
    cd $casePath/DEM/post
    python -i $CFDEM_LPP_DIR/lpp.py  dump.liggghts_run

    #- get VTK data from CFD sim
    cd $casePath/CFD
    foamToVTK                                                   #- serial run of foamToVTK

    #- start paraview
    paraview

    #- keep terminal open (if started in new terminal)
    echo "...press enter to clean up case"
    echo "press Ctr+C to keep data"
    read
fi

#- clean up case
if [ $cleanUp == "true" ]
  then
    echo "deleting data at: $casePath :\n"
    source $WM_PROJECT_DIR/bin/tools/CleanFunctions
    cd $casePath/CFD
    cleanCase
    cd $casePath
    rm -r $casePath/CFD/clockData
    rm -r $casePath/DEM/post/*
    rm -r $casePath/DEM/liggghts.restartCFDEM*
    echo "done"
fi

#- preserve post directory
touch $casePath/DEM/post/.gitignore

echo "===================================================================="
echo "CFD-DEM混合边界耦合仿真完成"
echo "结果数据位置:"
echo "  - CFD: $casePath/CFD/VTK/"
echo "  - DEM: $casePath/DEM/post/" 
echo "  - 耦合: $casePath/CFD/post/"
echo "===================================================================="
