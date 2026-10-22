import json
import sys

sys.path.insert(0, r"D:\ai_film_projects\tools")
from handoff_manager import HandoffManager

PROJECT = r"D:\ai_film_projects\projects\雨夜寻猫"
mgr = HandoffManager(PROJECT)

check = mgr.check_handoff("EDIT-20260925-0FE4", "editor")
print("CHECK:", json.dumps(check, ensure_ascii=False, indent=2))

if check.get("passed", False):
    accept = mgr.accept_handoff("EDIT-20260925-0FE4", "editor")
    print("ACCEPT:", json.dumps(accept, ensure_ascii=False, indent=2))
else:
    print("检查未通过，不执行接受")
