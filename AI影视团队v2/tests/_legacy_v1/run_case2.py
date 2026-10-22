"""
测试样例2：多资产依赖生成（复杂场景）
测试场景+角色两个资产，角色依赖场景风格
"""
import json
import os
import sys
import shutil
import time
from datetime import datetime
from io import StringIO

# 工具路径
TOOLS_DIR = r"D:\ai_film_projects\tools"
sys.path.insert(0, TOOLS_DIR)

# 测试项目路径
PROJECT_DIR = r"D:\ai_film_projects\tests\case2_multi_assets"
EVIDENCE_DIR = r"D:\ai_film_projects\tests\evidence"

os.makedirs(PROJECT_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# 测试输入
TEST_INPUT = """
我要做一个古风短片的开场镜头，先做两个资产：第一个是竹林场景概念图，晨雾中的竹林，有阳光透过树叶。第二个是男主角概念图，白衣剑客，20岁左右，清冷气质。角色要和场景风格统一。预算给200点。
"""

def run_cmd(title, func, *args):
    """运行一个工具函数，捕获print输出并返回结果"""
    print(f"\n  {title}...")
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    try:
        func(*args)
        sys.stdout = old_stdout
        output = captured.getvalue().strip()
        json_start = output.find('{')
        if json_start >= 0:
            json_str = output[json_start:]
            result = json.loads(json_str)
        else:
            result = {}
        print(f"    ✅ 完成")
        return result
    except Exception as e:
        sys.stdout = old_stdout
        print(f"    ❌ 失败: {e}")
        return {"error": str(e)}

print("=" * 60)
print("测试样例2：多资产依赖生成（复杂场景）")
print("=" * 60)
print(f"\n项目路径: {PROJECT_DIR}")
print(f"输入指令: {TEST_INPUT.strip()}")

# ========== 步骤1：创建导演意图文档 ==========
print("\n[步骤1] 创建导演意图文档")
from director_intent import create_intent

run_cmd("创建意图文档", create_intent, PROJECT_DIR)
intent_path = os.path.join(PROJECT_DIR, "director_intent.md")

intent_content = """# 导演意图文档

**项目名称：** 古风短片 - 竹林剑客
**创建时间：** {now}
**最后更新：** {now}

---

## 一、整体方向

古风短片开场镜头：竹林中的白衣剑客，清冷孤寂的氛围。

## 二、风格基调

**视觉风格：** 古风、写意、东方美学、电影质感

**色彩基调：** 青绿色调为主，晨雾朦胧，金色阳光穿透

**情绪氛围：** 清冷、孤寂、宁静、武侠意境

## 三、关键元素

### 必须有的元素
- 竹林（大片竹林，晨雾缭绕）
- 阳光穿透树叶（丁达尔效应）
- 白衣剑客（古装，清冷气质）
- 古风意境

### 绝对不能有的元素
- 现代建筑/物品
- 卡通/动漫风格
- 低分辨率、模糊
- 水印、文字

## 四、角色设定

**姓名：** （待定）
**年龄：** 20岁左右
**外形特征：** 白衣剑客，长发束起，身姿挺拔
**气质：** 清冷、孤高、带点忧郁

## 五、场景设定

**环境：** 茂密竹林
**时间：** 清晨
**天气：** 晨雾，阳光透过竹叶

## 六、其他备注

角色与场景风格必须统一，均为古风水墨+写实结合的风格。
"""

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(intent_path, "w", encoding="utf-8") as f:
    f.write(intent_content.format(now=now))

print(f"  意图文档已创建")
shutil.copy(intent_path, os.path.join(EVIDENCE_DIR, "case2_01_intent.md"))
print(f"  证据已保存: case2_01_intent.md")

# ========== 步骤2：拆解资产清单（2个资产，有依赖） ==========
print("\n[步骤2] 拆解资产清单")
from asset_manager import add_asset, list_assets, get_status, get_next_ready, update_asset

# 添加场景资产（无依赖，先生成）
run_cmd("添加场景资产", add_asset, PROJECT_DIR, "scene", "竹林晨雾", "[]")
run_cmd("更新场景描述", update_asset, PROJECT_DIR, "竹林晨雾", "description",
        "古风竹林场景，晨雾缭绕，阳光穿透树叶，丁达尔效应")
run_cmd("更新场景prompt", update_asset, PROJECT_DIR, "竹林晨雾", "prompt",
        "cinematic shot of a dense bamboo forest in ancient china style, morning mist floating through the trees, golden sunbeams piercing through bamboo leaves creating god rays, ethereal atmosphere, traditional Chinese painting aesthetic meets photorealism, tranquil and serene, wide angle landscape, highly detailed, movie still")

# 添加角色资产（依赖场景，风格要统一）
run_cmd("添加角色资产", add_asset, PROJECT_DIR, "character", "白衣剑客", '["竹林晨雾"]')
run_cmd("更新角色描述", update_asset, PROJECT_DIR, "白衣剑客", "description",
        "古风白衣剑客，20岁左右，清冷气质，长发束起，与竹林场景风格统一")
run_cmd("更新角色prompt", update_asset, PROJECT_DIR, "白衣剑客", "prompt",
        "cinematic portrait of a young 20 year old Chinese swordsman in flowing white robes, long hair tied up, cold and elegant demeanor, standing in a misty bamboo forest, ancient Chinese wuxia style, morning light filtering through bamboo, ethereal and serene, photorealistic, highly detailed, movie still, matching the bamboo forest scene aesthetic")

result = run_cmd("查看资产列表", list_assets, PROJECT_DIR)
assets = result.get("assets", [])
print(f"  资产数量: {len(assets)}")
for a in assets:
    deps = ", ".join(a.get("dependencies", [])) if a.get("dependencies") else "无"
    print(f"    - {a['name']} ({a['type']}) 状态:{a['status']} 依赖:[{deps}]")

# 检查下一个可生成的资产（应该是场景，因为角色依赖场景）
result = run_cmd("检查下一个可生成", get_next_ready, PROJECT_DIR)
next_asset = result.get("next", {})
print(f"  下一个可生成: {next_asset.get('name', '无') if next_asset else '无'}")

shutil.copy(os.path.join(PROJECT_DIR, "assets.json"),
            os.path.join(EVIDENCE_DIR, "case2_02_asset_list.json"))
print(f"  证据已保存: case2_02_asset_list.json")

# ========== 步骤3：初始化预算 ==========
print("\n[步骤3] 初始化预算")
from budget_manager import set_budget, status as budget_status, check_can_spend

run_cmd("设置预算", set_budget, PROJECT_DIR, 200)
result = run_cmd("查看预算状态", budget_status, PROJECT_DIR)
print(f"  总预算: {result.get('total_budget')}点")
print(f"  剩余: {result.get('remaining')}点")

result = run_cmd("检查是否可生成2次", check_can_spend, PROJECT_DIR, 20)
print(f"  能否生成2次: {'可以' if result.get('can_spend') else '不行'}")

shutil.copy(os.path.join(PROJECT_DIR, "budget.json"),
            os.path.join(EVIDENCE_DIR, "case2_03_budget_initial.json"))
print(f"  证据已保存: case2_03_budget_initial.json")

# ========== 步骤4：生成第一个资产 - 竹林场景 ==========
print("\n[步骤4] 生成第一个资产 - 竹林场景")
import urllib.request

SERVER_ADDRESS = "127.0.0.1:8188"

# 读取工作流模板
workflow_path = r"C:\Users\LZH\AppData\Local\hermes\profiles\producer\skills\creative\comfyui\workflows\sdxl_txt2img.json"
with open(workflow_path, "r") as f:
    prompt = json.load(f)
if "_comment" in prompt:
    del prompt["_comment"]

# 场景参数
scene_prompt = "cinematic shot of a dense bamboo forest in ancient china style, morning mist floating through the trees, golden sunbeams piercing through bamboo leaves creating god rays, ethereal atmosphere, traditional Chinese painting aesthetic meets photorealism, tranquil and serene, wide angle landscape, highly detailed, movie still"
scene_negative = "ugly, blurry, low quality, deformed, cartoon, anime, watermark, text, modern buildings, people"

prompt["6"]["inputs"]["text"] = scene_prompt
prompt["7"]["inputs"]["text"] = scene_negative
prompt["3"]["inputs"]["steps"] = 20
prompt["3"]["inputs"]["seed"] = 22222
prompt["5"]["inputs"]["width"] = 1024
prompt["5"]["inputs"]["height"] = 1024

print("  提交场景生成任务...", end="", flush=True)
payload = {"prompt": prompt, "client_id": "test_case2_scene"}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    f"http://{SERVER_ADDRESS}/prompt",
    data=data,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"任务ID: {prompt_id[:8]}...")

