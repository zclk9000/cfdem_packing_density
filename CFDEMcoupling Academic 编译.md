# CFDEMcoupling Academic 编译

## 编译环境信息

### 系统环境

- **操作系统**: Ubuntu 20.04.6 LTS (Focal Fossa)
- **OpenFOAM**: 5.x（官方建议用openfoam 6 版本，见Q1: 版本兼容性问题）
- **LIGGGHTS**: PFM版本 24.01
- **CFDEMcoupling**: PFM版本 24.01
- **编译器**: g++ 9.4.0

## 重要补充：架构兼容性要求

### 🚨 **架构兼容性要求**

**重要提示**：OpenFOAM版本与系统架构的兼容性

- **OpenFOAM 5.x**: 仅支持 x86_64 和 ARM32 (armv7l)，不支持 ARM64 (aarch64)
- **OpenFOAM 6.x**: 支持 x86_64 和 ARM64 (aarch64)，但需要特殊配置
- **ARM64用户**: 强烈建议使用 OpenFOAM 6.x 或更高版本

**ARM64架构特殊配置**：
1. 在 `etc/config.sh/settings` 中添加 aarch64 支持
2. 修改 `wmake/rules/linux64Gcc/c` 和 `c++` 文件，移除 `-m64` 参数

### 🔧 **OpenFOAM 5.x ARM64架构配置（实验性）**

#### 步骤1：添加ARM64架构支持
编辑 `$WM_PROJECT_DIR/etc/config.sh/settings`，在 armv7l 部分后添加：

```bash
aarch64)
    WM_ARCH=linux64
    export WM_ARCH_OPTION=64
    export WM_COMPILER_LIB_ARCH=64
    export WM_CC='gcc'
    export WM_CXX='g++'
    export WM_CFLAGS='-fPIC'
    export WM_CXXFLAGS='-fPIC -std=c++0x'
    export WM_LDFLAGS=
    ;;
```

#### 步骤2：修复wmake规则文件
修改 `wmake/rules/linux64Gcc/c`：
```bash
# 将 cc = gcc -m64 改为 cc = gcc
```

修改 `wmake/rules/linux64Gcc/c++`：
```bash
# 将 CC = g++ -std=c++11 -m64 改为 CC = g++ -std=c++11
```

**注意**：此配置为实验性，建议优先使用OpenFOAM 6.x

### 🔧 **OpenFOAM 6.x ARM64架构配置（推荐）**

#### 步骤1：添加ARM64架构支持
编辑 `$WM_PROJECT_DIR/etc/config.sh/settings`，在 armv7l 部分后添加：

```bash
aarch64)
    WM_ARCH=linux64
    export WM_ARCH_OPTION=64
    export WM_COMPILER_LIB_ARCH=64
    export WM_CC='gcc'
    export WM_CXX='g++'
    export WM_CFLAGS='-fPIC'
    export WM_CXXFLAGS='-fPIC -std=c++0x'
    export WM_LDFLAGS=
    ;;
```

#### 步骤2：修复wmake规则文件
修改 `wmake/rules/linux64Gcc/c`：
```bash
# 将 cc = gcc -m64 改为 cc = gcc
```

修改 `wmake/rules/linux64Gcc/c++`：
```bash
# 将 CC = g++ -std=c++11 -m64 改为 CC = g++ -std=c++11
```

## 已验证成功的版本组合

### 🎯 **推荐配置**：
- **操作系统**: Ubuntu 20.04.6 LTS
- **架构**: ARM64 (aarch64)
- **OpenFOAM**: 6.x (经过ARM64适配)
- **LIGGGHTS**: PFM 24.01
- **CFDEMcoupling**: PFM 24.01
- **编译器**: gcc 9.4.0

### ✅ **编译结果**：
- ✅ OpenFOAM 6.x 核心库和工具
- ✅ LIGGGHTS-PFM 24.01 可执行文件和库
- ✅ CFDEMcoupling-PFM 24.01 所有标准求解器
- ✅ 系统测试通过

## 正确的目录结构设置

### 📁 **重要**：LIGGGHTS必须放在CFDEM目录下作为库

```bash
$HOME/
├── OpenFOAM/
│   ├── OpenFOAM-6/
│   └── ThirdParty-6/
├── CFDEM/
│   ├── CFDEMcoupling/          # CFDEM主目录
│   └── LIGGGHTS/               # LIGGGHTS库目录
└── LIGGGHTS/                   # 临时目录（编译完成后可删除）
```

### 🔧 **设置步骤**：
1. 将LIGGGHTS源码放在 `$HOME/CFDEM/LIGGGHTS/`
2. 确保CFDEM环境变量指向正确路径
3. 使用 `cfdemCompLIG` 编译LIGGGHTS

## 环境变量验证清单

### ✅ **编译前必须验证以下环境变量**：

