param()

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$voiceDir = Join-Path $root "assets\audio\voice"
New-Item -ItemType Directory -Force -Path $voiceDir | Out-Null

try {
    Add-Type -AssemblyName System.Speech
} catch {
    Write-Warning "[VOICE_GEN][WARN] System.Speech is unavailable on this Windows installation."
    exit 1
}

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = -1
$synth.Volume = 85

$chineseVoice = $synth.GetInstalledVoices() |
    Where-Object {
        $_.Enabled -and (
            $_.VoiceInfo.Culture.Name -like "zh*" -or
            $_.VoiceInfo.Name -match "Chinese|Huihui|Yaoyao|Kangkang|Hanhan|Tracy"
        )
    } |
    Select-Object -First 1

if ($null -eq $chineseVoice) {
    Write-Warning "[VOICE_GEN][WARN] Chinese voice not found; using default system voice."
} else {
    $synth.SelectVoice($chineseVoice.VoiceInfo.Name)
    Write-Output "[VOICE_GEN] using voice $($chineseVoice.VoiceInfo.Name)"
}

function Decode-Utf8Text([string]$Base64Text) {
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Base64Text))
}

$lines = @(
    @{
        File = "elder_01.wav"
        Text = Decode-Utf8Text "5a2p5a2Q77yM6IqC5bqG6ZO26aWw55qE5YWJ5q2j5Zyo5oWi5oWi5Y+Y5pqX44CC"
    },
    @{
        File = "elder_02.wav"
        Text = Decode-Utf8Text "5b2x57q55omw5Lmx5LqG57q55qC355qE56ep5bqP77yM5oiR5Lus6ZyA6KaB6YeN5paw5a+75om+5L+u5aSN57q/57Si44CC"
    },
    @{
        File = "elder_03.wav"
        Text = Decode-Utf8Text "5YWI5Y675bGx5Zyw6ZuG5biC5a+75om+6ZO25Lid5p2Q5paZ5ZKM57q55qC35pyo54mM77yM5YaN5YmN5b6A5rKz6LC35YeA5YyW5b2x57q544CC"
    }
)

foreach ($line in $lines) {
    $path = Join-Path $voiceDir $line.File
    $synth.SetOutputToWaveFile($path)
    $synth.Speak($line.Text)
    $synth.SetOutputToNull()
    $relative = "assets/audio/voice/$($line.File)"
    Write-Output "[VOICE_GEN] generated $relative"
}

$synth.Dispose()