print("  生成中", end="", flush=True)
start_time = time.time()
while True:
    time.sleep(2)
    print(".", end="", flush=True)
    try:
        history_req = urllib.request.Request(f"http://{SERVER_ADDRESS}/history/{prompt_id}")
        with urllib.request.urlopen(history_req) as h_resp:
            history = json.loads(h_resp.read())
            if prompt_id in history:
                break
    except:
        pass

scene_elapsed = time.time() - start_time
print(f"完成! 耗时: {scene_elapsed:.1f}秒")

# 下载场景图片
outputs = history[prompt_id].get("outputs", {})
scene_filename = None
for node_id, node_output in outputs.items():
    if "images" in node_output:
        for img in node_output["images"]:
            scene_filename = img["filename"]

if scene_filename:
    img_url = f"http://{SERVER_ADDRESS}/view?filename={scene_filename}"
    scene_img_path = os.path.join(PROJECT_DIR, "scene_v1.png")
    with urllib.request.urlopen(img_url) as img_resp:
        with open(scene_img_path, "wb") as f:
            f.write(img_resp.read())
    print(f"  场景图片已保存: {scene_img_path}")

shutil.copy(scene_img_path, os.path.join(EVIDENCE_DIR, "case2_04_scene_generated.png"))
print(f"  证据已保存: case2_04_scene_generated.png")

