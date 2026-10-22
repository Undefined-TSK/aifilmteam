"""
Agent 接力调度管理器（Handoff Manager）
=========================================
关卡8核心工具：实现两个Agent之间的任务接力，全程可追溯。

功能：
1. 创建交接任务（上游→下游）
2. 下游接收检查（材料完整性、权限、任务匹配）
3. 接受/退回交接
4. 完成交接并记录结果
5. 查询交接历史和状态

交接协议（标准格式）：
{
  "handoff_id": "CHAR-20240822-001",
  "task_name": "林月角色设计",
  "from_agent": "producer",
  "to_agent": "character_designer",
  "work_background": "工作背景描述",
  "deliverables": {
    "上游交付物列表": "..."
  },
  "downstream_task": "下游需要完成什么",
  "completion_criteria": "完成标准",
  "stop_conditions": "停止条件（什么情况不处理）",
  "pending_items": "待确认事项",
  "material_version": "v1",
  "created_at": "时间戳",
  "status": "pending_check / accepted / rejected / completed",
  "check_result": {
    "checked": true/false,
    "passed": true/false,
    "issues": ["问题列表"],
    "checked_at": "时间戳"
  },
  "result": {
    "deliverables": {},
    "completed_at": "时间戳"
  }
}
"""

import json
import uuid
from pathlib import Path
from datetime import datetime


