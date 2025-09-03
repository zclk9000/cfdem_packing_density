import bpy
import bmesh
import math

# 参数
inner_r1 = 0.14   # 第一段内半径（圆柱段）
inner_r3 = 0.07   # 第三段内半径（出口段）
thickness = 0.01  # 壁厚（设为0时生成曲面，非0时生成实体）
outer_r1 = inner_r1 + thickness
outer_r3 = inner_r3 + thickness

h1 = 0.14         # 第一段高度（圆柱段）
h2 = 0.07         # 第二段高度（锥形过渡段）
h3 = 0.07         # 第三段高度（出口段）

segments = 100   # 圆周分段数
position = (0, 0, 0)  # 模型摆放位置（漏斗底面中心在全局坐标系中的位置）
name = "ThickFunnel" if thickness > 0 else "SurfaceFunnel"  # 物体名称

# 删除已有同名物体（可选）
if name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

# 新建 mesh
mesh = bpy.data.meshes.new(name)
obj = bpy.data.objects.new(name, mesh)
bpy.context.collection.objects.link(obj)
bm = bmesh.new()

if thickness == 0:
    # ===== 曲面模式（厚度为0）=====
    print("生成曲面漏斗...")
    
    # 生成顶点（相对于坐标原点）
    top_verts = []
    mid_top_verts = []
    mid_bottom_verts = []
    bottom_verts = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x1 = inner_r1 * math.cos(angle)
        y1 = inner_r1 * math.sin(angle)
        z1 = h1 + h2 + h3
        x2 = inner_r1 * math.cos(angle)
        y2 = inner_r1 * math.sin(angle)
        z2 = h2 + h3
        x3 = inner_r3 * math.cos(angle)
        y3 = inner_r3 * math.sin(angle)
        z3 = h3
        x4 = inner_r3 * math.cos(angle)
        y4 = inner_r3 * math.sin(angle)
        z4 = 0
        
        top_verts.append(bm.verts.new((x1, y1, z1)))
        mid_top_verts.append(bm.verts.new((x2, y2, z2)))
        mid_bottom_verts.append(bm.verts.new((x3, y3, z3)))
        bottom_verts.append(bm.verts.new((x4, y4, z4)))
    
    bm.verts.ensure_lookup_table()
    
    # 生成曲面
    for i in range(segments):
        # 第一段面
        bm.faces.new([
            top_verts[i],
            mid_top_verts[i],
            mid_top_verts[(i + 1) % segments],
            top_verts[(i + 1) % segments]
        ])
        # 第二段面（锥形）
        bm.faces.new([
            mid_top_verts[i],
            mid_bottom_verts[i],
            mid_bottom_verts[(i + 1) % segments],
            mid_top_verts[(i + 1) % segments]
        ])
        # 第三段面
        bm.faces.new([
            mid_bottom_verts[i],
            bottom_verts[i],
            bottom_verts[(i + 1) % segments],
            mid_bottom_verts[(i + 1) % segments]
        ])
    
    # 生成顶盖（三角形剖分）
    top_center = bm.verts.new((0, 0, h1 + h2 + h3))  # 顶面中心点
    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = top_verts[next_i]  # 注意顺序，确保法向量向下
        v1 = top_verts[i]
        v2 = top_center
        bm.faces.new([v0, v1, v2])

