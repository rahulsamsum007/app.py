To help diagnose and fix the issue, let's create a test SQL query that can isolate the problem area and provide insights into where adjustments are needed. We'll start by simplifying the query and focusing on retrieving relevant data related to `BOP-RE-CHIP` and other `INPUT_ITEM_CODE` values. This will help us pinpoint any discrepancies or issues with the join conditions or calculations.

### Test SQL Query to Identify Issues:

```sql
SELECT 
    JT.ORGANIZATION_ID,
    JT.PROD_TYPE,
    JT.TRX_DATE,
    JT.JUMBO_ITEM_CODE,
    JT.INPUT_ITEM_CODE,
    JT.INPUT_QTY,
    JT.OUTPUT_QTY,
    JT.PER_KG_QTY,
    ROUND(JT.PER_KG_QTY * NVL(C.CUR_COST, D.ITEM_COST), 2) AS RM_CUR_VALUE,
    C.CUR_COST,
    D.ITEM_COST
FROM 
    (
        SELECT 
            A.ORGANIZATION_ID,
            A.PROD_TYPE,
            A.TRX_DATE,
            A.JUMBO_ITEM_CODE,
            A.INPUT_ITEM_CODE,
            A.INPUT_QTY,
            B.OUTPUT_QTY,
            A.INPUT_QTY / B.OUTPUT_QTY AS PER_KG_QTY
        FROM 
            (
                SELECT 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    TRX_DATE,
                    JUMBO_ITEM_CODE,
                    INPUT_ITEM_CODE,
                    SUM(INPUT_QTY) AS INPUT_QTY
                FROM 
                    XXSRF.JUMBO_MET_TRANSACTIONS
                WHERE 
                    PROD_TYPE = 'JUMBO'
                    AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                    AND TRX_DATE = :P_TRX_DATE
                    AND INPUT_ITEM_CODE <> 'BOP-RE-CHIP'  -- Exclude BOP-RE-CHIP for testing
                GROUP BY 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    TRX_DATE,
                    JUMBO_ITEM_CODE,
                    INPUT_ITEM_CODE
            ) A
        LEFT JOIN 
            (
                SELECT 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    TRX_DATE,
                    ITEM_CODE AS JUMBO_ITEM_CODE,
                    SUM(TRX_QTY) AS OUTPUT_QTY
                FROM 
                    XXSRF.JUMBO_MET_TRANSACTIONS
                WHERE 
                    PROD_TYPE = 'JUMBO'
                    AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                    AND TRX_DATE = :P_TRX_DATE
                    AND ITEM_CODE = 'BOP-RE-CHIP'  -- Only for BOP-RE-CHIP for testing
                    AND LINE_TYPE = 1
                GROUP BY 
                    ORGANIZATION_ID,
                    PROD_TYPE,
                    TRX_DATE,
                    ITEM_CODE
            ) B ON A.ORGANIZATION_ID = B.ORGANIZATION_ID
                AND A.PROD_TYPE = B.PROD_TYPE
                AND A.TRX_DATE = B.TRX_DATE
                AND A.JUMBO_ITEM_CODE = B.JUMBO_ITEM_CODE
    ) JT
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
    ) C ON JT.ORGANIZATION_ID = C.ORGANIZATION_ID
        AND JT.INPUT_ITEM_CODE = C.SEGMENT1
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
    ) D ON JT.ORGANIZATION_ID = D.ORGANIZATION_ID
        AND D.PRODUCT_TYPE = SUBSTR(JT.INPUT_ITEM_CODE, 1, INSTR(JT.INPUT_ITEM_CODE, '-') - 1);
```

### Explanation of the Test Query:

1. **Subquery `A`**: 
   - Retrieves `INPUT_QTY` for all `INPUT_ITEM_CODE` values except `BOP-RE-CHIP` for testing purposes. This helps us verify if calculations are correct for other items.

2. **Subquery `B`**: 
   - Retrieves `OUTPUT_QTY` specifically for `BOP-RE-CHIP`. This is to ensure that calculations are correct when `BOP-RE-CHIP` is involved.

3. **Main Query (`JT`)**: 
   - Joins the results of `A` and `B` to calculate `PER_KG_QTY` and `RM_CUR_VALUE` based on `PER_KG_QTY` multiplied by the appropriate cost (`CUR_COST` from `C` or `ITEM_COST` from `D`).

4. **Joins (`C` and `D`)**: 
   - Ensure that `C` and `D` are joined correctly with `JT` based on `ORGANIZATION_ID` and `INPUT_ITEM_CODE`.

### Steps to Diagnose and Fix:

- **Run the Query**: Execute this test query with appropriate bind variables (`:P_ORGANIZATION_ID`, `:P_TRX_DATE`, etc.) to see the output.
  
- **Inspect Results**: Check the output to ensure that `RM_CUR_VALUE` is calculated correctly for different `INPUT_ITEM_CODE` values, especially `BOP-RE-CHIP` and others.

- **Adjust Joins and Conditions**: If `RM_CUR_VALUE` is not correct for all `INPUT_ITEM_CODE` values, adjust the joins (`LEFT JOIN`, `INNER JOIN`, etc.) and conditions in the main query (`JT`) to correctly associate `PER_KG_QTY` with the respective cost (`CUR_COST` or `ITEM_COST`).

- **Debugging SQL**: Use SQL logging or output to debug and verify each step of the calculation. Ensure that all join conditions are correctly matched and that aggregation (`SUM`, `GROUP BY`) is applied appropriately.

By following these steps, you should be able to identify where the issue lies in your SQL query and make the necessary adjustments to calculate `RM_CUR_VALUE` correctly for all `INPUT_ITEM_CODE` values. Adjustments may include refining join conditions, ensuring data availability (`C` and `D` tables), and verifying calculation logic (`PER_KG_QTY` and cost multiplication).