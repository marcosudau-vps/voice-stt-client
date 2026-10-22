' Normal Windows desktop entry, repository-local programs only.
' No execution-policy change, credentials, V1 profile or automatic test start.
Set fileSystem = CreateObject("Scripting.FileSystemObject")
entry = fileSystem.BuildPath(fileSystem.GetParentFolderName(WScript.ScriptFullName), "Start-GuidedTests.ps1")
Set launcher = CreateObject("WScript.Shell")
launcher.Run "powershell.exe -NoProfile -WindowStyle Hidden -File """ & entry & """ -ProfileRuntime", 0, False
