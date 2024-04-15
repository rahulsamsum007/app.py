Sure, here's the complete PL/SQL code filled in with placeholders. You can adjust it according to your specific requirements:

```sql
DECLARE
    VCONNECTION UTL_SMTP.CONNECTION;
    CMIMEBOUNDARY CONSTANT VARCHAR2(256) := '-----AABCDEFBBCCC0123456789DE';
    VCRLF CHAR(2) := CHR(13) || CHR(10);
    P_ORGANIZATION_ID NUMBER := 122; -- Change as needed
    P_DATE DATE := SYSDATE - 1; -- Change as needed

    -- Cursor to fetch distinct zones from all relevant tables
    CURSOR DISTINCT_ZONES IS
        SELECT DISTINCT ZONE_NAME AS ZONE FROM BARCODE.LFCF_ZONE_SALES_MIS_BUDGET_DATA
        UNION
        SELECT DISTINCT ZONE FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA
        UNION
        SELECT DISTINCT ZONE FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA;

BEGIN
    -- Open SMTP connection
    VCONNECTION := UTL_SMTP.OPEN_CONNECTION('your_smtp_server', 25); -- Change SMTP server details as needed
    UTL_SMTP.HELO(VCONNECTION, 'your_domain.com'); -- Change domain name as needed
    UTL_SMTP.MAIL(VCONNECTION, 'LF_Sales_MIS@srf.com');

    -- New section to process distinct zones and calculate segment-wise details for the "North" segment
    FOR ZONE_REC IN DISTINCT_ZONES LOOP
        -- Check if the zone is in the "North" segment
        IF ZONE_REC.ZONE LIKE '%North%' THEN
            -- Your existing logic to calculate segment-wise details can go here,
            -- filtering the data based on the "North" zone and aggregating the totals.
            -- For demonstration purposes, I'll just print placeholder values.
            DBMS_OUTPUT.PUT_LINE('Processing data for the North segment...');
            -- Placeholder values for demonstration purposes
            DBMS_OUTPUT.PUT_LINE('Segment: North Segment');
            DBMS_OUTPUT.PUT_LINE('Total Order Booked: 1000');
            DBMS_OUTPUT.PUT_LINE('Total Sale: 50000');
        END IF;
    END LOOP;

    -- Close SMTP connection
    UTL_SMTP.CLOSE_DATA(VCONNECTION);
    UTL_SMTP.QUIT(VCONNECTION);
END;
/
```

Replace `'your_smtp_server'` with your actual SMTP server details and adjust other placeholders as necessary. You can also replace the placeholder logic inside the loop with your actual business logic to calculate segment-wise details for the "North" segment. Let me know if you need further assistance!