```bash
# 检查OpenFOAM环境
echo $WM_PROJECT_DIR          # 应显示OpenFOAM路径
echo $WM_ARCH                 # ARM64应显示linux64

# 检查CFDEM环境
echo $CFDEM_PROJECT_DIR       # 应显示CFDEM路径
echo $CFDEM_LIGGGHTS_INST_DIR # 应显示LIGGGHTS路径

# 检查LIGGGHTS命令
which liggghts                # 应显示LIGGGHTS可执行文件路径
```

## 编译顺序和依赖关系

### 🔄 **正确的编译顺序**：
1. OpenFOAM 6.x 核心库
2. OpenFOAM 6.x 第三方包
3. LIGGGHTS-PFM 24.01
4. CFDEMcoupling-PFM 24.01

### 🔗 **依赖关系**：
- CFDEMcoupling 依赖 OpenFOAM 6.x
- CFDEMcoupling 依赖 LIGGGHTS-PFM
- LIGGGHTS 可以独立编译，但建议放在CFDEM目录下

## 安装流程

### 1. 安装OpenFOAM

#### 获取源代码

```bash
cd $HOME
mkdir OpenFOAM
cd OpenFOAM
git clone https://github.com/OpenFOAM/OpenFOAM-5.x.git
git clone https://github.com/OpenFOAM/ThirdParty-5.x.git
```

#### 安装依赖包

```bash
sudo su -
apt-get install build-essential flex bison git-core cmake zlib1g-dev libboost-system-dev libboost-thread-dev libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev libxt-dev
apt-get install libqt5x11extras5-dev libxt-dev qt5-default qttools5-dev curl
```

#### 设置环境

```bash
gedit ~/.bashrc
```

添加以下内容：

```bash
source $HOME/OpenFOAM/OpenFOAM-5.x/etc/bashrc
export WM_NCOMPPROCS=8 #编译采用8核心
```

重新加载环境：

```bash
source ~/.bashrc
```

#### 编译第三方包

```bash
cd $WM_THIRD_PARTY_DIR
./Allwmake
```

#### 编译Paraview（可选 ）

```bash
cd $WM_THIRD_PARTY_DIR
./makeParaView
```

#### 编译OpenFOAM

```bash
cd $WM_PROJECT_DIR
./Allwmake
```

#### 测试安装

```bash
mkdir -p $FOAM_RUN
cp -r $FOAM_TUTORIALS $FOAM_RUN
cd $FOAM_RUN/tutorials/incompressible/icoFoam/cavity/cavity
blockMesh
icoFoam
paraFoam
```

### 2. 安装CFDEMcoupling

#### 下载源代码

```bash
cd $HOME
mkdir LIGGGHTS
cd LIGGGHTS
git clone https://github.com/ParticulateFlow/LPP.git
git clone https://github.com/ParticulateFlow/LIGGGHTS-PFM.git

cd $HOME
mkdir CFDEM
cd CFDEM
git clone https://github.com/ParticulateFlow/CFDEMcoupling.git
```

#### 配置环境

```bash
gedit ~/CFDEM/CFDEMcoupling/etc/bashrc &
```

根据实际情况修改环境文件，例如openfoam版本，liggghts路径等等

编辑标记为 *USER EDITABLE PART* 的行。
保存后重新加载：

```bash
source ~/CFDEM/CFDEMcoupling/etc/bashrc
```

#### 编译LIGGGHTS

```bash
cfdemCompLIG
```

#### 编译CFDEMcoupling

```bash
cfdemCompCFDEM
```

或者分步编译：

```bash
cfdemCompCFDEMsrc
cfdemCompCFDEMsol
cfdemCompCFDEMuti
```

#### 验证安装

```bash
cfdemSysTest
```

#### 安装后处理工具

```bash
sudo apt-get install octave
```

#### 运行测试案例

```bash
cfdemTestTUT
```

## 设置LIGGGHTS命令路径

**目的**: 使 `liggghts`命令在终端中可直接使用

**设置步骤**:

```bash
# 添加LIGGGHTS路径到.bashrc
echo 'export LIGGGHTS_BIN_DIR=$HOME/CFDEM/LIGGGHTS/src-build' >> ~/.bashrc
echo 'export PATH=$PATH:$LIGGGHTS_BIN_DIR' >> ~/.bashrc

# 重新加载环境
source ~/.bashrc

# 验证设置
which liggghts
liggghts -help
```

## 常见问题与解答

### Q1: 版本兼容性问题

**问题**: CFDEMcoupling-PFM与OpenFOAM版本的兼容性如何？

**答案**:

- CFDEMcoupling-PFM 20.05版本声明支持OpenFOAM 4.x/5.x/6
- 但某些求解器有硬编码版本限制，只允许OpenFOAM 4.x或5.x
- 可使用OpenFOAM-5.x进行编译

使用OpenFOAM-5.x 编译CFDEMcoupling-PFM 24.01版本时，以下求解器编译失败：

