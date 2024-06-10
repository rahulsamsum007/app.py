CREATE TABLE XXSRF.PFB_CONTRI_ITEM_AVG_COST (ORGANIZATION_ID  NUMBER,
											   TRX_DATE         DATE,
											   PRODUCT_TYPE     VARCHAR2(100),
											   ITEM_CODE        VARCHAR2(100),
											   ITEM_CATEGORY    VARCHAR2(100),
											   ITEM_COST        NUMBER,
											   INSERT_DATE      DATE    DEFAULT SYSDATE);
------------------------------------------------------------------------------------------------------------------
--------------------------------------   INSERT HOMOPOLYMER COST -------------------------------------------------			 
------------------------------------------------------------------------------------------------------------------

SET SERVEROUTPUT ON;

DECLARE
    V_COST              NUMBER;
    V_ORGANIZATION_ID   NUMBER := 1036;
    V_DATE              DATE := '30-NOV-2023';
    V_PRODUCT_TYPE      VARCHAR2 (100) := 'BOP';
    V_ITEM_CODE         VARCHAR2 (100);
    V_ITEM_CATEGORY     VARCHAR2 (100) := 'NHP';
BEGIN
    DELETE FROM
        XXSRF.PFB_CONTRI_ITEM_AVG_COST
          WHERE     ORGANIZATION_ID = V_ORGANIZATION_ID
                AND TRX_DATE = TRUNC (LAST_DAY (V_DATE))
                AND PRODUCT_TYPE = V_PRODUCT_TYPE
                AND NVL (ITEM_CODE, 'ITEM_CODE') = NVL (V_ITEM_CODE, 'ITEM_CODE')
                AND NVL (ITEM_CATEGORY, 'ITEM_CATEGORY') = NVL (V_ITEM_CATEGORY, 'ITEM_CATEGORY');


    V_COST := XXSRF.FN_PFB_GET_ITEM_COST (V_ORGANIZATION_ID,
                                          TRUNC (LAST_DAY (V_DATE)),
                                          V_PRODUCT_TYPE,
                                          V_ITEM_CATEGORY);

    DBMS_OUTPUT.PUT_LINE (V_DATE || '     ' || V_COST);

    INSERT INTO XXSRF.PFB_CONTRI_ITEM_AVG_COST (ORGANIZATION_ID,
                                                TRX_DATE,
                                                PRODUCT_TYPE,
                                                ITEM_CATEGORY,
                                                ITEM_COST)
         VALUES (V_ORGANIZATION_ID,
                 TRUNC (LAST_DAY (V_DATE)),
                 V_PRODUCT_TYPE,
                 V_ITEM_CATEGORY,
                 V_COST);

    COMMIT;
END;
------------------------------------------------------------------------------------------------------------------


CREATE TABLE XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP
(
  ORGANIZATION_ID  NUMBER,
  PRODUCT_TYPE     VARCHAR2(100 BYTE),
  ITEM_GROUP       VARCHAR2(100 BYTE),
  FG_ITEM_CODE     VARCHAR2(100 BYTE),
  JUMBO_ITEM_CODE  VARCHAR2(100 BYTE),
  MET_FILM		   VARCHAR2(10),
  PERCENTAGE       NUMBER,
  CONSTRAINT UK_PFB_CONTRI_JUMBO_FG_ITEM_MAP
  UNIQUE (ORGANIZATION_ID, FG_ITEM_CODE, JUMBO_ITEM_CODE)
);

------------------------------------------------------------------------------------------------------------------
CREATE TABLE XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA
(
  ORGANIZATION_ID       NUMBER,
  RECIPE_NO             VARCHAR2(100 BYTE),
  RECIPE_VERSION        NUMBER,
  FORMULA_NO            VARCHAR2(100 BYTE),
  FORMULA_VERS          NUMBER,
  FG_ITEM_CODE          VARCHAR2(100 BYTE),
  JUMBO_ITEM_CODE       VARCHAR2(100 BYTE),
  RM_ITEM_CODE          VARCHAR2(100 BYTE),
  RM_INVENTORY_ITEM_ID  NUMBER,
  DESCRIPTION           VARCHAR2(240 BYTE),
  INV_SEGMENT1          VARCHAR2(100 BYTE),
  INV_SEGMENT2          VARCHAR2(100 BYTE),
  INV_SEGMENT3          VARCHAR2(100 BYTE),
  INV_SEGMENT4          VARCHAR2(100 BYTE),
  TRX_DATE              DATE,
  PLAN_QTY              NUMBER,
  PERCENTAGE            NUMBER,
  RM_CUR_COST           NUMBER,
  RM_CUR_VALUE          NUMBER,
  INSERT_DATE           DATE                    DEFAULT SYSDATE
);

