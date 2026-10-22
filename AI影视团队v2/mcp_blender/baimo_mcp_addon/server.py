# -*- coding: utf-8 -*-
"""白模 MCP addon 核心实现（R17-8a）—— socket 服务端 + 工具集

SPDX-License-Identifier: GPL-2.0-or-later

协议：JSON-RPC 2.0 over TCP，换行符分隔帧（每行一个 JSON 消息）。
  请求：{"jsonrpc":"2.0","id":1,"method":"create_primitive","params":{...}}
  成功：{"jsonrpc":"2.0","id":1,"result":{...}}
  失败：{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"..."}}

T6 教训：blender.exe 按自身 cwd 解析相对路径——本模块所有落盘路径
  （渲染输出/save_blend/op_log）一律强制绝对路径（_abs_path）。
"""
import json
import math
import os
import socket
import time
import traceback

import bpy

DEFAULT_PORT = 17800
DEFAULT_HOST = "127.0.0.1"
# 维度25：根路径由 addon 文件位置反推（原硬编码 D:/aifilmteam，换机即失效）。
# addon 位于 <根>/AI影视团队v2/mcp_blender/baimo_mcp_addon/，上溯 3 级即项目根。
ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DEFAULT_LOG = os.path.join(ROOT, "outputs", "mcp_pilot", "op_log.jsonl").replace("\\", "/")

RPC_PARSE_ERROR = -32700
RPC_METHOD_NOT_FOUND = -32601
RPC_INVALID_PARAMS = -32602
RPC_INTERNAL_ERROR = -32603


def _abs_path(p):
    """强制绝对路径：相对路径按项目根 ROOT 解析（T6 教训）。"""
    p = str(p).replace("\\", "/")
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    return os.path.normpath(p)


def _err(code, msg):
    return {"code": code, "message": msg}


def _scene():
    return bpy.context.scene


def _find_obj(name):
    o = bpy.context.scene.objects.get(name)
    if o is None:
        raise ValueError("场景中不存在对象 %r" % name)
    return o


def _deg2rad(v):
    return [math.radians(float(a)) for a in v]


def _rgb01(color):
    """颜色入参：0-1 浮点或 0-255 整数（任一分量 >1 即按 255 制换算）。"""
    c = [float(x) for x in color]
    if any(v > 1.0 for v in c):
        c = [max(0.0, min(1.0, v / 255.0)) for v in c]
    return c + [1.0] * (4 - len(c)) if len(c) < 4 else c[:4] + [1.0]


def _gray_material(shade):
    shade = max(0.0, min(1.0, float(shade)))
    name = "gray_%.2f" % shade
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if b is None:  # 5.x 节点名兜底
            for n in m.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    b = n
                    break
        b.inputs["Base Color"].default_value = (shade, shade, shade, 1.0)
        b.inputs["Roughness"].default_value = 0.9
    return m


# ============================ 工具实现 ============================
# 每个方法 params 带 schema 注释（与 MCP tools/list 的 inputSchema 对应）。

def h_ping(params):
    return {"pong": True, "blender": bpy.app.version_string,
            "engine": _scene().render.engine}


def h_scene_state(params):
    """scene_state() -> 场景全量 JSON（对象/相机/灯光/帧区间/渲染设置）。"""
    scn = _scene()
    objs = []
    for o in scn.objects:
        e = {"name": o.name, "type": o.type,
             "location": [round(v, 4) for v in o.location],
             "rotation_euler_deg": [round(math.degrees(a), 2)
                                    for a in o.rotation_euler],
             "scale": [round(v, 4) for v in o.scale]}
        if o.type == "CAMERA":
            e["lens_mm"] = round(o.data.lens, 1)
            e["has_track_to"] = any(c.type == "TRACK_TO" for c in o.constraints)
        elif o.type == "LIGHT":
            e["light_kind"] = o.data.type
            e["energy"] = o.data.energy
            e["color"] = [round(v, 3) for v in o.data.color]
        elif o.type == "MESH":
            e["dimensions"] = [round(v, 3) for v in o.dimensions]
            e["materials"] = [ms.material.name if ms.material else None
                              for ms in o.material_slots]
        objs.append(e)
    return {"frame_start": scn.frame_start, "frame_end": scn.frame_end,
            "fps": scn.render.fps,
            "resolution": [scn.render.resolution_x, scn.render.resolution_y],
            "engine": scn.render.engine,
            "active_camera": scn.camera.name if scn.camera else None,
            "current_frame": scn.frame_current,
            "objects": objs}


