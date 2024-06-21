To achieve the desired result, you can use a combination of `DISTINCT` and `SUM` in your query. The goal is to select unique batch numbers with the same product item code and then calculate their total product quantity. Below is the modified query to achieve this:

```sql
SELECT
    A.BATCH_NO,
    A.PRODUCT_ITEM_CODE,
    A.INPUT_ITEM_CODE,
    A.PRODUCT_QTY
FROM (
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
        ROW_NUMBER() OVER (PARTITION BY A.ITEM_CODE ORDER BY A.BATCH_NO) AS ROW_NUM
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
            ITEM_CODE) A,
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
    WHERE
        A.ORGANIZATION_ID = :ORGANIZATION_ID
        AND A.TRX_DATE = :TRX_DATE
        AND A.BATCH_NO = B.BATCH_NO
) A
WHERE
    A.ROW_NUM = 1
ORDER BY
    A.BATCH_NO;

-- Calculate the total sum of PRODUCT_QTY
WITH Total_Sum AS (
    SELECT SUM(PRODUCT_QTY) AS TOTAL_PRODUCT_QTY
    FROM (
        SELECT
            A.BATCH_NO,
            A.PRODUCT_ITEM_CODE,
            A.INPUT_ITEM_CODE,
            A.PRODUCT_QTY
        FROM (
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
                ROW_NUMBER() OVER (PARTITION BY A.ITEM_CODE ORDER BY A.BATCH_NO) AS ROW_NUM
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
                    ITEM_CODE) A,
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
            WHERE
                A.ORGANIZATION_ID = :ORGANIZATION_ID
                AND A.TRX_DATE = :TRX_DATE
                AND A.BATCH_NO = B.BATCH_NO
        ) A
        WHERE
            A.ROW_NUM = 1
    )
)
SELECT * FROM Total_Sum;
```

Explanation:

1. The main query uses a `ROW_NUMBER()` window function to assign a unique row number to each row partitioned by `ITEM_CODE` and ordered by `BATCH_NO`. This helps in selecting the first occurrence of each `ITEM_CODE`.

2. The `WHERE A.ROW_NUM = 1` clause ensures that only the first occurrence of each `ITEM_CODE` is selected, effectively giving you unique `BATCH_NO` with the same `PRODUCT_ITEM_CODE`.

3. The `WITH Total_Sum AS` clause calculates the total sum of `PRODUCT_QTY` for the selected unique batches.

This approach should yield the desired result with unique batch numbers, corresponding product item codes, and their total sum of product quantity.