------------------------------------------------------------------------------------------------------------------
---------------------------------------   RECIPE, RM QTY and RM COST DETAILS--------------------------------------
------------------------------------------------------------------------------------------------------------------
INSERT INTO XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA (ORGANIZATION_ID,
                                                RECIPE_NO,
                                                RECIPE_VERSION,
                                                FORMULA_NO,
                                                FORMULA_VERS,
                                                FG_ITEM_CODE,
                                                JUMBO_ITEM_CODE,
                                                MET_FILM,
                                                TRX_DATE,
                                                PERCENTAGE,
                                                RM_CUR_VALUE,
                                                HOMOPOLYMER_COST)
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

------------------------------------------------------------------------------------------------------------------
--------------------------------------   UPDATE HOMOPOLYMER COST -------------------------------------------------			 
------------------------------------------------------------------------------------------------------------------

SET SERVEROUTPUT ON;

DECLARE
    V_COST              NUMBER;
    V_ORGANIZATION_ID   NUMBER := 1036;
    V_DATE              DATE := '30-NOV-2023';
BEGIN
    V_COST :=
        XXSRF.FN_PFB_GET_ITEM_COST (V_ORGANIZATION_ID,
                                    TRUNC (LAST_DAY (V_DATE)),
                                    'BOP',
                                    'NHP');

    DBMS_OUTPUT.PUT_LINE (V_DATE || '     ' || V_COST);

    UPDATE XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA
       SET HOMOPOLYMER_COST = V_COST
     WHERE     ORGANIZATION_ID = V_ORGANIZATION_ID
           AND TRUNC (TRX_DATE) = TRUNC (LAST_DAY (V_DATE));

    COMMIT;
END;
------------------------------------------------------------------------------------------------------------------
--------------------------------------   JUMBO & MET PRODUCTION TIME AND QUANTITY --------------------------------
------------------------------------------------------------------------------------------------------------------

INSERT INTO XXSRF.PFB_CONTRI_PRODUCTION_DATA (ORGANIZATION_ID,
                                              PROD_TYPE,
                                              TRX_DATE,
                                              PRODUCT_TYPE,
                                              ITEM_CODE,
                                              MICRON,
                                              PROD_TIME,
                                              PROD_QTY) 
  SELECT ORGANIZATION_ID,
         'JUMBO'                              PROD_TYPE,
         LAST_DAY (TRX_DATE)                  TRX_DATE,
         PRODUCT_TYPE,
         ITEM_CODE,
         MICRON,
         ROUND (SUM (PRODUCTION_TIME), 2)     PRODUCTION_TIME,
         SUM (TRX_QTY)                        TRX_QTY
    FROM (  SELECT GBH.ORGANIZATION_ID,
                   GBH.BATCH_NO,
                   TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS') START_DATE,
                   TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS') END_DATE,
                   (TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS') - TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS')) * 24 PRODUCTION_TIME,
                   DECODE (GBH.ORGANIZATION_ID, 112, 'PET',
                                                280, 'BOP',
                                                1640, 'PET',
                                                NVL (INVENTORY.SEGMENT2, 'PET')) PRODUCT_TYPE,
                   ICMB.SEGMENT1 ITEM_CODE,
                   TO_NUMBER (ICMB.ATTRIBUTE1) MICRON,
                   MTLN.GRADE_CODE,
                   TRUNC (MMT.TRANSACTION_DATE) TRX_DATE,
                   SUM (MMT.TRANSACTION_QUANTITY) TRX_QTY
              FROM APPS.GME_MATERIAL_DETAILS      GMD,
                   APPS.GME_BATCH_HEADER          GBH,
                   APPS.FM_ROUT_HDR               FRH,
                   APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                   APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                   APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN,
                   (SELECT MIC.ORGANIZATION_ID,
                           MIC.INVENTORY_ITEM_ID,
                           MCV.SEGMENT2
                      FROM APPS.MTL_ITEM_CATEGORIES MIC,
                           APPS.MTL_CATEGORY_SETS MCS,
                           APPS.MTL_CATEGORIES_VL MCV
                     WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID --(112, 240, 1036)
                           AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                           AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                           AND MCS.CATEGORY_SET_NAME = 'Inventory') INVENTORY
             WHERE     TRUNC (MMT.TRANSACTION_DATE) BETWEEN TRUNC (:P_DATE_FROM, 'MON') AND :P_DATE
                   AND LINE_TYPE = 1
                   AND GMD.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                   AND GMD.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                   AND GMD.BATCH_ID = GBH.BATCH_ID
                   AND GBH.ORGANIZATION_ID = FRH.OWNER_ORGANIZATION_ID
                   AND GBH.ROUTING_ID = FRH.ROUTING_ID
                   AND GBH.ORGANIZATION_ID = :P_ORGANIZATION_ID
                   AND FRH.ROUTING_NO LIKE '%J%'
                   AND ITEM_TYPE = 'FILM'
                   AND GBH.ORGANIZATION_ID = MMT.ORGANIZATION_ID
                   AND GMD.MATERIAL_DETAIL_ID = MMT.TRX_SOURCE_LINE_ID
                   AND GMD.BATCH_ID = MMT.TRANSACTION_SOURCE_ID
                   AND GMD.INVENTORY_ITEM_ID = MMT.INVENTORY_ITEM_ID
                   AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                   AND MMT.TRANSACTION_TYPE_ID IN (44, 17)
                   AND MMT.ORGANIZATION_ID = MTLN.ORGANIZATION_ID
                   AND MTLN.TRANSACTION_ID = MMT.TRANSACTION_ID
                   AND MMT.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                   AND INVENTORY.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                   AND INVENTORY.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                   AND INVENTORY.SEGMENT2 = 'BOP'
          GROUP BY GBH.ORGANIZATION_ID,
                   GBH.BATCH_NO,
                   TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS'),
                   TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS'),
                   DECODE (GBH.ORGANIZATION_ID, 112, 'PET',
                                                280, 'BOP',
                                                1640, 'PET',
                                                NVL (INVENTORY.SEGMENT2, 'PET')),
                   ICMB.SEGMENT1,
                   TO_NUMBER (ICMB.ATTRIBUTE1),
                   MTLN.GRADE_CODE,
                   TRUNC (MMT.TRANSACTION_DATE))