class HandoffManager:
    """Agent 接力调度管理器"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.handoff_dir = self.project_path / "handoffs"
        self.handoff_dir.mkdir(parents=True, exist_ok=True)
        self.record_file = self.handoff_dir / "handoff_record.json"
        self._init_record()
    
    def _init_record(self):
        """初始化交接记录文件"""
        if not self.record_file.exists():
            record = {
                "handoffs": [],
                "stats": {
                    "total": 0,
                    "completed": 0,
                    "rejected": 0,
                    "in_progress": 0
                }
            }
            self._save_record(record)
    
    def _load_record(self):
        """加载交接记录"""
        with open(self.record_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_record(self, record):
        """保存交接记录"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    
    def create_handoff(self, from_agent, to_agent, task_name, 
                       work_background, deliverables, downstream_task,
                       completion_criteria, stop_conditions, 
                       pending_items=None, material_version="v1"):
        """
        创建一个新的交接任务
        
        Args:
            from_agent: 上游Agent名称
            to_agent: 下游Agent名称
            task_name: 任务名称
            work_background: 工作背景
            deliverables: 上游交付物（dict）
            downstream_task: 下游任务描述
            completion_criteria: 完成标准
            stop_conditions: 停止条件
            pending_items: 待确认事项列表
            material_version: 材料版本
        
        Returns:
            交接任务信息
        """
        handoff_id = f"{to_agent[:4].upper()}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        handoff = {
            "handoff_id": handoff_id,
            "task_name": task_name,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "work_background": work_background,
            "deliverables": deliverables,
            "downstream_task": downstream_task,
            "completion_criteria": completion_criteria,
            "stop_conditions": stop_conditions,
            "pending_items": pending_items or [],
            "material_version": material_version,
            "created_at": datetime.now().isoformat(),
            "status": "pending_check",
            "timeline": [
                {
                    "event": "created",
                    "agent": from_agent,
                    "message": f"创建交接任务，等待 {to_agent} 检查",
                    "time": datetime.now().isoformat()
                }
            ],
            "check_result": None,
            "result": None
        }
        
        # 保存单个交接文件
        handoff_file = self.handoff_dir / f"{handoff_id}.json"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff, f, ensure_ascii=False, indent=2)
        
        # 更新总记录
        record = self._load_record()
        record["handoffs"].append({
            "handoff_id": handoff_id,
            "task_name": task_name,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "status": "pending_check",
            "created_at": handoff["created_at"]
        })
        record["stats"]["total"] += 1
        record["stats"]["in_progress"] += 1
        self._save_record(record)
        
        return handoff
    
    def get_handoff(self, handoff_id):
        """获取交接任务详情"""
        handoff_file = self.handoff_dir / f"{handoff_id}.json"
        if not handoff_file.exists():
            return None
        with open(handoff_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _update_handoff(self, handoff):
        """更新交接任务文件"""
        handoff_file = self.handoff_dir / f"{handoff['handoff_id']}.json"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff, f, ensure_ascii=False, indent=2)
        
        # 更新总记录中的状态
        record = self._load_record()
        for h in record["handoffs"]:
            if h["handoff_id"] == handoff["handoff_id"]:
                h["status"] = handoff["status"]
                break
        self._save_record(record)
    
    def check_handoff(self, handoff_id, checker_agent):
        """
        下游Agent检查交接材料
        
        检查项：
        1. 材料是否完整（关键字段是否存在）
        2. 交付物路径是否存在（文件检查）
        3. 任务是否属于本Agent职责范围
        4. 待确认事项是否明确标注
        5. 停止条件是否触发
        
        Returns:
            {
                "passed": bool,
                "issues": [问题列表],
                "should_stop": bool,
                "stop_reason": str
            }
        """
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return {"passed": False, "issues": ["交接任务不存在"], "should_stop": True}
        
        issues = []
        should_stop = False
        stop_reason = ""
        
        # 检查1: 基本字段完整性
        required_fields = ["task_name", "work_background", "deliverables", 
                          "downstream_task", "completion_criteria"]
        for field in required_fields:
            if not handoff.get(field):
                issues.append(f"缺少必填字段: {field}")
                should_stop = True
        
        # 检查2: 交付物中的文件是否存在（仅检查看起来像文件路径的值）
        deliverables = handoff.get("deliverables", {})
        if isinstance(deliverables, dict):
            for key, value in deliverables.items():
                if isinstance(value, str):
                    # 判断是否为文件路径：包含路径分隔符或常见文件扩展名
                    is_filepath = (
                        '/' in value or '\\' in value or
                        value.endswith('.png') or value.endswith('.jpg') or 
                        value.endswith('.jpeg') or value.endswith('.md') or
                        value.endswith('.json') or value.endswith('.mp4')
                    )
                    # 判断是否为"描述性文字"（较长的中文描述，不像路径）
                    is_description = (
                        len(value) > 20 and 
                        '\u4e00' <= value[0] <= '\u9fff' and
                        not '/' in value and not '\\' in value
                    )
                    
                    if is_filepath and not is_description:
                        filepath = Path(value)
                        filepath2 = self.project_path / value
                        if not filepath.exists() and not filepath2.exists():
                            issues.append(f"交付物文件不存在: {key}")
                            should_stop = True
        
        # 检查2b: 交付物质量检查（角色描述是否足够详细）
        if checker_agent == "character_designer":
            char_desc = ""
            # 找角色描述字段
            for key in ["角色描述", "character_desc", "description"]:
                if key in deliverables and isinstance(deliverables[key], str):
                    char_desc = deliverables[key]
                    break
            
            # 如果角色描述太短或太模糊
            if char_desc and len(char_desc) < 10:
                issues.append("角色描述过于模糊，缺少足够的外貌特征")
                should_stop = True
            elif char_desc and any(kw in char_desc for kw in ["路人", "随便", "一个人", "普通"]):
                issues.append("角色描述过于笼统，缺乏辨识度特征")
                should_stop = True
        
        # 检查3: 任务是否匹配（基于Agent职责的简单判断）
        # 角色设计师只接角色相关任务
        if checker_agent == "character_designer":
            task_lower = handoff["downstream_task"].lower()
            name_lower = handoff["task_name"].lower()
            character_keywords = ["角色", "人物", "character", "三视图", "表情", "角色设计"]
            is_character_task = any(kw in task_lower or kw in name_lower 
                                    for kw in character_keywords)
            if not is_character_task:
                issues.append("任务类型不匹配：角色设计师只处理角色设计任务")
                should_stop = True
                stop_reason = "任务类型不匹配"
        
        # 检查4: 停止条件是否触发
        stop_conditions = handoff.get("stop_conditions", "")
        if stop_conditions and "链接打不开" in stop_conditions:
            # 如果有文件不存在的问题，触发停止条件
            if any("交付物不存在" in i for i in issues):
                should_stop = True
                stop_reason = "触发停止条件：必要交付物不存在"
        
        # 记录检查结果
        handoff["check_result"] = {
            "checked": True,
            "checked_by": checker_agent,
            "passed": len(issues) == 0,
            "issues": issues,
            "should_stop": should_stop,
            "stop_reason": stop_reason,
            "checked_at": datetime.now().isoformat()
        }
        
        handoff["timeline"].append({
            "event": "checked",
            "agent": checker_agent,
            "message": f"检查完成：{'通过' if len(issues) == 0 else f'发现 {len(issues)} 个问题'}",
            "time": datetime.now().isoformat()
        })
        
        self._update_handoff(handoff)
        return handoff["check_result"]
    
    def accept_handoff(self, handoff_id, agent):
        """下游Agent接受交接任务"""
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return None
        
        # 必须先检查
        if not handoff.get("check_result") or not handoff["check_result"].get("checked"):
            return {"error": "请先执行检查后再决定是否接受"}
        
        if handoff["check_result"]["should_stop"]:
            return {"error": "检查不通过，无法接受，请先退回上游", 
                    "reason": handoff["check_result"]["stop_reason"]}
        
        handoff["status"] = "in_progress"
        handoff["timeline"].append({
            "event": "accepted",
            "agent": agent,
            "message": "已接受任务，开始处理",
            "time": datetime.now().isoformat()
        })
        
        self._update_handoff(handoff)
        return handoff
    
    def reject_handoff(self, handoff_id, agent, reason, details=None):
        """
        下游Agent退回交接任务
        
        Args:
            handoff_id: 交接ID
            agent: 退回的Agent
            reason: 退回原因
            details: 详细说明
        """
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return None
        
        handoff["status"] = "rejected"
        handoff["rejection"] = {
            "rejected_by": agent,
            "reason": reason,
            "details": details or "",
            "rejected_at": datetime.now().isoformat()
        }
        handoff["timeline"].append({
            "event": "rejected",
            "agent": agent,
            "message": f"任务被退回，原因：{reason}",
            "time": datetime.now().isoformat()
        })
        
        # 更新统计
        record = self._load_record()
        record["stats"]["rejected"] += 1
        record["stats"]["in_progress"] -= 1
        self._save_record(record)
        
        self._update_handoff(handoff)
        return handoff
    
    def complete_handoff(self, handoff_id, agent, result_deliverables):
        """
        下游Agent完成任务，交付结果
        
        Args:
            handoff_id: 交接ID
            agent: 完成的Agent
            result_deliverables: 结果交付物dict
        """
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return None
        
        handoff["status"] = "completed"
        handoff["result"] = {
            "deliverables": result_deliverables,
            "completed_by": agent,
            "completed_at": datetime.now().isoformat()
        }
        handoff["timeline"].append({
            "event": "completed",
            "agent": agent,
            "message": "任务完成，已交付结果",
            "time": datetime.now().isoformat()
        })
        
        # 更新统计
        record = self._load_record()
        record["stats"]["completed"] += 1
        record["stats"]["in_progress"] -= 1
        self._save_record(record)
        
        self._update_handoff(handoff)
        return handoff
    
    def list_handoffs(self, status=None, from_agent=None, to_agent=None):
        """列出交接任务，可按条件筛选"""
        record = self._load_record()
        handoffs = record["handoffs"]
        
        if status:
            handoffs = [h for h in handoffs if h["status"] == status]
        if from_agent:
            handoffs = [h for h in handoffs if h["from_agent"] == from_agent]
        if to_agent:
            handoffs = [h for h in handoffs if h["to_agent"] == to_agent]
        
        return handoffs
    
    def get_timeline(self, handoff_id):
        """获取交接任务的时间线（可追溯）"""
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return None
        return handoff.get("timeline", [])
    
    def get_stats(self):
        """获取统计信息"""
        record = self._load_record()
        return record["stats"]
    
    def print_summary(self, handoff_id):
        """打印交接任务摘要（用于日志输出）"""
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return "交接任务不存在"
        
        lines = [
            f"=== 交接任务: {handoff['handoff_id']} ===",
            f"任务名称: {handoff['task_name']}",
            f"上游: {handoff['from_agent']} → 下游: {handoff['to_agent']}",
            f"状态: {handoff['status']}",
            f"创建时间: {handoff['created_at']}",
            "",
            f"工作背景: {handoff['work_background'][:80]}...",
            f"下游任务: {handoff['downstream_task'][:80]}...",
            "",
            "--- 时间线 ---"
        ]
        
        for i, event in enumerate(handoff.get("timeline", [])):
            lines.append(f"  {i+1}. [{event['time']}] {event['agent']}: {event['message']}")
        
        if handoff.get("check_result"):
            cr = handoff["check_result"]
            lines.append("")
            lines.append("--- 检查结果 ---")
            lines.append(f"  检查人: {cr['checked_by']}")
            lines.append(f"  通过: {cr['passed']}")
            if cr["issues"]:
                lines.append(f"  问题:")
                for issue in cr["issues"]:
                    lines.append(f"    - {issue}")
        
        if handoff.get("result"):
            r = handoff["result"]
            lines.append("")
            lines.append("--- 交付结果 ---")
            lines.append(f"  完成人: {r['completed_by']}")
            lines.append(f"  交付物: {list(r['deliverables'].keys())}")
        
        return "\n".join(lines)


