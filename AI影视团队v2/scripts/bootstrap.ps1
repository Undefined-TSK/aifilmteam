# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    AI影视团队v2 — 一键部署与环境自检（维度25 跨机器迁移 / 维度33 配置管理）

.DESCRIPTION
    在新机器上从零到可运行的自检脚本。只做「检查 + 提示 + 可选安装」，
    不修改项目源码、不删除任何文件。所有检查项输出 PASS/FAIL 回显。

.PARAMETER Install
    加 -Install 时才执行 pip 安装（默认只检查）。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1
    powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1 -Install
#>
param(
    [switch]$Install
)

$ErrorActionPreference = "Continue"
$ROOT = Split-Path -Parent $PSScriptRoot   # AI影视团队v2
$results = @()

function Check($name, $ok, $detail) {
    $script:results += [pscustomobject]@{ 检查项 = $name; 结果 = $(if ($ok) { "PASS" } else { "FAIL" }); 说明 = $detail }
    $tag = if ($ok) { "[PASS]" } else { "[FAIL]" }
    Write-Host "$tag $name — $detail"
}

Write-Host "=== AI影视团队v2 环境自检（根：$ROOT）==="

# 1. Python
try {
    $py = (python --version 2>&1).ToString()
    Check "Python" ($py -match "3\.1[0-9]") $py
} catch { Check "Python" $false "未找到 python" }

# 2. 依赖清单
$req = Join-Path $ROOT "requirements.txt"
Check "requirements.txt" (Test-Path $req) $(if (Test-Path $req) { $req } else { "缺失" })
if ($Install -and (Test-Path $req)) {
    Write-Host "--- 执行 pip install -r requirements.txt ---"
    python -m pip install -r $req
}

# 3. 配置中心校验
$loader = Join-Path $ROOT "config\config_loader.py"
if (Test-Path $loader) {
    $out = (python $loader 2>&1) -join "`n"
    Check "配置校验" ($out -match "\[OK\]") ($out.Split("`n")[0])
} else { Check "配置校验" $false "config\config_loader.py 缺失" }

# 4. 路径中心
Check "路径中心" (Test-Path (Join-Path $ROOT "config\paths.py")) "config\paths.py"

# 5. 外部可执行
foreach ($exe in @("ffmpeg", "ollama")) {
    $cmd = Get-Command $exe -ErrorAction SilentlyContinue
    Check $exe ($null -ne $cmd) $(if ($cmd) { $cmd.Source } else { "未安装或不在 PATH" })
}

# 6. Blender 便携版
$blender = Get-ChildItem -Path $ROOT -Recurse -Filter "blender.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
Check "Blender" ($null -ne $blender) $(if ($blender) { $blender.FullName } else { "未找到便携版" })

# 7. 模型权重
$vace = Join-Path $ROOT "models\wan_vace_1.3b"
if (Test-Path $vace) {
    $mb = [math]::Round((Get-ChildItem $vace -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 0)
    Check "VACE 权重" ($mb -gt 4000) "$mb MB（全量应 ~16800 MB）"
} else { Check "VACE 权重" $false "models\wan_vace_1.3b 缺失" }

# 8. 密钥（只检查存在性，不读内容）
$secret = "D:\aifilmteam\runtime\secrets\dashscope.env"
Check "密钥文件" (Test-Path $secret) $(if (Test-Path $secret) { "已就位（内容不读取）" } else { "缺失，请放置 dashscope.env" })

Write-Host "`n=== 自检汇总 ==="
$results | Format-Table -AutoSize
$fail = ($results | Where-Object { $_.结果 -eq "FAIL" }).Count
Write-Host "PASS: $(($results | Where-Object { $_.结果 -eq 'PASS' }).Count)  FAIL: $fail"
exit $fail
