To achieve this, you can modify your cursor `SEG` to accept the `ZONE_NAME` parameter and then filter the data based on that parameter. Then, within your loop, you can pass each distinct zone name from the `ZONE_CUR` cursor to the `SEG` cursor. Here's how you can do it:

```sql
CURSOR SEG(ZONE_NAME VARCHAR2) IS 
 WITH
    TAB
    AS
        (  
            SELECT SEGMENT_NAME,
                  ROUND(SUM(BUDGET_QTY), 2) AS PLAN_QTY,
                  0 AS INVOICE_QTY,
                  0 AS ORDER_QTY
             FROM BARCODE.LFCF_SEGMENT_SALES_MIS_BUDGET_DATA
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID
              AND TRUNC(BUDGET_DATE) BETWEEN TRUNC(P_DATE, 'MM') AND LAST_DAY(TRUNC(P_DATE))
              AND ZONE_NAME = SEG.ZONE_NAME -- Filter by zone name
         GROUP BY SEGMENT_NAME                      
         UNION ALL                            
           SELECT NVL(ITEM_CATEGORY, ITEM_NAME) AS SEGMENT_NAME,
                  0 AS PLAN_QTY,
                  ROUND(SUM(SHIPPED_QTY), 2) AS INVOICE_QTY,
                  0 AS ORDER_QTY
             FROM BARCODE.LFCF_SALES_MIS_INVOICE_DATA
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID
              AND TRUNC(INVOICE_DATE) BETWEEN TRUNC(P_DATE, 'MM') AND LAST_DAY(TRUNC(P_DATE))
              AND ZONE_NAME = SEG.ZONE_NAME -- Filter by zone name
         GROUP BY NVL(ITEM_CATEGORY, ITEM_NAME)
         UNION ALL
           SELECT NVL(PRODUCT_CATEGORY, PRODUCT) AS SEGMENT_NAME,
                  0 AS PLAN_QTY,
                  0 AS INVOICE_QTY,
                  ROUND(SUM(ORDER_QTY), 2) AS ORDER_QTY
             FROM BARCODE.LFCF_SALES_MIS_ORDER_DATA
            WHERE ORGANIZATION_ID = P_ORGANIZATION_ID
              AND TRUNC(SCHEDULE_SHIP_DATE) <= LAST_DAY(TRUNC(P_DATE))
              AND ZONE_NAME = SEG.ZONE_NAME -- Filter by zone name
         GROUP BY NVL(PRODUCT_CATEGORY, PRODUCT))
  SELECT SEQ_NO,
         SEGMENT_NAME,
         PLAN_QTY,
         INVOICE_QTY,
         ORDER_QTY,
         ROUND(INVOICE_QTY + ORDER_QTY, 2) AS TOTAL_ORDER_BOOKED,
         ROUND(PLAN_QTY - (INVOICE_QTY + ORDER_QTY), 2) AS ORDER_TO_BE_BOOKED
    FROM (  
          SELECT 1 AS SEQ_NO,
                 SEGMENT_NAME,
                 SUM(PLAN_QTY) AS PLAN_QTY,
                 SUM(INVOICE_QTY) AS INVOICE_QTY,
                 SUM(ORDER_QTY) AS ORDER_QTY
            FROM TAB
        GROUP BY SEGMENT_NAME
        UNION ALL
        SELECT 2 AS SEQ_NO,
               'Total' AS SEGMENT_NAME,
               SUM(PLAN_QTY) AS PLAN_QTY,
               SUM(INVOICE_QTY) AS INVOICE_QTY,
               SUM(ORDER_QTY) AS ORDER_QTY
          FROM TAB)
ORDER BY 1, 2;
```

Then, within your loop, you can iterate over the distinct zone names and pass each zone name to the `SEG` cursor:

```sql
FOR Z IN ZONE_CUR LOOP
    -- Print Zone Name
    UTL_SMTP.WRITE_DATA(VCONNECTION, '<h2>' || Z.ZONE || '</h2>');

    -- Execute SEG cursor for the current zone
    FOR J IN SEG(Z.ZONE) LOOP
        -- Print segment data
        -- Your existing code to print segment data goes here
    END LOOP;
END LOOP;
```

This way, the `SEG` cursor will only retrieve data for the specified zone name, and you can loop through each distinct zone name from the `ZONE_CUR` cursor and print the corresponding segment data.