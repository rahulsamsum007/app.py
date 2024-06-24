To calculate the `RM_CUR_VALUE` in your new query, you need to incorporate the logic for determining the current raw material value, similar to what was done in the original complex query. The key components required are:

1. Identifying the `RM_CUR_COST` for each `INPUT_ITEM_CODE`.
2. Calculating the `RM_CUR_VALUE` as `INPUT_QTY * RM_CUR_COST`.

Here's how you can add this to your existing query:

### Adding RM_CUR_VALUE Calculation

1. **Extracting Costs**:
   - You need to join with the necessary tables to get the current costs for each raw material item.
   - Ensure that you filter the costs based on the same conditions as before.

2. **Calculating RM_CUR_VALUE**:
   - Use the `INPUT_QTY` and the fetched `RM_CUR_COST` to compute the `RM_CUR_VALUE`.

### Modified Query

Here is your modified query with the `RM_CUR_VALUE` calculation:

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.PROD_TYPE,
       INPUT.TRX_DATE,
       INPUT.JUMBO_ITEM_CODE,
       INPUT.INPUT_ITEM_CODE,
       INPUT.INPUT_QTY,
       OUTPUT.OUTPUT_QTY,
       INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY AS PER_KG_QTY,
       ROUND(INPUT.INPUT_QTY * NVL(C.CUR_COST, D.ITEM_COST), 2) AS RM_CUR_VALUE
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

### Explanation

1. **LEFT JOIN for Current Cost (`C`)**:
   - The `C` subquery calculates the current cost (`CUR_COST`) for inventory items.
   - It joins based on `ORGANIZATION_ID` and `SEGMENT1` which matches the `INPUT_ITEM_CODE`.

2. **LEFT JOIN for Average Cost (`D`)**:
   - The `D` subquery fetches the average item cost (`ITEM_COST`) from the `XXSRF.PFB_CONTRI_ITEM_AVG_COST` table.
   - It joins based on `ORGANIZATION_ID` and product type extracted from `INPUT_ITEM_CODE`.

3. **Calculating `RM_CUR_VALUE`**:
   - The `RM_CUR_VALUE` is calculated using the `ROUND` function.
   - The formula used is `INPUT.INPUT_QTY * NVL(C.CUR_COST, D.ITEM_COST)` which multiplies the `INPUT_QTY` by the cost (preferring `CUR_COST` if available, otherwise `ITEM_COST`).

This modification ensures that `RM_CUR_VALUE` is calculated and included in the final result set based on the provided query structure and logic for fetching and computing the current raw material value.