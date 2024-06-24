To ensure that the `RM_CUR_VALUE` is calculated for all rows, let's address a few potential issues:

1. **Missing Cost Data**: There might be missing cost data in either the `APPS.CM_CMPT_DTL_VW` or `XXSRF.PFB_CONTRI_ITEM_AVG_COST` tables for some `INPUT_ITEM_CODE` values.

2. **Join Conditions**: The join conditions might be too restrictive, causing some records to be excluded.

### Steps to Troubleshoot and Fix

1. **Check for Missing Data**: Verify if there are any `INPUT_ITEM_CODE` values that do not have corresponding entries in the cost tables.
2. **Simplify Joins**: Ensure the joins are correctly set up and not excluding relevant records.
3. **Fallback Mechanism**: Ensure the fallback mechanism (using `NVL`) works correctly.

### Improved Query with Debugging

First, let's improve the query to include a check for missing cost data and use a clearer fallback mechanism:

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.PROD_TYPE,
       INPUT.TRX_DATE,
       INPUT.JUMBO_ITEM_CODE,
       INPUT.INPUT_ITEM_CODE,
       INPUT.INPUT_QTY,
       OUTPUT.OUTPUT_QTY,
       INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY AS PER_KG_QTY,
       ROUND(INPUT.INPUT_QTY * NVL(C.CUR_COST, D.ITEM_COST), 2) AS RM_CUR_VALUE,
       C.CUR_COST,
       D.ITEM_COST
  FROM (  SELECT ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 JUMBO_ITEM_CODE,
                 INPUT_ITEM_CODE,
                 SUM (INPUT_QTY)     INPUT_QTY
            FROM (  SELECT ORGANIZATION_ID,
                           PROD_TYPE,
                           LINE_TYPE,
                           TRX_DATE,
                           BATCH_NO,
                           (SELECT DISTINCT ITEM_CODE
                              FROM XXSRF.JUMBO_MET_TRANSACTIONS B
                             WHERE     LINE_TYPE = 1
                                   AND PROD_TYPE = 'JUMBO'
                                   AND A.ORGANIZATION_ID = B.ORGANIZATION_ID
                                   AND A.BATCH_NO = B.BATCH_NO
                                   AND A.TRX_DATE = B.TRX_DATE
                                   AND A.PROD_TYPE = B.PROD_TYPE)
                               JUMBO_ITEM_CODE,
                           ITEM_CODE
                               INPUT_ITEM_CODE,
                           SUM (TRX_QTY) INPUT_QTY
                      FROM XXSRF.JUMBO_MET_TRANSACTIONS A
                     WHERE     LINE_TYPE = -1
                           AND PROD_TYPE = 'JUMBO'
                           AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                           AND TRX_DATE = :P_TRX_DATE
                  GROUP BY ORGANIZATION_ID,
                           PROD_TYPE,
                           LINE_TYPE,
                           TRX_DATE,
                           BATCH_NO,
                           ITEM_CODE)
        GROUP BY ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 JUMBO_ITEM_CODE,
                 INPUT_ITEM_CODE) INPUT
       LEFT JOIN (  SELECT MSI.INVENTORY_ITEM_ID,
                          MSI.SEGMENT1,
                          OOD.ORGANIZATION_ID,
                          SUM (CMPNT_COST) AS CUR_COST
                     FROM APPS.CM_CMPT_DTL_VW C,
                          APPS.MTL_PARAMETERS MTP,
                          APPS.ORG_ORGANIZATION_DEFINITIONS OOD,
                          APPS.MTL_SYSTEM_ITEMS MSI
                    WHERE     C.ORGANIZATION_ID = MTP.ORGANIZATION_ID
                          AND MTP.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                          AND MSI.ORGANIZATION_ID = MTP.ORGANIZATION_ID
                          AND MSI.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
                          AND PROCESS_ENABLED_FLAG = 'Y'
                          AND OOD.OPERATING_UNIT = :P_ORG_ID
                          AND MTP.ORGANIZATION_ID = NVL(:P_ORGANIZATION_ID, MTP.ORGANIZATION_ID)
                          AND DELETE_MARK = 0
                          AND PERIOD_ID = (SELECT PERIOD_ID
                                             FROM APPS.GMF_PERIOD_STATUSES A,
                                                  APPS.HR_OPERATING_UNITS B
                                            WHERE B.ORGANIZATION_ID = :P_ORG_ID
                                                  AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                                                  AND COST_TYPE_ID IN (SELECT COST_TYPE_ID
                                                                         FROM APPS.CM_MTHD_MST
                                                                        WHERE COST_MTHD_CODE = 'PMAC')
                                                  AND TO_CHAR(START_DATE, 'MON-RR') = TO_CHAR(:P_TRX_DATE, 'MON-RR'))
                          AND (SELECT COST_MTHD_CODE
                                 FROM APPS.CM_MTHD_MST
                                WHERE COST_TYPE_ID = C.COST_TYPE_ID) IN (SELECT TAG
                                                                           FROM APPS.FND_LOOKUP_VALUES
                                                                          WHERE LOOKUP_TYPE = 'XXSRF_11I_R12_MAPPING_LOOKUP'
                                                                                AND ATTRIBUTE1 = 'SRF PFB Location Wise Stock Summary with Values(Raw Material)'
                                                                                AND MEANING IN ('COST-MTHD-1', 'COST-MTHD-2'))
                    GROUP BY MSI.INVENTORY_ITEM_ID,
                             MSI.SEGMENT1,
                             OOD.ORGANIZATION_ID) C
              ON INPUT.ORGANIZATION_ID = C.ORGANIZATION_ID
             AND INPUT.INPUT_ITEM_CODE = C.SEGMENT1
       LEFT JOIN (  SELECT *
                      FROM XXSRF.PFB_CONTRI_ITEM_AVG_COST
                     WHERE ORGANIZATION_ID = :P_ORGANIZATION_ID
                       AND TRX_DATE = TRUNC(LAST_DAY(:P_TRX_DATE))
                       AND ITEM_CATEGORY = 'NHP') D
              ON INPUT.ORGANIZATION_ID = D.ORGANIZATION_ID
             AND D.PRODUCT_TYPE = SUBSTR(INPUT.INPUT_ITEM_CODE, 1, INSTR(INPUT.INPUT_ITEM_CODE, '-') - 1),
       (  SELECT ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 ITEM_CODE         JUMBO_ITEM_CODE,
                 SUM (TRX_QTY)     OUTPUT_QTY
            FROM XXSRF.JUMBO_MET_TRANSACTIONS A
           WHERE     LINE_TYPE = 1
                 AND PROD_TYPE = 'JUMBO'
                 AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                 AND TRX_DATE = :P_TRX_DATE
        GROUP BY ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 ITEM_CODE) OUTPUT
