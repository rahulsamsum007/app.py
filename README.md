To achieve the desired output where you want to select one `PRODUCT_QTY` for each unique `PRODUCT_ITEM_CODE` and then calculate their total sum, you can modify the query as follows:

```sql
WITH CTE AS (
    SELECT
        A.ORGANIZATION_ID,
        CASE
            WHEN A.PROD_TYPE LIKE '%J%' THEN 'JUMBO'
            WHEN A.PROD_TYPE LIKE '%M%' THEN 'MET'
        END AS PROD_TYPE,
        A.TRX_DATE,
        A.BATCH_NO,
        A.ITEM_CODE AS PRODUCT_ITEM_CODE,
        B.ITEM_CODE AS INPUT_ITEM_CODE,
        ABS(A.TOTAL_QTY) AS PRODUCT_QTY,
        ABS(B.TOTAL_QTY) AS INPUT_QTY,
        ROW_NUMBER() OVER (PARTITION BY A.PRODUCT_ITEM_CODE ORDER BY A.BATCH_NO) AS ROW_NUM
    FROM
        (SELECT
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            BATCH_NO,
            ITEM_CODE,
            SUM(TRX_QTY) AS TOTAL_QTY
        FROM
            XXSRF.JUMBO_MET_TRANSACTIONS
        WHERE
            LINE_TYPE = 1
        GROUP BY
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            BATCH_NO,
            ITEM_CODE) A
    JOIN
        (SELECT
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            BATCH_NO,
            ITEM_CODE,
            SUM(TRX_QTY) AS TOTAL_QTY
        FROM
            XXSRF.JUMBO_MET_TRANSACTIONS
        WHERE
            LINE_TYPE = -1
        GROUP BY
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            BATCH_NO,
            ITEM_CODE) B ON A.BATCH_NO = B.BATCH_NO
    WHERE
        A.ORGANIZATION_ID = :ORGANIZATION_ID
        AND A.TRX_DATE = :TRX_DATE
)
SELECT
    BATCH_NO,
    PRODUCT_ITEM_CODE,
    MAX(PRODUCT_QTY) AS PRODUCT_QTY
FROM CTE
WHERE ROW_NUM = 1
GROUP BY BATCH_NO, PRODUCT_ITEM_CODE
UNION ALL
SELECT
    NULL,
    NULL,
    SUM(PRODUCT_QTY)
FROM CTE;
```
