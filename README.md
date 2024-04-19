Here's a VBA code snippet that checks the order quantity in the "detail" and "sheet1" sheets and generates a report:

```vba
Sub ValidateOrderQty()
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim detailQty As Double
    Dim sheet1Qty As Double
    
    ' Set references to the detail and sheet1 sheets
    Set wsDetail = ThisWorkbook.Sheets("detail")
    Set wsSheet1 = ThisWorkbook.Sheets("sheet1")
    
    ' Find the last row in both sheets
    lastRow = wsDetail.Cells(wsDetail.Rows.Count, "A").End(xlUp).Row
    
    ' Loop through each row in the detail sheet
    For i = 2 To lastRow ' Assuming row 1 is header row
        ' Get the order quantity from the detail sheet
        detailQty = wsDetail.Cells(i, "B").Value
        
        ' Get the corresponding order quantity from sheet1
        sheet1Qty = Application.VLookup(wsDetail.Cells(i, "A").Value, wsSheet1.Range("A:B"), 2, False)
        
        ' Compare the order quantities
        If detailQty <> sheet1Qty Then
            ' Generate report
            MsgBox "Order quantity for item " & wsDetail.Cells(i, "A").Value & " does not match between detail and sheet1."
            ' You can customize the report output as per your requirement
        End If
    Next i
    
    ' Cleanup
    Set wsDetail = Nothing
    Set wsSheet1 = Nothing
End Sub
```

This code assumes that:
- Both sheets have the order items listed in column A and the corresponding order quantities listed in column B.
- There are headers in row 1.
- The order items in the "detail" sheet match exactly with those in the "sheet1" sheet.
- The order quantity in the "detail" sheet is to be validated against the order quantity in the "sheet1" sheet.

You can customize the report output within the `If` statement as per your specific requirements. This code compares order quantities for each item and alerts if there's a mismatch.