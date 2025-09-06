#!/bin/bash

#===================================================================#
# Allrun script for cfdemSolverMultiphase
#===================================================================#

#- define variables
postProcessing=true
casePath="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"

# check if mesh was built
if [ -f "$casePath/CFD/constant/polyMesh/points" ]; then
    echo "mesh was built before - using old mesh"
else
    echo "mesh needs to be built"
    cd $casePath/CFD
    blockMesh
fi

cd $casePath/CFD
cp -r 0.org 0
setFields

if [ -f "$casePath/DEM/post/restart/liggghts.restart" ];  then
    echo "LIGGGHTS init was run before - using existing restart file"
else
    #- run DEM in new terminal
    $casePath/parDEMrun.sh
fi

# 启动CFD-DEM仿真和平衡监控 [第三步：恢复监控脚本]
echo "启动CFD-DEM仿真和平衡监控..."

# 在后台启动CFD-DEM仿真
bash $casePath/parCFDDEMrun.sh &
CFDDEM_PID=$!

# 等待一下确保CFD-DEM启动
sleep 5

# 启动平衡监控(前台运行)
bash $casePath/monitor_balance.sh

# 等待CFD-DEM进程完成
wait $CFDDEM_PID

if [ "$postProcessing" = true ]; then
    bash $casePath/postrun.sh
fi
