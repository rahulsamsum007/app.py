The issue with getting blank `ITEM_CODE` values in your result could stem from the outer join conditions or the inner queries not matching up correctly. Here’s a revised version of your query that ensures all necessary joins are inner joins where applicable to prevent `ITEM_CODE` from being blank, while keeping the intended data structure intact.

### Revised Query:

```sql
SELECT 
    SALE.ORGANIZATION_ID,
    SALE.ITEM_CODE,
    SALE.INV_QUANTITY,
    SALE.NET_VALUE,
    SALE.NPR,
    EXPENSE.THROUGHPUT,
    EXPENSE.RM_COST,
    ROUND(EXPENSE.HOMOPOLYMER_COST, 2) HOMOPOLYMER_COST,
    ROUND(EXPENSE.ADDITIVE_COST, 2) ADDITIVE_COST,
    ROUND(EXPENSE.FILM_IO_RATIO, 3) IO_RATIO,
    ROUND(EXPENSE.IO_COST_PER_KG, 2) IO_COST_PER_KG,
    EXPENSE.POWER_COST,
    EXPENSE.FUEL_AND_WATER,
    EXPENSE.PRODUCTION_CONSUMABLE,
    ROUND(EXPENSE.MET_COST, 2) MET_COST,
    ROUND(EXPENSE.MET_IO_RATIO, 3) MET_IO_RATIO,
    ROUND((CASE WHEN EXPENSE.MET_COST > 0 THEN ROUND(((EXPENSE.MET_IO_RATIO - 1) * EXPENSE.TOTAL_COST), 2) ELSE 0 END), 2) MET_IO_COST_PER_KG,
    ROUND(EXPENSE.TOTAL_COST + EXPENSE.MET_COST + (CASE WHEN EXPENSE.MET_COST > 0 THEN ((EXPENSE.MET_IO_RATIO - 1) * EXPENSE.TOTAL_COST) ELSE 0 END), 2) TOTAL_COST,
    ROUND(SALE.NPR - (EXPENSE.TOTAL_COST + EXPENSE.MET_COST + (CASE WHEN EXPENSE.MET_COST > 0 THEN ((EXPENSE.MET_IO_RATIO - 1) * EXPENSE.TOTAL_COST) ELSE 0 END)), 2) CONTRI_PER_KG
FROM 
    (SELECT 
        ORGANIZATION_ID,
        ITEM_CODE,
        SUM(SALES_QTY_MT) AS INV_QUANTITY,
        SUM(SALE_VALUE) AS NET_VALUE,
        SUM(SALES_QTY_MT * NET_NPR) / SUM(SALES_QTY_MT) AS NPR
    FROM 
        PFBCUSTOM.PFB_CONTRI_SALES_NPR
    WHERE 
        TRUNC(TRX_DATE) >= TRUNC(:P_DATE, 'MM')
        AND TRUNC(TRX_DATE) <= TRUNC(LAST_DAY(:P_DATE))
        AND ORGANIZATION_ID = :P_ORGANIZATION_ID
    GROUP BY 
        ORGANIZATION_ID, ITEM_CODE) SALE
JOIN 
    (SELECT 
        X.ORGANIZATION_ID,
        X.FG_ITEM_CODE,
        X.JUMBO_ITEM_CODE,
        X.RM_CUR_VALUE,
        X.HOMOPOLYMER_COST,
        X.MET_COST,
        X.MET_IO_RATIO,
        X.RM_CUR_VALUE - (X.HOMOPOLYMER_COST + ((X.FILM_IO_RATIO - 1) * X.HOMOPOLYMER_COST)) ADDITIVE_COST,
        X.FILM_IO_RATIO,
        ((X.FILM_IO_RATIO - 1) * X.HOMOPOLYMER_COST) IO_COST_PER_KG,
        Y.POWER_COST,
        Y.FUEL_AND_WATER,
        Y.PRODUCTION_CONSUMABLE,
        Y.THROUGHPUT,
        ROUND((X.HOMOPOLYMER_COST + X.ADDITIVE_COST + X.IO_COST_PER_KG + Y.POWER_COST + Y.FUEL_AND_WATER + Y.PRODUCTION_CONSUMABLE), 2) TOTAL_COST
    FROM 
        (SELECT 
            ORGANIZATION_ID,
            FG_ITEM_CODE,
            JUMBO_ITEM_CODE,
            TRX_DATE,
            SUM(RM_CUR_VALUE) RM_CUR_VALUE,
            SUM(HOMOPOLYMER_COST) HOMOPOLYMER_COST,
            MAX(MET_COST) MET_COST,
            SUM(FILM_IO_RATIO) FILM_IO_RATIO,
            MAX(MET_IO_RATIO) MET_IO_RATIO
        FROM 
            (SELECT 
                ORGANIZATION_ID,
                FG_ITEM_CODE,
                JUMBO_ITEM_CODE,
                TRX_DATE,
                RM_CUR_VALUE,
                HOMOPOLYMER_COST,
                (SELECT MAX(MET_COST)
                 FROM XXSRF.PFB_CONTRI_VC_COST_DATA B
                 WHERE B.ORGANIZATION_ID = A.ORGANIZATION_ID
                   AND B.ITEM_CODE = A.FG_ITEM_CODE
                   AND TRUNC(B.TRX_DATE) <= TRUNC(LAST_DAY(:P_DATE))
                   AND B.ORGANIZATION_ID = :P_ORGANIZATION_ID) MET_COST,
                0 FILM_IO_RATIO,
                (SELECT MAX(IO_RATIO)
                 FROM XXSRF.PFB_CONTRI_IORATIO_DATA C
                 WHERE C.ORGANIZATION_ID = A.ORGANIZATION_ID
                   AND C.FG_ITEM_CODE = A.FG_ITEM_CODE
                   AND TRUNC(C.TRX_DATE) <= TRUNC(LAST_DAY(:P_DATE))
                   AND C.ORGANIZATION_ID = :P_ORGANIZATION_ID) MET_IO_RATIO
            FROM 
                PFBCUSTOM.PFB_CONTRI_RM_COST_DATA A
            WHERE 
                TRUNC(TRX_DATE) = TRUNC(LAST_DAY(:P_DATE))
                AND ORGANIZATION_ID = :P_ORGANIZATION_ID
            UNION ALL
            SELECT 
                ORGANIZATION_ID,
                FG_ITEM_CODE,
                JUMBO_ITEM_CODE,
                TRUNC(LAST_DAY(:P_DATE)) TRX_DATE,
                0 RM_CUR_VALUE,
                0 HOMOPOLYMER_COST,
                0 MET_COST,
                MAX(IO_RATIO) IO_RATIO,
                0 MET_IO_RATIO
            FROM 
                XXSRF.PFB_CONTRI_IORATIO_DATA
            WHERE 
                TRUNC(TRX_DATE) <= TRUNC(LAST_DAY(:P_DATE))
                AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                AND PROD_TYPE = 'JUMBO'
            GROUP BY 
                ORGANIZATION_ID, FG_ITEM_CODE, JUMBO_ITEM_CODE)
        GROUP BY 
            ORGANIZATION_ID,
            FG_ITEM_CODE,
            JUMBO_ITEM_CODE,
            TRX_DATE) X
    JOIN 
        (SELECT 
            ORGANIZATION_ID,
            TRUNC(LAST_DAY(:P_DATE)) TRX_DATE,
            ITEM_CODE,
            MAX(MICRON) MICRON,
            MAX(POWER_COST) POWER_COST,
            MAX(FUEL_AND_WATER) FUEL_AND_WATER,
            MAX(PRODUCTION_CONSUMABLE) PRODUCTION_CONSUMABLE,
            MAX(THROUGHPUT) THROUGHPUT
        FROM 
            XXSRF.PFB_CONTRI_VC_COST_DATA
        WHERE 
            ORGANIZATION_ID = :P_ORGANIZATION_ID
            AND TRUNC(TRX_DATE) <= TRUNC(LAST_DAY(:P_DATE))
            AND PRODUCTION_TYPE = 'JUMBO'
        GROUP BY 
            ORGANIZATION_ID, ITEM_CODE) Y
    ON 
        X.ORGANIZATION_ID = Y.ORGANIZATION_ID
        AND X.TRX_DATE = Y.TRX_DATE
        AND X.JUMBO_ITEM_CODE = Y.ITEM_CODE) EXPENSE
ON 
    SALE.ORGANIZATION_ID = EXPENSE.ORGANIZATION_ID
    AND SALE.ITEM_CODE = EXPENSE.FG_ITEM_CODE
GROUP BY 
    SALE.ORGANIZATION_ID,
    SALE.ITEM_CODE,
    SALE.INV_QUANTITY,
    SALE.NET_VALUE,
    SALE.NPR,
    EXPENSE.THROUGHPUT,
    EXPENSE.RM_COST,
    EXPENSE.HOMOPOLYMER_COST,
    EXPENSE.ADDITIVE_COST,
    EXPENSE.IO_RATIO,
    EXPENSE.IO_COST_PER_KG,
    EXPENSE.POWER_COST,
    EXPENSE.FUEL_AND_WATER,
    EXPENSE.PRODUCTION_CONSUMABLE,
    EXPENSE.MET_COST,
    EXPENSE.MET_IO_RATIO,
    EXPENSE.TOTAL_COST;
```

### Explanation of Changes:
1. Changed outer joins (`LEFT JOIN`) to inner joins (`JOIN`) to ensure only matching records are returned, thus preventing `ITEM_CODE` from being blank.
2. Ensured that all joins between `SALE` and `EXPENSE` are based on matching `ORGANIZATION_ID` and `ITEM_CODE`.
3. Simplified and cleaned up subqueries to make sure that the join logic is clear and correct.

This should help in resolving the issue of blank `ITEM_CODE` values. If there are still blank `ITEM_CODE` values, it could indicate missing or mismatched data in the underlying tables, which might require further data validation.