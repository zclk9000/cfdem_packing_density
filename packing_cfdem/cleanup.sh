#!/bin/bash

#===================================================================#
# Cleanup script for CFD-DEM hybrid boundary case
# Removes simulation results and temporary files
#===================================================================#

casePath="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"

echo "===================================================================="
echo "清理CFD-DEM混合边界案例数据"
echo "案例目录: $casePath"
echo "===================================================================="

read -p "确认清理所有仿真结果数据? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "取消清理操作"
    exit 0
fi

echo "🧹 清理CFD数据..."
cd $casePath/CFD

# Clean OpenFOAM case
if [ -f "$WM_PROJECT_DIR/bin/tools/CleanFunctions" ]; then
    source $WM_PROJECT_DIR/bin/tools/CleanFunctions
    cleanCase
else
    # Manual cleanup
    rm -rf processor*
    rm -rf [0-9]*.[0-9]* [1-9]*
    rm -rf VTK/
    rm -rf postProcessing/
fi

# Clean CFD-DEM coupling files
rm -rf clockData/
rm -rf couplingFiles/
rm -rf post/
rm -f log.* 
rm -f *.log

echo "🧹 清理DEM数据..."
cd $casePath/DEM
rm -rf post/*
rm -rf log/
rm -f log.*
rm -f *.log
rm -f liggghts.restart*

# Preserve post directory structure
mkdir -p post
touch post/.gitignore

echo "🧹 清理根目录日志..."
cd $casePath
rm -f log_*
rm -f *.log

echo ""
echo "✅ 清理完成!"
echo "保留的文件:"
echo "  - 配置文件 (CFD/, DEM/, STL/)"
echo "  - 运行脚本 (Allrun.sh, parCFDDEMrun.sh, cleanup.sh)"
echo "  - 文档文件 (*.md)"
echo ""
echo "可以重新运行: ./Allrun.sh"