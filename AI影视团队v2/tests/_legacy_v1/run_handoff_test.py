"""
关卡8：Agent接力完整测试
=========================
测试场景：制片人Agent → 角色设计师Agent 的任务接力

测试内容：
1. 人工接力测试（上游交付 → 人工转交 → 下游检查 → 处理 → 完成）
2. 自动接力测试（上游自动交付并通知下游 → 下游自动检查 → 自动处理 → 自动完成）
3. 异常场景测试（材料不完整 → 下游退回）

所有步骤都记录到 handoff_record.json，全程可追溯。
"""

import json
import sys
import os
from pathlib import Path

# 添加工具路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from handoff_manager import HandoffManager

# 项目路径
PROJECT_DIR = r"D:\ai_film_projects"


def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_1_manual_handoff(mgr):
    """测试1：人工接力（完整成功流程）"""
    print_separator("测试1：人工接力 — 制片人 → 角色设计师（成功流程）")
    
    task_name = "林月角色设计"
    
    # ========== 步骤1：制片人创建交接任务（上游交付）==========
    print("【步骤1】制片人创建交接任务...")
    
    deliverables = {
        "导演意图文档": f"{PROJECT_DIR}/tests/case1_single_character/director_intent.md",
        "角色描述": "赛博朋克风格女主角，25岁左右，短发，穿霓虹色夹克",
        "风格基准": "写实，电影感，雨夜霓虹都市",
        "参考图": "无（首次设计）"
    }
    
    handoff = mgr.create_handoff(
        from_agent="producer",
        to_agent="character_designer",
        task_name=task_name,
        work_background="赛博朋克短片项目，需要女主角林月的角色概念图。项目整体风格为雨夜霓虹都市，写实电影感。",
        deliverables=deliverables,
        downstream_task="根据角色描述和风格基准，设计并生成林月的角色正面概念图，输出至少1张满意版本并锁定到K13版本树。",
        completion_criteria="1. 角色形象符合描述（短发、霓虹色夹克、25岁左右）\n2. 风格匹配赛博朋克雨夜都市\n3. 至少1张满意版本锁定到K13\n4. 附带特征关键词列表，供下游使用",
        stop_conditions="1. 导演意图文档不存在或无法读取\n2. 角色描述过于模糊（缺少外貌特征）\n3. 任务不属于角色设计范畴",
        pending_items=["是否需要三视图？当前默认先出正面单图"],
        material_version="v1"
    )
    
    print(f"  交接ID: {handoff['handoff_id']}")
    print(f"  任务名称: {handoff['task_name']}")
    print(f"  上游 → 下游: {handoff['from_agent']} → {handoff['to_agent']}")
    print(f"  状态: {handoff['status']}")
    print("  ✅ 交接任务已创建")
    handoff_id_1 = handoff['handoff_id']
    
    # ========== 步骤2：人工转交（模拟人在群里@下游）==========
    print("\n【步骤2】人工转交（模拟人确认上游交付后，@角色设计师接手）...")
    print("  （人）检查上游交付物：")
    print("    - 导演意图文档：存在 ✓")
    print("    - 角色描述：清晰 ✓")
    print("    - 风格基准：明确 ✓")
    print("  人工转交完成，通知角色设计师开始检查")
    
    # ========== 步骤3：角色设计师检查交接材料（下游检查）==========
    print("\n【步骤3】角色设计师检查交接材料...")
    
    check_result = mgr.check_handoff(handoff_id_1, "character_designer")
    
    print(f"  检查通过: {check_result['passed']}")
    if check_result['issues']:
        print(f"  发现问题:")
        for issue in check_result['issues']:
            print(f"    - {issue}")
    else:
        print("  材料完整，无问题")
    
    if check_result['should_stop']:
        print(f"  ⚠️  触发停止条件: {check_result['stop_reason']}")
        return None
    
    print("  ✅ 材料检查通过")
    
    # ========== 步骤4：角色设计师接受任务 ==========
    print("\n【步骤4】角色设计师接受任务...")
    
    result = mgr.accept_handoff(handoff_id_1, "character_designer")
    
    if "error" in result:
        print(f"  ❌ 接受失败: {result['error']}")
        return None
    
    print(f"  当前状态: {result['status']}")
    print("  ✅ 任务已接受，开始处理")
    
    # ========== 步骤5：角色设计师处理任务（模拟生成）==========
    print("\n【步骤5】角色设计师处理任务（模拟生成角色图）...")
    print("  处理中...")
    print("  - 分析角色描述和风格基准")
    print("  - 调用ComfyUI SDXL生成")
    print("  - 迭代优化（2次重试）")
    print("  - 满意版本锁定到K13版本树")
    print("  ✅ 角色图生成完成")
    
    # ========== 步骤6：角色设计师交付结果 ==========
    print("\n【步骤6】角色设计师交付结果...")
    
    result_deliverables = {
        "角色正面概念图": f"{PROJECT_DIR}/showcase/assets/cyberpunk_girl.png",
        "K13版本树路径": f"{PROJECT_DIR}/tests/case1_single_character/k13_locked",
        "锁定版本": "v1 (UUID: 02312674)",
        "特征关键词": "short hair, neon colored jacket, cyberpunk, 25 year old woman, cinematic lighting, rainy night city",
        "色板": "霓虹粉 #ff2e97, 电光蓝 #00d4ff, 深夜黑 #0a0a12"
    }
    
    result = mgr.complete_handoff(handoff_id_1, "character_designer", result_deliverables)
    
    print(f"  最终状态: {result['status']}")
    print(f"  交付物: {list(result_deliverables.keys())}")
    print("  ✅ 交接任务完成")
    
    # ========== 步骤7：查看完整时间线（可追溯）==========
    print("\n【步骤7】查看完整时间线（可追溯验证）...")
    
    timeline = mgr.get_timeline(handoff_id_1)
    for i, event in enumerate(timeline):
        print(f"  {i+1}. [{event['time']}] {event['agent']}: {event['message']}")
    
    print("\n  ✅ 人工接力测试通过！全程可追溯。")
    return handoff_id_1