GROUP BY ORGANIZATION_ID,
         PRODUCT_TYPE,
         ITEM_CODE,
         MICRON,
         LAST_DAY (TRX_DATE)
UNION ALL
  SELECT ORGANIZATION_ID,
         'MET'                                PROD_TYPE,
         LAST_DAY (TRX_DATE)                  TRX_DATE,
         PRODUCT_TYPE,
         ITEM_CODE,
         MICRON,
         TO_NUMBER(TO_CHAR(LAST_DAY (TRX_DATE), 'DD')) * 24 PRODUCTION_TIME,  
--         ROUND (SUM (PRODUCTION_TIME), 2)     PRODUCTION_TIME,
         SUM (TRX_QTY)                        TRX_QTY
    FROM (  SELECT GBH.ORGANIZATION_ID,
                   GBH.BATCH_NO,
                   TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS') START_DATE,
                   TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS') END_DATE,
                   (TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS') - TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS')) * 24 PRODUCTION_TIME,
                   DECODE (GBH.ORGANIZATION_ID, 112, 'PET',
                                                280, 'BOP',
                                                1640, 'PET',
                                                NVL (INVENTORY.SEGMENT2, 'PET')) PRODUCT_TYPE,
                   ICMB.SEGMENT1 ITEM_CODE,
                   TO_NUMBER (ICMB.ATTRIBUTE1) MICRON,
                   MTLN.GRADE_CODE,
                   TRUNC (MMT.TRANSACTION_DATE) TRX_DATE,
                   SUM (MMT.TRANSACTION_QUANTITY) TRX_QTY
              FROM APPS.GME_MATERIAL_DETAILS      GMD,
                   APPS.GME_BATCH_HEADER          GBH,
                   APPS.FM_ROUT_HDR               FRH,
                   APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                   APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                   APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN,
                   (SELECT MIC.ORGANIZATION_ID,
                           MIC.INVENTORY_ITEM_ID,
                           MCV.SEGMENT2
                      FROM APPS.MTL_ITEM_CATEGORIES MIC,
                           APPS.MTL_CATEGORY_SETS MCS,
                           APPS.MTL_CATEGORIES_VL MCV
                     WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID --(112, 240, 1036)
                           AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                           AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                           AND MCS.CATEGORY_SET_NAME = 'Inventory') INVENTORY
             WHERE     TRUNC (MMT.TRANSACTION_DATE) BETWEEN TRUNC (:P_DATE_FROM, 'MON') AND :P_DATE
                   AND LINE_TYPE = 1
                   AND GMD.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                   AND GMD.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                   AND GMD.BATCH_ID = GBH.BATCH_ID
                   AND GBH.ORGANIZATION_ID = FRH.OWNER_ORGANIZATION_ID
                   AND GBH.ROUTING_ID = FRH.ROUTING_ID
                   AND GBH.ORGANIZATION_ID = :P_ORGANIZATION_ID
                   AND FRH.ROUTING_NO LIKE '%M%'
                   AND ICMB.SEGMENT1 LIKE '%_M'
                   AND ITEM_TYPE = 'FILM'
                   AND GBH.ORGANIZATION_ID = MMT.ORGANIZATION_ID
                   AND GMD.MATERIAL_DETAIL_ID = MMT.TRX_SOURCE_LINE_ID
                   AND GMD.BATCH_ID = MMT.TRANSACTION_SOURCE_ID
                   AND GMD.INVENTORY_ITEM_ID = MMT.INVENTORY_ITEM_ID
                   AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                   AND MMT.TRANSACTION_TYPE_ID IN (44, 17)
                   AND MMT.ORGANIZATION_ID = MTLN.ORGANIZATION_ID
                   AND MTLN.TRANSACTION_ID = MMT.TRANSACTION_ID
                   AND MMT.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                   AND INVENTORY.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                   AND INVENTORY.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                   AND INVENTORY.SEGMENT2 = 'BOP'
          GROUP BY GBH.ORGANIZATION_ID,
                   GBH.BATCH_NO,
                   TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS'),
                   TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS'),
                   DECODE (GBH.ORGANIZATION_ID, 112, 'PET',
                                                280, 'BOP',
                                                1640, 'PET',
                                                NVL (INVENTORY.SEGMENT2, 'PET')),
                   ICMB.SEGMENT1,
                   TO_NUMBER (ICMB.ATTRIBUTE1),
                   MTLN.GRADE_CODE,
                   TRUNC (MMT.TRANSACTION_DATE))
