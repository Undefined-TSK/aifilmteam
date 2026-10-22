# K13 版本树 - 使用指南

> 让AI生成的满意结果，永远不会消失。

---

## 快速开始

### 1. 安装

不需要安装，直接复制 `scripts/k13.py` 到你的项目中即可使用。

```bash
# 也可以作为Skill放入Agent的skills目录
cp -r k13-version-tree/ /path/to/your/skills/
```

### 2. 初始化

在你的项目目录中初始化K13：

```bash
python scripts/k13.py init ./my_project
```

这会在项目中创建 `k13_locked/` 目录。

### 3. 保存版本

生成一张图后，保存并锁定为一个版本：

```bash
python scripts/k13.py save ./my_project character 林月 generated.png \
  --params '{"prompt": "cyberpunk girl", "seed": 12345, "steps": 20}' \
  --note "初版，赛博朋克风格"
```

输出：
```json
{
  "status": "ok",
  "message": "版本已锁定: v1 (a1b2c3d4)",
  "uuid": "a1b2c3d4",
  "version": "v1"
}
```

### 4. 查看版本列表

```bash
python scripts/k13.py list ./my_project character 林月
```

### 5. 查看版本详情

```bash
python scripts/k13.py get ./my_project character 林月 a1b2c3d4
```

---

## 完整命令参考

### init - 初始化

```
python k13.py init <项目路径>
```

在项目中创建 `k13_locked/` 目录结构。

---

### save - 保存并锁定版本

```
python k13.py save <项目> <类型> <名称> <文件> [选项]
```

**参数：**
- `项目`: 项目根目录路径
- `类型`: 资产类型 - `character` | `scene` | `storyboard` | `animation`
- `名称`: 资产名称（中文也可以）
- `文件`: 要保存的结果文件路径

**选项：**
- `--params '<JSON>'`: 参数快照，如 `'{"prompt":"...","seed":123}'`
- `--note "备注"`: 版本备注说明
- `--parent <UUID>`: 父版本UUID，用于建立版本树关系

**示例：**
```bash
# 基础保存
python k13.py save ./proj character 林月 out.png

# 带参数和备注
python k13.py save ./proj character 林月 out.png \
  --params '{"seed": 12345, "steps": 20, "prompt": "..."}' \
  --note "调整了眼睛颜色"

# 从某个版本分支
python k13.py save ./proj character 林月 out_v2.png \
  --parent a1b2c3d4 \
  --note "长发版试试"
```

---

### list - 列出所有版本

```
python k13.py list <项目> <类型> <名称>
```

以树状结构展示所有版本，包含版本号、UUID、状态、备注。

---

### get - 查看单个版本

```
python k13.py get <项目> <类型> <名称> <UUID>
```

查看某个版本的完整信息，包括参数快照。

---

### compare - 对比两个版本

```
python k13.py compare <项目> <类型> <名称> <UUID1> <UUID2>
```

对比两个版本的参数差异，输出：
- 相同的参数
- 不同的参数（分别列出两个版本的值）
- 只在A版本有的参数
- 只在B版本有的参数

**使用场景：**
- 看两个版本具体改了什么参数
- 分析哪个参数对结果影响最大
- 回退时对比差异

---

### delete - 删除版本（危险）

```
python k13.py delete <项目> <类型> <名称> <UUID> --force
```

⚠️ **删除是危险操作！** K13的核心理念是"锁定即冻结"，不建议删除。

必须加 `--force` 才能执行。有子版本的版本不能删除。

---

## Python API 调用

除了命令行，也可以在Python代码中直接调用：

```python
from k13 import save_version, list_versions, get_version, compare_versions

# 保存版本
result = save_version(
    project_path="./my_project",
    asset_type="character",
    asset_name="林月",
    file_path="generated.png",
    params={"seed": 12345, "prompt": "..."},
    note="初版"
)
print(result["uuid"])  # 新版本UUID

# 列出版本
versions = list_versions("./my_project", "character", "林月")
print(f"共有 {versions['count']} 个版本")

# 查看版本
v = get_version("./my_project", "character", "林月", "a1b2c3d4")
print(v["version"]["params"])

# 对比版本
diff = compare_versions("./my_project", "character", "林月", "uuid1", "uuid2")
print(f"不同的参数有 {diff['different_count']} 个")
```

完整示例见 [examples/example_usage.py](examples/example_usage.py)

---

## 目录结构

```
k13_locked/
├── character/              # 角色资产
│   └── 林月/
│       ├── versions.json       # 版本树元数据
│       ├── a1b2c3d4/           # v1 版本目录
│       │   ├── result.png      # 结果文件
│       │   └── params.json     # 参数快照
│       └── e5f6g7h8/           # v2 版本目录
│           ├── result.png
│           └── params.json
├── scene/                  # 场景资产
├── storyboard/             # 分镜资产
└── animation/              # 动画资产
```

---

## 最佳实践

### 1. 每次满意就锁定

不要攒着"等更好的"。AI生成是探索过程，每张满意的都值得锁定。
存储空间很便宜，重新生成一张满意的图的成本要高得多。

### 2. 写好备注

版本多了之后，光看缩略图可能记不清差异。
`--note` 参数花5秒钟写一句话，以后省很多事。

### 3. 善用分支

想试一个大胆的改动？从当前版本分支出去，
失败了不影响原版，成功了就选分支版本。

```bash
# 从v1分支试长发版
python k13.py save ./proj character 林月 long_hair.png \
  --parent <v1的UUID> \
  --note "试试长发，可能不好看"
```

### 4. 用 compare 分析差异

两个版本看起来都不错，但不知道具体差在哪？
用 `compare` 命令看参数差异，帮你理解哪些参数影响最大。

---

## 常见问题

**Q: 为什么叫K13？**
A: 这是一个内部代号，K=Key（关键），13=不吉利数字→用了就吉利了。
   不用纠结名字，好用就行。

**Q: 和Git有什么区别？**
A: Git是为代码设计的，K13是为AI生成设计的：
   - 更简单：只有"保存/锁定"一个核心动作
   - 二进制友好：图片视频直接存，不用管diff
   - 参数快照：每个版本自带生成参数
   - 短UUID：8位，好记好说
   - 零依赖：不需要安装Git

**Q: 支持哪些资产类型？**
A: 内置4种：character（角色）、scene（场景）、storyboard（分镜）、animation（动画）。
   其实类型名是自由的，传什么字符串都行，会自动创建对应目录。

**Q: 能存视频吗？**
A: 当然可以。任何文件都能存，K13不关心文件内容，只负责管理版本。
   视频文件比较大，注意存储空间。

**Q: 数据存在哪？会丢吗？**
A: 所有数据都存在项目的 `k13_locked/` 目录下，纯文件系统。
   只要你不手动删这个目录，数据就不会丢。
   建议把整个项目目录加入备份。
