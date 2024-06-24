To include the `RM_CUR_VALUE` in the provided query, we need to ensure the calculations align with the previous query's logic. We will include the necessary joins and subqueries to compute `RM_CUR_VALUE` appropriately.

Here’s the revised query with `RM_CUR_VALUE` added:

```sql
SELECT INPUT.ORGANIZATION_ID,
       INPUT.PROD_TYPE,
       INPUT.TRX_DATE,
       INPUT.JUMBO_ITEM_CODE,
       INPUT.INPUT_ITEM_CODE,
       INPUT.INPUT_QTY,
       OUTPUT.OUTPUT_QTY,
       INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY AS PER_KG_QTY,
       RM_CUR.RM_CUR_VALUE
  FROM (  SELECT ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 JUMBO_ITEM_CODE,
                 INPUT_ITEM_CODE,
                 SUM (INPUT_QTY) AS INPUT_QTY
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
                                   AND A.PROD_TYPE = B.PROD_TYPE) AS JUMBO_ITEM_CODE,
                           ITEM_CODE AS INPUT_ITEM_CODE,
                           SUM (TRX_QTY) AS INPUT_QTY
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
       JOIN (  SELECT ORGANIZATION_ID,
                      PROD_TYPE,
                      LINE_TYPE,
                      TRX_DATE,
                      ITEM_CODE AS JUMBO_ITEM_CODE,
                      SUM (TRX_QTY) AS OUTPUT_QTY
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
          ON     INPUT.ORGANIZATION_ID = OUTPUT.ORGANIZATION_ID
             AND INPUT.PROD_TYPE = OUTPUT.PROD_TYPE
             AND INPUT.TRX_DATE = OUTPUT.TRX_DATE
             AND INPUT.JUMBO_ITEM_CODE = OUTPUT.JUMBO_ITEM_CODE
       LEFT JOIN (  SELECT B.ORGANIZATION_ID,
                           B.FG_ITEM_CODE AS JUMBO_ITEM_CODE,
                           B.RM_ITEM_CODE AS INPUT_ITEM_CODE,
                           SUM (ROUND(B.PLAN_QTY * A.PERCENTAGE * CASE WHEN B.RM_ITEM_CODE LIKE '%RE%CHIP%'
                                                                      THEN D.ITEM_COST
                                                                      ELSE NVL (C.CUR_COST, D.ITEM_COST)
                                                                 END, 2)) AS RM_CUR_VALUE
                      FROM XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP A
                           JOIN TAB B ON A.ORGANIZATION_ID = B.ORGANIZATION_ID
                                      AND A.JUMBO_ITEM_CODE = B.FG_ITEM_CODE
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
                                               AND MTP.ORGANIZATION_ID = NVL (:P_ORGANIZATION_ID, MTP.ORGANIZATION_ID)
                                               AND (DELETE_MARK = 0)
                                               AND PERIOD_ID = (SELECT PERIOD_ID
                                                                  FROM APPS.GMF_PERIOD_STATUSES A,
                                                                       APPS.HR_OPERATING_UNITS B
                                                                 WHERE     B.ORGANIZATION_ID = :P_ORG_ID
                                                                       AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                                                                       AND COST_TYPE_ID IN (SELECT COST_TYPE_ID
                                                                                              FROM APPS.CM_MTHD_MST
                                                                                             WHERE COST_MTHD_CODE = 'PMAC')
                                                                       AND TO_CHAR (START_DATE, 'MON-RR') = TO_CHAR (:P_DATE, 'MON-RR'))
                                               AND (SELECT COST_MTHD_CODE
                                                      FROM APPS.CM_MTHD_MST
                                                     WHERE COST_TYPE_ID = C.COST_TYPE_ID) IN (SELECT TAG
                                                                                                FROM APPS.FND_LOOKUP_VALUES
                                                                                               WHERE     LOOKUP_TYPE IN 'XXSRF_11I_R12_MAPPING_LOOKUP'
                                                                                                     AND ATTRIBUTE1 = 'SRF PFB Location Wise Stock Summary with Values(Raw Material)'
                                                                                                     AND MEANING IN ('COST-MTHD-1', 'COST-MTHD-2'))
                                      GROUP BY MSI.INVENTORY_ITEM_ID, MSI.SEGMENT1, OOD.ORGANIZATION_ID) C
                              ON B.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
                             AND B.ORGANIZATION_ID = C.ORGANIZATION_ID
                           LEFT JOIN (SELECT *
                                        FROM XXSRF.PFB_CONTRI_ITEM_AVG_COST
                                       WHERE ORGANIZATION_ID = :P_ORGANIZATION_ID
                                         AND TRX_DATE = TRUNC (LAST_DAY (:P_DATE))
                                         AND ITEM_CATEGORY = 'NHP') D
                              ON B.INVENTORY_ITEM_ID = D.INVENTORY_ITEM_ID
                             AND B.ORGANIZATION_ID = D.ORGANIZATION_ID
                             AND D.TRX_DATE = TRUNC (LAST_DAY (:P_DATE))
                   GROUP BY B.ORGANIZATION_ID, B.FG_ITEM_CODE, B.RM_ITEM_CODE) RM_CUR
          ON INPUT.ORGANIZATION_ID = RM_CUR.ORGANIZATION_ID
         AND INPUT.JUMBO_ITEM_CODE = RM_CUR.JUMBO_ITEM_CODE
         AND INPUT.INPUT_ITEM_CODE = RM_CUR.INPUT_ITEM_CODE
```

### Key Points:
1. **Subquery for `RM_CUR_VALUE` Calculation**:
   - This subquery computes `RM_CUR_VALUE` using similar logic to your previous query, including necessary joins with cost-related tables.

2. **Joins**:
   - The main query joins `INPUT`, `OUTPUT`, and the new subquery `RM_CUR` to include the calculated `RM_CUR_VALUE`.

3. **Grouping and Summarizing**:
   - The query ensures data is grouped and summarized properly to provide accurate results for `INPUT_QTY`, `OUTPUT_QTY`, and `RM_CUR_VALUE`.

This structure keeps the original logic intact while incorporating the additional calculation for `RM_CUR_VALUE`. Ensure you replace `:P_ORGANIZATION_ID`, `:P_TRX_DATE`, `:P_ORG_ID`, and `:P_DATE` with appropriate values or parameters as needed.