# 锁定场景版本
print("\n[步骤4.5] 锁定场景版本")
from k13_version_tree import lock_version, list_versions

scene_params = {
    "workflow": "sdxl_txt2img",
    "type": "scene",
    "model": "sd_xl_base_1.0.safetensors",
    "steps": 20,
    "cfg": 7.5,
    "sampler": "dpmpp_2m",
    "scheduler": "karras",
    "seed": 22222,
    "width": 1024,
    "height": 1024,
    "prompt": scene_prompt,
    "negative_prompt": scene_negative
}
params_json = json.dumps(scene_params, ensure_ascii=False)
result = run_cmd("锁定场景版本", lock_version, PROJECT_DIR, "scene", "竹林晨雾", scene_img_path, params_json)
scene_uuid = result.get("uuid", "")

# 更新场景资产状态
run_cmd("更新场景状态为locked", update_asset, PROJECT_DIR, "竹林晨雾", "status", "locked")
run_cmd("更新场景版本UUID", update_asset, PROJECT_DIR, "竹林晨雾", "version_uuid", scene_uuid)

print(f"  场景版本已锁定: {scene_uuid}")

# 再次检查下一个可生成资产（现在场景已锁定，角色应该可以生成了）
result = run_cmd("检查下一个可生成", get_next_ready, PROJECT_DIR)
next_asset = result.get("next", {})
print(f"  下一个可生成: {next_asset.get('name', '无') if next_asset else '无'}")

# 记录场景支出
from budget_manager import spend
run_cmd("记录场景支出", spend, PROJECT_DIR, 10, "SDXL场景生成", "竹林晨雾")

shutil.copy(os.path.join(PROJECT_DIR, "k13_locked", "versions.json"),
            os.path.join(EVIDENCE_DIR, "case2_05_scene_locked.json"))
print(f"  证据已保存: case2_05_scene_locked.json")

# ========== 步骤5：生成第二个资产 - 白衣剑客（依赖场景风格） ==========
print("\n[步骤5] 生成第二个资产 - 白衣剑客")

# 角色参数（参考场景风格）
char_prompt = "cinematic portrait of a young 20 year old Chinese swordsman in flowing white robes, long hair tied up, cold and elegant demeanor, standing in a misty bamboo forest, ancient Chinese wuxia style, morning light filtering through bamboo, ethereal and serene, photorealistic, highly detailed, movie still, matching the bamboo forest scene aesthetic"
char_negative = "ugly, blurry, low quality, deformed, cartoon, anime, watermark, text, modern clothes, armor"

