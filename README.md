Sure, to achieve that, we can modify the existing SQL query to incorporate the requirement of selecting distinct zones from the order, invoice, and sales tables. Then, we can filter the data to only include the "North" segment and calculate the total order booked and total sale for this segment. Here's how we can do it:

```sql
DECLARE
    VCONNECTION UTL_SMTP.CONNECTION;
    CMIMEBOUNDARY CONSTANT VARCHAR2(256) := '-----AABCDEFBBCCC0123456789DE';
    VCRLF CHAR(2) := CHR(13) || CHR(10);
    P_ORGANIZATION_ID NUMBER := 122; -- Change as needed
    P_DATE DATE := SYSDATE - 1; -- Change as needed
    -- Other declarations as per your code...

    -- Cursor to fetch distinct zones from all relevant tables
    CURSOR DISTINCT_ZONES IS
        SELECT DISTINCT ZONE_NAME AS ZONE FROM BARCODE.LFCF_ZONE_SALES_MIS_BUDGET_DATA
        UNION
        SELECT DISTINCT ZONE FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA
        UNION
        SELECT DISTINCT ZONE FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA;

BEGIN
    -- Your existing PL/SQL code...

    -- New section to process distinct zones and calculate segment-wise details for the "North" segment
    FOR ZONE_REC IN DISTINCT_ZONES LOOP
        -- Check if the zone is in the "North" segment
        IF ZONE_REC.ZONE LIKE '%North%' THEN
            -- Your existing logic to calculate segment-wise details can go here,
            -- filtering the data based on the "North" zone and aggregating the totals.
            -- For example:
            FOR SEG_REC IN SEG LOOP
                -- Check if the segment name is "Total"
                IF SEG_REC.SEGMENT_NAME = 'Total' THEN
                    -- Calculate total order booked and total sale for the "North" segment
                    -- This can be done by aggregating data where the segment name is "Total"
                    -- and the zone matches the "North" zone.
                    -- You can then write this data to your email content using UTL_SMTP.WRITE_DATA.
                    -- For demonstration purposes, I'll just print the values.
                    DBMS_OUTPUT.PUT_LINE('Segment: ' || SEG_REC.SEGMENT_NAME);
                    DBMS_OUTPUT.PUT_LINE('Total Order Booked: ' || SEG_REC.TOTAL_ORDER_BOOKED);
                    DBMS_OUTPUT.PUT_LINE('Total Sale: ' || SEG_REC.SALE);
                END IF;
            END LOOP;
        END IF;
    END LOOP;

    -- Your existing PL/SQL code continues...
END;
/
```

Please replace the placeholders such as `-- Your existing PL/SQL code...` with your actual PL/SQL logic. This code assumes you have existing logic to calculate segment-wise details. If not, you'll need to implement that logic as well. Let me know if you need further assistance!