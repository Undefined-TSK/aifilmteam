# -*- coding: utf-8 -*-
"""白模 MCP addon（R17-8a）—— Blender 内嵌 socket 服务端

SPDX-License-Identifier: GPL-2.0-or-later

架构（调研文档 docs/03-规划与调研/自包含Blender控制层方案-2026-10-04.md 主线 C）：
  JSON-RPC 2.0 over TCP（默认 127.0.0.1:17800，换行分隔帧）→
  本模块在 Blender 主线程执行 bpy（bpy 非线程安全，绝不开线程直接调 bpy）。

线程模型（先例：abdelouafitahiri/claude-blender 的 timer 轮询方案）：
  socket 的 accept/recv 在 bpy.app.timers 主线程回调里以非阻塞方式完成，
  命令解析与 bpy 执行同在该回调 —— 无跨线程 bpy 调用，不会崩 Blender。

headless 兼容：`blender -b --python-expr "import ...; start_server()"` 可用
  （先例：minihellboy/claude-blender headless_blender.py）。

启动方式：
  import sys; sys.path.append(r"<本 addon 上级目录>")
  import baimo_mcp_addon
  baimo_mcp_addon.start_server()          # 默认端口 17800
  baimo_mcp_addon.stop_server()
"""
import bpy

from .server import BlenderRPCServer, DEFAULT_PORT, DEFAULT_LOG

_registered = {"server": None}


def start_server(port=DEFAULT_PORT, log_path=DEFAULT_LOG, host="127.0.0.1"):
    """启动 socket 服务端并注册主线程轮询定时器（幂等）。"""
    if _registered["server"] is not None:
        return _registered["server"]
    srv = BlenderRPCServer(host=host, port=int(port), log_path=log_path)
    _registered["server"] = srv
    bpy.app.timers.register(srv.poll, first_interval=0.1, persistent=True)
    print("BAIMO_MCP_SERVER_LISTENING %s:%s" % (host, port))
    return srv


def stop_server():
    """停止轮询并关闭监听 socket（幂等）。"""
    srv = _registered["server"]
    if srv is None:
        return
    try:
        if bpy.app.timers.is_registered(srv.poll):
            bpy.app.timers.unregister(srv.poll)
    except Exception:
        pass
    srv.close()
    _registered["server"] = None
    print("BAIMO_MCP_SERVER_STOPPED")


def start_headless(port=DEFAULT_PORT, log_path=DEFAULT_LOG):
    """headless 驻留入口：阻塞主线程轮询直至收到 shutdown_server。

    ⚠️ blender -b 在启动脚本结束后即退出且 timers 不保活（实测 5.2.2），
    headless 必须走本入口；GUI 模式用 start_server()（timers 驱动）。
    """
    srv = _registered.get("server")
    if srv is None:
        srv = BlenderRPCServer(port=int(port), log_path=log_path)
        _registered["server"] = srv
    print("BAIMO_MCP_HEADLESS_ENTER")
    srv.run_forever()
    print("BAIMO_MCP_HEADLESS_EXIT")
    return srv


# ---------- Blender UI 注册（可选；headless 用不到，UI 手动启停用） ----------

class BAIMO_OT_mcp_start(bpy.types.Operator):
    bl_idname = "baimo.mcp_start"
    bl_label = "启动白模 MCP 服务端"
    bl_description = "在 127.0.0.1:17800 启动 JSON-RPC socket 服务端"
    bl_options = {"REGISTER"}

    def execute(self, context):
        start_server()
        self.report({"INFO"}, "白模 MCP 服务端已启动 :17800")
        return {"FINISHED"}


class BAIMO_OT_mcp_stop(bpy.types.Operator):
    bl_idname = "baimo.mcp_stop"
    bl_label = "停止白模 MCP 服务端"
    bl_options = {"REGISTER"}

    def execute(self, context):
        stop_server()
        self.report({"INFO"}, "白模 MCP 服务端已停止")
        return {"FINISHED"}


classes = (BAIMO_OT_mcp_start, BAIMO_OT_mcp_stop)


def register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except Exception:
            pass  # headless 重复注册容错


def unregister():
    stop_server()
    for c in classes:
        try:
            bpy.utils.unregister_class(c)
        except Exception:
            pass


if __name__ == "__main__":
    register()