WHERE     INPUT.ORGANIZATION_ID = OUTPUT.ORGANIZATION_ID
       AND INPUT.PROD_TYPE = OUTPUT.PROD_TYPE
       AND INPUT.TRX_DATE = OUTPUT.TRX_DATE
       AND INPUT.JUMBO_ITEM_CODE = OUTPUT.JUMBO_ITEM_CODE;
```

### Debugging

1. **Columns Added**: `C.CUR_COST` and `D.ITEM_COST` columns are included in the result set to see which costs are being used.
2. **Check Data**: Review the results to identify any missing `CUR_COST` or `ITEM_COST`.

### Next Steps

1. **Review Missing Costs**: Identify `INPUT_ITEM_CODE` values with missing `CUR_COST` and `ITEM_COST` and investigate why the costs are not available.
2. **Data Completeness**: Ensure the cost data tables (`APPS.CM_CMPT_DTL_VW` and `XXSRF.PFB_CONTRI_ITEM_AVG_COST`) are updated and include all necessary cost data.
3. **Fallback Mechanism**: Verify that the fallback logic (`NVL(C.CUR_COST, D.ITEM_COST)`) correctly substitutes costs when one of the cost types is missing.

By implementing these changes, you can better understand where the calculation might be failing and take appropriate actions to fix any issues with missing cost d
To check for missing cost data, you can create a couple of queries to isolate and identify the records where the cost information is missing. Here are two queries that will help you identify the records with missing `CUR_COST` and `ITEM_COST`.

### Query to Check Missing `CUR_COST`

This query checks if there are any `INPUT_ITEM_CODE` values from the main query that do not have corresponding entries in the `APPS.CM_CMPT_DTL_VW` table.

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.INPUT_ITEM_CODE,
       INPUT.TRX_DATE
  FROM (  SELECT ORGANIZATION_ID,
                 INPUT_ITEM_CODE,
                 TRX_DATE
            FROM (  SELECT ORGANIZATION_ID,
                           ITEM_CODE AS INPUT_ITEM_CODE,
                           TRX_DATE
                      FROM XXSRF.JUMBO_MET_TRANSACTIONS
                     WHERE LINE_TYPE = -1
                           AND PROD_TYPE = 'JUMBO'
                           AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                           AND TRX_DATE = :P_TRX_DATE
                  GROUP BY ORGANIZATION_ID, ITEM_CODE, TRX_DATE)) INPUT
       LEFT JOIN (  SELECT MSI.SEGMENT1,
                          OOD.ORGANIZATION_ID
                     FROM APPS.CM_CMPT_DTL_VW C,
                          APPS.MTL_SYSTEM_ITEMS MSI,
                          APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                    WHERE C.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                          AND MSI.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
                          AND OOD.OPERATING_UNIT = :P_ORG_ID
                          AND PERIOD_ID = (SELECT PERIOD_ID
                                             FROM APPS.GMF_PERIOD_STATUSES A,
                                                  APPS.HR_OPERATING_UNITS B
                                            WHERE B.ORGANIZATION_ID = :P_ORG_ID
                                                  AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                                                  AND COST_TYPE_ID IN (SELECT COST_TYPE_ID
                                                                         FROM APPS.CM_MTHD_MST
                                                                        WHERE COST_MTHD_CODE = 'PMAC')
                                                  AND TO_CHAR(START_DATE, 'MON-RR') = TO_CHAR(:P_TRX_DATE, 'MON-RR'))) C
              ON INPUT.ORGANIZATION_ID = C.ORGANIZATION_ID
             AND INPUT.INPUT_ITEM_CODE = C.SEGMENT1
 WHERE C.SEGMENT1 IS NULL;
```

