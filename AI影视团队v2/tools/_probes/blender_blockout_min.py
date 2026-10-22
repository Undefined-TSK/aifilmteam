# -*- coding: utf-8 -*-
"""Blender 白模最小可行性验证（路线：Blender 白模占位 + 大模型写实化）

目的：验证「Blender 里把相机运动 / 灯光 / 道具位置 / 时间轴全定死并渲染成粗片」这一步
在 12GB 显存的 Windows 机器上**跑得通**，并给大模型后期提供确定性输入。

白模内容（极简几何体 + 能渲的全渲）：
  - 场景：平面地 + 三面方墙 + 雨棚板
  - 道具：寻猫启事薄板、猫窝方块、路灯（柱 + 灯头方块）
  - 人形占位：球头 + 圆柱身 + 双腿（无五官/表情/头发/皮肤材质）
  - 相机：dolly-in 推轨（位置关键帧）
  - 灯光：路灯点光 + 主光，亮度/色彩关键帧变化

用法：
  blender -b -P tools/_probes/blender_blockout_min.py -- --out <dir> [--frames 48] [--res 960x540] [--fps 24]
"""
import argparse
import math
import os
import sys

import bpy

# vram_lock 全引擎接入（R0-T6）：Blender 渲染期间独占显存锁。
# 本脚本在 tools/_probes/ 内，vram_lock.py 在 tools/，向上取一级注入 sys.path。
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    from vram_lock import vram_lock as _vram_lock
except Exception:  # 锁模块不可用时降级为 no-op（不阻塞渲染）
    import contextlib as _cl

    @_cl.contextmanager
    def _vram_lock(*a, **k):
        yield


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser("blender_blockout_min")
    p.add_argument("--out", required=True, help="输出目录")
    p.add_argument("--frames", type=int, default=48)
    p.add_argument("--res", default="960x540")
    p.add_argument("--fps", type=int, default=24)
    return p.parse_args(argv)