else:
    # ===== 实体模式（厚度不为0）=====
    print("生成实体漏斗...")
    
    # 生成顶点（相对于坐标原点，外圈和内圈）
    top_outer = []
    mid_top_outer = []
    mid_bottom_outer = []
    bottom_outer = []

    top_inner = []
    mid_top_inner = []
    mid_bottom_inner = []
    bottom_inner = []

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        # 外圈
        x1o = outer_r1 * math.cos(angle)
        y1o = outer_r1 * math.sin(angle)
        z1 = h1 + h2 + h3
        x2o = outer_r1 * math.cos(angle)  # 第二段顶部，与第一段相同
        y2o = outer_r1 * math.sin(angle)
        z2 = h2 + h3
        x3o = outer_r3 * math.cos(angle)  # 第二段底部，与第三段相同
        y3o = outer_r3 * math.sin(angle)
        z3 = h3
        x4o = outer_r3 * math.cos(angle)
        y4o = outer_r3 * math.sin(angle)
        z4 = 0
        top_outer.append(bm.verts.new((x1o, y1o, z1)))
        mid_top_outer.append(bm.verts.new((x2o, y2o, z2)))
        mid_bottom_outer.append(bm.verts.new((x3o, y3o, z3)))
        bottom_outer.append(bm.verts.new((x4o, y4o, z4)))
        # 内圈
        x1i = inner_r1 * math.cos(angle)
        y1i = inner_r1 * math.sin(angle)
        x2i = inner_r1 * math.cos(angle)  # 第二段顶部，与第一段相同
        y2i = inner_r1 * math.sin(angle)
        x3i = inner_r3 * math.cos(angle)  # 第二段底部，与第三段相同
        y3i = inner_r3 * math.sin(angle)
        x4i = inner_r3 * math.cos(angle)
        y4i = inner_r3 * math.sin(angle)
        top_inner.append(bm.verts.new((x1i, y1i, z1)))
        mid_top_inner.append(bm.verts.new((x2i, y2i, z2)))
        mid_bottom_inner.append(bm.verts.new((x3i, y3i, z3)))
        bottom_inner.append(bm.verts.new((x4i, y4i, z4)))

    bm.verts.ensure_lookup_table()

    # 生成外壁
    for i in range(segments):
        # 第一段外壁（圆柱）
        bm.faces.new([
            top_outer[i],
            mid_top_outer[i],
            mid_top_outer[(i + 1) % segments],
            top_outer[(i + 1) % segments]
        ])
        # 第二段外壁（锥形）
        bm.faces.new([
            mid_top_outer[i],
            mid_bottom_outer[i],
            mid_bottom_outer[(i + 1) % segments],
            mid_top_outer[(i + 1) % segments]
        ])
        # 第三段外壁（圆柱）
        bm.faces.new([
            mid_bottom_outer[i],
            bottom_outer[i],
            bottom_outer[(i + 1) % segments],
            mid_bottom_outer[(i + 1) % segments]
        ])

    # 生成内壁
    for i in range(segments):
        # 第一段内壁（圆柱）
        bm.faces.new([
            top_inner[(i + 1) % segments],
            mid_top_inner[(i + 1) % segments],
            mid_top_inner[i],
            top_inner[i]
        ])
        # 第二段内壁（锥形）
        bm.faces.new([
            mid_top_inner[(i + 1) % segments],
            mid_bottom_inner[(i + 1) % segments],
            mid_bottom_inner[i],
            mid_top_inner[i]
        ])
        # 第三段内壁（圆柱）
        bm.faces.new([
            mid_bottom_inner[(i + 1) % segments],
            bottom_inner[(i + 1) % segments],
            bottom_inner[i],
            mid_bottom_inner[i]
        ])

    # 生成下口和中间连接面（移除上口，因为已被顶盖替换）
    for i in range(segments):
        # 下口
        bm.faces.new([
            bottom_outer[(i + 1) % segments],
            bottom_outer[i],
            bottom_inner[i],
            bottom_inner[(i + 1) % segments]
        ])
        # 第一段底/第二段顶连接
        bm.faces.new([
            mid_top_outer[(i + 1) % segments],
            mid_top_outer[i],
            mid_top_inner[i],
            mid_top_inner[(i + 1) % segments]
        ])
        # 第二段底/第三段顶连接
        bm.faces.new([
            mid_bottom_outer[(i + 1) % segments],
            mid_bottom_outer[i],
            mid_bottom_inner[i],
            mid_bottom_inner[(i + 1) % segments]
        ])
    
    # 生成完全封闭的顶盖
    top_center = bm.verts.new((0, 0, h1 + h2 + h3))  # 顶面中心点
    for i in range(segments):
        next_i = (i + 1) % segments
        # 外圈三角形（法向量向上）
        bm.faces.new([
            top_outer[i],
            top_outer[next_i], 
            top_center
        ])
        # 内圈三角形（法向量向下）
        bm.faces.new([
            top_inner[next_i],
            top_inner[i],
            top_center
        ])
        # 连接外圈和内圈的环形面
        bm.faces.new([
            top_outer[i],
            top_inner[i],
            top_inner[next_i],
            top_outer[next_i]
        ])

# 写入 mesh
bm.to_mesh(mesh)
bm.free()

# 设置原点到坐标原点（底面中心）
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# 移动模型到指定位置
obj.location = position

if thickness == 0:
    print("已生成曲面漏斗：上段内径=%.3f，下段内径=%.3f，位置=%s，分段数=%d" % (inner_r1, inner_r3, position, segments))
else:
    print("已生成实体漏斗：上段内径=%.3f，下段内径=%.3f，壁厚=%.3f，位置=%s，分段数=%d" % (inner_r1, inner_r3, thickness, position, segments))