def h_create_primitive(params):
    """create_primitive(kind, size=1.0, location=[0,0,0], rotation=[0,0,0](度), name=None)
    kind ∈ cube|sphere|cylinder|plane|cone。默认赋中灰材质。"""
    kind = str(params.get("kind", "cube")).lower()
    size = float(params.get("size", 1.0))
    loc = [float(v) for v in params.get("location", [0, 0, 0])]
    rot = _deg2rad(params.get("rotation", [0, 0, 0]))
    ops = bpy.ops.mesh
    if kind == "cube":
        ops.primitive_cube_add(size=size, location=loc, rotation=rot)
    elif kind == "sphere":
        ops.primitive_uv_sphere_add(radius=size / 2.0, segments=24,
                                    ring_count=16, location=loc, rotation=rot)
    elif kind == "cylinder":
        ops.primitive_cylinder_add(radius=size / 2.0, depth=size,
                                   vertices=24, location=loc, rotation=rot)
    elif kind == "plane":
        ops.primitive_plane_add(size=size, location=loc, rotation=rot)
    elif kind == "cone":
        ops.primitive_cone_add(radius1=size / 2.0, depth=size,
                               vertices=24, location=loc, rotation=rot)
    else:
        raise ValueError("kind 仅支持 cube|sphere|cylinder|plane|cone，收到 %r" % kind)
    o = bpy.context.active_object
    if params.get("name"):
        o.name = str(params["name"])
    o.data.materials.append(_gray_material(params.get("shade", 0.8)))
    return {"name": o.name, "kind": kind, "location": list(o.location)}


def h_place_object(params):
    """place_object(name, location?, rotation?(度), scale?) —— 摆位既有对象。"""
    o = _find_obj(str(params["name"]))
    if params.get("location") is not None:
        o.location = [float(v) for v in params["location"]]
    if params.get("rotation") is not None:
        o.rotation_euler = _deg2rad(params["rotation"])
    if params.get("scale") is not None:
        s = params["scale"]
        o.scale = [float(s)] * 3 if isinstance(s, (int, float)) else [float(v) for v in s]
    return {"name": o.name,
            "location": [round(v, 4) for v in o.location],
            "rotation_euler_deg": [round(math.degrees(a), 2) for a in o.rotation_euler],
            "scale": [round(v, 4) for v in o.scale]}


def h_set_gray_material(params):
    """set_gray_material(name, shade=0.8) —— 白模统一灰阶材质（0黑-1白）。"""
    o = _find_obj(str(params["name"]))
    m = _gray_material(params.get("shade", 0.8))
    if m.name not in [ms.material.name for ms in o.material_slots
                      if ms.material]:
        o.data.materials.append(m)
    return {"name": o.name, "material": m.name}


def h_add_camera(params):
    """add_camera(name, lens=50, location, rotation?(度), aim?)
    rotation 与 aim 二选一：给 aim 则挂 TRACK_TO 空靶（dolly/pan 更稳）。
    幂等：同名相机已存在则复用更新（防止重复相机抢占 scn.camera、
    丢掉已打的关键帧——试点第3轮实测教训）。"""
    name = str(params.get("name", "cam"))
    existing = _scene().objects.get(name)
    if existing is not None and existing.type == "CAMERA":
        co = existing
        co.data.lens = float(params.get("lens", co.data.lens))
        reused = True
    else:
        cam = bpy.data.cameras.new(name)
        cam.lens = float(params.get("lens", 50))
        co = bpy.data.objects.new(name, cam)
        _scene().collection.objects.link(co)
        reused = False
    if params.get("location") is not None:
        co.location = [float(v) for v in params["location"]]
    aim = params.get("aim")
    tgt_name = "target_%s" % name
    if aim is not None:
        tgt = bpy.data.objects.get(tgt_name)
        if tgt is None:
            tgt = bpy.data.objects.new(tgt_name, None)
            _scene().collection.objects.link(tgt)
        tgt.location = [float(v) for v in aim]
        con = next((c for c in co.constraints if c.type == "TRACK_TO"), None)
        if con is None:
            con = co.constraints.new("TRACK_TO")
            con.track_axis = "TRACK_NEGATIVE_Z"
            con.up_axis = "UP_Y"
        con.target = tgt
    elif params.get("rotation") is not None:
        co.rotation_euler = _deg2rad(params["rotation"])
    _scene().camera = co
    return {"name": co.name, "lens_mm": co.data.lens, "reused": reused,
            "location": [round(v, 4) for v in co.location],
            "aim_target": tgt_name if aim is not None else None}


