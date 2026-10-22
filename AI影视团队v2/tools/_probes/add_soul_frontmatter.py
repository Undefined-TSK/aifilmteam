# -*- coding: utf-8 -*-
"""给缺 frontmatter 的 SOUL.md 批量补 name/description（对齐 Anthropic Agent Skills 规范）。

依据：审计件 §8「P0（半天）：15 份 SOUL.md 全部补 name/description frontmatter」。
幂等：已有 frontmatter 的跳过，可重复执行。
用法：python tools/_probes/add_soul_frontmatter.py
"""
import io
import os

ROOT = r"D:\ai_film_projects\roles"

DATA = {
    "character_designer": ("character-designer",
        "人物外观与一致性守护——角色三视图/特征库/K13 锁定，管「人长什么样」；向艺术总监汇报"),
    "editor": ("editor",
        "成片兜底与节奏终裁——时间线拼装、混音合入、交付检查表与版本快照；向艺术总监汇报"),
    "producer": ("producer",
        "项目总指挥与老板接口——接老板指令→拆任务→派艺术总监→汇总交付；只对老板负责"),
    "scene_designer": ("scene-designer",
        "氛围与世界观造景——场景概念图/氛围关键词/光影说明/scene_lock 锁定；向艺术总监汇报"),
    "sound_engineer": ("sound-engineer",
        "听觉氛围调音——对白/音效/环境/BGM 与终混，管「声音世界」；向艺术总监汇报"),
    "storyboard_artist": ("storyboard-artist",
        "镜头语言与节奏——把剧本翻译成镜头序列（景别/运镜/时长/转场），自动注入角色与场景资产；向艺术总监汇报"),
}


def main():
    changed, skipped = [], []
    for role, (name, desc) in DATA.items():
        p = os.path.join(ROOT, role, "SOUL.md")
        if not os.path.exists(p):
            skipped.append((role, "SOUL.md 不存在"))
            continue
        with io.open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        if txt.lstrip().startswith("---"):
            skipped.append((role, "已有 frontmatter，跳过"))
            continue
        fm = "---\nname: %s\ndescription: %s\n---\n\n" % (name, desc)
        with io.open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(fm + txt.lstrip("\n"))
        changed.append(role)

    print("changed %d: %s" % (len(changed), ", ".join(changed)))
    for r, why in skipped:
        print("skipped %s: %s" % (r, why))


if __name__ == "__main__":
    main()
