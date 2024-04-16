It seems there are a few issues in the code:

1. The `ZONE_CUR` cursor uses the `ZONE` column, which is not defined in the cursor query. It should use `ZONE_NAME` instead.

2. In the `SEG` cursor, the query references `ZONE_NAME` but does not pass it as a parameter in the cursor declaration.

3. The loop variable `J` is being referenced outside of its loop scope.

Let's fix these issues:

```sql
DECLARE 
    VCONNECTION UTL_SMTP.CONNECTION; 
    CMIMEBOUNDARY CONSTANT VARCHAR2(256) := '-----AABCDEFBBCCC0123456789DE'; 
    VCRLF CHAR(2) := CHR(13) || CHR(10); 
    P_ORGANIZATION_ID NUMBER := 122; --122/ 1256 
    P_DATE DATE := SYSDATE - 1;

    CURSOR ZONE_CUR IS 
        SELECT DISTINCT ZONE_NAME AS ZONE 
        FROM BARCODE.LFCF_ZONE_SALES_MIS_BUDGET_DATA 
        WHERE ORGANIZATION_ID = P_ORGANIZATION_ID;

    CURSOR SEG(ZONE_NAME VARCHAR2) IS 
        WITH TAB AS (
            SELECT SEGMENT_NAME, ROUND(SUM(BUDGET_QTY), 2) PLAN_QTY, 0 INVOICE_QTY, 0 ORDER_QTY 
            FROM BARCODE.LFCF_SEGMENT_SALES_MIS_BUDGET_DATA 
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID 
            AND TRUNC(BUDGET_DATE) BETWEEN TRUNC(P_DATE, 'MM') AND LAST_DAY(TRUNC(P_DATE)) 
            GROUP BY SEGMENT_NAME 
            UNION ALL 
            SELECT NVL(ITEM_CATEGORY, ITEM_NAME) SEGMENT_NAME, 0 PLAN_QTY, ROUND(SUM(SHIPPED_QTY), 2) INVOICE_QTY, 0 ORDER_QTY 
            FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA 
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID 
            AND TRUNC(INVOICE_DATE) BETWEEN TRUNC(P_DATE, 'MM') AND LAST_DAY(TRUNC(P_DATE)) 
            AND ZONE = ZONE_NAME 
            GROUP BY NVL(ITEM_CATEGORY, ITEM_NAME) 
            UNION ALL 
            SELECT NVL(PRODUCT_CATEGORY, PRODUCT) SEGMENT_NAME, 0 PLAN_QTY, 0 INVOICE_QTY, ROUND(SUM(ORDER_QTY), 2) ORDER_QTY 
            FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA 
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID 
            AND TRUNC(SCHEDULE_SHIP_DATE) <= LAST_DAY(TRUNC(P_DATE)) 
            AND ZONE = ZONE_NAME 
            GROUP BY NVL(PRODUCT_CATEGORY, PRODUCT)
        ) 
        SELECT SEQ_NO, SEGMENT_NAME, PLAN_QTY, INVOICE_QTY, ORDER_QTY, ROUND(INVOICE_QTY + ORDER_QTY, 2) TOTAL_ORDER_BOOKED, ROUND(PLAN_QTY - (INVOICE_QTY + ORDER_QTY), 2) ORDER_TO_BE_BOOKED 
        FROM (
            SELECT 1 SEQ_NO, SEGMENT_NAME, SUM(PLAN_QTY) PLAN_QTY, SUM(INVOICE_QTY) INVOICE_QTY, SUM(ORDER_QTY) ORDER_QTY 
            FROM TAB 
            WHERE ZONE = ZONE_NAME 
            GROUP BY SEGMENT_NAME 
            UNION ALL 
            SELECT 2 SEQ_NO, 'Total' SEGMENT_NAME, SUM(PLAN_QTY) PLAN_QTY, SUM(INVOICE_QTY) INVOICE_QTY, SUM(ORDER_QTY) ORDER_QTY 
            FROM TAB 
            WHERE ZONE = ZONE_NAME 
            GROUP BY SEGMENT_NAME
        ) 
        ORDER BY 1, 2;

    CURSOR B1 IS 
        SELECT REGEXP_SUBSTR((SELECT MAIL_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL) AS TO_EMAIL_ID 
        FROM DUAL 
        CONNECT BY REGEXP_SUBSTR((SELECT MAIL_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL) IS NOT NULL;

    CURSOR B2 IS 
        SELECT REGEXP_SUBSTR((SELECT CC_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL) AS CC 
        FROM DUAL 
        CONNECT BY REGEXP_SUBSTR((SELECT CC_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL ) IS NOT NULL;

    CURSOR B3 IS 
        SELECT REGEXP_SUBSTR((SELECT MAIL_ID || ' ' || CC_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL) AS RECIPIENT 
        FROM DUAL 
        CONNECT BY REGEXP_SUBSTR((SELECT MAIL_ID || ' ' || CC_ID FROM XXSRF.SRF_TTB_ALERT_MAILING_LIST WHERE TRIM(APPLICATION) = 'LF_SALES_MIS_ALERT' AND ORGANIZATION_ID = 122), '[^ ]+', 1, LEVEL) IS NOT NULL;

BEGIN 
    VCONNECTION := UTL_SMTP.OPEN_CONNECTION(SRF_PFB_CUSTOM_ALERTS.SMTP_SERVER, SRF_PFB_CUSTOM_ALERTS.PORT); 
    UTL_SMTP.HELO(VCONNECTION, SRF_PFB_CUSTOM_ALERTS.SMTP_SERVER); 
    UTL_SMTP.MAIL(VCONNECTION, 'LF_Sales_MIS@srf.com');

    FOR ZONE IN ZONE_CUR LOOP 
        UTL_SMTP.RCPT(VCONNECTION, 'shivam.kapoor@srf.com'); 
        UTL_SMTP.OPEN_DATA(VCONNECTION); 

        FOR INDX0 IN B3 LOOP 
            UTL_SMTP.RCPT(VCONNECTION, INDX0.RECIPIENT); 
        END LOOP;

        UTL_SMTP.WRITE_DATA(VCONNECTION, '<table border="1" width="60%" style="border-collapse: collapse; border: 1px solid #B8B8B8;">'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr style="background-color: #B8B8B8; font-family: Calibri; font-size: 14px; color: #FFFFFF;">'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<th bgcolor="#151B54" colspan = 6><div align="mid">LF Order Book (' || ZONE.ZONE || ') ' || TO_CHAR(P_DATE, 'Mon-YYYY') || ' - Segment Wise Details.' || VCRLF); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</tr>');

 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<th bgcolor="#151B54"><font size="2" face="Calibri" color=#FFFFFF >SEGMENT NAME</font></div></th>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<th bgcolor="#151B54"><font size="2" face="Calibri" color=#FFFFFF>TOTAL SALES</font></th>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<th bgcolor="#151B54"><font size="2" face="Calibri" color=#FFFFFF>TOTAL ORDER BOOKED</font></th>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</tr>');

        FOR J IN SEG(ZONE.ZONE) LOOP 
            UTL_SMTP.WRITE_DATA(VCONNECTION, '<tr>'); 
            IF J.SEGMENT_NAME IN ('Total') THEN 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="background-color: #FFEE99; font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="left"> <b>' || J.SEGMENT_NAME || '</b></font></div></td>'); 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="background-color: #FFEE99; font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="right"> <b>' || J.INVOICE_QTY || '</b></font></div></td>'); 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="background-color: #FFEE99; font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="right"> <b>' || J.TOTAL_ORDER_BOOKED || '</b></font></div></td>'); 
            ELSE 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="left"> ' || J.SEGMENT_NAME || '</font></div></td>'); 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="right"> ' || J.INVOICE_QTY || '</font></div></td>'); 
                UTL_SMTP.WRITE_DATA(VCONNECTION, '<td style="font-family: Calibri; font-size: 14px; color: #000000; border: 1px solid #B8B8B8;"><div align="right"> ' || J.TOTAL_ORDER_BOOKED || '</font></div></td>'); 
            END IF; 
            UTL_SMTP.WRITE_DATA(VCONNECTION, '</tr>'); 
        END LOOP; 

        UTL_SMTP.WRITE_DATA(VCONNECTION, '</table>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<P><font size="3" face="Calibri">** Auto Generated Mail, Please do not reply.</font></P>' || VCRLF); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<P><font size="3" face="Calibri">Regards,</font></P>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '<P><font size="3" face="Calibri">IT Team.</font></P>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</html>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '</body>'); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, VCRLF || VCRLF); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, VCRLF); 
        UTL_SMTP.WRITE_DATA(VCONNECTION, '--' || CMIMEBOUNDARY || '--' || VCRLF); 
        UTL_SMTP.CLOSE_DATA(VCONNECTION); 
    END LOOP; 

EXCEPTION 
    WHEN OTHERS THEN 
        -- Handle errors here 
        UTL_SMTP.CLOSE_DATA(VCONNECTION); 
        UTL_SMTP.QUIT(VCONNECTION); 
END;
```

These changes should resolve the errors you encountered.