def h_keyframe_camera(params):
    """keyframe_camera(name, frame, location?, aim?) —— 机位关键帧（dolly/truck 用）。"""
    co = _find_obj(str(params["name"]))
    frame = int(params["frame"])
    moved = {}
    if params.get("location") is not None:
        co.location = [float(v) for v in params["location"]]
        co.keyframe_insert("location", frame=frame)
        moved["location"] = [round(v, 4) for v in co.location]
    if params.get("aim") is not None:
        tgt = bpy.data.objects.get("target_%s" % co.name)
        if tgt is None:
            raise ValueError("相机 %r 无 aim 靶（创建时未传 aim）" % co.name)
        tgt.location = [float(v) for v in params["aim"]]
        tgt.keyframe_insert("location", frame=frame)
        moved["aim"] = [round(v, 4) for v in tgt.location]
    if not moved:
        raise ValueError("keyframe_camera 至少需要 location 或 aim 之一")
    return {"name": co.name, "frame": frame, "keyed": moved}


def h_add_light(params):
    """add_light(kind=SUN|AREA|POINT|SPOT, energy, location, color?, rotation?(度),
    name?, size?, size_y?, shape?)
    energy 语义：SUN 为 W/m2（建议 1-5），其余为 W（建议 100-2000）。
    AREA 专属：size/size_y（米，默认1）、shape（SQUARE|RECTANGLE|DISK|ELLIPSE）。
    窗光配方：AREA 大面光贴窗口朝室内，energy≥1000。"""
    kind = str(params.get("kind", "SUN")).upper()
    if kind not in ("SUN", "AREA", "POINT", "SPOT"):
        raise ValueError("kind 仅支持 SUN|AREA|POINT|SPOT，收到 %r" % kind)
    name = str(params.get("name", "light_%s" % kind.lower()))
    li = bpy.data.lights.new(name, kind)
    li.energy = float(params.get("energy", 3.0 if kind == "SUN" else 1000.0))
    if params.get("color") is not None:
        li.color = _rgb01(params["color"])[:3]
    if kind == "AREA":
        if params.get("size") is not None:
            li.size = float(params["size"])
        if params.get("size_y") is not None and hasattr(li, "size_y"):
            li.size_y = float(params["size_y"])
            if params.get("shape") is not None:
                li.shape = str(params["shape"]).upper()
        elif params.get("shape") is not None:
            li.shape = str(params["shape"]).upper()
    lo = bpy.data.objects.new(name, li)
    _scene().collection.objects.link(lo)
    lo.location = [float(v) for v in params.get("location", [0, 0, 5])]
    if params.get("rotation") is not None:
        lo.rotation_euler = _deg2rad(params["rotation"])
    return {"name": lo.name, "kind": kind, "energy": li.energy,
            "color": [round(v, 3) for v in li.color]}


def h_set_world(params):
    """set_world(strength=1.0, color=[r,g,b] 0-1 或 0-255) —— 世界背景环境光。
    add_world 别名同此实现（世界不存在时自动创建）。
    室内黑根因对策：世界环境光给基础照明（strength 0.3-1.0 白/冷灰），
    再配 AREA 窗光塑形。"""
    scn = _scene()
    w = scn.world
    created = False
    if w is None or not w.use_nodes:
        w = bpy.data.worlds.new("world")
        w.use_nodes = True
        scn.world = w
        created = True
    bg = None
    for n in w.node_tree.nodes:
        if n.type == "BACKGROUND":
            bg = n
            break
    if bg is None:
        bg = w.node_tree.nodes.new("ShaderNodeBackground")
        out = next((n for n in w.node_tree.nodes if n.type == "OUTPUT_WORLD"), None)
        if out is None:
            out = w.node_tree.nodes.new("ShaderNodeOutputWorld")
        w.node_tree.links.new(bg.outputs["Background"], out.inputs["Surface"])
    strength = float(params.get("strength", 1.0))
    bg.inputs["Strength"].default_value = strength
    if params.get("color") is not None:
        bg.inputs["Color"].default_value = _rgb01(params["color"])
    return {"world": w.name, "created": created,
            "strength": round(strength, 3),
            "color": [round(v, 3) for v in bg.inputs["Color"].default_value[:3]]}