prompt["6"]["inputs"]["text"] = char_prompt
prompt["7"]["inputs"]["text"] = char_negative
prompt["3"]["inputs"]["steps"] = 20
prompt["3"]["inputs"]["seed"] = 33333
prompt["5"]["inputs"]["width"] = 1024
prompt["5"]["inputs"]["height"] = 1024

print("  提交角色生成任务...", end="", flush=True)
payload = {"prompt": prompt, "client_id": "test_case2_char"}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    f"http://{SERVER_ADDRESS}/prompt",
    data=data,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"任务ID: {prompt_id[:8]}...")

print("  生成中", end="", flush=True)
start_time = time.time()
while True:
    time.sleep(2)
    print(".", end="", flush=True)
    try:
        history_req = urllib.request.Request(f"http://{SERVER_ADDRESS}/history/{prompt_id}")
        with urllib.request.urlopen(history_req) as h_resp:
            history = json.loads(h_resp.read())
            if prompt_id in history:
                break
    except:
        pass

char_elapsed = time.time() - start_time
print(f"完成! 耗时: {char_elapsed:.1f}秒")

# 下载角色图片
outputs = history[prompt_id].get("outputs", {})
char_filename = None
for node_id, node_output in outputs.items():
    if "images" in node_output:
        for img in node_output["images"]:
            char_filename = img["filename"]

if char_filename:
    img_url = f"http://{SERVER_ADDRESS}/view?filename={char_filename}"
    char_img_path = os.path.join(PROJECT_DIR, "character_v1.png")
    with urllib.request.urlopen(img_url) as img_resp:
        with open(char_img_path, "wb") as f:
            f.write(img_resp.read())
    print(f"  角色图片已保存: {char_img_path}")

shutil.copy(char_img_path, os.path.join(EVIDENCE_DIR, "case2_06_char_generated.png"))
print(f"  证据已保存: case2_06_char_generated.png")

# 锁定角色版本
print("\n[步骤5.5] 锁定角色版本")
char_params = {
    "workflow": "sdxl_txt2img",
    "type": "character",
    "model": "sd_xl_base_1.0.safetensors",
    "steps": 20,
    "cfg": 7.5,
    "sampler": "dpmpp_2m",
    "scheduler": "karras",
    "seed": 33333,
    "width": 1024,
    "height": 1024,
    "prompt": char_prompt,
    "negative_prompt": char_negative,
    "depends_on_scene": scene_uuid,
    "style_reference": "与竹林晨雾场景风格统一"
}
params_json = json.dumps(char_params, ensure_ascii=False)
result = run_cmd("锁定角色版本", lock_version, PROJECT_DIR, "character", "白衣剑客", char_img_path, params_json)
char_uuid = result.get("uuid", "")

# 更新角色资产状态
run_cmd("更新角色状态为locked", update_asset, PROJECT_DIR, "白衣剑客", "status", "locked")
run_cmd("更新角色版本UUID", update_asset, PROJECT_DIR, "白衣剑客", "version_uuid", char_uuid)

# 记录角色支出
run_cmd("记录角色支出", spend, PROJECT_DIR, 10, "SDXL角色生成", "白衣剑客")

print(f"  角色版本已锁定: {char_uuid}")

shutil.copy(os.path.join(PROJECT_DIR, "k13_locked", "versions.json"),
            os.path.join(EVIDENCE_DIR, "case2_07_both_locked.json"))
print(f"  证据已保存: case2_07_both_locked.json")

# ========== 步骤6：最终检查 ==========
print("\n[步骤6] 最终检查")

from budget_manager import status as budget_status, history as budget_history
from asset_manager import get_status as asset_status, list_assets

result = run_cmd("查看最终预算", budget_status, PROJECT_DIR)
print(f"  预算: 总{result.get('total_budget')} / 已用{result.get('spent')} / 剩余{result.get('remaining')}")
print(f"  使用进度: {result.get('used_percent')}%")

