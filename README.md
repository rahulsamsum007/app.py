To achieve the desired result where you select only one `PRODUCT_QTY` for each `PRODUCT_ITEM_CODE` per unique `BATCH_NO` and calculate the total sum, you can modify your SQL query. Here’s how you can structure it:

### Revised SQL Query:

```sql
SELECT
    A.ORGANIZATION_ID,
    'JUMBO' AS PROD_TYPE,
    A.TRX_DATE,
    A.BATCH_NO,
    A.PRODUCT_ITEM_CODE,
    B.INPUT_ITEM_CODE,
    A.PRODUCT_QTY,
    B.INPUT_QTY,
    SUM(A.PRODUCT_QTY) OVER (PARTITION BY A.PRODUCT_ITEM_CODE) AS TOTAL_PRODUCT_QTY
FROM (
    SELECT
        ORGANIZATION_ID,
        TRX_DATE,
        BATCH_NO,
        ITEM_CODE AS PRODUCT_ITEM_CODE,
        SUM(TRX_QTY) AS PRODUCT_QTY
    FROM
        XXSRF.JUMBO_MET_TRANSACTIONS
    WHERE
        LINE_TYPE = 1
        AND PROD_TYPE LIKE '%J%'
        AND ORGANIZATION_ID = :ORGANIZATION_ID
        AND TRX_DATE = :TRX_DATE
    GROUP BY
        ORGANIZATION_ID,
        TRX_DATE,
        BATCH_NO,
        ITEM_CODE
) A
JOIN (
    SELECT
        ORGANIZATION_ID,
        TRX_DATE,
        BATCH_NO,
        ITEM_CODE AS INPUT_ITEM_CODE,
        SUM(TRX_QTY) AS INPUT_QTY
    FROM
        XXSRF.JUMBO_MET_TRANSACTIONS
    WHERE
        LINE_TYPE = -1
        AND PROD_TYPE LIKE '%J%'
        AND ORGANIZATION_ID = :ORGANIZATION_ID
        AND TRX_DATE = :TRX_DATE
    GROUP BY
        ORGANIZATION_ID,
        TRX_DATE,
        BATCH_NO,
        ITEM_CODE
) B ON A.BATCH_NO = B.BATCH_NO
   AND A.PRODUCT_ITEM_CODE = B.ITEM_CODE
ORDER BY
    A.ORGANIZATION_ID,
    A.TRX_DATE,
    A.BATCH_NO;
```

### Explanation:

1. **Subquery `A` (PRODUCT_QTY)**:
   - Calculates `PRODUCT_QTY` grouped by `ORGANIZATION_ID`, `TRX_DATE`, `BATCH_NO`, and `PRODUCT_ITEM_CODE` where `LINE_TYPE = 1`.

2. **Subquery `B` (INPUT_QTY)**:
   - Calculates `INPUT_QTY` grouped by `ORGANIZATION_ID`, `TRX_DATE`, `BATCH_NO`, and `INPUT_ITEM_CODE` where `LINE_TYPE = -1`.

3. **Main Query**:
   - Joins subqueries `A` and `B` on `BATCH_NO` and `PRODUCT_ITEM_CODE`.
   - Selects necessary columns (`ORGANIZATION_ID`, `PROD_TYPE`, `TRX_DATE`, `BATCH_NO`, `PRODUCT_ITEM_CODE`, `INPUT_ITEM_CODE`, `PRODUCT_QTY`, `INPUT_QTY`).
   - Computes `TOTAL_PRODUCT_QTY` using `SUM(A.PRODUCT_QTY) OVER (PARTITION BY A.PRODUCT_ITEM_CODE)` to get the total `PRODUCT_QTY` for each `PRODUCT_ITEM_CODE`.
   - Orders the result set by `ORGANIZATION_ID`, `TRX_DATE`, and `BATCH_NO`.

### Verification:

- Ensure that `:ORGANIZATION_ID` and `:TRX_DATE` have valid values that match existing data in your `XXSRF.JUMBO_MET_TRANSACTIONS` table.
- Verify that the join condition `A.BATCH_NO = B.BATCH_NO AND A.PRODUCT_ITEM_CODE = B.ITEM_CODE` correctly links `PRODUCT_QTY` and `INPUT_QTY` based on your business logic.
- Execute the query and inspect the results to confirm that each `PRODUCT_ITEM_CODE` has only one `PRODUCT_QTY` per unique `BATCH_NO` and that `TOTAL_PRODUCT_QTY` sums correctly.

This query should provide you with the desired output structure where `PRODUCT_QTY` for each `PRODUCT_ITEM_CODE` is selected uniquely per `BATCH_NO` and the total sum is calculated accordingly. Adjust the query as needed based on your specific database schema and requirements.