def h_set_frame_range(params):
    """set_frame_range(start, end, fps=24) —— 帧区间与帧率。"""
    scn = _scene()
    scn.frame_start = int(params["start"])
    scn.frame_end = int(params["end"])
    if params.get("fps") is not None:
        scn.render.fps = int(params["fps"])
    return {"frame_start": scn.frame_start, "frame_end": scn.frame_end,
            "fps": scn.render.fps}


def _setup_eevee(scn, samples=16):
    scn.render.engine = "BLENDER_EEVEE"
    ee = getattr(scn, "eevee", None)
    if ee is not None:
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = samples
        if hasattr(ee, "use_gtao"):
            ee.use_gtao = True


def h_render_preview(params):
    """render_preview(camera, output_path, frame=1, res=[640,360])
    EEVEE 低采样单帧 PNG —— 给 VL 自检看图用。"""
    scn = _scene()
    co = _find_obj(str(params["camera"]))
    if co.type != "CAMERA":
        raise ValueError("%r 不是相机" % co.name)
    scn.camera = co
    scn.frame_set(int(params.get("frame", 1)))
    res = params.get("res", [640, 360])
    scn.render.resolution_x, scn.render.resolution_y = int(res[0]), int(res[1])
    scn.render.resolution_percentage = 100
    _setup_eevee(scn, samples=int(params.get("samples", 16)))
    out = _abs_path(params["output_path"])
    if not out.lower().endswith(".png"):
        out += ".png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # ⚠️ 顺序：先 media_type 后 file_format（media_type=VIDEO 时 file_format
    #    枚举仅 'FFMPEG'，先设 PNG 会报 enum not found）
    if hasattr(scn.render.image_settings, "media_type"):
        scn.render.image_settings.media_type = "IMAGE"
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGB"
    scn.render.filepath = out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    return {"saved": out, "bytes": os.path.getsize(out),
            "resolution": [scn.render.resolution_x, scn.render.resolution_y],
            "frame": scn.frame_current, "seconds": round(time.time() - t0, 2)}


def _ffmpeg_exe():
    import shutil
    w = shutil.which("ffmpeg")
    if w:
        return w
    cand = os.path.join(ROOT, "..", "ffmpeg.exe")  # 兜底位（本机已在 PATH）
    return w


