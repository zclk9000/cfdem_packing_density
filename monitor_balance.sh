#!/bin/bash

#===================================================================#
# CFD-DEM平衡状态监控脚本 - 方案C
# 监控DEM输出的速度数据并在达到平衡时终止仿真
#===================================================================#

# 监控参数
AVG_VEL_THRESHOLD=0.3    # 平均速度阈值 (m/s)
MAX_VEL_THRESHOLD=0.5    # 最大速度阈值 (m/s)  
MAX_SIM_TIME=604800        # 最大仿真时间 (秒) - 7天，仅作极端情况保护
CHECK_INTERVAL=60         # 检查间隔 (秒)
VELOCITY_FILE="../DEM/monitor/velocity.dat"
ABORT_FILE="ABORT"

# 获取CFD-DEM进程PID (通过进程名查找)
get_cfd_pid() {
    pgrep -f "cfdemSolverMultiphase" | head -1
}

DEBUG_FILE="monitor_debug.log"

echo "启动CFD-DEM平衡状态监控..." | tee $DEBUG_FILE
echo "平衡判断阈值: 平均速度 < ${AVG_VEL_THRESHOLD} m/s, 最大速度 < ${MAX_VEL_THRESHOLD} m/s" | tee -a $DEBUG_FILE
echo "最大仿真时间: ${MAX_SIM_TIME} 秒" | tee -a $DEBUG_FILE
echo "检查间隔: ${CHECK_INTERVAL} 秒" | tee -a $DEBUG_FILE
echo "监控文件: ${VELOCITY_FILE}" | tee -a $DEBUG_FILE

# 清理之前的ABORT文件
rm -f ${ABORT_FILE}

start_time=$(date +%s)
last_check_time=0
converged=false

while true; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    
    # 检查CFD-DEM进程是否还在运行
    CFD_PID=$(get_cfd_pid)
    #echo "调试: 进程查找结果: CFD_PID=$CFD_PID" | tee -a $DEBUG_FILE
    if [[ -z "$CFD_PID" ]]; then
        echo "CFD-DEM进程已结束" | tee -a $DEBUG_FILE
        echo "调试: 当前所有cfdem相关进程:" | tee -a $DEBUG_FILE
        ps aux | grep cfdem | grep -v grep | tee -a $DEBUG_FILE
        break
    fi
    
    # 检查是否超过最大仿真时间
    if (( elapsed_time > MAX_SIM_TIME )); then
        echo "达到最大仿真时间 ${MAX_SIM_TIME} 秒，终止仿真"
        touch ${ABORT_FILE}
        kill -TERM $CFD_PID 2>/dev/null
        break
    fi
    
    # 定期检查速度（每CHECK_INTERVAL秒）
    #echo "调试: elapsed_time=$elapsed_time, last_check_time=$last_check_time, 差值=$((elapsed_time - last_check_time))" | tee -a $DEBUG_FILE
    if (( elapsed_time - last_check_time >= CHECK_INTERVAL )); then
        #echo "调试: 进入速度检查逻辑" | tee -a $DEBUG_FILE
        #echo "调试: 检查文件 ${VELOCITY_FILE}" | tee -a $DEBUG_FILE
        #echo "调试: 文件存在检查: -f ${VELOCITY_FILE} = $([ -f ${VELOCITY_FILE} ] && echo true || echo false)" | tee -a $DEBUG_FILE
        #echo "调试: 文件非空检查: -s ${VELOCITY_FILE} = $([ -s ${VELOCITY_FILE} ] && echo true || echo false)" | tee -a $DEBUG_FILE
        if [[ -f ${VELOCITY_FILE} ]] && [[ -s ${VELOCITY_FILE} ]]; then
            #echo "调试: 监控文件存在且不为空" | tee -a $DEBUG_FILE
            # 从速度监控文件中读取最新数据
            latest_line=$(tail -n 1 ${VELOCITY_FILE} | grep -v "^#")
            
            if [[ ! -z "$latest_line" ]]; then
                # 解析数据: time avg_vel max_vel
                read -r sim_time avg_vel max_vel <<< "$latest_line"
                
                if [[ ! -z "$avg_vel" ]] && [[ ! -z "$max_vel" ]]; then
                    echo "仿真时间: ${elapsed_time}s, DEM时间: ${sim_time}s, 平均速度: ${avg_vel} m/s, 最大速度: ${max_vel} m/s" | tee -a $DEBUG_FILE
                    
                    # 检查平衡条件（改进的浮点数比较）
                    avg_check=$(awk -v a="$avg_vel" -v b="$AVG_VEL_THRESHOLD" 'BEGIN{print (a < b)}')
                    max_check=$(awk -v a="$max_vel" -v b="$MAX_VEL_THRESHOLD" 'BEGIN{print (a < b)}')
                    
                    #echo "调试: avg_check=$avg_check (${avg_vel} < ${AVG_VEL_THRESHOLD}), max_check=$max_check (${max_vel} < ${MAX_VEL_THRESHOLD})" | tee -a $DEBUG_FILE
                    
                    if [[ $avg_check -eq 1 ]] && [[ $max_check -eq 1 ]]; then
                        echo "达到平衡状态！平均速度: ${avg_vel} m/s < ${AVG_VEL_THRESHOLD} m/s, 最大速度: ${max_vel} m/s < ${MAX_VEL_THRESHOLD} m/s" | tee -a $DEBUG_FILE
                        echo "创建终止信号文件: ${ABORT_FILE}" | tee -a $DEBUG_FILE
                        touch ${ABORT_FILE}
                        converged=true
                        
                        # 等待CFD求解器检测到ABORT文件并自然终止
                        echo "等待CFD-DEM求解器自然终止..."
                        wait_count=0
                        while kill -0 $CFD_PID 2>/dev/null && [[ $wait_count -lt 30 ]]; do
                            sleep 2
                            wait_count=$((wait_count + 1))
                        done
                        
                        # 如果还没终止，手动终止
                        if kill -0 $CFD_PID 2>/dev/null; then
                            echo "手动终止CFD-DEM求解器..."
                            kill -TERM $CFD_PID
                        fi
                        break
                    fi
                else
                    echo "警告: 无法解析速度数据: $latest_line"
                fi
            else
                echo "等待速度数据更新..."
            fi
        else
            echo "等待监控文件生成: ${VELOCITY_FILE}" | tee -a $DEBUG_FILE
        fi
        
        last_check_time=$elapsed_time
    fi
    
    sleep 2
done

final_time=$(date +%s)
total_time=$((final_time - start_time))

if [[ $converged == true ]]; then
    echo "监控完成 - 颗粒达到平衡状态"
    echo "总监控时间: ${total_time} 秒"
    exit 0
else
    echo "监控结束 - 未达到平衡状态或进程异常终止"
    echo "总监控时间: ${total_time} 秒"
    exit 1
fi