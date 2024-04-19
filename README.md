Sub CompareOrderQuantities()
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim lastRowDetail As Long
    Dim lastRowSheet1 As Long
    Dim i As Long
    Dim mismatchReport As String
    
    ' Set references to the worksheets
    Set wsDetail = ThisWorkbook.Sheets("detail")
    Set wsSheet1 = ThisWorkbook.Sheets("sheet1")
    
    ' Find the last row with data in each sheet
    lastRowDetail = wsDetail.Cells(wsDetail.Rows.Count, "B").End(xlUp).Row
    lastRowSheet1 = wsSheet1.Cells(wsSheet1.Rows.Count, "O").End(xlUp).Row
    
    ' Initialize mismatch report string
    mismatchReport = "Items with mismatched order quantities:" & vbCrLf
    
    ' Loop through each item and compare order quantities
    For i = 3 To lastRowDetail ' Assuming data starts from row 3 in "detail" sheet
        If wsDetail.Cells(i, "B").Value <> "" Then ' Check if item is not empty
            If wsDetail.Cells(i, "F").Value <> wsSheet1.Cells(1, "R").Value Then ' Check if order quantities don't match
                mismatchReport = mismatchReport & "Item: " & wsDetail.Cells(i, "B").Value & ", Detail qty: " & wsDetail.Cells(i, "F").Value & ", Sheet1 qty: " & wsSheet1.Cells(1, "R").Value & vbCrLf
            End If
        End If
    Next i
    
    ' Display mismatch report
    MsgBox mismatchReport
End Sub
