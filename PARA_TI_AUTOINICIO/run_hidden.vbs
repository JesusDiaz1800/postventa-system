' run_hidden.vbs - Ejecutar comandos de forma invisible
Set WshShell = CreateObject("WScript.Shell") 
If WScript.Arguments.Count = 0 Then
    WScript.Quit
End If

' Construir el comando completo
command = ""
For Each arg In WScript.Arguments
    command = command & " " & chr(34) & arg & chr(34)
Next

' Ejecutar oculto (0 = Hide window)
WshShell.Run command, 0, False
