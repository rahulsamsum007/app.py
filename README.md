Based on the output you've shared and the SQL query provided earlier, it seems like the issue lies in how the join conditions are structured. Specifically, you want to calculate `RM_CUR_VALUE` for all `INPUT_ITEM_CODE` values, not just for `BOP-RE-CHIP`. 

Let's adjust the query to ensure that `RM_CUR_VALUE` is calculated for all `INPUT_ITEM_CODE` values:

```sql
SELECT 
    INPUT.ORGANIZATION_ID,
    INPUT.PROD_TYPE,
    INPUT.TRX_DATE,
    INPUT.JUMBO_ITEM_CODE,
    INPUT.INPUT_ITEM_CODE,
    INPUT.INPUT_QTY,
    OUTPUT.OUTPUT_QTY,
    INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY AS PER_KG_QTY,
    ROUND((INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY) * NVL(C.CUR_COST, D.ITEM_COST), 2) AS RM_CUR_VALUE,
    C.CUR_COST,
    D.ITEM_COST
FROM 
    (
        SELECT 
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            JUMBO_ITEM_CODE,
            INPUT_ITEM_CODE,
            SUM(INPUT_QTY) AS INPUT_QTY
        FROM 
            (
                SELECT 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    LINE_TYPE,
                    TRX_DATE,
                    BATCH_NO,
                    (
                        SELECT DISTINCT ITEM_CODE
                        FROM XXSRF.JUMBO_MET_TRANSACTIONS B
                        WHERE A.ORGANIZATION_ID = B.ORGANIZATION_ID
                            AND A.BATCH_NO = B.BATCH_NO
                            AND A.TRX_DATE = B.TRX_DATE
                            AND A.PROD_TYPE = B.PROD_TYPE
                            AND LINE_TYPE = 1 -- Assuming this is the correct condition for output
                    ) AS JUMBO_ITEM_CODE,
                    ITEM_CODE AS INPUT_ITEM_CODE,
                    SUM(TRX_QTY) AS INPUT_QTY
                FROM 
                    XXSRF.JUMBO_MET_TRANSACTIONS A
                WHERE 
                    LINE_TYPE IN (-1, 1) -- Adjust this to correctly capture both inputs and outputs
                    AND PROD_TYPE = 'JUMBO'
                    AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                    AND TRX_DATE = :P_TRX_DATE
                GROUP BY 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    LINE_TYPE,
                    TRX_DATE,
                    BATCH_NO,
                    ITEM_CODE
            ) INPUT_DATA
        GROUP BY 
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            JUMBO_ITEM_CODE,
            INPUT_ITEM_CODE
    ) INPUT
LEFT JOIN 
    (
        SELECT 
            MSI.INVENTORY_ITEM_ID,
            MSI.SEGMENT1,
            OOD.ORGANIZATION_ID,
            SUM(CMPNT_COST) AS CUR_COST
        FROM 
            APPS.CM_CMPT_DTL_VW C,
            APPS.MTL_PARAMETERS MTP,
            APPS.ORG_ORGANIZATION_DEFINITIONS OOD,
            APPS.MTL_SYSTEM_ITEMS MSI
        WHERE 
            C.ORGANIZATION_ID = MTP.ORGANIZATION_ID
            AND MTP.ORGANIZATION_ID = OOD.ORGANIZATION_ID
            AND MSI.ORGANIZATION_ID = MTP.ORGANIZATION_ID
            AND MSI.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
            AND PROCESS_ENABLED_FLAG = 'Y'
            AND OOD.OPERATING_UNIT = :P_ORG_ID
            AND MTP.ORGANIZATION_ID = NVL(:P_ORGANIZATION_ID, MTP.ORGANIZATION_ID)
            AND DELETE_MARK = 0
            AND PERIOD_ID = (
                SELECT 
                    PERIOD_ID
                FROM 
                    APPS.GMF_PERIOD_STATUSES A,
                    APPS.HR_OPERATING_UNITS B
                WHERE 
                    B.ORGANIZATION_ID = :P_ORG_ID
                    AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                    AND COST_TYPE_ID IN (
                        SELECT 
                            COST_TYPE_ID
                        FROM 
                            APPS.CM_MTHD_MST
                        WHERE 
                            COST_MTHD_CODE = 'PMAC'
                    )
                    AND TO_CHAR(START_DATE, 'MON-RR') = TO_CHAR(:P_TRX_DATE, 'MON-RR')
            )
            AND (
                SELECT 
                    COST_MTHD_CODE
                FROM 
                    APPS.CM_MTHD_MST
                WHERE 
                    COST_TYPE_ID = C.COST_TYPE_ID
            ) IN (
                SELECT 
                    TAG
                FROM 
                    APPS.FND_LOOKUP_VALUES
                WHERE 
                    LOOKUP_TYPE = 'XXSRF_11I_R12_MAPPING_LOOKUP'
                    AND ATTRIBUTE1 = 'SRF PFB Location Wise Stock Summary with Values(Raw Material)'
                    AND MEANING IN ('COST-MTHD-1', 'COST-MTHD-2')
            )
        GROUP BY 
            MSI.INVENTORY_ITEM_ID,
            MSI.SEGMENT1,
            OOD.ORGANIZATION_ID
    ) C ON INPUT.ORGANIZATION_ID = C.ORGANIZATION_ID
        AND INPUT.INPUT_ITEM_CODE = C.SEGMENT1
LEFT JOIN 
    (
        SELECT 
            *
        FROM 
            XXSRF.PFB_CONTRI_ITEM_AVG_COST
        WHERE 
            ORGANIZATION_ID = :P_ORGANIZATION_ID
            AND TRX_DATE = TRUNC(LAST_DAY(:P_TRX_DATE))
            AND ITEM_CATEGORY = 'NHP'
    ) D ON INPUT.ORGANIZATION_ID = D.ORGANIZATION_ID
        AND D.PRODUCT_TYPE = SUBSTR(INPUT.INPUT_ITEM_CODE, 1, INSTR(INPUT.INPUT_ITEM_CODE, '-') - 1)
LEFT JOIN 
    (
        SELECT 
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            ITEM_CODE AS JUMBO_ITEM_CODE,
            SUM(TRX_QTY) AS OUTPUT_QTY
        FROM 
            XXSRF.JUMBO_MET_TRANSACTIONS A
        WHERE 
            LINE_TYPE = 1 -- Assuming this is the correct condition for output
            AND PROD_TYPE = 'JUMBO'
            AND ORGANIZATION_ID = :P_ORGANIZATION_ID
            AND TRX_DATE = :P_TRX_DATE
        GROUP BY 
            ORGANIZATION_ID,
            PROD_TYPE,
            LINE_TYPE,
            TRX_DATE,
            ITEM_CODE
    ) OUTPUT ON INPUT.ORGANIZATION_ID = OUTPUT.ORGANIZATION_ID
        AND INPUT.PROD_TYPE = OUTPUT.PROD_TYPE
        AND INPUT.TRX_DATE = OUTPUT.TRX_DATE
        AND INPUT.JUMBO_ITEM_CODE = OUTPUT.JUMBO_ITEM_CODE;
```

