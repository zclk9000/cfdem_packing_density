import bpy
import bmesh
import math

# =========================
# 参数设置
radius = 0.14      # 圆板半径（如0.14米=14cm）
thickness = 0.01   # 圆板厚度（设为0时生成圆平面，非0时生成实体）
position = (0, 0, 1.01)  # 模型摆放位置（下底面中心在全局坐标系中的位置）
segments = 100      # 圆周分段数，数值越大越光滑
name = "Circular_Plate" if thickness > 0 else "Circular_Face"  # 物体名称
# =========================

# 删除已有同名物体（可选）
if name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

if thickness == 0:
    # ===== 圆平面模式（厚度为0）=====
    print("生成圆平面...")
    
    # 创建圆平面（在坐标原点）
    bpy.ops.mesh.primitive_circle_add(
        radius=radius,
        location=(0, 0, 0),
        fill_type='NGON',  # 填充为面
        vertices=segments
    )
    
    # 获取生成的物体
    obj = bpy.context.active_object
    
    # 移动到指定位置
    obj.location = position
    
    # 重命名物体
    obj.name = name
    
    print(f"已生成圆平面：半径={radius}m，位置={position}，分段数={segments}")

else:
    # ===== 实体圆板模式（厚度不为0）=====
    print("生成实体圆板...")
    
    # 创建圆柱体（即圆板），让下底面在z=0，上底面在z=thickness
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=thickness,
        location=(0, 0, thickness/2),  # 几何中心在z=thickness/2，这样下底面在z=0
        vertices=segments
    )

    # 获取生成的物体
    obj = bpy.context.active_object
    
    # 设置原点到下底面中心（坐标原点）
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # 移动到指定位置
    obj.location = position

    # 重命名物体
    obj.name = name

    print(f"已生成实体圆板：半径={radius}m，厚度={thickness}m，下底面位置={position}，分段数={segments}")