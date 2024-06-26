Here is the modified SQL query with the requested changes:

1. Updated column names from the `XXSRF.XXSRF_PFB_NPR_FINAL_DETAILS_TESTING` table:
   - `SALE.INV_QUANTITY` to `SALE.SALES_QTY_MT`
   - `SALE.NET_VALUE` to `SALE.SALE_VALUE`
   - `SALE.NPR` to `SALE.GROSS_NPR`

2. Added `CUSTOMER_NAME` column.

```sql
----------------------------------------------------------------------------------------------------------------------------
-------------------------------------------- FINAL OUTPUT ------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
SELECT ORGANIZATION_ID,
       TRX_DATE,
       ITEM_CODE,
       INV_QUANTITY,
       NET_VALUE,
       NPR,
       THROUGHPUT,
       RM_COST,
       HOMOPOLYMER_COST,
       ADDITIVE_COST,
       IO_RATIO,
       IO_COST_PER_KG,
       POWER_COST,
       FUEL_AND_WATER,
       PRODUCTION_CONSUMABLE,
       ROUND(MET_COST, 2) MET_COST,
       ROUND(MET_IO_RATIO, 3) MET_IO_RATIO,
       ROUND((CASE WHEN MET_COST > 0 THEN ROUND(((MET_IO_RATIO - 1) * TOTAL_COST), 2) ELSE 0 END), 2) MET_IO_COST_PER_KG,
       ROUND(TOTAL_COST + MET_COST + (CASE WHEN MET_COST > 0 THEN ((MET_IO_RATIO - 1) * TOTAL_COST) ELSE 0 END), 2) TOTAL_COST,
       ROUND(NPR - (TOTAL_COST + MET_COST + (CASE WHEN MET_COST > 0 THEN ((MET_IO_RATIO - 1) * TOTAL_COST) ELSE 0 END)), 2) CONTRI_PER_KG
FROM
(SELECT SALE.ORGANIZATION_ID,
       SALE.TRX_DATE,
       SALE.ITEM_CODE,
       SALE.SALES_QTY_MT AS INV_QUANTITY,
       SALE.SALE_VALUE AS NET_VALUE,
       SALE.GROSS_NPR AS NPR,
       SALE.CUSTOMER_NAME,
       EXPENSE.THROUGHPUT,
       EXPENSE.RM_CUR_VALUE RM_COST,
       ROUND(EXPENSE.HOMOPOLYMER_COST, 2) HOMOPOLYMER_COST,
       ROUND(EXPENSE.ADDITIVE_COST, 2) ADDITIVE_COST,
       ROUND(EXPENSE.FILM_IO_RATIO, 3) IO_RATIO,
       ROUND(EXPENSE.IO_COST_PER_KG, 2) IO_COST_PER_KG,
       EXPENSE.POWER_COST,
       EXPENSE.FUEL_AND_WATER,
       EXPENSE.PRODUCTION_CONSUMABLE,
       EXPENSE.MET_COST,
       EXPENSE.MET_IO_RATIO,
       ROUND((HOMOPOLYMER_COST + ADDITIVE_COST + IO_COST_PER_KG + POWER_COST + FUEL_AND_WATER + PRODUCTION_CONSUMABLE), 2) TOTAL_COST
FROM (SELECT ORGANIZATION_ID,
             LAST_DAY (TRX_DATE) TRX_DATE,
             ITEM_CODE,
             JUMBO_ITEM_CODE,
             MET_FILM,
             MICRON,
             ROUND (SUM (SALES_QTY_MT), 2) SALES_QTY_MT,
             ROUND (SUM (SALE_VALUE), 2) SALE_VALUE,
             ROUND ((SUM (SALE_VALUE) / SUM (SALES_QTY_MT)), 2) - 4 NPR,
             CUSTOMER_NAME
      FROM (SELECT A.ORGANIZATION_ID,
                   B.NPR_HEADER_ID,
                   B.NPR_DETAIL_ID,
                   B.CUSTOMER_TRX_ID,
                   B.TRX_NUMBER,
                   B.TRX_DATE,
                   TO_CHAR (B.TRX_DATE, 'MON') TRX_MONTH,
                   TO_CHAR (B.TRX_DATE, 'RRRR') TRX_YEAR,
                   B.INVOICE_TYPE,
                   B.CUSTOMER_ID,
                   B.CUSTOMER_NAME,
                   B.REGION,
                   B.PRICE_LIST_NAME,
                   B.ITEM_CODE,
                   JFG.JUMBO_ITEM_CODE,
                   JFG.MET_FILM,
                   MSI.ATTRIBUTE1 MICRON,
                   B.SALES_QTY_MT,
                   B.GROSS_NPR,
                   B.SALES_QTY_MT * (B.GROSS_NPR - DECODE (NVL (B.PACKING_TYPE, 'LOOSE'), 'LOOSE', 2, 5)) SALE_VALUE
            FROM XXSRF.XXSRF_PFB_NPR_HEADERS A,
                 XXSRF.XXSRF_PFB_NPR_FINAL_DETAILS B,
                 APPS.MTL_SYSTEM_ITEMS_B MSI,
                 XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP JFG,
                 (SELECT MIC.ORGANIZATION_ID,
                         MIC.INVENTORY_ITEM_ID,
                         MCV.SEGMENT2
                    FROM APPS.MTL_ITEM_CATEGORIES MIC,
                         APPS.MTL_CATEGORY_SETS MCS,
                         APPS.MTL_CATEGORIES_VL MCV,
                         APPS.ORG_ORGANIZATION_DEFINITIONS OOD1
                   WHERE MIC.ORGANIZATION_ID = OOD1.ORGANIZATION_ID
                         AND OOD1.OPERATING_UNIT = 87
                         AND MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID
                         AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                         AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                         AND MCS.CATEGORY_SET_NAME = 'Inventory') INVENTORY
               WHERE TRUNC (TRX_DATE) >= TRUNC ( :P_DATE, 'MM')
                     AND TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                     AND A.NPR_HEADER_ID = B.NPR_HEADER_ID
                     AND MSI.ORGANIZATION_ID = A.ORGANIZATION_ID
                     AND A.ORGANIZATION_ID = :P_ORGANIZATION_ID
                     AND MSI.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                     AND MSI.ITEM_TYPE = 'FILM'
                     AND INVENTORY.ORGANIZATION_ID = A.ORGANIZATION_ID
                     AND INVENTORY.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                     AND A.ORGANIZATION_ID = JFG.ORGANIZATION_ID(+)
                     AND B.ITEM_CODE = JFG.FG_ITEM_CODE(+))
      GROUP BY ORGANIZATION_ID,
               LAST_DAY (TRX_DATE),
               ITEM_CODE,
               JUMBO_ITEM_CODE,
               MET_FILM,
               MICRON,
               CUSTOMER_NAME) SALE,
(SELECT X.ORGANIZATION_ID,
       X.FG_ITEM_CODE,
       X.JUMBO_ITEM_CODE,
       X.MET_FILM,
       X.TRX_DATE,
       X.RM_CUR_VALUE,
       X.HOMOPOLYMER_COST,
       X.MET_COST,
       X.MET_IO_RATIO,
       X.RM_CUR_VALUE - (X.HOMOPOLYMER_COST + ((X.FILM_IO_RATIO-1) * X.HOMOPOLYMER_COST)) ADDITIVE_COST,
       X.FILM_IO_RATIO,
       ((X.FILM_IO_RATIO-1) * X.HOMOPOLYMER_COST) IO_COST_PER_KG,
       Y.POWER_COST,
       Y.FUEL_AND_WATER,
       Y.PRODUCTION_CONSUMABLE,
       Y.THROUGHPUT
  FROM (SELECT ORGANIZATION_ID,
               FG_ITEM_CODE,
               JUMBO_ITEM_CODE,
               MAX (MET_FILM) MET_FILM,
               TRX_DATE,
               SUM (RM_CUR_VALUE) RM_CUR_VALUE,
               SUM (HOMOPOLYMER_COST) HOMOPOLYMER_COST,
               SUM (MET_COST) MET_COST,
               SUM (FILM_IO_RATIO) FILM_IO_RATIO,
               SUM (MET_IO_RATIO) MET_IO_RATIO
        FROM (SELECT ORGANIZATION_ID,
                     FG_ITEM_CODE,
                     JUMBO_ITEM_CODE,
                     MET_FILM,
                     TRX_DATE,
                     RM_CUR_VALUE,
                     HOMOPOLYMER_COST,
                     (SELECT MET_COST
                        FROM (SELECT P.*,
                                     RANK () OVER (PARTITION BY ORGANIZATION_ID, ITEM_CODE ORDER BY TRX_DATE DESC) RN
                                FROM XXSRF.PFB_CONTRI_VC_COST_DATA P
                               WHERE TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                                     AND ORGANIZATION_ID = :P_ORGANIZATION_ID) B
                       WHERE RN = 1
                         AND A.ORGANIZATION_ID = B.ORGANIZATION_ID
                         AND A.FG_ITEM_CODE = B.ITEM_CODE) MET_COST,
                     0 FILM_IO_RATIO,
                     (SELECT IO_RATIO MET_IO_RATIO
                        FROM (SELECT Q.*,
                                     RANK () OVER (PARTITION BY ORGANIZATION_ID, FG_ITEM_CODE, JUMBO_ITEM_CODE ORDER BY TRX_DATE DESC) RN
                                FROM XXSRF.IORATIO_TEST Q
                               WHERE TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                                     AND ORGANIZATION_ID = :P_ORGANIZATION_ID) C
                       WHERE RN = 1
                         AND A.ORGANIZATION_ID = C.ORGANIZATION_ID
                         AND A.FG_ITEM_CODE = C.FG_ITEM_CODE) MET_IO_RATIO
                FROM XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA A
               WHERE TRUNC (TRX_DATE) = TRUNC (LAST_DAY ( :P_DATE))
                     AND ORGANIZATION_ID = :P_ORGANIZATION_ID
              UNION ALL
              SELECT ORGANIZATION_ID,
                     FG_ITEM_CODE,
                     JUMBO_ITEM_CODE,
                     NULL MET_FILM,
                     TRUNC (LAST_DAY ( :P_DATE)) TRX_DATE,
                     0 RM_CUR_VALUE,
                     0 HOMOPOLYMER_COST,
                     0 MET_COST,
                     IO_RATIO,
                     0 MET_IO_RATIO
                FROM (SELECT A.*,
                             RANK () OVER (PARTITION BY ORGANIZATION_ID, FG_ITEM_CODE, JUMBO_ITEM_CODE ORDER BY```sql
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