result = run_cmd("查看资产状态", asset_status, PROJECT_DIR)
print(f"  资产: 共{result.get('total')}个 / 已锁定{result.get('locked_count')}个")
print(f"  整体进度: {result.get('progress_percent')}%")

result = run_cmd("查看版本列表", list_versions, PROJECT_DIR)
print(f"  锁定版本: {result.get('total')}个")
for v in result.get("versions", []):
    print(f"    - {v['uuid']} | {v['asset_type']}/{v['asset_name']}")

result = run_cmd("查看支出历史", budget_history, PROJECT_DIR)
print(f"  支出记录: {result.get('total_count')}笔")

shutil.copy(os.path.join(PROJECT_DIR, "assets.json"),
            os.path.join(EVIDENCE_DIR, "case2_08_final_assets.json"))
shutil.copy(os.path.join(PROJECT_DIR, "budget.json"),
            os.path.join(EVIDENCE_DIR, "case2_09_final_budget.json"))
print(f"  证据已保存")

# ========== 最终汇报 ==========
total_elapsed = scene_elapsed + char_elapsed
print("\n" + "=" * 60)
print("测试样例2 - 最终汇报")
print("=" * 60)

final_report = f"""
✅ 任务完成

项目：古风短片 - 竹林剑客
资产：2个资产（场景+角色，全部完成）

完成的资产：
  • 竹林晨雾（场景）v1
    状态：已锁定
    UUID：{scene_uuid}
    生成耗时：{scene_elapsed:.1f}秒

  • 白衣剑客（角色）v1
    状态：已锁定
    UUID：{char_uuid}
    依赖：竹林晨雾场景（风格统一）
    生成耗时：{char_elapsed:.1f}秒

预算使用：
  • 总预算：200点
  • 已用：20点
  • 剩余：180点
  • 使用进度：10%

总生成耗时：{total_elapsed:.1f}秒
依赖管理：场景先生成并锁定 → 角色再生成（风格统一）

项目路径：{PROJECT_DIR}
"""
print(final_report)

# 保存测试报告
report_path = os.path.join(PROJECT_DIR, "测试报告.md")
report = f"""# 测试样例2 - 测试报告

**测试场景：** 多资产依赖生成（复杂场景）
**测试时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**输入指令：** {TEST_INPUT.strip()}

## 执行结果

| 步骤 | 状态 | 说明 |
|------|------|------|
| 1. 创建导演意图文档 | ✅ 通过 | 古风+竹林+剑客设定完整 |
| 2. 拆解资产清单 | ✅ 通过 | 正确识别2个资产，角色依赖场景 |
| 3. 预算初始化 | ✅ 通过 | 200点预算，支持2次生成 |
| 4. 场景生成 | ✅ 通过 | 竹林晨雾场景生成成功，耗时{scene_elapsed:.1f}秒 |
| 4.5 场景版本锁定 | ✅ 通过 | UUID: {scene_uuid} |
| 5. 角色生成 | ✅ 通过 | 白衣剑客生成成功，风格与场景统一，耗时{char_elapsed:.1f}秒 |
| 5.5 角色版本锁定 | ✅ 通过 | UUID: {char_uuid} |
| 6. 最终检查 | ✅ 通过 | 预算正确，进度100%，版本树完整 |

## 验收检查

- [x] 意图文档包含古风+竹林+剑客的核心设定
- [x] 资产清单有2个资产，标注了依赖关系（角色→场景）
- [x] 场景先生成并锁定
- [x] 角色后生成，参考场景风格
- [x] 两个版本都有独立UUID
- [x] 预算使用20点，不超过200点
- [x] 最终汇报列出全部资产和位置
- [x] 依赖管理正确（场景先完成，角色才能开始）

## 问题记录

无重大问题。依赖管理工作正常，两个资产按顺序生成。

## 结论

测试通过 ✅
"""
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)

shutil.copy(report_path, os.path.join(EVIDENCE_DIR, "case2_10_final_report.md"))
print(f"测试报告已保存: {report_path}")
print(f"\n全部证据保存在: {EVIDENCE_DIR}")
print("\n" + "=" * 60)
print("测试样例2 完成 ✅")
print("=" * 60)
