$W = "D:\ai_film_projects\projects\雨夜寻猫\output\tech_v5"
$FP = "C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin\ffprobe.exe"
"=== 1) stem 时长/格式/字节/修改时间 ==="
foreach ($f in @("stem_ambience.wav", "stem_dialogue.wav", "stem_sfx.wav", "stem_music.wav")) {
    $p = Join-Path $W $f
    if (Test-Path $p) {
        $i = Get-Item $p
        $d = & $FP -v error -show_entries format=duration,size -show_entries stream=codec_name,sample_rate,channels,bits_per_sample -of default=nw=1:nk=1 $p
        "--- $f bytes=$($i.Length) mtime=$($i.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        ($d -join " | ")
    } else {
        "--- $f 不存在"
    }
}
"`n=== 2) sha256 前16（判是否同一内容） ==="
foreach ($f in @("stem_ambience.wav", "stem_dialogue.wav", "stem_sfx.wav", "stem_music.wav")) {
    $p = Join-Path $W $f
    if (Test-Path $p) {
        $h = (Get-FileHash $p -Algorithm SHA256).Hash
        "$f = $($h.Substring(0,16))"
    }
}
"`n=== 3) audio_mix.py 中产出 stem 的函数原文 ==="
$src = Get-Content "D:\ai_film_projects\pipeline\audio_mix.py" -Encoding UTF8
$marks = $src | Select-String -Pattern "def build_group", "def dlg_chain", "def main", "def mux" | ForEach-Object { "$($_.LineNumber): $($_.Line)" }
$marks

