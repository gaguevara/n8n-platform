$ProjectRoot = "C:\dev\projects\framework_multiagent"
$PythonExe = "python"
$ScriptPath = Join-Path $ProjectRoot ".multiagent\core\proto_watch.py"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`" --loop"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "FrameworkMultiagentWatch" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Standalone watcher for SPEC-005"