### Explanation and Adjustments:
1. **Subquery Adjustments**: 
   - Ensure that the subquery (`INPUT_DATA`) correctly sums up `INPUT_QTY` for each `INPUT_ITEM_CODE`.
   - Adjust `LINE_TYPE` condition in the subquery to correctly capture both input and output transactions.

2. **LEFT JOINs**: 
   - Ensure all `INPUT_ITEM_CODE` values are considered by joining `INPUT` with the `C` and `D` tables appropriately.
   - Make sure to join `INPUT` with `OUTPUT` on all key columns (`ORGANIZATION_ID`, `PROD_TYPE`, `TRX_DATE`, `JUMBO_ITEM_CODE`).

3. **Calculation**: 
   - `RM_CUR_VALUE` calculation remains the same: multiply `PER_KG_QTY` by the cost (`CUR_COST` or `ITEM_COST`) and round it to two decimal places.

### Debugging Tips:
- **Check Join Conditions**: Verify that all join conditions are correctly matching columns from `INPUT` with corresponding columns from `C`, `D`, and `OUTPUT`.
- **Data Integrity**: Ensure that data exists in `C` and `D` tables for all `INPUT_ITEM_CODE` values on the given `TRX_DATE`.
- **SQL Execution**: Execute the SQL query step-by-step to identify where the filtering or joining might be incorrect.