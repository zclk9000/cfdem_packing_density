import bpy
import bmesh
import math

# 参数
inner_radius = 0.14  # 内半径
thickness = 0     # 壁厚（设为0时生成曲面，非0时生成实体）
outer_radius = inner_radius + thickness
height = 1.0            # 筒壁净高度（不包含底板厚度）
bottom_thickness = 0.01 # 底板厚度
segments = 50          # 圆周分段数
position = (0, 0, 0.0)    # 模型摆放位置（底面中心在全局坐标系中的位置）
name = "SolidHollowCylinder" if thickness > 0 else "SurfaceCylinder"  # 物体名称

# 删除已有同名物体（可选）
if name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

if thickness == 0:
    # ===== 曲面模式（厚度为0）=====
    print("生成曲面圆柱筒...")
    
    # 新建 mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    
    # 生成顶点（相对于坐标原点）
    top_verts = []
    bottom_verts = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = inner_radius * math.cos(angle)
        y = inner_radius * math.sin(angle)
        z_top = height
        z_bottom = 0
        top_verts.append(bm.verts.new((x, y, z_top)))
        bottom_verts.append(bm.verts.new((x, y, z_bottom)))
    
    bm.verts.ensure_lookup_table()
    
    # 生成侧面
    for i in range(segments):
        v0 = top_verts[i]
        v1 = bottom_verts[i]
        v2 = bottom_verts[(i + 1) % segments]
        v3 = top_verts[(i + 1) % segments]
        bm.faces.new([v0, v1, v2, v3])
    
    # 封底（三角形剖分）
    bottom_center = bm.verts.new((0, 0, 0))  # 底面中心点
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = bottom_verts[i]  # 注意顺序，确保法向量向上
        v1 = bottom_verts[next_i]
        v2 = bottom_center
        bm.faces.new([v0, v1, v2])
    
    # 写入 mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # 移动模型到指定位置（保持原点在坐标原点）
    obj.location = position
    
    print("已生成曲面圆柱筒（带底），内半径=%.3f，净高=%.3f，位置=%s，分段数=%d" % (inner_radius, height, position, segments))

else:
    # ===== 实体模式（厚度不为0）- 直接生成mesh避免布尔运算=====
    print("生成实体圆柱筒...")
    
    # 计算总高度（净高度 + 底板厚度）
    total_height = height + bottom_thickness
    
    # 新建 mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    
    # 生成顶点
    outer_top_verts = []
    outer_bottom_verts = []
    inner_top_verts = []
    inner_bottom_verts = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 外圆顶点
        outer_top_verts.append(bm.verts.new((outer_radius * cos_a, outer_radius * sin_a, total_height)))
        outer_bottom_verts.append(bm.verts.new((outer_radius * cos_a, outer_radius * sin_a, 0)))
        
        # 内圆顶点（从底板上表面开始）
        inner_top_verts.append(bm.verts.new((inner_radius * cos_a, inner_radius * sin_a, total_height)))
        inner_bottom_verts.append(bm.verts.new((inner_radius * cos_a, inner_radius * sin_a, bottom_thickness)))
    
    bm.verts.ensure_lookup_table()
    
    # 生成外侧面
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = outer_top_verts[i]
        v1 = outer_bottom_verts[i]
        v2 = outer_bottom_verts[next_i]
        v3 = outer_top_verts[next_i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 生成内侧面
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = inner_top_verts[next_i]
        v1 = inner_bottom_verts[next_i]
        v2 = inner_bottom_verts[i]
        v3 = inner_top_verts[i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 生成顶面环形面
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = outer_top_verts[i]
        v1 = inner_top_verts[i]
        v2 = inner_top_verts[next_i]
        v3 = outer_top_verts[next_i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 生成底板（实心圆盘，厚度为bottom_thickness）
    # 底板底面中心点和底面内圆顶点
    center_bottom = bm.verts.new((0, 0, 0))
    inner_bottom_bottom_verts = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        inner_bottom_bottom_verts.append(bm.verts.new((inner_radius * cos_a, inner_radius * sin_a, 0)))
    
    bm.verts.ensure_lookup_table()
    
    # 底板底面：从中心到内圆的三角形面
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = center_bottom
        v1 = inner_bottom_bottom_verts[next_i]  # 注意顺序，确保法向量向下
        v2 = inner_bottom_bottom_verts[i]
        bm.faces.new([v0, v1, v2])
    
    # 底板底面环形部分
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = inner_bottom_bottom_verts[i]
        v1 = inner_bottom_bottom_verts[next_i]
        v2 = outer_bottom_verts[next_i]
        v3 = outer_bottom_verts[i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 底板顶面：从中心到内圆的三角形面
    center_top = bm.verts.new((0, 0, bottom_thickness))
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = center_top
        v1 = inner_bottom_verts[i]
        v2 = inner_bottom_verts[next_i]
        bm.faces.new([v0, v1, v2])
    
    # 底板顶面环形部分
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = inner_bottom_verts[next_i]
        v1 = outer_bottom_verts[next_i]
        v2 = outer_bottom_verts[i]
        v3 = inner_bottom_verts[i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 底板内圆侧面（从底面到顶面）
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = inner_bottom_bottom_verts[i]
        v1 = inner_bottom_verts[i]
        v2 = inner_bottom_verts[next_i]
        v3 = inner_bottom_bottom_verts[next_i]
        bm.faces.new([v0, v1, v2, v3])
    
    # 确保法向量正确
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    # 写入 mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # 移动模型到指定位置
    obj.location = position
    
    print("已生成实体圆柱筒（带底），内半径=%.3f，壁厚=%.3f，净高=%.3f，底厚=%.3f，总高=%.3f，位置=%s，分段数=%d" % (inner_radius, thickness, height, bottom_thickness, total_height, position, segments))
