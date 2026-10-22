# -*- coding: utf-8 -*-
"""白模批量渲染包装器（R17 自研件 1）

按 master_v2.json 的 camera 轨镜头清单逐镜调用 blender，输出帧序列
（RGB PNG + EXR 含 Z 深度通道）到 outputs/blockout/<shot_id>/。

⚠️ T6 教训：blender.exe 按自身 cwd 解析相对路径——所有传入 blender 的
   路径一律绝对路径。

MVP 档位：
  inventory  列出 camera 轨镜头与签署状态（哪些可渲/缺机位数据）
  render     单镜试渲（默认 24 帧），全量渲染留给冲刺批次

用法：
  python blockout_batch_render.py inventory
  python blockout_batch_render.py render --shot 1-1 --frames 24
  python blockout_batch_render.py render --shot 1-2 --frames 8 --res 832x480
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# 维度25：根路径改由 config/paths.py 中心化推导（原为字面量 D:/aifilmteam）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.paths import ROOT as V2_ROOT  # noqa: E402

# ---- 默认路径（全部绝对，T6 教训）----
WORK_ROOT = str(V2_ROOT.parent)
MASTER_JSON = str(V2_ROOT / "projects" / "雨夜寻猫" / "00_brief"
                  / "timeline" / "master_v2.json")
OUT_ROOT = str(V2_ROOT.parent / "outputs" / "blockout")

# blender.exe 探测顺序：env > PATH > 常见安装位 > legacy 便携版
BLENDER_CANDIDATES = [
    r"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe",
    r"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe",
    r"C:/Program Files/Blender Foundation/Blender 4.5/blender.exe",
    r"C:/Program Files/Blender Foundation/Blender 4.2/blender.exe",
    os.path.join(WORK_ROOT, "_legacy_projects", "v2-intermediate",
                 "blender", "blender-5.2.2-windows-x64", "blender.exe"),
]


def find_blender():
    p = os.environ.get("BLENDER_EXE", "")
    if p and os.path.exists(p):
        return p
    import shutil
    w = shutil.which("blender")
    if w:
        return w
    for c in BLENDER_CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def load_camera_track(master_path):
    with open(master_path, encoding="utf-8") as f:
        d = json.load(f)
    return d["clock"], d["tracks"]["camera"]["items"]


def cmd_inventory(a):
    clock, items = load_camera_track(a.master)
    print("master: %s  fps=%s total_frames=%s" % (
        a.master, clock.get("fps"), clock.get("total_frames")))
    signed = 0
    for it in items:
        sg = it.get("signoff")
        ok = bool(sg)
        signed += ok
        pos = it.get("pos")
        aim = it.get("aim")
        state = "SIGNED " if ok else "UNSIGN"
        renderable = ok and pos is not None and aim is not None
        print("  [%s] %-4s move=%-6s focal=%-3s pos=%s aim=%s -> %s" % (
            state, it["shot_id"], it.get("move_type"), it.get("focal_mm"),
            "Y" if pos else "-", "Y" if aim else "-",
            "可渲(真实机位)" if renderable else "缺机位数值(占位机位或跳过)"))
    print("小结: %d/%d 镜已签。未签镜头的 pos/aim 为 null（见 master meta."
          "auto_draft_needs_confirm），真实机位渲染待 DP 签核；"
          "试渲链路用占位机位打通。" % (signed, len(items)))
    return 0


def scene_script(shot_id, cam, frames, res, fps, rgb_dir, exr_dir):
    """生成单镜白模场景 bpy 脚本文本（写入后由 blender.exe -b 执行）。

    场景：走廊白模（地/墙/门框/猫窝方块）+ 人形占位 + 四足占位，
    风格沿用 make_r4_l1_blockout.py 的占位几何体路线。
    相机参数：pos/aim 已签则用真实值；未签用默认占位机位（并打 WARN）。
    move_type 决定运动：static/dolly/truck/pan。
    输出：RGB PNG 序列 + OpenEXR(Z) 序列。
    """
    pos = cam.get("pos") or [0.0, -3.2, 1.6]
    aim = cam.get("aim") or [0.0, 0.0, 1.1]
    focal = cam.get("focal_mm") or 50
    move = cam.get("move_type") or "static"
    signed = bool(cam.get("signoff"))
    warn = "" if signed else "print('BLOCKOUT_WARN camera shot %s 未签，使用占位机位')" % shot_id
    return r'''
import bpy, os, math, json

SHOT   = %(shot)r
POS    = %(pos)r
AIM    = %(aim)r
FOCAL  = %(focal)s
MOVE   = %(move)r
FRAMES = %(frames)s
RESX, RESY = %(resx)s, %(resy)s
FPS    = %(fps)s
RGB    = %(rgb)r
EXR    = %(exr)r

bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = 'BLENDER_EEVEE'
ee = getattr(scn, 'eevee', None)
if ee is not None and hasattr(ee, 'use_gtao'):
    ee.use_gtao = True            # 接触阴影：给白模小物件更多结构
    if hasattr(ee, 'taa_render_samples'):
        ee.taa_render_samples = 32
scn.render.resolution_x, scn.render.resolution_y = RESX, RESY
scn.render.resolution_percentage = 100
scn.render.fps = FPS
scn.frame_start, scn.frame_end = 1, FRAMES

world = bpy.data.worlds.new('w'); world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.75,0.75,0.75,1)
scn.world = world

def box(name, size, loc, shade=0.8):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = size
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (shade,shade,shade,1)
    b.inputs['Roughness'].default_value = 0.9
    o.data.materials.append(m); o.data.shade_flat()
    return o

# 走廊白模
box('ground',  (10, 12, 0.1), (0, 0, -0.05), 0.62)
box('wall_L',  (0.15, 12, 3), (-3, 0, 1.5))
box('wall_R',  (0.15, 12, 3), (3, 0, 1.5))
box('wall_end',(10, 0.15, 3), (0, 6, 1.5))
box('doorframe',(1.2, 0.1, 2.2), (0, 5.9, 1.1), 0.55)
box('cat_nest',(0.9, 0.7, 0.4), (0.8, 3.4, 0.2), 0.9)
box('carton',  (0.6, 0.6, 0.6), (-1.6, 2.2, 0.3), 0.85)
# 人形占位
box('human_torso',(0.5, 0.3, 0.7), (0.4, 1.6, 1.05), 0.9)
box('human_head', (0.28,0.28,0.28),(0.4, 1.6, 1.62), 0.9)
# 四足占位
box('animal', (0.6, 0.3, 0.3), (-0.9, 3.4, 0.3), 0.92)
# ECU/特写推镜（dolly）需要被推向的主体：按特写比例搭"空猫窝+窗台+窗框"
# （占位几何，真实场景资产待后续批次；机位/朝向为 master 已签真实值）
if MOVE == 'dolly':
    az, ay = AIM[2] - 0.13, AIM[1]          # 窝顶开口约在 aim 高度下方
    box('sill',      (0.9, 0.35, 0.04), (AIM[0], ay + 0.02, az - 0.19), 0.70)
    box('nest_b',    (0.26, 0.20, 0.03), (AIM[0], ay, az - 0.16), 0.35)
    box('nest_wl',   (0.03, 0.20, 0.11), (AIM[0] - 0.115, ay, az - 0.10), 0.88)
    box('nest_wr',   (0.03, 0.20, 0.11), (AIM[0] + 0.115, ay, az - 0.10), 0.88)
    box('nest_wf',   (0.26, 0.03, 0.11), (AIM[0], ay - 0.085, az - 0.10), 0.88)
    box('nest_wb',   (0.26, 0.03, 0.11), (AIM[0], ay + 0.085, az - 0.10), 0.55)
    box('pebble_1',  (0.045, 0.04, 0.03), (AIM[0] - 0.05, ay - 0.02, az - 0.125), 0.75)
    box('pebble_2',  (0.03, 0.03, 0.025), (AIM[0] + 0.06, ay + 0.03, az - 0.128), 0.62)
    box('pebble_3',  (0.025, 0.025, 0.02), (AIM[0] + 0.02, ay - 0.05, az - 0.13), 0.80)
    box('win_glow',  (1.6, 0.05, 1.2),  (AIM[0], ay + 0.55, az + 0.45), 1.0)
    box('win_bar_v', (0.05, 0.04, 1.2), (AIM[0] - 0.28, ay + 0.42, az + 0.45), 0.30)
    box('win_bar_h', (1.6, 0.04, 0.05), (AIM[0], ay + 0.42, az + 0.95), 0.30)
    # 前景遮挡杆（窗框近端）：推镜时从画面侧缘扫出，运动读感强
    fx = POS[0] + (AIM[0]-POS[0]) * 0.45 - 0.045
    fy = POS[1] + (AIM[1]-POS[1]) * 0.45
    fz = POS[2] + (AIM[2]-POS[2]) * 0.45 + 0.10
    box('fg_bar', (0.035, 0.035, 0.6), (fx, fy, fz), 0.25)

light = bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN'))
light.data.energy = 3.0; light.rotation_euler = (math.radians(50),0,math.radians(30))
scn.collection.objects.link(light)

cam = bpy.data.cameras.new('cam'); cam.lens = FOCAL
co = bpy.data.objects.new('cam', cam); scn.collection.objects.link(co)
co.location = POS
tgt = bpy.data.objects.new('tgt', None); scn.collection.objects.link(tgt)
tgt.location = AIM
con = co.constraints.new('TRACK_TO'); con.target = tgt
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'

co.keyframe_insert('location', frame=1)
if MOVE == 'dolly':
    # dolly in：pos 沿 (aim-pos) 方向线性推进 70%%（推近不越过主体）
    dx, dy, dz = AIM[0]-POS[0], AIM[1]-POS[1], AIM[2]-POS[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz) or 1.0
    k = 0.35 / L   # 推进 35%%：末帧停在窝口外沿，保持画面结构
    co.location = (POS[0] + dx*k, POS[1] + dy*k, POS[2] + dz*k)
    co.keyframe_insert('location', frame=FRAMES)
elif MOVE == 'truck':
    co.location.x = co.location.x + 2.0
    co.keyframe_insert('location', frame=FRAMES)
elif MOVE == 'pan':
    tgt.location.x = tgt.location.x + 2.5
    tgt.keyframe_insert('location', frame=FRAMES)
# static: 无第二关键帧
scn.camera = co

os.makedirs(RGB, exist_ok=True); os.makedirs(EXR, exist_ok=True)
DEPTH = os.path.abspath(os.path.join(EXR, os.pardir, 'depth'))
os.makedirs(DEPTH, exist_ok=True)
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_mode = 'RGB'
scn.render.filepath = os.path.join(RGB, 'f_')
bpy.ops.render.render(animation=True, write_still=True)

# compositor 深度路：Depth pass -> Map Range(近=1 白, 远=0 黑) -> PNG
# ⚠️ 本构建(5.2.2)单层 OPEN_EXR 不写 Z、也无 OPEN_EXR_MULTILAYER，
#    compositor 直出灰度深度 PNG 是唯一确定性几何深度输出。
scn.view_layers[0].use_pass_z = True
scn.render.use_compositing = True
# ⚠️ Blender 5.x：Scene.node_tree 已移除，改用 compositing_node_group
tree = getattr(scn, "compositing_node_group", None) or \
    getattr(scn, "node_tree", None)
if tree is None:
    tree = bpy.data.node_groups.new("comp_tree", 'CompositorNodeTree')
    scn.compositing_node_group = tree
tree.nodes.clear()
# 4.x+ 组接口 API：声明合成输出 socket（NodeGroupOutput 才有 'Image' 输入）
tree.interface.new_socket(name='Image', in_out='OUTPUT',
                          socket_type='NodeSocketColor')
rl = tree.nodes.new('CompositorNodeRLayers')
# 5.x 新合成器：组输出节点即最终合成出口（Composite 节点已移除）
ngo = tree.nodes.new('NodeGroupOutput')
tree.links.new(rl.outputs['Image'], ngo.inputs['Image'])
mr = tree.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = 0.5   # near (m)
mr.inputs['From Max'].default_value = 12.0  # far  (m)
mr.inputs['To Min'].default_value = 1.0     # near(0.5m) -> 1(白)
mr.inputs['To Max'].default_value = 0.0     # far (12m)  -> 0(黑)，与 EXR-Z 路径约定一致
mr.clamp = True
tree.links.new(rl.outputs['Depth'], mr.inputs['Value'])
fo = tree.nodes.new('CompositorNodeOutputFile')
fo.name = 'd'   # 文件名前缀 = 节点名（默认 'Unsaved'）
fo.file_output_items.new(name='depth', socket_type='FLOAT')
fo.format.media_type = 'IMAGE'   # 5.2 默认 MULTI_LAYER_IMAGE，会锁死 PNG 枚举
fo.format.file_format = 'PNG'
fo.format.color_mode = 'BW'
fo.format.color_depth = '8'
fo.directory = DEPTH
tree.links.new(mr.outputs['Result'], fo.inputs['depth'])
tree.links.new(mr.outputs['Result'], fo.inputs[0])

scn.render.image_settings.file_format = 'OPEN_EXR'
scn.render.image_settings.color_depth = '32'
scn.render.filepath = os.path.join(EXR, 'f_')
bpy.ops.render.render(animation=True, write_still=True)

sidecar = {'shot_id': SHOT, 'resolution': [RESX, RESY], 'fps': FPS,
           'frames': FRAMES, 'move_type': MOVE, 'focal_mm': FOCAL,
           'camera_pos_signed': POS, 'aim_signed': AIM,
           'engine': 'BLENDER_EEVEE', 'source_master': 'master_v2.json'}
json.dump(sidecar, open(os.path.join(EXR, os.pardir, 'shot_sidecar.json'),'w'), indent=2)
print('BLOCKOUT_DONE frames=%%d %%dx%%d %%s' %% (FRAMES, RESX, RESY, SHOT))
''' % dict(shot=shot_id, pos=pos, aim=aim, focal=focal, move=move,
           frames=frames, resx=res[0], resy=res[1], fps=fps,
           rgb=rgb_dir, exr=exr_dir) + warn


def cmd_render(a):
    blender = find_blender()
    if not blender:
        print("BLOCKOUT_FAIL 未找到 blender.exe：设环境变量 BLENDER_EXE 或安装到 "
              "C:/Program Files/Blender Foundation/。试渲接口已就绪，本机暂不可渲。")
        return 2
    print("blender: %s" % blender)

    clock, items = load_camera_track(a.master)
    if a.shot:
        items = [it for it in items if it["shot_id"] == a.shot]
        if not items:
            print("BLOCKOUT_FAIL master 中无镜头 %s" % a.shot)
            return 1
    res = [int(x) for x in a.res.lower().split("x")]

    results = []
    for it in items:
        shot_id = it["shot_id"].replace(".", "-")
        out_dir = os.path.join(a.out_root, shot_id)          # 绝对
        rgb_dir = os.path.join(out_dir, "rgb")
        exr_dir = os.path.join(out_dir, "exr")
        bpy_dir = os.path.join(out_dir, "_bpy")
        os.makedirs(bpy_dir, exist_ok=True)
        script = os.path.join(bpy_dir, "%s_scene.py" % shot_id)
        with open(script, "w", encoding="utf-8") as f:
            f.write(scene_script(shot_id, it, a.frames, res, a.fps,
                                 rgb_dir, exr_dir))
        print("--- render shot %s (%s 帧 %s, move=%s, focal=%s) ---" % (
            shot_id, a.frames, a.res, it.get("move_type"), it.get("focal_mm")))
        t0 = time.time()
        # cwd 固定 work_root，且传给 blender 的路径全部绝对（T6 教训）
        r = subprocess.run(
            [blender, "-b", "-P", os.path.abspath(script)],
            capture_output=True, text=True, cwd=os.path.abspath(a.out_root),
            timeout=a.timeout)
        log = os.path.join(out_dir, "blender_log.txt")
        with open(log, "w", encoding="utf-8", errors="replace") as f:
            f.write((r.stdout or "") + "\n===STDERR===\n" + (r.stderr or ""))
        ok_tail = "BLOCKOUT_DONE" in (r.stdout or "")
        rgb_n = len([x for x in os.listdir(rgb_dir) if x.endswith(".png")]) \
            if os.path.isdir(rgb_dir) else 0
        exr_n = len([x for x in os.listdir(exr_dir) if x.endswith(".exr")]) \
            if os.path.isdir(exr_dir) else 0
        depth_dir = os.path.join(out_dir, "depth")
        dep_n = len([x for x in os.listdir(depth_dir) if x.endswith(".png")]) \
            if os.path.isdir(depth_dir) else 0
        fresh = os.path.isdir(rgb_dir) and (
            time.time() - os.path.getmtime(os.path.join(rgb_dir,
                                           sorted(os.listdir(rgb_dir))[0]))
            < 600) if rgb_n else False
        ok = r.returncode == 0 and rgb_n >= a.frames and exr_n >= a.frames \
            and dep_n >= a.frames
        results.append((shot_id, ok, rgb_n, exr_n, dep_n, fresh,
                        time.time() - t0, log))
        print("  rc=%s rgb=%d exr=%d depth=%d fresh=%s %.1fs log=%s -> %s" % (
            r.returncode, rgb_n, exr_n, dep_n, fresh, time.time() - t0,
            log, "PASS" if ok else "FAIL"))

    n_ok = sum(1 for x in results if x[1])
    print("BLOCKOUT_SUMMARY %d/%d PASS" % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 1


def main():
    p = argparse.ArgumentParser("blockout_batch_render")
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("inventory", help="镜头清单+签署状态")
    pi.add_argument("--master", default=MASTER_JSON)
    pi.set_defaults(fn=cmd_inventory)
    pr = sub.add_parser("render", help="渲染（MVP：单镜试渲）")
    pr.add_argument("--shot", default=None, help="镜头 id（如 1-1）；缺省=全清单")
    pr.add_argument("--frames", type=int, default=24)
    pr.add_argument("--res", default="832x480")
    pr.add_argument("--fps", type=int, default=24)
    pr.add_argument("--master", default=MASTER_JSON)
    pr.add_argument("--out-root", default=OUT_ROOT)
    pr.add_argument("--timeout", type=int, default=1800,
                    help="单镜 blender 超时秒数")
    pr.set_defaults(fn=cmd_render)
    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