def make_mat(name, v):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (v, v, v, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.9
    return m


def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    return o


def cyl(name, loc, r, d, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    return o


def sph(name, loc, r, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    return o


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    g = make_mat("blockout_gray", 0.55)

    # 地面 + 三面墙 + 雨棚
    box("ground", (0, 0, 0), (14, 14, 0.1), g)
    box("wall_back", (0, 5.0, 2.0), (14, 0.2, 4.0), g)
    box("wall_left", (-5.0, 0, 2.0), (0.2, 10.0, 4.0), g)
    box("wall_right", (5.0, 0, 2.0), (0.2, 10.0, 4.0), g)
    box("awning", (0, 4.2, 3.2), (6.0, 1.6, 0.1), g)

    # 路灯：柱 + 灯头
    cyl("lamp_pole", (2.6, 1.2, 1.6), 0.08, 3.2, g)
    box("lamp_head", (2.6, 1.2, 3.25), (0.5, 0.3, 0.12), g)

    # 道具：寻猫启事薄板（贴在墙上）、猫窝方块、纸箱
    box("poster", (-1.8, 4.85, 1.5), (0.5, 0.02, 0.7), g)
    box("cat_nest", (-1.0, 2.6, 0.22), (0.9, 0.7, 0.44), g)
    box("carton", (1.4, 2.2, 0.3), (0.6, 0.6, 0.6), g)

    # 人形占位（球头 + 圆柱身 + 双腿；无五官/表情/头发）
    sph("human_head", (0.0, 1.0, 1.62), 0.12, g)
    cyl("human_body", (0.0, 1.0, 1.14), 0.18, 0.72, g)
    cyl("human_leg_l", (-0.08, 1.0, 0.42), 0.06, 0.84, g)
    cyl("human_leg_r", (0.08, 1.0, 0.42), 0.06, 0.84, g)

    # 动物占位（通用四足：身 + 头 + 四腿）
    box("animal_body", (0.42, 2.5, 0.24), (0.34, 0.16, 0.16), g)
    sph("animal_head", (0.62, 2.5, 0.30), 0.09, g)
    for i, (dx, dy) in enumerate([(-0.12, -0.06), (-0.12, 0.06), (0.12, -0.06), (0.12, 0.06)]):
        cyl("animal_leg_%d" % i, (0.42 + dx, 2.5 + dy, 0.12), 0.02, 0.24, g)

    return g


def setup_camera(scene, frames):
    """相机 dolly-in：从后景推向墙角。摄影运动在 Blender 里定死。"""
    cam_data = bpy.data.cameras.new("blockout_cam")
    cam_data.lens = 35.0
    cam = bpy.data.objects.new("blockout_cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    cam.location = (0.0, -6.0, 1.7)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    start = cam.location.copy()
    cam.location = start
    cam.keyframe_insert("location", frame=1)

    cam.location = (0.0, -2.2, 1.55)     # 推近 3.8m
    cam.keyframe_insert("location", frame=frames)

    # 插值设为 BEZIER。
    # ⚠️ Blender 4.4+ 引入 slotted action（Animation 2025），`action.fcurves` 被移除，
    #    改走 action.layers[].strips[].channelbags[].fcurves。此处两种结构都兼容。
    try:
        act = cam.animation_data.action if cam.animation_data else None
        if act is not None:
            fcurves = list(getattr(act, "fcurves", None) or [])
            if not fcurves:
                for layer in getattr(act, "layers", []) or []:
                    for strip in getattr(layer, "strips", []) or []:
                        for cbag in getattr(strip, "channelbags", []) or []:
                            fcurves.extend(getattr(cbag, "fcurves", []) or [])
            for fc in fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
            print("BLOCKOUT_FCURVES=%d" % len(fcurves))
    except Exception as e:                      # 插值非关键路径，失败不阻塞渲染
        print("BLOCKOUT_WARN interpolation skip: %r" % (e,))
    return cam


def setup_lights(frames, g):
    """路灯（点光，亮度+色彩关键帧）+ 环境主光。灯光运动/亮度/色彩全在 Blender 里做。"""
    lamp_data = bpy.data.lights.new("lamp_point", type="POINT")
    lamp_data.energy = 220.0
    lamp_data.color = (1.0, 0.85, 0.6)
    lamp = bpy.data.objects.new("lamp_point", lamp_data)
    bpy.context.scene.collection.objects.link(lamp)
    lamp.location = (2.6, 1.2, 3.1)

    # 亮度渐强 + 色温偏冷（模拟雨夜雷闪后）
    lamp_data.energy = 120.0
    lamp.keyframe_insert("location", frame=1)
    lamp.data.keyframe_insert("energy", frame=1)
    lamp_data.energy = 420.0
    lamp.data.keyframe_insert("energy", frame=int(frames * 0.6))
    lamp_data.color = (0.75, 0.85, 1.0)
    lamp.data.keyframe_insert("color", frame=int(frames * 0.6))

    # 环境主光（天光，极弱）
    world = bpy.data.worlds.new("blockout_world")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.05, 0.06, 0.09, 1.0)   # 冷蓝灰氛围
        bg.inputs[1].default_value = 1.0
    return lamp


def setup_render(scene, out_dir, frames, res, fps):
    w, h = [int(x) for x in res.lower().split("x")]
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frames

    # EEVEE 采样（兼顾速度）
    ee = getattr(scene, "eevee", None)
    if ee is not None:
        for attr, val in (("taa_render_samples", 16), ("use_gtao", True)):
            if hasattr(ee, attr):
                setattr(ee, attr, val)

    os.makedirs(out_dir, exist_ok=True)
    # ⚠️ 本机 Blender 5.2.2 构建**不含 FFMPEG 内建编码器**（实测 image_settings
    #    合法值仅 AVIF/JPEG/OPEN_EXR/PNG/WEBP/BMP/CINEON/DPX/IRIS/JPEG2000/HDR/TARGA），
    #    故输出 PNG 序列，mp4 由外部 ffmpeg 合成：
    #    ffmpeg -framerate <fps> -i <out>/frames/f_%%04d.png -c:v libx264 -crf 16 -pix_fmt yuv420p <out>/blockout_min.mp4
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = os.path.join(out_dir, "frames", "f_")


def main():
    a = parse_args()
    build_scene()
    scene = bpy.context.scene
    g = bpy.data.materials.get("blockout_gray")
    setup_camera(scene, a.frames)
    setup_lights(a.frames, g)
    setup_render(scene, a.out, a.frames, a.res, a.fps)

    print("BLOCKOUT_FRAMES=%d RES=%s FPS=%d ENGINE=%s" % (
        a.frames, a.res, a.fps, scene.render.engine))
    with _vram_lock("blender-blockout", wait_sec=1800):  # R0-T6：渲染期间独占显存锁
        bpy.ops.render.render(animation=True)
    print("BLOCKOUT_DONE out=%s" % scene.render.filepath)


if __name__ == "__main__":
    main()
