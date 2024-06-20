Based on your requirements, I'll rewrite the SQL query to reflect the necessary changes. Here are the adjustments:
1. Renaming columns as specified.
2. Adding parameters for `ORGANIZATION_ID` and `TRX_DATE`.
3. Removing the `NVL` function and simplifying the join conditions.

Here's the updated SQL query:

```sql
SELECT
    A.ORGANIZATION_ID,
    CASE
        WHEN A.PROD_TYPE LIKE '%J%' THEN 'JUMBO'
        WHEN A.PROD_TYPE LIKE '%M%' THEN 'MET'
    END AS PROD_TYPE,
    A.LINE_TYPE,
    A.TRX_DATE,
    A.BATCH_NO,
    A.ITEM_CODE AS PRODUCT_ITEM_CODE,
    B.ITEM_CODE AS INPUT_ITEM_CODE,
    ABS(A.TOTAL_QTY) AS PRODUCT_QTY,
    ABS(B.TOTAL_QTY) AS INPUT_QTY
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
        ITEM_CODE) B
ON A.ORGANIZATION_ID = B.ORGANIZATION_ID
AND A.TRX_DATE = B.TRX_DATE
AND A.BATCH_NO = B.BATCH_NO
WHERE
    A.ORGANIZATION_ID = :organization_id
AND A.TRX_DATE = :trx_date
ORDER BY
    A.ORGANIZATION_ID,
    A.TRX_DATE,
    A.BATCH_NO,
    A.LINE_TYPE;
```

In this updated query:
1. The columns `A.ITEM_CODE` and `B.ITEM_CODE` are renamed to `PRODUCT_ITEM_CODE` and `INPUT_ITEM_CODE`, respectively.
2. The `TOTAL_QTY` columns are renamed to `PRODUCT_QTY` and `INPUT_QTY`.
3. The `ORGANIZATION_ID` and `TRX_DATE` are parameterized as `:organization_id` and `:trx_date`.
4. The `NVL` function is removed, as it is not required based on your input.

Ensure to replace the `:organization_id` and `:trx_date` parameters with actual values when running the query.