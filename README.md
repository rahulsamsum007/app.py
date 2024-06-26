```sql
                    TRX_DATE DESC) RN
                        FROM XXSRF.IORATIO_TEST A
                       WHERE TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                             AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                             AND PROD_TYPE = 'JUMBO')
                   WHERE RN = 1)
        GROUP BY ORGANIZATION_ID,
                 FG_ITEM_CODE,
                 JUMBO_ITEM_CODE,
                 TRX_DATE) X,
       (SELECT ORGANIZATION_ID,
               TRUNC (LAST_DAY ( :P_DATE)) TRX_DATE,
               ITEM_CODE,
               MICRON,
               POWER_COST,
               FUEL_AND_WATER,
               PRODUCTION_CONSUMABLE,
               THROUGHPUT
          FROM (SELECT A.*,
                       RANK ()
                           OVER (PARTITION BY A.ORGANIZATION_ID, A.ITEM_CODE
                                 ORDER BY TRX_DATE DESC) RN
                  FROM XXSRF.PFB_CONTRI_VC_COST_DATA A
                 WHERE A.ORGANIZATION_ID = :P_ORGANIZATION_ID
                       AND TRUNC (A.TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                       AND A.PRODUCTION_TYPE = 'JUMBO')
         WHERE RN = 1) Y
 WHERE X.ORGANIZATION_ID = Y.ORGANIZATION_ID
       AND X.TRX_DATE = Y.TRX_DATE
       AND X.JUMBO_ITEM_CODE = Y.ITEM_CODE) EXPENSE
 WHERE SALE.ORGANIZATION_ID = EXPENSE.ORGANIZATION_ID(+)
       AND SALE.TRX_DATE = EXPENSE.TRX_DATE(+)
       AND SALE.ITEM_CODE = EXPENSE.FG_ITEM_CODE(+));
```

This completes the query with the requested modifications:

1. Column names updated as specified.
2. Added `CUSTOMER_NAME` column to the SELECT clause and the inner query.