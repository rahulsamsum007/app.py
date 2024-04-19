Sub ValidateOrderQty()
    Dim detailFile As Workbook
    Dim sheet1File As Workbook
    Dim detailQty As Double
    Dim sheet1Qty As Double
    Dim report As Worksheet
    Dim rowNum As Integer
    
    ' Open Detail file
    Set detailFile = Workbooks.Open("C:\Path\to\Detail.xlsx")
    ' Open Sheet1 file
    Set sheet1File = ThisWorkbook ' Change this if Sheet1 is in a different workbook
    
    ' Set report worksheet
    Set report = ThisWorkbook.Sheets.Add
    report.Name = "Validation Report"
    rowNum = 1
    
    ' Loop through each row to compare order_qty
    For rowNum = 3 To detailFile.Sheets("Sheet1").Cells(Rows.Count, "B").End(xlUp).Row
        detailQty = detailFile.Sheets("Sheet1").Cells(rowNum, "B").Value
        sheet1Qty = sheet1File.Sheets("Sheet1").Cells(1, rowNum).Value
        
        ' Compare order_qty and report any discrepancies
        If detailQty <> sheet1Qty Then
            report.Cells(rowNum, 1).Value = "Discrepancy found in row " & rowNum
            report.Cells(rowNum, 2).Value = "Detail Qty: " & detailQty
            report.Cells(rowNum, 3).Value = "Sheet1 Qty: " & sheet1Qty
        End If
    Next rowNum
    
    ' Close files
    detailFile.Close
    ' If Sheet1 is in a different workbook, you may need to close it too
    
    ' Notify user
    MsgBox "Validation complete. Check 'Validation Report' for details."
End Sub
