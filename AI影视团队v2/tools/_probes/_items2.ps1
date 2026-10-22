$W = (Get-ChildItem "D:\ai_film_projects\projects\*\output\tech_v5" | Select-Object -First 1).FullName
$W
$FP = "C:\Users\LZH\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build-shared\bin\ffprobe.exe"
Write-Output "=== 1) duration / format / bytes / mtime ==="
foreach ($f in @("stem_ambience.wav", "stem_dialogue.wav", "stem_sfx.wav", "stem_music.wav")) {
    $p = Join-Path $W $f
    if (Test-Path $p) {
        $i = Get-Item $p
        $d = & $FP -v error -show_entries format=duration,size -show_entries stream=codec_name,sample_rate,channels,bits_per_sample -of default=nw=1:nk=1 $p
        Write-Output ("--- " + $f + " bytes=" + $i.Length + " mtime=" + $i.LastWriteTime.ToString("MM-dd HH:mm:ss"))
        Write-Output (($d -join " | ") + " samples=" + [math]::Round(($i.Length - 44) / 6))
    } else {
        Write-Output ("--- " + $f + " MISSING")
    }
}
Write-Output "=== 2) sha256 first16 (same content check) ==="
foreach ($f in @("stem_ambience.wav", "stem_dialogue.wav", "stem_sfx.wav", "stem_music.wav")) {
    $p = Join-Path $W $f
    if (Test-Path $p) {
        $h = (Get-FileHash $p -Algorithm SHA256).Hash
        Write-Output ($f + " = " + $h.Substring(0, 16))
    }
}
Write-Output "=== 3) audio_mix.py stem-producing functions ==="
$src = Get-Content "D:\ai_film_projects\pipeline\audio_mix.py" -Encoding UTF8
$src | Select-String -Pattern "^def " | ForEach-Object { Write-Output ($_.LineNumber.ToString() + ": " + $_.Line) }
$bg = ($src | Select-String -Pattern "^def build_group" | Select-Object -First 1).LineNumber
if ($bg) { $src[($bg - 1)..($bg + 24)] }

