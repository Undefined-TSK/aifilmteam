import sys

sys.path.insert(0, r"D:\ai_film_projects\tools")
from handoff_manager import HandoffManager

mgr = HandoffManager(r"D:\ai_film_projects\projects\雨夜寻猫")

h1 = mgr.create_handoff(
    from_agent="编剧",
    to_agent="角色设计师",
    task_name="剧本v1角色描述交付-林小雨与小白",
    work_background="雨夜寻猫剧本v1已落盘（三幕四场80秒）。角色视觉基准以K13已锁资产为准：林小雨v2（米色风衣深色短发）、流浪猫v1（绿眼湿毛白猫）+分镜02（small white kitten）",
    deliverables=[
        "screenplay/雨夜寻猫_角色描述.md",
        "screenplay/雨夜寻猫_剧本_v1.json",
    ],
    downstream_task="林小雨定调图复检+三视图+表情集写入character_lock；小白定调图+character_lock",
    completion_criteria=[
        "character_lock包含feature_keywords/prompt_injection/views",
        "与K13已锁资产（短发/米色风衣/绿眼白猫）无冲突",
    ],
    stop_conditions=["与已锁资产特征冲突无法调和时上报艺术总监"],
)
print("handoff1:", h1["handoff_id"], h1["status"])

h2 = mgr.create_handoff(
    from_agent="编剧",
    to_agent="场景设计师",
    task_name="剧本v1场景描述交付-四场戏",
    work_background="雨夜寻猫剧本v1已落盘。四场戏中：雨夜街道（scene_lock已锁）与归途（分镜01已锁）直接沿用；出租屋内与雨夜巷口待出概念图并正式lock",
    deliverables=[
        "screenplay/雨夜寻猫_场景描述.md",
        "screenplay/雨夜寻猫_剧本_v1.json",
    ],
    downstream_task="出租屋内概念图+scene_lock（冷暖对比）；雨夜巷口基于分镜02出正式scene_lock",
    completion_criteria=[
        "出租屋内/雨夜巷口写入scene_lock",
        "与scene_lock雨夜街道及分镜01/02无视觉冲突",
    ],
    stop_conditions=["与已锁场景色板冲突无法调和时上报艺术总监"],
)
print("handoff2:", h2["handoff_id"], h2["status"])