### Query to Check Missing `ITEM_COST`

This query checks if there are any `INPUT_ITEM_CODE` values from the main query that do not have corresponding entries in the `XXSRF.PFB_CONTRI_ITEM_AVG_COST` table.

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.INPUT_ITEM_CODE,
       INPUT.TRX_DATE
  FROM (  SELECT ORGANIZATION_ID,
                 INPUT_ITEM_CODE,
                 TRX_DATE
            FROM (  SELECT ORGANIZATION_ID,
                           ITEM_CODE AS INPUT_ITEM_CODE,
                           TRX_DATE
                      FROM XXSRF.JUMBO_MET_TRANSACTIONS
                     WHERE LINE_TYPE = -1
                           AND PROD_TYPE = 'JUMBO'
                           AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                           AND TRX_DATE = :P_TRX_DATE
                  GROUP BY ORGANIZATION_ID, ITEM_CODE, TRX_DATE)) INPUT
       LEFT JOIN (  SELECT ORGANIZATION_ID,
                          PRODUCT_TYPE,
                          ITEM_COST
                     FROM XXSRF.PFB_CONTRI_ITEM_AVG_COST
                    WHERE ORGANIZATION_ID = :P_ORGANIZATION_ID
                      AND TRX_DATE = TRUNC(LAST_DAY(:P_TRX_DATE))
                      AND ITEM_CATEGORY = 'NHP') D
              ON INPUT.ORGANIZATION_ID = D.ORGANIZATION_ID
             AND SUBSTR(INPUT.INPUT_ITEM_CODE, 1, INSTR(INPUT.INPUT_ITEM_CODE, '-') - 1) = D.PRODUCT_TYPE
 WHERE D.ITEM_COST IS NULL;