GROUP BY ORGANIZATION_ID,
         PRODUCT_TYPE,
         ITEM_CODE,
         MICRON,
         LAST_DAY (TRX_DATE);
----------------------------------------------------------------------------------------------------------------------------
-------------------------------------------- ITEM WISE IO RATIO	 -----------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
INSERT INTO XXSRF.PFB_CONTRI_IORATIO_DATA (ORGANIZATION_ID,
                                           JUMBO_ITEM_CODE,
                                           FG_ITEM_CODE,
                                           TRX_DATE,
                                           INPUT_QTY,
                                           OUTPUT_QTY,
                                           BYPRODUCT_QTY,
                                           IO_RATIO)
    WITH
        TAB
        AS
            (  SELECT GBH.ORGANIZATION_ID,
                      GBH.BATCH_NO,
                      MMT.TRANSACTION_DATE,
                      ICMB.INVENTORY_ITEM_ID,
                      ICMB.SEGMENT1                               ITEM_CODE,
                      GMD.LINE_TYPE,
                      ICMB.DESCRIPTION,
                      SUBINVENTORY_CODE,
                      ICMB.ITEM_TYPE,
                      INV.SEGMENT1,
                      INV.SEGMENT2,
                      INV.SEGMENT3,
                      INV.SEGMENT4,
                      TRUNC (LAST_DAY (MMT.TRANSACTION_DATE))     TRX_DATE,
                      SUM (ABS (MMT.TRANSACTION_QUANTITY))        TRX_QTY
                 FROM APPS.GME_MATERIAL_DETAILS     GMD,
                      APPS.GME_BATCH_HEADER         GBH,
                      APPS.FM_ROUT_HDR              FRH,
                      APPS.MTL_SYSTEM_ITEMS_B       ICMB,
                      APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                      (SELECT MIC.ORGANIZATION_ID,
                              MIC.INVENTORY_ITEM_ID,
                              MIC.CATEGORY_ID,
                              MCV.SEGMENT1,
                              MCV.SEGMENT2,
                              MCV.SEGMENT3,
                              MCV.SEGMENT4
                         FROM APPS.MTL_ITEM_CATEGORIES MIC,
                              APPS.MTL_CATEGORY_SETS  MCS,
                              APPS.MTL_CATEGORIES_VL  MCV
                        WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID
                              AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                              AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                              AND MCS.CATEGORY_SET_NAME = 'Inventory') INV
                WHERE     TRUNC (MMT.TRANSACTION_DATE) BETWEEN TRUNC (
                                                                   :P_DATE_FROM)
                                                           AND TRUNC ( :P_DATE)
                      --AND GMD.LINE_TYPE IN (-1, 1)
                      AND GMD.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                      AND GMD.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                      AND GMD.BATCH_ID = GBH.BATCH_ID
                      AND GBH.ROUTING_ID = FRH.ROUTING_ID
                      AND GBH.ORGANIZATION_ID = :P_ORGANIZATION_ID
                      AND FRH.ROUTING_NO LIKE '%J%'
                      AND INV.SEGMENT2 = 'BOP'
                      AND GMD.MATERIAL_DETAIL_ID = MMT.TRX_SOURCE_LINE_ID
					  AND GBH.BATCH_STATUS IN (3, 4)
                      --             AND MMT.TRANSACTION_TYPE_ID IN (35, 43)
                      AND GMD.BATCH_ID = MMT.TRANSACTION_SOURCE_ID
                      AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                      AND ICMB.ORGANIZATION_ID = INV.ORGANIZATION_ID
                      AND ICMB.INVENTORY_ITEM_ID = INV.INVENTORY_ITEM_ID
             --                  AND GBH.BATCH_NO = 382209
             GROUP BY GBH.ORGANIZATION_ID,
                      GBH.BATCH_NO,
                      MMT.TRANSACTION_DATE,
                      ICMB.INVENTORY_ITEM_ID,
                      ICMB.SEGMENT1,
                      GMD.LINE_TYPE,
                      ICMB.DESCRIPTION,
                      SUBINVENTORY_CODE,
                      ICMB.ITEM_TYPE,
                      TRUNC (LAST_DAY (MMT.TRANSACTION_DATE)),
                      INV.SEGMENT1,
                      INV.SEGMENT2,
                      INV.SEGMENT3,
                      INV.SEGMENT4)
      SELECT ORGANIZATION_ID,
             JUMBO_ITEM_CODE,
             FG_ITEM_CODE,
             TRX_DATE,
             SUM (INPUT_QTY)                                               INPUT_QTY,
             SUM (OUTPUT_QTY)                                              OUTPUT_QTY,
             SUM (BYPRODUCT_QTY)                                           BYPRODUCT_QTY,
             SUM (INPUT_QTY) / (SUM (OUTPUT_QTY) + SUM (BYPRODUCT_QTY))    IO_RATIO
        FROM (SELECT A.ORGANIZATION_ID,
                     A.BATCH_NO,
                     B.TRX_DATE,
                     B.JUMBO_ITEM_CODE,
                     B.FG_ITEM_CODE,
                     A.INPUT_QTY,
                     B.OUTPUT_QTY,
                     NVL (C.BYPRODUCT_QTY, 0)     BYPRODUCT_QTY
                FROM (  SELECT ORGANIZATION_ID, BATCH_NO, SUM (TRX_QTY) INPUT_QTY
                          FROM TAB
                         WHERE LINE_TYPE = '-1'
                      GROUP BY ORGANIZATION_ID, BATCH_NO) A,
                     (  SELECT X.ORGANIZATION_ID,
                               X.BATCH_NO,
                               X.ITEM_CODE         JUMBO_ITEM_CODE,
                               Y.FG_ITEM_CODE,
                               X.TRX_DATE,
                               SUM (X.TRX_QTY)     OUTPUT_QTY
                          FROM TAB X, XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP Y
                         WHERE     X.LINE_TYPE = '1'
                               AND X.ORGANIZATION_ID = Y.ORGANIZATION_ID(+)
                               AND X.ITEM_CODE = Y.JUMBO_ITEM_CODE(+)
                      GROUP BY X.ORGANIZATION_ID,
                               X.BATCH_NO,
                               X.ITEM_CODE,
                               X.TRX_DATE,
                               Y.FG_ITEM_CODE) B,
                     (  SELECT ORGANIZATION_ID,
                               BATCH_NO,
                               SUM (TRX_QTY)     BYPRODUCT_QTY
                          FROM TAB
                         WHERE     LINE_TYPE = '2'
                               AND ITEM_CODE <> 'BOP-EVOH-RE-FILM'
                      GROUP BY ORGANIZATION_ID, BATCH_NO) C
               WHERE     A.ORGANIZATION_ID = B.ORGANIZATION_ID
                     AND A.BATCH_NO = B.BATCH_NO
                     AND A.ORGANIZATION_ID = C.ORGANIZATION_ID(+)
                     AND A.BATCH_NO = C.BATCH_NO(+))
    GROUP BY ORGANIZATION_ID,
             JUMBO_ITEM_CODE,
             FG_ITEM_CODE,
             TRX_DATE;
