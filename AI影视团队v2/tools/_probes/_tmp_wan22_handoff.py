import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from handoff_manager import HandoffManager

PROJ = r"D:\ai_film_projects\projects\雨夜寻猫"
hm = HandoffManager(PROJ)

h = hm.create_handoff(
    from_agent="animator",
    to_agent="editor",
    task_name="Wan2.2视频引擎升级-关键镜3-3/4-1重生成",
    work_background=(
        "老板反馈粗剪v3存在PPT感和五官奇怪问题，根因是AnimateDiff-Lightning(SD1.5系)动效天花板低。"
        "动画师完成Wan2.2 TI2V 5B本地部署（模型15.6GB已就位），用其重生成3-3绿眼亮起(73帧/3.04s)与4-1归途(193帧/8.04s)，"
        "自检通过：五官无崩坏、人猫同行真实动效、时码差0.04s内。已扣预算30点(15点/镜)，剩余530/1000点"
    ),
    deliverables={
        "dynamic_clips": [
            "shots/wan22_3_3.mp4（896x512, 73帧@24fps=3.04s, seed 2842292338, 生成139s）",
            "shots/wan22_4_1.mp4（832x480, 193帧@24fps=8.04s, seed 17152292, 生成383s）",
        ],
        "self_check": "3-3静镜微动效（猫眼微睁+呼吸+雨滴）五官无崩坏；4-1横移跟踪真实动效（人物行进+猫跟随+雨+霓虹反光），16帧网格抽样猫全程在场，无场景硬切",
        "tooling": "tools/wan22_client.py + tools/wan22_shots_33_41.py（可复用于其他降级镜追加i2v，15点/镜）",
        "budget_spent": "30点（15点/镜×2），剩余530/1000点",
    },
    downstream_task=(
        "剪辑师将两镜替换进粗剪时间线（3-3直接替换3s段、4-1直接替换8s段，无需慢放/推拉补强），"
        "音轨沿用v3混音，验证前后镜边界与音画对齐"
    ),
    completion_criteria="粗剪v4落盘：两镜Wan2.2版就位、音轨完整、80s总长、前后镜无损",
    stop_conditions="若新镜头与前后镜色调跳变明显，退回动画师调整（Wan2.2冷蓝紫调已验证与分镜一致，预期无需触发）",
    material_version="v2",
)

hid = h["handoff_id"]
print("created:", hid)
hm.check_handoff(hid, checker_agent="editor")
hm.accept_handoff(hid, agent="editor")
hm.complete_handoff(hid, agent="editor", result_deliverables={
    "粗剪v4成片": "output/雨夜寻猫_粗剪_v4.mp4（80.00s，1280x720/30fps，14.95MB）",
    "替换说明": "3-3/4-1为Wan2.2直出（等比缩放+居中裁剪至1280x720，24fps→30fps）；其余16镜无损保留；音轨整轨copy自v3混音",
    "剪辑验证": "43.5s=绿眼猫、61.5s=人猫同行街道（新素材就位）；41.5s/68.5s前后镜与v3一致；音画偏移0.03s<1帧无感",
    "镜头清单更新": "shots/雨夜寻猫_镜头清单_v1.json + .md 已记录Wan2.2版参数与自检结果，AnimateDiff版留档调参历史",
    "剪辑实现备注": "ffmpeg 8.1.2的split+多trim+concat组合bug（只输出首段），改用五段独立编码+concat demuxer文件化拼接",
})
print("completed:", hid)