def h_render_playblast(params):
    """render_playblast(camera, output_dir, start?, end?, fps=24, res=[832,480], mp4=True)
    白模动画：优先 Blender 内建 FFMPEG 直出 MP4（H.264）；
    内建不可用则回退 PNG 序列 + 系统 ffmpeg 封装。"""
    scn = _scene()
    co = _find_obj(str(params["camera"]))
    if co.type != "CAMERA":
        raise ValueError("%r 不是相机" % co.name)
    scn.camera = co
    start = int(params.get("start", scn.frame_start))
    end = int(params.get("end", scn.frame_end))
    scn.frame_start, scn.frame_end = start, end
    scn.render.fps = int(params.get("fps", 24))
    res = params.get("res", [832, 480])
    scn.render.resolution_x, scn.render.resolution_y = int(res[0]), int(res[1])
    scn.render.resolution_percentage = 100
    _setup_eevee(scn, samples=int(params.get("samples", 32)))
    out_dir = _abs_path(params["output_dir"])
    os.makedirs(out_dir, exist_ok=True)
    scn.render.image_settings.color_mode = "RGB"

    made = []
    iset = scn.render.image_settings
    ffmpeg_ok = (params.get("mp4", True)
                 and hasattr(scn.render, "ffmpeg")
                 and scn.render.ffmpeg is not None)
    if ffmpeg_ok:
        # 5.2.2：电影输出须 media_type='VIDEO'（file_format 枚举已无 'FFMPEG' 图像项）
        if hasattr(iset, "media_type"):
            iset.media_type = "VIDEO"
        iset.file_format = "FFMPEG"
        ff = scn.render.ffmpeg
        ff.format = "MPEG4"
        ff.codec = "H264"
        ff.constant_rate_factor = "HIGH"
        ff.audio_codec = "NONE"
        scn.render.filepath = os.path.join(out_dir, "blockout.mp4")
        t0 = time.time()
        bpy.ops.render.render(animation=True)
        made = [os.path.join(out_dir, f) for f in sorted(os.listdir(out_dir))
                if f.endswith(".mp4")]
        if not made:
            ffmpeg_ok = False  # 内建直出失败 → 回退序列
    if not ffmpeg_ok:
        seq_dir = os.path.join(out_dir, "rgb")
        os.makedirs(seq_dir, exist_ok=True)
        if hasattr(iset, "media_type"):
            iset.media_type = "IMAGE"          # 先 media_type 后 file_format
        iset.file_format = "PNG"
        scn.render.filepath = os.path.join(seq_dir, "f_")
        t0 = time.time()
        bpy.ops.render.render(animation=True)
        ff = _ffmpeg_exe()
        mp4 = os.path.join(out_dir, "blockout.mp4")
        if ff:
            import subprocess
            r = subprocess.run(
                [ff, "-y", "-framerate", str(scn.render.fps), "-i",
                 os.path.join(seq_dir, "f_%04d.png"), "-c:v", "libx264",
                 "-pix_fmt", "yuv420p", mp4],
                capture_output=True, text=True, timeout=600)
            if r.returncode == 0 and os.path.exists(mp4):
                made = [mp4]
        else:
            made = [seq_dir]  # 无 ffmpeg：返回序列目录
    return {"files": made, "frames": [start, end], "fps": scn.render.fps,
            "resolution": [scn.render.resolution_x, scn.render.resolution_y],
            "seconds": round(time.time() - t0, 2)}


def h_save_blend(params):
    """save_blend(path, pack=False) —— 保存 .blend（目录自动创建）。"""
    p = _abs_path(params["path"])
    if not p.lower().endswith(".blend"):
        p += ".blend"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if params.get("pack"):
        bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=p, compress=True)
    return {"saved": p, "bytes": os.path.getsize(p)}


HANDLERS = {
    "ping": h_ping,
    "scene_state": h_scene_state,
    "create_primitive": h_create_primitive,
    "place_object": h_place_object,
    "set_gray_material": h_set_gray_material,
    "add_camera": h_add_camera,
    "keyframe_camera": h_keyframe_camera,
    "add_light": h_add_light,
    "set_world": h_set_world,
    "add_world": h_set_world,   # 别名：同一实现（世界不存在自动创建）
    "set_frame_range": h_set_frame_range,
    "render_preview": h_render_preview,
    "render_playblast": h_render_playblast,
    "save_blend": h_save_blend,
    "shutdown_server": None,   # 占位，_dispatch 内前置处理（需访问 self.alive）
}


# ============================ 服务端 ============================