----------------------------------------------------------------------------------------------------------------------------
-------------------------------------------- COMPONENT WISE VC COST --------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
INSERT INTO XXSRF.PFB_CONTRI_VC_COST_DATA (ORGANIZATION_ID,
                                           PRODUCTION_TYPE,
                                           PRODUCT_TYPE,
                                           TRX_DATE,
                                           ITEM_CODE,
                                           THROUGHPUT,
                                           MICRON,
                                           POWER_COST,
                                           FUEL_AND_WATER,
                                           PRODUCTION_CONSUMABLE,
                                           MET_COST)
    SELECT ORGANIZATION_ID,
           'JUMBO'     PRODUCTION_TYPE,
           PRODUCT_TYPE,
           TRX_DATE,
           ITEM_CODE,
           ROUND(PER_HR_PROD_QTY/ 1000, 2) THROUGHPUT,
           MICRON,
           POWER_COST,
           FUEL_AND_WATER,
           PRODUCTION_CONSUMABLE,
           0           MET_COST
      FROM (SELECT A.ORGANIZATION_ID,
                   A.PRODUCT_TYPE,
                   A.TRX_DATE,
                   B.ITEM_CODE,
                   B.MICRON,
                   A.MIS_HEAD,
                   PER_HR_PROD_QTY,
                   ROUND ((A.EXPENSE_AMT / A.TOTAL_HRS) / PER_HR_PROD_QTY, 2)    VC_COST
              FROM (  SELECT ORGANIZATION_ID,
                             PRODUCT_TYPE,
                             MIS_HEAD,
                             TRX_DATE,
                             SUM (REC_QTY)    EXPENSE_AMT,
                             TO_NUMBER (TO_CHAR (LAST_DAY ( :P_DATE), 'DD')) * 24             TOTAL_HRS
                        FROM PFBCUSTOM.FCT_PFB_KPI_GL_DATA
                       WHERE     ORGANIZATION_ID = :P_ORGANIZATION_ID
                             AND TRX_DATE = TRUNC (LAST_DAY ( :P_DATE))
                             AND PRODUCT_TYPE = 'BOP'
                             AND COST_CENTER <> '4139' 
                             AND MIS_HEAD IN
                                     ('FUEL AND WATER', --'METALLIZING MATERIAL',
                                                         --'PACKING MATERIAL',
                                       'PRODUCTION CONSUMABLE', 
                                       'POWER')
                    GROUP BY ORGANIZATION_ID,
                             PRODUCT_TYPE,
                             MIS_HEAD,
                             TRX_DATE) A,
                   (  SELECT ORGANIZATION_ID,
                             TRX_DATE,
                             PRODUCT_TYPE,
                             ITEM_CODE,
                             MICRON,
                             (SUM (PROD_QTY) / SUM (PROD_TIME))    PER_HR_PROD_QTY
                        FROM XXSRF.PFB_CONTRI_PRODUCTION_DATA
                       WHERE     PROD_TYPE = 'JUMBO'
                             AND PRODUCT_TYPE = 'BOP'
                             AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                             AND TRX_DATE = TRUNC (LAST_DAY ( :P_DATE))
                    GROUP BY ORGANIZATION_ID,
                             TRX_DATE,
                             PRODUCT_TYPE,
                             ITEM_CODE,
                             MICRON) B
             WHERE     A.ORGANIZATION_ID = B.ORGANIZATION_ID
                   AND A.PRODUCT_TYPE = B.PRODUCT_TYPE
				   AND PER_HR_PROD_QTY > 0)
           PIVOT (SUM (VC_COST)
                  FOR MIS_HEAD IN ('POWER' POWER_COST,
                                   'FUEL AND WATER' FUEL_AND_WATER,
                                   'PRODUCTION CONSUMABLE' PRODUCTION_CONSUMABLE))  
