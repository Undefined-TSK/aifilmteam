#!/usr/bin/env python3
"""
预算管理工具
支持设置预算、记录消耗、预警、熔断

用法：
  python budget.py status <project_path>              # 查看预算状态
  python budget.py set <project_path> <total_amount>  # 设置总预算
  python budget.py add <project_path> <amount> <description>  # 追加预算
  python budget.py spend <project_path> <amount> <description> <asset_name>  # 记录一笔支出
  python budget.py check <project_path> <amount>      # 检查是否还能支出amount（返回can_spend: bool）
  python budget.py history <project_path>             # 查看支出历史
"""

import sys
import json
from datetime import datetime
from pathlib import Path

BUDGET_FILE = "budget.json"


def get_budget_path(project_path):
    return Path(project_path) / BUDGET_FILE


def load_budget(project_path):
    """加载预算数据"""
    budget_path = get_budget_path(project_path)
    if not budget_path.exists():
        return {
            "total_budget": 0,
            "spent": 0,
            "remaining": 0,
            "currency": "CNY",
            "warning_threshold": 0.8,  # 用了80%时预警
            "frozen": False,
            "transactions": []
        }
    with open(budget_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_budget(project_path, budget):
    """保存预算数据"""
    budget_path = get_budget_path(project_path)
    budget_path.parent.mkdir(parents=True, exist_ok=True)
    with open(budget_path, "w", encoding="utf-8") as f:
        json.dump(budget, f, ensure_ascii=False, indent=2)


def status(project_path):
    """查看预算状态"""
    budget = load_budget(project_path)
    
    used_percent = (budget["spent"] / budget["total_budget"] * 100) if budget["total_budget"] > 0 else 0
    remaining_percent = 100 - used_percent
    
    warning = False
    critical = False
    if used_percent >= 80:
        warning = True
    if used_percent >= 100:
        critical = True
    
    result = {
        "total_budget": budget["total_budget"],
        "spent": budget["spent"],
        "remaining": budget["remaining"],
        "currency": budget["currency"],
        "used_percent": round(used_percent, 1),
        "remaining_percent": round(remaining_percent, 1),
        "warning": warning,
        "critical": critical,
        "frozen": budget.get("frozen", False),
        "transaction_count": len(budget["transactions"])
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def set_budget(project_path, total_amount):
    """设置总预算"""
    budget = load_budget(project_path)
    budget["total_budget"] = float(total_amount)
    budget["remaining"] = budget["total_budget"] - budget["spent"]
    
    save_budget(project_path, budget)
    print(json.dumps({
        "status": "set",
        "total_budget": budget["total_budget"],
        "remaining": budget["remaining"]
    }, ensure_ascii=False, indent=2))


def add_budget(project_path, amount, description):
    """追加预算"""
    budget = load_budget(project_path)
    amount = float(amount)
    
    budget["total_budget"] += amount
    budget["remaining"] += amount
    
    budget["transactions"].append({
        "type": "add",
        "amount": amount,
        "description": description,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    if budget.get("frozen", False):
        budget["frozen"] = False  # 追加预算后解冻
    
    save_budget(project_path, budget)
    print(json.dumps({
        "status": "added",
        "added_amount": amount,
        "new_total": budget["total_budget"],
        "remaining": budget["remaining"]
    }, ensure_ascii=False, indent=2))


def spend(project_path, amount, description, asset_name):
    """记录一笔支出"""
    budget = load_budget(project_path)
    amount = float(amount)
    
    # 检查是否冻结
    if budget.get("frozen", False):
        print(json.dumps({
            "status": "frozen",
            "message": "预算已冻结，无法支出。请先追加预算。"
        }, ensure_ascii=False, indent=2))
        return
    
    # 检查余额
    if amount > budget["remaining"]:
        print(json.dumps({
            "status": "insufficient",
            "message": f"余额不足。需要: {amount}, 剩余: {budget['remaining']}"
        }, ensure_ascii=False, indent=2))
        return
    
    budget["spent"] += amount
    budget["remaining"] -= amount
    
    budget["transactions"].append({
        "type": "spend",
        "amount": amount,
        "description": description,
        "asset_name": asset_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # 检查是否触发熔断
    if budget["remaining"] <= 0:
        budget["frozen"] = True
    
    save_budget(project_path, budget)
    
    used_percent = (budget["spent"] / budget["total_budget"] * 100) if budget["total_budget"] > 0 else 0
    warning = used_percent >= 80
    critical = budget.get("frozen", False)
    
    print(json.dumps({
        "status": "spent",
        "spent_amount": amount,
        "remaining": budget["remaining"],
        "used_percent": round(used_percent, 1),
        "warning": warning,
        "critical": critical
    }, ensure_ascii=False, indent=2))


def check_can_spend(project_path, amount):
    """检查是否还能支出amount"""
    budget = load_budget(project_path)
    amount = float(amount)
    
    can_spend = amount <= budget["remaining"] and not budget.get("frozen", False)
    used_percent = (budget["spent"] / budget["total_budget"] * 100) if budget["total_budget"] > 0 else 0
    
    print(json.dumps({
        "can_spend": can_spend,
        "requested": amount,
        "remaining": budget["remaining"],
        "used_percent": round(used_percent, 1),
        "frozen": budget.get("frozen", False),
        "warning": used_percent >= 80
    }, ensure_ascii=False, indent=2))


def history(project_path):
    """查看支出历史"""
    budget = load_budget(project_path)
    transactions = budget.get("transactions", [])
    transactions.reverse()  # 最新的在前
    
    print(json.dumps({
        "total_count": len(transactions),
        "transactions": transactions[:20]  # 最多显示20条
    }, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    project_path = sys.argv[2]
    
    if command == "status":
        status(project_path)
    elif command == "set":
        if len(sys.argv) < 4:
            print("用法: set <project_path> <total_amount>")
            sys.exit(1)
        set_budget(project_path, sys.argv[3])
    elif command == "add":
        if len(sys.argv) < 5:
            print("用法: add <project_path> <amount> <description>")
            sys.exit(1)
        add_budget(project_path, sys.argv[3], sys.argv[4])
    elif command == "spend":
        if len(sys.argv) < 6:
            print("用法: spend <project_path> <amount> <description> <asset_name>")
            sys.exit(1)
        spend(project_path, sys.argv[3], sys.argv[4], sys.argv[5])
    elif command == "check":
        if len(sys.argv) < 4:
            print("用法: check <project_path> <amount>")
            sys.exit(1)
        check_can_spend(project_path, sys.argv[3])
    elif command == "history":
        history(project_path)
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
