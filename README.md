Sub ValidateOrderQuantities()
    Dim wb As Workbook
    Dim wsDetail As Worksheet
    Dim wsSheet1 As Worksheet
    Dim detailQty As Double
    Dim sheet1Qty As Double
    Dim detailItem As String
    Dim sheet1Item As String
    Dim reportRow As Long
    
    ' Set workbook
    Set wb = ThisWorkbook
    
    ' Set worksheets
    Set wsDetail = wb.Sheets("Detail") ' Adjust sheet name if needed
    Set wsSheet1 = wb.Sheets("Sheet1") ' Adjust sheet name if needed
    
    ' Initialize report
    reportRow = 1
    wsSheet1.Cells(reportRow, 1).Value = "Ordered Item"
    wsSheet1.Cells(reportRow, 2).Value = "Detail Order Qty"
    wsSheet1.Cells(reportRow, 3).Value = "Sheet1 Order Qty"
    reportRow = reportRow + 1
    
    ' Loop through each row in detail and compare quantities with Sheet1
    For Each row In wsDetail.UsedRange.Rows
        detailItem = wsDetail.Cells(row.Row, 2).Value ' Assuming item is in column B
        detailQty = wsDetail.Cells(row.Row, 6).Value ' Assuming qty is in column F
        
        ' Find matching item in Sheet1
        For Each sRow In wsSheet1.UsedRange.Rows
            sheet1Item = wsSheet1.Cells(sRow.Row, 15).Value ' Assuming item is in column O
            If detailItem = sheet1Item Then
                sheet1Qty = wsSheet1.Cells(sRow.Row, 18).Value ' Assuming qty is in column R
                ' Compare quantities
                If detailQty <> sheet1Qty Then
                    ' Report mismatch
                    wsSheet1.Cells(reportRow, 1).Value = detailItem
                    wsSheet1.Cells(reportRow, 2).Value = detailQty
                    wsSheet1.Cells(reportRow, 3).Value = sheet1Qty
                    reportRow = reportRow + 1
                End If
                Exit For ' Exit loop once match is found
            End If
        Next sRow
    Next row
    
    MsgBox "Validation complete. Report generated in Sheet1."
End Sub
