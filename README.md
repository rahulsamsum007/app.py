Sub CompareOrderQuantities()
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim lastRowDetail As Long
    Dim lastRowSheet1 As Long
    Dim i As Long
    Dim mismatchReport As String
    Dim reportWS As Worksheet
    Dim nextRow As Long
    
    ' Set references to the worksheets
    Set wsDetail = ThisWorkbook.Sheets("detail")
    Set wsSheet1 = ThisWorkbook.Sheets("sheet1")
    
    ' Find the last row with data in each sheet
    lastRowDetail = wsDetail.Cells(wsDetail.Rows.Count, "B").End(xlUp).Row
    lastRowSheet1 = wsSheet1.Cells(wsSheet1.Rows.Count, "O").End(xlUp).Row
    
    ' Initialize mismatch report string
    mismatchReport = "Items with mismatched order quantities:" & vbCrLf
    
    ' Create a new worksheet to output the report
    On Error Resume Next
    Set reportWS = ThisWorkbook.Sheets("MismatchReport")
    On Error GoTo 0
    
    If reportWS Is Nothing Then
        Set reportWS = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        reportWS.Name = "MismatchReport"
    Else
        reportWS.Cells.Clear ' Clear existing content
    End If
    
    ' Set the initial row for output
    nextRow = 1
    
    ' Loop through each item and compare order quantities
    For i = 3 To lastRowDetail ' Assuming data starts from row 3 in "detail" sheet
        If wsDetail.Cells(i, "B").Value <> "" Then ' Check if item is not empty
            If wsDetail.Cells(i, "F").Value <> wsSheet1.Cells(1, "R").Value Then ' Check if order quantities don't match
                reportWS.Cells(nextRow, 1).Value = "Item: " & wsDetail.Cells(i, "B").Value
                reportWS.Cells(nextRow, 2).Value = "Detail qty: " & wsDetail.Cells(i, "F").Value
                reportWS.Cells(nextRow, 3).Value = "Sheet1 qty: " & wsSheet1.Cells(1, "R").Value
                nextRow = nextRow + 1
            End If
        End If
    Next i
    
    MsgBox "Mismatch report has been generated on the worksheet 'MismatchReport'."
End Sub
