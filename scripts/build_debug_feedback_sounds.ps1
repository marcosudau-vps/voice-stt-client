param(
    [string]$SourceDirectory = "assets\sound_effects\home-assistant-voice-pe_sounds",
    [string]$OutputDirectory = "assets\feedback_sounds\debug"
)

$ErrorActionPreference = "Stop"
$source = Resolve-Path -LiteralPath $SourceDirectory
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$jobs = @(
    @{ Input = "wake_word_triggered.flac"; Output = "wake_word.wav"; Duration = "0.80" },
    @{ Input = "center_button_press.flac"; Output = "start.wav"; Duration = "0.90" },
    @{ Input = "mute_switch_on.flac"; Output = "stop.wav"; Duration = "0.80" },
    @{ Input = "timer_finished.flac"; Output = "complete.wav"; Duration = "2.30" },
    @{ Input = "center_button_double_press.flac"; Output = "cancel.wav"; Duration = "1.35" },
    @{ Input = "jack_disconnected.flac"; Output = "warning.wav"; Duration = "1.35" },
    @{ Input = "mute_switch_off.flac"; Output = "error.wav"; Duration = "2.00" },
    @{ Input = "easter_egg_tick.mp3"; Output = "timeout_tick.wav"; Duration = "3.00" }
)

foreach ($job in $jobs) {
    $inputPath = Join-Path $source $job.Input
    $outputPath = Join-Path $OutputDirectory $job.Output
    $filter = "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB,atrim=duration=$($job.Duration),loudnorm=I=-16:LRA=7:TP=-1.5"
    & ffmpeg -hide_banner -loglevel error -y -i $inputPath -af $filter -ar 48000 -ac 1 -c:a pcm_s16le $outputPath
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed for $($job.Input)"
    }
}

Get-ChildItem -LiteralPath $OutputDirectory -Filter *.wav | Sort-Object Name |
    Select-Object Name, Length, @{Name="SHA256"; Expression={(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()}}
