Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\cat_audio_cutter.pyw"
pythonwPath = shell.ExpandEnvironmentStrings("%LocalAppData%") & "\Programs\Python\Python311\pythonw.exe"

If Not fso.FileExists(pythonwPath) Then
    pythonwPath = "pythonw.exe"
End If

shell.Run """" & pythonwPath & """ """ & appPath & """", 0, False