UNION ALL
    SELECT A.ORGANIZATION_ID,
           'MET'                                                         PRODUCTION_TYPE,
           A.PRODUCT_TYPE,
           A.TRX_DATE,
           'MET ITEM'                                                    ITEM_CODE,
           PER_HR_PROD_QTY,
           NULL                                                          MICRON,
           0                                                             POWER_COST,
           0                                                             FUEL_AND_WATER,
           0                                                             PRODUCTION_CONSUMABLE,
           --       B.ITEM_CODE,
           --       B.MICRON,
           --       A.MIS_HEAD,
           ROUND ((A.EXPENSE_AMT / A.TOTAL_HRS) / PER_HR_PROD_QTY, 2)    MET_COST
      FROM (  SELECT ORGANIZATION_ID,
                     PRODUCT_TYPE,
--                     MIS_HEAD,
                     TRX_DATE,
                     SUM (REC_QTY)                                           EXPENSE_AMT,
                     TO_NUMBER (TO_CHAR (LAST_DAY ( :P_DATE), 'DD')) * 24    TOTAL_HRS
                FROM PFBCUSTOM.FCT_PFB_KPI_GL_DATA
               WHERE     ORGANIZATION_ID = :P_ORGANIZATION_ID
                     AND TRX_DATE = TRUNC (LAST_DAY ( :P_DATE))
                     AND PRODUCT_TYPE = 'BOP'
                     AND COST_CENTER = '4139'
                     AND MIS_HEAD IN ('FUEL AND WATER', 
                                      'METALLIZING MATERIAL',
                                      'PRODUCTION CONSUMABLE', 
                                      'POWER')
            GROUP BY ORGANIZATION_ID,
                     PRODUCT_TYPE,
--                     MIS_HEAD,
                     TRX_DATE) A,
           (  SELECT ORGANIZATION_ID,
                     TRX_DATE,
                     PRODUCT_TYPE,
                     --                 ITEM_CODE,
                     --                 MICRON,
                     (SUM (PROD_QTY) / PROD_TIME)     PER_HR_PROD_QTY
                FROM XXSRF.PFB_CONTRI_PRODUCTION_DATA
               WHERE     PROD_TYPE = 'MET'
                     AND PRODUCT_TYPE = 'BOP'
                     AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                     AND TRX_DATE = TRUNC (LAST_DAY ( :P_DATE))
            GROUP BY ORGANIZATION_ID,
                     TRX_DATE,
                     PRODUCT_TYPE,
                     --                 ITEM_CODE,
                     --                 MICRON,
                     PROD_TIME) B
     WHERE     A.ORGANIZATION_ID = B.ORGANIZATION_ID
           AND A.PRODUCT_TYPE = B.PRODUCT_TYPE;
