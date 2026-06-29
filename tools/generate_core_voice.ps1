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
    },
    @{
        File = "market_auntie_01.wav"
        Text = Decode-Utf8Text "6ZuG5biC6YeM5pyJ6ZO25Lid5p2Q5paZ77yM5Lmf5pyJ6K645aSa57q55qC357q/57Si44CC"
    },
    @{
        File = "market_auntie_02.wav"
        Text = Decode-Utf8Text "5LuU57uG55yL55yL5pGK5L2N5LiK55qE57q55qC35pyo54mM77yM5Lmf6K646IO95om+5Yiw5L+u5aSN6ZO26aWw55qE5pa55rOV44CC"
    },
    @{
        File = "festival_host_01.wav"
        Text = Decode-Utf8Text "6IqC5bqG6ZO26aWw55qE5YWJ6IqS5b+r6KaB5oGi5aSN5LqG77yM6K+35a6I5oqk5bGV56S65Y+w77yB"
    },
    @{
        File = "festival_host_02.wav"
        Text = Decode-Utf8Text "5YeA5YyW6Z2g6L+R55qE5b2x57q577yM5Yir6K6p5a6D5Lus5omw5Lmx5Luq5byP77yB"
    },
    @{
        File = "silversmith_01.wav"
        Text = Decode-Utf8Text "5L+u5aSN6ZO26aWw6ZyA6KaB5p2Q5paZ77yM5Lmf6ZyA6KaB5q2j56Gu55qE57q55qC357q/57Si44CC"
    },
    @{
        File = "silversmith_02.wav"
        Text = Decode-Utf8Text "5bim552A5pS26ZuG5Yiw55qE57q/57Si57un57ut5YmN6L+b77yM6ZO26aWw55qE5YWJ5Lya5oWi5oWi5Zue5p2l44CC"
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