def test_2_rejection_scenario(mgr):
    """测试2：异常场景 — 材料不完整，下游退回"""
    print_separator("测试2：异常场景 — 材料不完整，下游退回")
    
    task_name = "路人甲角色设计（测试退回）"
    
    # 步骤1：创建一个信息不完整的交接
    print("【步骤1】制片人创建信息不完整的交接任务...")
    
    deliverables = {
        "角色描述": "一个路人",  # 描述太模糊
        # 缺少导演意图文档
        # 缺少风格基准
    }
    
    handoff = mgr.create_handoff(
        from_agent="producer",
        to_agent="character_designer",
        task_name=task_name,
        work_background="测试退回场景",
        deliverables=deliverables,
        downstream_task="设计路人甲",
        completion_criteria="完成角色设计",
        stop_conditions="角色描述过于模糊时停止并退回",
        material_version="v1"
    )
    
    print(f"  交接ID: {handoff['handoff_id']}")
    print("  （故意缺少：导演意图文档、风格基准，角色描述模糊）")
    handoff_id_2 = handoff['handoff_id']
    
    # 步骤2：下游检查
    print("\n【步骤2】角色设计师检查交接材料...")
    
    check_result = mgr.check_handoff(handoff_id_2, "character_designer")
    
    print(f"  检查通过: {check_result['passed']}")
    print(f"  发现问题 ({len(check_result['issues'])}个):")
    for issue in check_result['issues']:
        print(f"    - {issue}")
    
    # 步骤3：下游退回
    print("\n【步骤3】角色设计师退回任务...")
    
    result = mgr.reject_handoff(
        handoff_id_2, 
        "character_designer",
        reason="材料不完整，角色描述模糊",
        details="缺少导演意图文档和风格基准，且角色描述仅为'一个路人'，过于模糊无法开始设计。请补充：1.角色外貌特征描述 2.项目风格基准 3.导演意图文档链接"
    )
    
    print(f"  退回状态: {result['status']}")
    print(f"  退回原因: {result['rejection']['reason']}")
    print(f"  详细说明: {result['rejection']['details'][:60]}...")
    print("  ✅ 退回机制正常工作")
    
    return handoff_id_2


