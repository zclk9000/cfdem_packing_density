#!/bin/bash

#===================================================================#
# allrun script for CFD-DEM hybrid boundary test case
# run packingCFDEM with 5-cycle filling mechanism
# Hybrid boundary: upper STL + lower CFD-DEM coupling
#===================================================================#

#- define variables
casePath="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"

echo "===================================================================="
echo "CFD-DEM混合边界案例 - 主运行脚本"
echo "案例目录: $casePath"
echo "===================================================================="

# check if mesh was built
if [ -f "$casePath/CFD/constant/polyMesh/points" ]; then
    echo "✅ 网格已存在 - 使用现有网格"
else
    echo "🔧 需要生成网格"
    cd $casePath/CFD
    blockMesh
    if [ $? -ne 0 ]; then
        echo "❌ 网格生成失败"
        exit 1
    fi
    echo "✅ 网格生成成功"
fi

echo ""
echo "🚀 启动CFD-DEM并行耦合仿真..."

#- run parallel CFD-DEM
bash $casePath/parCFDDEMrun.sh

echo ""
echo "🎉 CFD-DEM混合边界案例运行完成!"
echo "📊 查看结果数据:"
echo "   paraview $casePath/CFD/VTK/"
echo "   paraview $casePath/DEM/post/particles_*.vtk"