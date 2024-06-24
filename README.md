------------------------------------------------------------------------------------------------------------------
-----------------------------------------   RECIPE, RM QTY and RM COST DETAILS--------------------------------------
--------------------------------------------------------------------------------------------------------------------
--INSERT INTO XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA (ORGANIZATION_ID,
--                                                RECIPE_NO,
--                                                RECIPE_VERSION,
--                                                FORMULA_NO,
--                                                FORMULA_VERS,
--                                                FG_ITEM_CODE,
--                                                JUMBO_ITEM_CODE,
--                                                MET_FILM,
--                                                TRX_DATE,
--                                                PERCENTAGE,
--                                                RM_CUR_VALUE,
--                                                HOMOPOLYMER_COST)
    WITH
        TAB
        AS
            (SELECT GR.CREATION_ORGANIZATION_ID     ORGANIZATION_ID,
                    GR.RECIPE_ID,
                    GR.RECIPE_NO,
                    GR.RECIPE_VERSION,
                    GT.ROUTING_NO,
                    FM.FORMULA_NO,
                    FM.FORMULA_VERS,
                    FD.LINE_TYPE,
                    IM.INVENTORY_ITEM_ID,
                    IM1.SEGMENT1                    FG_ITEM_CODE,
                    IM.SEGMENT1                     RM_ITEM_CODE,
                    IM.DESCRIPTION,
                    INVENTORY.SEGMENT1              INV_SEGMENT1,
                    INVENTORY.SEGMENT2              INV_SEGMENT2,
                    INVENTORY.SEGMENT3              INV_SEGMENT3,
                    INVENTORY.SEGMENT4              INV_SEGMENT4,
                    FD.QTY                          PLAN_QTY,
                    FD.SCRAP_FACTOR
               FROM APPS.GMD_RECIPES                GR,
                    APPS.GMD_ROUTINGS               GT,
                    APPS.FM_FORM_MST                FM,
                    APPS.FM_MATL_DTL                FD,
                    APPS.MTL_SYSTEM_ITEMS_B         IM,
                    APPS.GMD_RECIPE_VALIDITY_RULES  GRV,
                    APPS.MTL_SYSTEM_ITEMS_B         IM1,
                    (SELECT MIC.ORGANIZATION_ID,
                            MIC.INVENTORY_ITEM_ID,
                            MCV.SEGMENT1,
                            MCV.SEGMENT2,
                            MCV.SEGMENT3,
                            MCV.SEGMENT4
                       FROM APPS.MTL_ITEM_CATEGORIES  MIC,
                            APPS.MTL_CATEGORY_SETS    MCS,
                            APPS.MTL_CATEGORIES_VL    MCV
                      WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID --(112, 240, 1036)
                            AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                            AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                            AND MCS.CATEGORY_SET_NAME = 'Inventory') INVENTORY
              WHERE     FM.FORMULA_ID = FD.FORMULA_ID
                    AND GR.FORMULA_ID = FM.FORMULA_ID
                    AND GT.ROUTING_ID = GR.ROUTING_ID
                    AND GR.CREATION_ORGANIZATION_ID IN (1036)
                    AND GR.RECIPE_STATUS = 700
                    AND FM.FORMULA_STATUS = 700
                    AND GRV.VALIDITY_RULE_STATUS = 700
                    AND IM.ORGANIZATION_ID = FD.ORGANIZATION_ID
                    AND IM.INVENTORY_ITEM_ID = FD.INVENTORY_ITEM_ID
                    AND GR.RECIPE_ID = GRV.RECIPE_ID
                    AND GR.CREATION_ORGANIZATION_ID = GRV.ORGANIZATION_ID
                    AND GRV.ORGANIZATION_ID = IM1.ORGANIZATION_ID
                    AND GRV.INVENTORY_ITEM_ID = IM1.INVENTORY_ITEM_ID
                    AND INVENTORY.ORGANIZATION_ID = IM.ORGANIZATION_ID
                    AND INVENTORY.INVENTORY_ITEM_ID = IM.INVENTORY_ITEM_ID
                    AND GT.ROUTING_NO LIKE '%J%'
                    AND FD.LINE_TYPE = '-1')
      SELECT ORGANIZATION_ID,
             RECIPE_NO,
             RECIPE_VERSION,
             FORMULA_NO,
             FORMULA_VERS,
             FG_ITEM_CODE,
             JUMBO_ITEM_CODE,
             MET_FILM,
             TRX_DATE,
             PERCENTAGE,
             SUM (RM_CUR_VALUE)     RM_CUR_VALUE,
             HOMOPOLYMER_COST
        --       XXSRF.FN_PFB_GET_ITEM_COST (ORGANIZATION_ID, TRX_DATE, 'BOP', 'NHP') HOMOPOLYMER_COST
        FROM (SELECT A.ORGANIZATION_ID,
                     B.RECIPE_NO,
                     B.RECIPE_VERSION,
                     B.FORMULA_NO,
                     B.FORMULA_VERS,
                     A.FG_ITEM_CODE,
                     A.JUMBO_ITEM_CODE,
                     A.MET_FILM,
                     B.RM_ITEM_CODE,
                     B.INVENTORY_ITEM_ID                                           RM_INVENTORY_ITEM_ID,
                     B.DESCRIPTION,
                     B.INV_SEGMENT1,
                     B.INV_SEGMENT2,
                     B.INV_SEGMENT3,
                     B.INV_SEGMENT4,
                     TRUNC (LAST_DAY ( :P_DATE))                                   TRX_DATE,
                     B.PLAN_QTY,
                     A.PERCENTAGE,
                     C.CUR_COST,
                     CASE WHEN B.RM_ITEM_CODE LIKE '%RE%CHIP%'
                          THEN ROUND(D.ITEM_COST, 2)
                          ELSE ROUND(NVL (C.CUR_COST, D.ITEM_COST), 2)
                     END  RM_CUR_COST,
                     ROUND(B.PLAN_QTY * A.PERCENTAGE * CASE WHEN B.RM_ITEM_CODE LIKE '%RE%CHIP%'
                                                            THEN D.ITEM_COST
                                                            ELSE NVL (C.CUR_COST, D.ITEM_COST)
                                                       END, 2) RM_CUR_VALUE,
                     D.ITEM_COST HOMOPOLYMER_COST
                FROM XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP A,
                     (SELECT *
                        FROM TAB X
                       WHERE     1 = 1     --B.FG_ITEM_CODE = 'NCL28-TI/A09_J'
                             AND RECIPE_ID =
                                 (SELECT MAX (RECIPE_ID)
                                    FROM TAB Y
                                   WHERE X.ORGANIZATION_ID = Y.ORGANIZATION_ID
                                     AND X.FG_ITEM_CODE = Y.FG_ITEM_CODE)) B,
                     (  SELECT MSI.INVENTORY_ITEM_ID,
                               MSI.SEGMENT1,
                               OOD.ORGANIZATION_ID,
                               SUM (CMPNT_COST)     CUR_COST
                          FROM APPS.CM_CMPT_DTL_VW            C,
                               APPS.MTL_PARAMETERS            MTP,
                               APPS.ORG_ORGANIZATION_DEFINITIONS OOD,
                               APPS.MTL_SYSTEM_ITEMS          MSI
                         WHERE     1 = 1
                               AND C.ORGANIZATION_ID = MTP.ORGANIZATION_ID
                               AND MTP.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                               AND MSI.ORGANIZATION_ID = MTP.ORGANIZATION_ID
                               AND MSI.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID
                               AND PROCESS_ENABLED_FLAG = 'Y'
                               AND OOD.OPERATING_UNIT = :P_ORG_ID
                               AND MTP.ORGANIZATION_ID = NVL ( :P_ORGANIZATION_ID, MTP.ORGANIZATION_ID)
                               AND (DELETE_MARK = 0)
                               AND PERIOD_ID =
                                   (SELECT PERIOD_ID
                                      FROM APPS.GMF_PERIOD_STATUSES A,
                                           APPS.HR_OPERATING_UNITS B
                                     WHERE     B.ORGANIZATION_ID = :P_ORG_ID
                                           AND A.LEGAL_ENTITY_ID = B.DEFAULT_LEGAL_CONTEXT_ID
                                           AND COST_TYPE_ID IN
                                                   (SELECT COST_TYPE_ID
                                                      FROM APPS.CM_MTHD_MST
                                                     WHERE COST_MTHD_CODE = 'PMAC')
                                           AND TO_CHAR (START_DATE, 'MON-RR') = TO_CHAR ( :P_DATE, 'MON-RR'))
                               AND (SELECT COST_MTHD_CODE
                                      FROM APPS.CM_MTHD_MST
                                     WHERE COST_TYPE_ID = C.COST_TYPE_ID) IN
                                       (SELECT TAG
                                          FROM APPS.FND_LOOKUP_VALUES
                                         WHERE     LOOKUP_TYPE IN 'XXSRF_11I_R12_MAPPING_LOOKUP'
                                               AND ATTRIBUTE1 = 'SRF PFB Location Wise Stock Summary with Values(Raw Material)'
                                               AND MEANING IN ('COST-MTHD-1', 'COST-MTHD-2'))
                      GROUP BY MSI.INVENTORY_ITEM_ID,
                               MSI.SEGMENT1,
                               OOD.ORGANIZATION_ID) C,
                     (SELECT * 
                        FROM XXSRF.PFB_CONTRI_ITEM_AVG_COST
                       WHERE ORGANIZATION_ID = :P_ORGANIZATION_ID
                         AND TRX_DATE = TRUNC (LAST_DAY ( :P_DATE))
                         AND ITEM_CATEGORY = 'NHP') D         
               WHERE     A.ORGANIZATION_ID = B.ORGANIZATION_ID
                     AND A.JUMBO_ITEM_CODE = B.FG_ITEM_CODE
                     AND B.ORGANIZATION_ID = C.ORGANIZATION_ID(+)
                     AND B.INVENTORY_ITEM_ID = C.INVENTORY_ITEM_ID(+)
                     AND A.ORGANIZATION_ID = D.ORGANIZATION_ID
                     AND D.TRX_DATE = TRUNC (LAST_DAY (:P_DATE))
                     AND D.PRODUCT_TYPE = B.INV_SEGMENT2)
    GROUP BY ORGANIZATION_ID,
             RECIPE_NO,
             RECIPE_VERSION,
             FORMULA_NO,
             FORMULA_VERS,
             FG_ITEM_CODE,
             JUMBO_ITEM_CODE,
             MET_FILM,
             TRX_DATE,
             PERCENTAGE,
             HOMOPOLYMER_COST;