# ============ 命令行接口 ============

import sys

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python handoff_manager.py <项目路径> create <参数...>  - 创建交接")
        print("  python handoff_manager.py <项目路径> check <handoff_id> <agent> - 检查交接")
        print("  python handoff_manager.py <项目路径> accept <handoff_id> <agent> - 接受交接")
        print("  python handoff_manager.py <项目路径> reject <handoff_id> <agent> <原因> - 退回交接")
        print("  python handoff_manager.py <项目路径> complete <handoff_id> <agent> <交付物JSON> - 完成交接")
        print("  python handoff_manager.py <项目路径> get <handoff_id> - 查看交接详情")
        print("  python handoff_manager.py <项目路径> list [状态] - 列出交接")
        print("  python handoff_manager.py <项目路径> stats - 查看统计")
        print("  python handoff_manager.py <项目路径> timeline <handoff_id> - 查看时间线")
        return
    
    project_path = sys.argv[1]
    command = sys.argv[2]
    
    mgr = HandoffManager(project_path)
    
    if command == "create":
        # 简化版：直接用参数创建一个示例交接
        if len(sys.argv) < 9:
            print("参数不足")
            return
        handoff = mgr.create_handoff(
            from_agent=sys.argv[3],
            to_agent=sys.argv[4],
            task_name=sys.argv[5],
            work_background=sys.argv[6],
            deliverables=json.loads(sys.argv[7]),
            downstream_task=sys.argv[8],
            completion_criteria=sys.argv[9] if len(sys.argv) > 9 else "按标准交付",
            stop_conditions=sys.argv[10] if len(sys.argv) > 10 else ""
        )
        print(json.dumps(handoff, ensure_ascii=False, indent=2))
    
    elif command == "check":
        if len(sys.argv) < 5:
            print("参数不足")
            return
        result = mgr.check_handoff(sys.argv[3], sys.argv[4])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "accept":
        if len(sys.argv) < 5:
            print("参数不足")
            return
        result = mgr.accept_handoff(sys.argv[3], sys.argv[4])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "reject":
        if len(sys.argv) < 6:
            print("参数不足")
            return
        result = mgr.reject_handoff(sys.argv[3], sys.argv[4], sys.argv[5])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "complete":
        if len(sys.argv) < 6:
            print("参数不足")
            return
        deliverables = json.loads(sys.argv[5])
        result = mgr.complete_handoff(sys.argv[3], sys.argv[4], deliverables)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 4:
            print("参数不足")
            return
        handoff = mgr.get_handoff(sys.argv[3])
        if handoff:
            print(mgr.print_summary(sys.argv[3]))
        else:
            print("交接任务不存在")
    
    elif command == "list":
        status = sys.argv[3] if len(sys.argv) > 3 else None
        handoffs = mgr.list_handoffs(status=status)
        print(json.dumps(handoffs, ensure_ascii=False, indent=2))
    
    elif command == "stats":
        stats = mgr.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif command == "timeline":
        if len(sys.argv) < 4:
            print("参数不足")
            return
        timeline = mgr.get_timeline(sys.argv[3])
        print(json.dumps(timeline, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