----------------------------------------------------------------------------------------------------------------------------
-------------------------------------------- FINAL OUTPUT ------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
SELECT SALE.ORGANIZATION_ID,
       SALE.TRX_DATE,
       SALE.PRODUCT_TYPE,
       SALE.ITEM_CODE,
       SALE.INV_QUANTITY,
       SALE.NET_VALUE,
       SALE.NPR,
       EXPENSE.THROUGHPUT,
       EXPENSE.RM_CUR_VALUE RM_COST,
       ROUND(EXPENSE.HOMOPOLYMER_COST, 2) HOMOPOLYMER_COST,
       ROUND(EXPENSE.ADDITIVE_COST, 2) ADDITIVE_COST,
       ROUND(EXPENSE.IO_RATIO, 3) IO_RATIO,
       EXPENSE.POWER_COST,
       EXPENSE.FUEL_AND_WATER,
       EXPENSE.PRODUCTION_CONSUMABLE,
       EXPENSE.MET_COST,
       ROUND((HOMOPOLYMER_COST + ADDITIVE_COST + IO_RATIO + POWER_COST + FUEL_AND_WATER + PRODUCTION_CONSUMABLE + MET_COST), 2) TOTAL_COST,
       ROUND(SALE.NPR - (HOMOPOLYMER_COST + ADDITIVE_COST + IO_RATIO + POWER_COST + FUEL_AND_WATER + PRODUCTION_CONSUMABLE + MET_COST), 2) CONTRI_PER_KG
  FROM (  SELECT ORGANIZATION_ID,
                 LAST_DAY (TRX_DATE)                                       TRX_DATE,
                 PRODUCT_TYPE,
                 ITEM_CODE,
                 JUMBO_ITEM_CODE,
                 MET_FILM,
                 MICRON,
                 ROUND (SUM (INV_QUANTITY), 2)                             INV_QUANTITY,
                 ROUND (SUM (NET_VALUE), 2)                                NET_VALUE,
                 ROUND ((SUM (NET_VALUE) / SUM (INV_QUANTITY)), 2) - 4 /* FREIGHT AMT*/  NPR
            FROM (SELECT A.ORGANIZATION_ID,
                         B.NPR_HEADER_ID,
                         B.NPR_DETAIL_ID,
                         B.CUSTOMER_TRX_ID,
                         B.TRX_NUMBER,
                         B.TRX_DATE,
                         TO_CHAR (B.TRX_DATE, 'MON')     TRX_MONTH,
                         TO_CHAR (B.TRX_DATE, 'RRRR')    TRX_YEAR,
                         B.INVOICE_TYPE,
                         B.CUSTOMER_ID,
                         B.CUSTOMER_NAME,
                         B.REGION,
                         B.PRICE_LIST_NAME,
                         B.ITEM_CODE,
                         JFG.JUMBO_ITEM_CODE,
                         JFG.MET_FILM,
                         MSI.ATTRIBUTE1                  MICRON,
                         CASE
                             WHEN INVENTORY.SEGMENT2 IN ('PET', 'BOP')
                             THEN INVENTORY.SEGMENT2
                             WHEN B.INVOICE_TYPE LIKE '%PET%'
                             THEN 'PET'
                             WHEN B.INVOICE_TYPE LIKE '%BOP%'
                             THEN 'BOP'
                             ELSE INVENTORY.SEGMENT2
                         END                             PRODUCT_TYPE,
                         B.INV_QUANTITY,
                         B.NPR,
                         B.INV_QUANTITY * (B.NPR - DECODE (NVL (B.PACKING_TYPE, 'LOOSE'), 'LOOSE', 2, 5)) NET_VALUE --B.NET_VALUE
                    FROM XXSRF.XXSRF_PFB_NPR_HEADERS       A,
                         XXSRF.XXSRF_PFB_NPR_FINAL_DETAILS B,
                         APPS.MTL_SYSTEM_ITEMS_B           MSI,
                         XXSRF.PFB_CONTRI_JUMBO_FG_ITEM_MAP JFG,
                         (SELECT MIC.ORGANIZATION_ID,
                                 MIC.INVENTORY_ITEM_ID,
                                 MCV.SEGMENT2
                            FROM APPS.MTL_ITEM_CATEGORIES         MIC,
                                 APPS.MTL_CATEGORY_SETS           MCS,
                                 APPS.MTL_CATEGORIES_VL           MCV,
                                 APPS.ORG_ORGANIZATION_DEFINITIONS OOD1
                           WHERE     MIC.ORGANIZATION_ID = OOD1.ORGANIZATION_ID --IN (112, 114, 1036, 1076, 1700, 1801, 1941)
                                 AND OOD1.OPERATING_UNIT = 87
                                 AND MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID
                                 AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                                 AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                                 AND MCS.CATEGORY_SET_NAME = 'Inventory') INVENTORY
                   WHERE     TRUNC (TRX_DATE) >= TRUNC ( :P_DATE, 'MM')
                         AND TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                         AND A.NPR_HEADER_ID = B.NPR_HEADER_ID
                         AND MSI.ORGANIZATION_ID = A.ORGANIZATION_ID
                         AND A.ORGANIZATION_ID = :P_ORGANIZATION_ID
                         AND MSI.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                         AND MSI.ITEM_TYPE = 'FILM'
                         AND INVENTORY.ORGANIZATION_ID = A.ORGANIZATION_ID
                         AND INVENTORY.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                         AND INVENTORY.SEGMENT2 = 'BOP'
                         AND A.ORGANIZATION_ID = JFG.ORGANIZATION_ID(+)
                         AND B.ITEM_CODE = JFG.FG_ITEM_CODE(+))
--                         AND B.ITEM_CODE IN ('SSW15-TI/A01-HO', 'SM18-TI/A01-P2'))
        GROUP BY ORGANIZATION_ID,
                 LAST_DAY (TRX_DATE),
                 PRODUCT_TYPE,
                 ITEM_CODE,
                 JUMBO_ITEM_CODE,
                 MET_FILM,
                 MICRON) SALE,