```

### Combined Query for Better Overview

Combining the checks into a single query to get a comprehensive view of missing costs for each `INPUT_ITEM_CODE`.

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.INPUT_ITEM_CODE,
       INPUT.TRX_DATE,
       C.CUR_COST,
       D.ITEM_COST
  FROM (  SELECT ORGANIZATION_ID,
                 INPUT_ITEM_CODE,
                 TRX_DATE
            FROM (  SELECT ORGANIZATION_ID,
                           ITEM_CODE AS INPUT_ITEM_CODE,
                           TRX_DATE
                      FROM XXSRF.JUMBO_MET_TRANSACTIONS
                     WHERE LINE_TYPE = -1
                           AND PROD_TYPE = 'JUMBO'
                           AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                           AND TRX_DATE = :P_TRX_DATE
                  GROUP BY ORGANIZATION_ID, ITEM_CODE, TRX_DATE)) INPUT
       LEFT JOIN (  SELECT MSI.SEGMENT1,
                          OOD.ORGANIZATION_ID,
                          SUM (CMPNT_COST) AS CUR_COST
                     FROM APPS.CM_CMPT_DTL_VW C,
                          APPS.MTL_SYSTEM_ITEMS MSI,
                          APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                    WHERE C.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                          AND MSI.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
                          AND OOD.OPERATING_UNIT = :P_ORG_ID
                          AND PERIOD_ID = (SELECT PERIOD_ID
                                             FROM APPS.GMF_PERIOD_STATUSES A,
                                                  APPS.HR_OPERATING_UNITS B
                                            WHERE B.ORGANIZATION_ID = :P_ORG_ID
                                                  AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                                                  AND COST_TYPE_ID IN (SELECT COST_TYPE_ID
                                                                         FROM APPS.CM_MTHD_MST
                                                                        WHERE COST_MTHD_CODE = 'PMAC')
                                                  AND TO_CHAR(START_DATE, 'MON-RR') = TO_CHAR(:P_TRX_DATE, 'MON-RR'))
                    GROUP BY MSI.SEGMENT1,
                             OOD.ORGANIZATION_ID) C
              ON INPUT.ORGANIZATION_ID = C.ORGANIZATION_ID
             AND INPUT.INPUT_ITEM_CODE = C.SEGMENT1
       LEFT JOIN (  SELECT ORGANIZATION_ID,
                          PRODUCT_TYPE,
                          ITEM_COST
                     FROM XXSRF.PFB_CONTRI_ITEM_AVG_COST
                    WHERE ORGANIZATION_ID = :P_ORGANIZATION_ID
                      AND TRX_DATE = TRUNC(LAST_DAY(:P_TRX_DATE))
                      AND ITEM_CATEGORY = 'NHP') D
              ON INPUT.ORGANIZATION_ID = D.ORGANIZATION_ID
             AND SUBSTR(INPUT.INPUT_ITEM_CODE, 1, INSTR(INPUT.INPUT_ITEM_CODE, '-') - 1) = D.PRODUCT_TYPE
 WHERE C.CUR_COST IS NULL OR D.ITEM_COST IS NULL;
```

### Explanation

- **`CUR_COST IS NULL`**: Indicates the missing cost from `APPS.CM_CMPT_DTL_VW`.
- **`ITEM_COST IS NULL`**: Indicates the missing cost from `XXSRF.PFB_CONTRI_ITEM_AVG_COST`.
- **`NVL` Usage**: `NVL(C.CUR_COST, D.ITEM_COST)` ensures that if `CUR_COST` is null, `ITEM_COST` is used and vice versa.

By running these queries, you can identify the missing cost data for specific `INPUT_ITEM_CODE` values and take appropriate steps to update or correct the cost data in your source tables.