- rcfdemSolverRhoSteadyPimpleChem - 化学反应稳态可压缩流求解器

  失败原因：

```

  rcfdemSolverRhoSteadyPimpleChem.C:103:59: error: 'small' was not declared in this scope; did you mean 'psmall'?

```

  解决方案：

- 在源代码中定义small变量或使用psmall替代
- 检查OpenFOAM-5.x中small变量的正确声明方式
- 不使用该求解器可以忽略错误

**使用OpenFOAM-6 进行编译受版本限制的求解器**:

1. cfdemSolverMultiphase - 多相流CFD-DEM求解器
2. cfdemSolverMultiphaseScalar - 多相流+标量传输CFD-DEM求解器

**版本限制代码**:

```cpp
#if OPENFOAM_VERSION_MAJOR >= 6
    FatalError << "cfdemSolverMultiphase requires OpenFOAM 4.x or 5.x to work properly" << exit(FatalError);
#endif
```

### Q2: 编译错误处理

**问题**: 编译LIGGGHTS时出现错误怎么办？

**错误信息**:

```
No rule to make target '/usr/lib/libpython2.7.so'
```

**解决方案**: 为有问题的库创建符号链接

### Q3: Ubuntu版本依赖包差异

**问题**: 不同Ubuntu版本的依赖包安装命令有差异吗？

**答案**: 是的，Ubuntu 21.04及更新版本移除了*qt5-default*包，需要使用不同的安装命令。

**Ubuntu 20.04及以下版本**:

```bash
apt-get install build-essential flex bison git-core cmake zlib1g-dev libboost-system-dev libboost-thread-dev libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev libxt-dev
apt-get install libqt5x11extras5-dev libxt-dev qt5-default qttools5-dev curl
```

**Ubuntu 21.04及更新版本**:

```bash
apt-get install build-essential flex bison git-core cmake zlib1g-dev libboost-system-dev libboost-thread-dev libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev libxt-dev
apt-get install libqt5x11extras5-dev libxt-dev qttools5-dev qttools5-dev-tools qtwebengine5-dev libqt5svg5-dev libqt5websockets5-dev libqt5xmlpatterns5 qtxmlpatterns5-dev-tools curl
```

### Q4: Paraview编译问题

**问题**: 编译Paraview时遇到VTK错误？

**错误信息**:

```
VTK/ThirdParty/hdf5/vtkhdf5/src/H5detect.c:158:1: error: unknown type name 'sigjmp_buf'
static H5JMP_BUF jbuf_g;
```

**解决方案**:
在VTK/ThirdParty/hdf5/config/cmake/ConfigureChecks.cmake的第445行左右，将：

```cmake
set (HDF5_EXTRA_FLAGS -D_DEFAULT_SOURCE -D_BSD_SOURCE)
```

更改为：

```cmake
set (HDF5_EXTRA_FLAGS -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_BSD_SOURCE)
```

### Q5: 环境变量设置

**问题**: 如何检查环境变量是否正确设置？

**检查方法**:

```bash
echo $CFDEM_PROJECT_DIR
```

如果输出"... is a directory"，说明设置正确。

**问题**: MPI设置问题？

**解决方案**:
检查~/OpenFOAM/OpenFOAM-6/etc/bashrc中的WM_MPLIB设置：

```bash
export WM_MPLIB=SYSTEMOPENMPI
```

### Q6: 编译日志查看

**问题**: 如何查看编译过程的日志？

**方法**:

```bash
cd ~/CFDEM/CFDEMcoupling/etc/log
ls
```

如果存在文件 **log_compile_results_success**，则编译成功。

### Q7: 其他求解器状态

**问题**: 哪些求解器支持OpenFOAM-6？

**答案**:

- cfdemSolverPiso/Pimple/IB等：无版本限制，支持OpenFOAM-6
- cfdemSolverRhoPimple系列：使用条件编译，兼容多版本

### Q8: 编译失败记录

**问题**: 哪些求解器编译失败？

**答案**:
使用OpenFOAM-5.x编译CFDEMcoupling-PFM 24.01版本时，以下求解器编译失败：

1. rcfdemSolverRhoSteadyPimpleChem - 化学反应稳态可压缩流求解器

**失败原因**: small变量未定义
**解决方案**: 在源代码中定义small变量或使用psmall替代

### Q9: ARM架构兼容性问题

**问题**: ARM64架构上编译OpenFOAM遇到架构不兼容错误？

**错误信息**:
```
cc: error: unrecognized command line option '-m64'
```

**解决方案**:
1. 在`etc/config.sh/settings`中添加`aarch64`架构支持
2. 修改`wmake/rules/linux64Gcc/c`和`c++`文件，移除`-m64`参数
3. 或者直接使用OpenFOAM 6.x版本（推荐）

**推荐方案**: 对于ARM64用户，建议使用OpenFOAM 6.x，兼容性更好