class BlenderRPCServer:
    """主线程轮询式 JSON-RPC socket 服务端（非阻塞，定时器驱动）。"""

    POLL_INTERVAL = 0.05   # 20Hz 轮询

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 log_path=DEFAULT_LOG):
        self.log_path = _abs_path(log_path)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, int(port)))
        self.sock.listen(4)
        self.sock.setblocking(False)
        self.clients = {}          # conn -> bytes 缓冲
        self.alive = True
        print("BAIMO_MCP_SERVER_LISTENING %s:%s log=%s" % (host, port,
                                                           self.log_path))

    # ---- op 日志：每个请求一行 JSONL（tools 调用流水 + 时间戳） ----
    def _log(self, rec):
        try:
            rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            traceback.print_exc()

    def _dispatch(self, req):
        rid = req.get("id")
        method = str(req.get("method", ""))
        params = req.get("params") or {}
        t0 = time.time()
        if method == "shutdown_server":
            self.alive = False
            self._log({"id": rid, "method": method, "params": params,
                       "ok": True, "result": "stopping",
                       "ms": round((time.time() - t0) * 1000, 1)})
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "result": "server_stopping"}).encode("utf-8")
        if method.startswith("rpc."):   # JSON-RPC 2.0 保留前缀
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "error": _err(RPC_METHOD_NOT_FOUND,
                                             "rpc.* 保留方法")}).encode("utf-8")
        h = HANDLERS.get(method)
        if h is None:
            avail = ", ".join(sorted(HANDLERS))
            self._log({"id": rid, "method": method, "params": params,
                       "ok": False, "error": "method_not_found",
                       "ms": round((time.time() - t0) * 1000, 1)})
            return json.dumps(
                {"jsonrpc": "2.0", "id": rid,
                 "error": _err(RPC_METHOD_NOT_FOUND,
                               "未知 method: %s（可用: %s）" % (method, avail))}
            ).encode("utf-8")
        try:
            result = h(params)
            self._log({"id": rid, "method": method, "params": params,
                       "ok": True, "result": result,
                       "ms": round((time.time() - t0) * 1000, 1)})
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "result": result}).encode("utf-8")
        except (TypeError, ValueError, KeyError) as exc:
            self._log({"id": rid, "method": method, "params": params,
                       "ok": False, "error": str(exc),
                       "ms": round((time.time() - t0) * 1000, 1)})
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "error": _err(RPC_INVALID_PARAMS,
                                             str(exc))}).encode("utf-8")
        except Exception as exc:
            self._log({"id": rid, "method": method, "params": params,
                       "ok": False, "error": str(exc),
                       "ms": round((time.time() - t0) * 1000, 1)})
            traceback.print_exc()
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "error": _err(RPC_INTERNAL_ERROR,
                                             "%s: %s" % (type(exc).__name__,
                                                         exc))}).encode("utf-8")

    def poll(self):
        """bpy.app.timers 主线程回调：accept + recv + 执行 + 回写。"""
        if not self.alive:
            return None                       # 返回 None = 注销定时器
        # 1) 受理新连接
        try:
            while True:
                conn, _addr = self.sock.accept()
                conn.setblocking(False)
                self.clients[conn] = b""
        except (BlockingIOError, OSError):
            pass
        # 2) 逐连接收包 + 执行 + 回写（命令在主线程顺序执行，天然串行）
        closed = []
        for conn, _buf in list(self.clients.items()):
            data = b""
            try:
                while True:
                    chunk = conn.recv(65536)
                    if not chunk:
                        closed.append(conn)
                        break
                    data += chunk
            except (BlockingIOError, OSError):
                pass
            buf = self.clients.get(conn, b"") + data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    req = json.loads(line.decode("utf-8"))
                except (ValueError, UnicodeDecodeError) as exc:
                    resp = json.dumps({"jsonrpc": "2.0", "id": None,
                                       "error": _err(RPC_PARSE_ERROR,
                                                     str(exc))}).encode("utf-8")
                else:
                    resp = self._dispatch(req)
                try:
                    conn.sendall(resp + b"\n")
                except OSError:
                    closed.append(conn)
            self.clients[conn] = buf
        # 3) 清理断连
        for conn in closed:
            try:
                conn.close()
            except OSError:
                pass
            self.clients.pop(conn, None)
        return self.POLL_INTERVAL

    def run_forever(self):
        """headless 主循环：阻塞本线程轮询（bpy 全部调用都在主线程，安全）。

        ⚠️ `blender -b --python xxx` 在启动脚本跑完后即退出且 timers 不保活，
        headless 必须用本方法驻留（等价 -P 场景脚本的执行环境，bpy 可用）。
        GUI 模式请勿调用（会卡死 UI），GUI 用 bpy.app.timers 注册 poll。
        """
        import time as _t
        while self.alive:
            self.poll()
            _t.sleep(self.POLL_INTERVAL)

    def close(self):
        self.alive = False
        for conn in list(self.clients):
            try:
                conn.close()
            except OSError:
                pass
        self.clients.clear()
        try:
            self.sock.close()
        except OSError:
            pass