(SELECT X.ORGANIZATION_ID,
       Y.PRODUCT_TYPE,
       X.FG_ITEM_CODE,
       X.JUMBO_ITEM_CODE,
       X.MET_FILM,
       X.TRX_DATE,
       X.RM_CUR_VALUE,
       X.HOMOPOLYMER_COST,
       X.MET_COST,
       X.RM_CUR_VALUE - (X.HOMOPOLYMER_COST + X.IO_RATIO)     ADDITIVE_COST,
       X.IO_RATIO,
       Y.POWER_COST,
       Y.FUEL_AND_WATER,
       Y.PRODUCTION_CONSUMABLE,
       Y.THROUGHPUT
  FROM (  SELECT ORGANIZATION_ID,
                 FG_ITEM_CODE,
                 JUMBO_ITEM_CODE,
                 MAX (MET_FILM)             MET_FILM,
                 TRX_DATE,
                 SUM (RM_CUR_VALUE)         RM_CUR_VALUE,
                 SUM (HOMOPOLYMER_COST)     HOMOPOLYMER_COST,
                 SUM (MET_COST)             MET_COST,
                 SUM (IO_RATIO)             IO_RATIO
            FROM (SELECT ORGANIZATION_ID,
                         FG_ITEM_CODE,
                         JUMBO_ITEM_CODE,
                         MET_FILM,
                         TRX_DATE,
                         RM_CUR_VALUE,
                         HOMOPOLYMER_COST,
                         NVL((SELECT MET_COST
                                FROM XXSRF.PFB_CONTRI_VC_COST_DATA C
                               WHERE     C.ORGANIZATION_ID = A.ORGANIZATION_ID
                                     AND TRUNC (C.TRX_DATE) = TRUNC (A.TRX_DATE)
                                     AND C.PRODUCT_TYPE = 'BOP'
                                     AND C.PRODUCTION_TYPE = 'MET'
                                     AND A.MET_FILM = 'Y'), 0)    MET_COST,
                         0         IO_RATIO
                    FROM XXSRF.PFB_CONTRI_JUMBO_RECIPE_DATA A
                   WHERE     TRUNC (TRX_DATE) = TRUNC (LAST_DAY ( :P_DATE))
                         AND ORGANIZATION_ID = :P_ORGANIZATION_ID
                  UNION ALL
                  SELECT ORGANIZATION_ID,
                         FG_ITEM_CODE,
                         JUMBO_ITEM_CODE,
                         NULL                            MET_FILM,
                         TRUNC (LAST_DAY ( :P_DATE))     TRX_DATE,
                         0                               RM_CUR_VALUE,
                         0                               HOMOPOLYMER_COST,
                         0                               MET_COST,
                         IO_RATIO
                    FROM (SELECT A.*,
                                 RANK ()
                                     OVER (
                                         PARTITION BY ORGANIZATION_ID,
                                                      FG_ITEM_CODE,
                                                      JUMBO_ITEM_CODE
                                         ORDER BY TRX_DATE DESC)    RN
                            FROM XXSRF.PFB_CONTRI_IORATIO_DATA A
                           WHERE     TRUNC (TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                                 AND ORGANIZATION_ID = :P_ORGANIZATION_ID)
                   WHERE RN = 1)
        GROUP BY ORGANIZATION_ID,
                 FG_ITEM_CODE,
                 JUMBO_ITEM_CODE,
                 TRX_DATE) X,
       (SELECT ORGANIZATION_ID,
               TRUNC (LAST_DAY ( :P_DATE))     TRX_DATE,
               PRODUCT_TYPE,
               ITEM_CODE,
               MICRON,
               POWER_COST,
               FUEL_AND_WATER,
               PRODUCTION_CONSUMABLE,
               THROUGHPUT
          FROM (SELECT A.*,
                       RANK ()
                           OVER (PARTITION BY A.ORGANIZATION_ID, A.ITEM_CODE
                                 ORDER BY TRX_DATE DESC)    RN
                  FROM XXSRF.PFB_CONTRI_VC_COST_DATA A
                 WHERE     A.ORGANIZATION_ID = :P_ORGANIZATION_ID
                       AND TRUNC (A.TRX_DATE) <= TRUNC (LAST_DAY ( :P_DATE))
                       AND A.PRODUCT_TYPE = 'BOP'
                       AND A.PRODUCTION_TYPE = 'JUMBO')
         WHERE RN = 1) Y
 WHERE     X.ORGANIZATION_ID = Y.ORGANIZATION_ID
       AND X.TRX_DATE = Y.TRX_DATE
       AND X.JUMBO_ITEM_CODE = Y.ITEM_CODE) EXPENSE
 WHERE     SALE.ORGANIZATION_ID = EXPENSE.ORGANIZATION_ID(+)
       AND SALE.PRODUCT_TYPE = EXPENSE.PRODUCT_TYPE(+)
       AND SALE.TRX_DATE = EXPENSE.TRX_DATE(+)
       AND SALE.ITEM_CODE = EXPENSE.FG_ITEM_CODE(+);
------------------------------------------------------------------------------------------------------------------
