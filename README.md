To modify your PL/SQL code to generate tables with segment-wise details and zone-wise segmentation, I'll create four separate tables for each zone and modify the segment-wise details table accordingly. Here's the modified code:

```sql
SET DEFINE OFF;

DECLARE
    VCONNECTION UTL_SMTP.CONNECTION;
    CMIMEBOUNDARY CONSTANT VARCHAR2(256) := '-----AABCDEFBBCCC0123456789DE';
    VCRLF CHAR(2) := CHR(13) || CHR(10);
    P_ORGANIZATION_ID NUMBER := 122;
    P_DATE DATE := SYSDATE - 1;

    -- Cursor to fetch data zone-wise
    CURSOR ZONE_DATA IS
        SELECT ZONE_NAME, 
               ROUND(SUM(BUDGET_QTY), 2) AS PLAN_QTY,
               ROUND(SUM(QUANTITY_INVOICED), 2) AS INVOICE_QTY,
               ROUND(SUM(ORDER_QTY), 2) AS ORDER_QTY
        FROM (
            SELECT ZONE_NAME, BUDGET_QTY, 0 AS QUANTITY_INVOICED, 0 AS ORDER_QTY
            FROM BARCODE.LFCF_ZONE_SALES_MIS_BUDGET_DATA
            UNION ALL
            SELECT ZONE, 0 AS BUDGET_QTY, QUANTITY_INVOICED, 0 AS ORDER_QTY
            FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA
            UNION ALL
            SELECT ZONE, 0 AS BUDGET_QTY, 0 AS QUANTITY_INVOICED, ORDER_QTY
            FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA
        )
        WHERE ORGANIZATION_ID = P_ORGANIZATION_ID
        AND TRUNC(SCHEDULE_SHIP_DATE) <= LAST_DAY(TRUNC(P_DATE))
        GROUP BY ZONE_NAME;

    -- Cursor to fetch segment-wise data
    CURSOR SEGMENT_DATA IS
        SELECT SEGMENT_NAME, 
               ROUND(SUM(BUDGET_QTY), 2) AS PLAN_QTY,
               ROUND(SUM(QUANTITY_INVOICED) + SUM(ORDER_QTY), 2) AS TOTAL_ORDER_BOOKED
        FROM (
            SELECT SEGMENT_NAME, BUDGET_QTY, 0 AS QUANTITY_INVOICED, 0 AS ORDER_QTY
            FROM BARCODE.LFCF_SEGMENT_SALES_MIS_BUDGET_DATA
            UNION ALL
            SELECT NVL(ITEM_CATEGORY, ITEM_NAME) AS SEGMENT_NAME, 
                   0 AS BUDGET_QTY, 
                   QUANTITY_INVOICED, 
                   0 AS ORDER_QTY
            FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA
            UNION ALL
            SELECT NVL(PRODUCT_CATEGORY, PRODUCT) AS SEGMENT_NAME, 
                   0 AS BUDGET_QTY, 
                   0 AS QUANTITY_INVOICED, 
                   ORDER_QTY
            FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA
        )
        WHERE ORGANIZATION_ID = P_ORGANIZATION_ID
        AND TRUNC(SCHEDULE_SHIP_DATE) <= LAST_DAY(TRUNC(P_DATE))
        GROUP BY SEGMENT_NAME;

BEGIN
    -- Code to send email with the data
    
    -- Open SMTP connection
    VCONNECTION := UTL_SMTP.OPEN_CONNECTION(SRF_PFB_CUSTOM_ALERTS.SMTP_SERVER, SRF_PFB_CUSTOM_ALERTS.PORT);
    UTL_SMTP.HELO(VCONNECTION, SRF_PFB_CUSTOM_ALERTS.SMTP_SERVER);
    UTL_SMTP.MAIL(VCONNECTION, 'LF_Sales_MIS@srf.com');
    
    -- Add recipients
    UTL_SMTP.RCPT(VCONNECTION, 'shivam.kapoor@srf.com');
    
    -- Start email data
    UTL_SMTP.OPEN_DATA(VCONNECTION);
    
    -- Add email headers
    UTL_SMTP.WRITE_DATA(VCONNECTION, 'Subject: LF SALES MIS - Date: '||TO_CHAR(P_DATE, 'Mon-YYYY')||'. ' || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, 'MIME-Version: 1.0' || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, 'Content-Type: multipart/mixed; boundary="' || CMIMEBOUNDARY || '"' || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, '--' || CMIMEBOUNDARY || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, 'Content-Type: text/html; charset="iso-8859-1"' || VCRLF || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, VCRLF);
    
    -- Add zone-wise tables
    FOR ZONE_ROW IN ZONE_DATA LOOP
        -- Add HTML table for each zone
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<table border="1">' || VCRLF);
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr><th>Zone</th><th>Plan Quantity</th><th>Invoice Quantity</th><th>Order Quantity</th></tr>' || VCRLF);
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || ZONE_ROW.ZONE_NAME || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || ZONE_ROW.PLAN_QTY || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || ZONE_ROW.INVOICE_QTY || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || ZONE_ROW.ORDER_QTY || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</tr>' || VCRLF);
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</table>' || VCRLF);
    END LOOP;
    
    -- Add segment-wise table
    -- Add HTML table for segment-wise details
    UTL_SMTP.WRITE_DATA(VCONNECTION, '<table border="1">' || VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr><th>Segment Name</th><th>Total Order Booked</th><th>Total Sales</th></tr>' || VCRLF);
    FOR SEGMENT_ROW IN SEGMENT_DATA LOOP
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || SEGMENT_ROW.SEGMENT_NAME || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || SEGMENT_ROW.TOTAL_ORDER_BOOKED || '</td>');
        -- Assuming total sales are sum of invoice quantity and order quantity
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<td>' || (SEGMENT_ROW.TOTAL_ORDER_BOOKED + SEGMENT_ROW.INVOICE_QTY) || '</td>');
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</tr>' || VCRLF);
    END LOOP;
    UTL_SMTP.WRITE_DATA(VCONNECTION, '</table>' || VCRLF);
    
    -- Close SMTP connection
    UTL_SMTP.WRITE_DATA(VCONNECTION, VCRLF);
    UTL_SMTP.WRITE_DATA(VCONNECTION, '--