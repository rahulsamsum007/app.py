
SELECT
    ORGANIZATION_ID,
    CASE
        WHEN PROD_TYPE LIKE '%J%' THEN 'JUMBO'
        WHEN PROD_TYPE LIKE '%M%' THEN 'MET'
    END AS PROD_TYPE,
    LINE_TYPE,
    TRX_DATE,
    BATCH_NO,
    PRODUCT_ITEM_CODE,
    INPUT_ITEM_CODE,
    PRODUCT_QTY,
    INPUT_QTY
FROM (
    SELECT
        A.ORGANIZATION_ID,
        A.PROD_TYPE,
        A.LINE_TYPE,
        A.TRX_DATE,
        A.BATCH_NO,
        A.ITEM_CODE AS PRODUCT_ITEM_CODE,
        NULL AS INPUT_ITEM_CODE,
        ABS(A.TOTAL_QTY) AS PRODUCT_QTY,
        NULL AS INPUT_QTY
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
    UNION ALL
    SELECT
        B.ORGANIZATION_ID,
        B.PROD_TYPE,
        B.LINE_TYPE,
        B.TRX_DATE,
        B.BATCH_NO,
        NULL AS PRODUCT_ITEM_CODE,
        B.ITEM_CODE AS INPUT_ITEM_CODE,
        NULL AS PRODUCT_QTY,
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
            LINE_TYPE = -1
        GROUP BY
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            BATCH_NO,
            ITEM_CODE) B
)
WHERE
    ORGANIZATION_ID = :ORGANIZATION_ID
    AND TRX_DATE = :TRX_DATE
ORDER BY
    ORGANIZATION_ID,
    TRX_DATE,
    BATCH_NO,
    LINE_TYPE;
