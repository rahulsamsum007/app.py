Sub CompareOrderQuantities()
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim detailQty As Variant
    Dim sheet1Qty As Variant
    
    ' Set references to the worksheets
    Set wsDetail = ThisWorkbook.Sheets("detail")
    Set wsSheet1 = ThisWorkbook.Sheets("sheet1")
    
    ' Get order quantities from both sheets
    detailQty = wsDetail.Range("F3").Value
    sheet1Qty = wsSheet1.Range("R1").Value
    
    ' Compare order quantities
    If detailQty = sheet1Qty Then
        MsgBox "Order quantities match: " & detailQty
    Else
        MsgBox "Order quantities do not match. Detail qty: " & detailQty & ", Sheet1 qty: " & sheet1Qty
    End If
End Sub