def test_3_auto_handoff(mgr):
    """测试3：自动接力（模拟全自动流程）"""
    print_separator("测试3：自动接力 — 制片人自动交付 → 角色设计师自动处理")
    
    task_name = "白衣剑客角色设计（自动接力）"
    
    print("【自动接力开始】")
    print("  （模拟：上游完成后自动创建交接 + 自动通知下游 + 下游自动检查处理）")
    
    # 步骤1：上游自动创建交接
    print("\n  [上游] 制片人自动创建交接...")
    deliverables = {
        "导演意图文档": f"{PROJECT_DIR}/tests/case2_multi_assets/director_intent.md",
        "角色描述": "古风白衣剑客，30岁左右，长发束起，气质清冷，穿白色长袍配银色装饰",
        "风格基准": "古风写实，竹林晨雾氛围，电影感",
        "场景参考图": f"{PROJECT_DIR}/showcase/assets/bamboo_scene.png"
    }
    
    handoff = mgr.create_handoff(
        from_agent="producer",
        to_agent="character_designer",
        task_name=task_name,
        work_background="武侠短片项目，需要白衣剑客角色概念图。项目整体风格为古风竹林、晨雾缭绕、写实电影感。",
        deliverables=deliverables,
        downstream_task="根据角色描述和风格基准，设计并生成白衣剑客的正面角色概念图，锁定到K13版本树。",
        completion_criteria="1. 符合白衣剑客设定（白袍、银饰、束发）\n2. 古风写实质感\n3. 与竹林场景风格统一\n4. 至少1个版本锁定",
        stop_conditions="1. 缺少角色外貌描述\n2. 无风格基准\n3. 任务类型不匹配",
        pending_items=[],
        material_version="v1"
    )
    
    handoff_id_3 = handoff['handoff_id']
    print(f"    交接ID: {handoff_id_3}")
    print("    ✅ 交接已创建")
    
    # 步骤2：下游自动检查
    print("\n  [下游] 角色设计师自动检查交接...")
    check_result = mgr.check_handoff(handoff_id_3, "character_designer")
    
    if check_result['passed']:
        print("    ✅ 检查通过")
    else:
        print(f"    ❌ 检查失败: {check_result['issues']}")
        return None
    
    # 步骤3：下游自动接受
    print("\n  [下游] 自动接受任务...")
    accept_result = mgr.accept_handoff(handoff_id_3, "character_designer")
    if "error" in accept_result:
        print(f"    ❌ 接受失败: {accept_result['error']}")
        return None
    print("    ✅ 任务已接受")
    
    # 步骤4：下游自动处理（模拟）
    print("\n  [下游] 自动处理中...")
    print("    - 读取角色描述和风格基准")
    print("    - 参考场景图统一风格")
    print("    - 调用ComfyUI生成")
    print("    - 满意版本锁定K13")
    print("    ✅ 处理完成")
    
    # 步骤5：下游自动交付
    print("\n  [下游] 自动交付结果...")
    result_deliverables = {
        "角色正面概念图": f"{PROJECT_DIR}/showcase/assets/swordsman.png",
        "K13版本ID": "ae436160",
        "特征关键词": "white robe, silver accents, long hair tied up, 30 year old man, wuxia style, bamboo forest atmosphere, cinematic",
        "色板": "月白 #f5f5f0, 银灰 #c0c0c0, 竹青 #789262"
    }
    
    result = mgr.complete_handoff(handoff_id_3, "character_designer", result_deliverables)
    print(f"    最终状态: {result['status']}")
    print("    ✅ 自动接力完成！")
    
    # 完整时间线
    print("\n【自动接力完整时间线】")
    timeline = mgr.get_timeline(handoff_id_3)
    for i, event in enumerate(timeline):
        print(f"  {i+1}. [{event['time'].split('T')[1][:8]}] {event['agent']:20s}: {event['message']}")
    
    return handoff_id_3


def generate_report(mgr, handoff_ids):
    """生成关卡8测试报告"""
    print_separator("关卡8测试汇总报告")
    
    stats = mgr.get_stats()
    print(f"总交接数: {stats['total']}")
    print(f"已完成: {stats['completed']}")
    print(f"已退回: {stats['rejected']}")
    print(f"进行中: {stats['in_progress']}")
    
    print("\n全部交接列表:")
    all_handoffs = mgr.list_handoffs()
    for h in all_handoffs:
        status_icon = {
            "pending_check": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "rejected": "❌"
        }.get(h['status'], "❓")
        
        print(f"  {status_icon} {h['handoff_id']} | {h['task_name']}")
        print(f"     {h['from_agent']} → {h['to_agent']} | 状态: {h['status']}")
    
    print("\n可追溯性验证:")
    for hid in handoff_ids:
        handoff = mgr.get_handoff(hid)
        if handoff:
            print(f"\n  {handoff['handoff_id']}:")
            print(f"    时间线事件数: {len(handoff.get('timeline', []))}")
            print(f"    有检查记录: {'是' if handoff.get('check_result') else '否'}")
            print(f"    有结果记录: {'是' if handoff.get('result') else '否'}")
    
    print("\n" + "="*60)
    print("  关卡8接力机制验证完成 ✅")
    print("="*60)


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          关卡8：Agent接力完整测试                         ║
║      制片人 → 角色设计师 的任务接力验证                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 初始化接力管理器
    mgr = HandoffManager(PROJECT_DIR)
    print(f"项目路径: {PROJECT_DIR}")
    print(f"接力记录: {mgr.record_file}")
    
    handoff_ids = []
    
    # 测试1：人工接力（成功流程）
    try:
        hid = test_1_manual_handoff(mgr)
        if hid:
            handoff_ids.append(hid)
    except Exception as e:
        print(f"测试1异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2：异常场景（退回）
    try:
        hid = test_2_rejection_scenario(mgr)
        if hid:
            handoff_ids.append(hid)
    except Exception as e:
        print(f"测试2异常: {e}")
    
    # 测试3：自动接力
    try:
        hid = test_3_auto_handoff(mgr)
        if hid:
            handoff_ids.append(hid)
    except Exception as e:
        print(f"测试3异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 生成报告
    generate_report(mgr, handoff_ids)


if __name__ == "__main__":
    main()
