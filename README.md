Sub CompareOrderQuantities()
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim lastRowDetail As Long
    Dim lastRowSheet1 As Long
    Dim i As Long
    
    ' Set references to the worksheets
    Set wsDetail = ThisWorkbook.Sheets("detail")
    Set wsSheet1 = ThisWorkbook.Sheets("sheet1")
    
    ' Find the last row with data in each sheet
    lastRowDetail = wsDetail.Cells(wsDetail.Rows.Count, "B").End(xlUp).Row
    lastRowSheet1 = wsSheet1.Cells(wsSheet1.Rows.Count, "O").End(xlUp).Row
    
    ' Loop through each item and compare order quantities
    For i = 3 To lastRowDetail ' Assuming data starts from row 3 in "detail" sheet
        If wsDetail.Cells(i, "B").Value <> "" Then ' Check if item is not empty
            If wsDetail.Cells(i, "F").Value = wsSheet1.Cells(1, "R").Value Then ' Check if order quantities match
                MsgBox "Order quantities match for item " & wsDetail.Cells(i, "B").Value & ": " & wsDetail.Cells(i, "F").Value
            Else
                MsgBox "Order quantities do not match for item " & wsDetail.Cells(i, "B").Value & ". Detail qty: " & wsDetail.Cells(i, "F").Value & ", Sheet1 qty: " & wsSheet1.Cells(1, "R").Value
            End If
        End If
    Next i
End Sub
