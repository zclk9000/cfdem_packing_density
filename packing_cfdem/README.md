# CFD-DEM混合边界耦合案例

## 项目简介

这是一个基于CFDEM框架的CFD-DEM流固耦合仿真案例，专门用于研究颗粒在圆柱筒内水中的沉降和堆积行为。

### 技术特点

- **混合边界方案**：创新的上部STL边界+下部CFD-DEM耦合处理方法
- **5次循环填充**：完整保留原始DEM实验的循环填充-排放机制  
- **版本兼容性**：解决了LIGGGHTS-PFM与LIGGGHTS-PUBLIC的语法差异
- **并行计算**：支持MPI并行，提高计算效率

### 物理模型

- **几何**：圆柱筒（内径0.28m，高度1.14m）
- **流体**：纯水环境（密度1000 kg/m³）
- **颗粒**：两种尺寸球形颗粒（密度2500 kg/m³）
  - 大颗粒：半径0.012m，比例20%
  - 小颗粒：半径0.010m，比例80%
- **力模型**：拖拽力、浮力、压力梯度力、虚质量力

## 快速开始

### 环境要求

- OpenFOAM 5.x 或更高版本
- LIGGGHTS-PFM 或兼容版本
- CFDEM 框架
- MPI 并行环境

### 运行方式

```bash
# 标准运行（推荐）
./Allrun.sh

# 或者使用标准CFDEM方式
bash parCFDDEMrun.sh
```

### 清理数据

```bash
./cleanup.sh
```

## 文件结构

```
packing_cfdem/
├── Allrun.sh              # 主运行脚本
├── parCFDDEMrun.sh        # CFDEM标准并行运行脚本  
├── cleanup.sh             # 清理脚本
├── CFD/                   # CFD配置目录
│   ├── 0/                 # 初始和边界条件
│   ├── constant/          # 物理属性和耦合参数
│   └── system/            # 求解器设置
├── DEM/                   # DEM配置目录  
│   ├── in.liggghts_hybrid_cycles  # 主要DEM配置
│   └── post/              # DEM结果输出
└── STL/                   # 几何文件
    ├── Silo.stl           # 圆柱筒几何
    └── Lid.stl            # 底部挡板几何
```

## 技术创新

### 混合边界处理
- **上部区域**（Z=0.86-1.14m）：STL边界，保持几何约束
- **下部区域**（Z=0-0.86m）：CFD-DEM耦合，流固相互作用

### 版本兼容性解决
解决了LIGGGHTS不同版本间的语法差异：
```liggghts
# PFM兼容写法
compute ke_atom all ke/atom
fix avg_ke_fix all ave/time 100 1 100 c_ke_atom mode scalar
variable avg_ke_var equal f_avg_ke_fix
```

## 结果分析

### 数据输出
- **CFD数据**：`CFD/VTK/` - 流场可视化
- **DEM数据**：`DEM/post/particles_*.vtk` - 颗粒轨迹
- **耦合数据**：`CFD/post/` - 动态边界和耦合信息

### ParaView可视化
```bash
# 查看流场
paraview CFD/VTK/CFD_*.vtk

# 查看颗粒运动
paraview DEM/post/particles_*.vtk
```

## 性能特点

- **计算效率**：4核并行，约13秒完成5次循环仿真
- **内存需求**：每核13-17MB
- **数据规模**：600+时间步，1200+动态STL文件
- **网格规模**：138,000个六面体单元

## 参考文档

详细的技术文档和实施方案请参考：`CFD-DEM耦合移植计划.md`

## 问题反馈

如遇到技术问题，请检查：
1. CFDEM环境变量设置
2. LIGGGHTS版本兼容性  
3. MPI配置是否正确
4. STL文件路径是否正确

## 版权说明

本案例基于开源CFDEM框架开发，遵循相应开源协议。