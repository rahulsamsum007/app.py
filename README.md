--INSERT INTO XXSRF.PFB_STAGING_DATA (ORGANIZATION_ID,                       --1
--                                    RECIPE_NO,                         -- NULL
--                                    RECIPE_VERSION,                    -- NULL
--                                    FORMULA_NO,                        -- NULL
--                                    FORMULA_VERS,                      -- NULL
--                                    FG_ITEM_CODE,                      -- NULL
--                                    JUMBO_ITEM_CODE,                   -- NULL
--                                    MET_FILM,                          -- NULL
--                                    TRX_DATE,                              --3
--                                    PERCENTAGE,                        -- NULL
--                                    RM_CUR_VALUE,                      -- NULL
--                                    HOMOPOLYMER_COST,                  -- NULL
--                                    PROD_TYPE,                             --2
--                                    PRODUCT_TYPE,                          --4
--                                    ITEM_CODE,                             --5
--                                    MICRON,                                --6
--                                    PROD_TIME,                             --7
--                                    PROD_QTY,                              --8
--                                    INPUT_QTY,                         -- NULL
--                                    OUTPUT_QTY,                        -- NULL
--                                    BYPRODUCT_QTY,                     -- NULL
--                                    IO_RATIO                           -- NULL
--                                            )

SELECT ORGANIZATION_ID,
       NULL                RECIPE_NO,
       NULL                RECIPE_VERSION,
       NULL                FORMULA_NO,
       NULL                FORMULA_VERS,
       NULL                FG_ITEM_CODE,
       NULL                JUMBO_ITEM_CODE,
       NULL                MET_FILM,
       TRX_DATE,
       NULL                PERCENTAGE,
       NULL                RM_CUR_VALUE,
       NULL                HOMOPOLYMER_COST,
       PROD_TYPE,
       PRODUCT_TYPE,
       ITEM_CODE,
       MICRON,
       PRODUCTION_TIME     PROD_TIME,
       TRX_QTY             PROD_QTY,
       NULL                INPUT_QTY,
       NULL                OUTPUT_QTY,
       NULL                BYPRODUCT_QTY,
       NULL                IO_RATIO
  FROM (  SELECT ORGANIZATION_ID,
                 'JUMBO'                              PROD_TYPE,
                 LAST_DAY (TRX_DATE)                  TRX_DATE,
                 PRODUCT_TYPE,
                 ITEM_CODE,
                 MICRON,
                 ROUND (SUM (PRODUCTION_TIME), 2)     PRODUCTION_TIME,
                 SUM (TRX_QTY)                        TRX_QTY
            FROM (  SELECT GBH.ORGANIZATION_ID,
                           GBH.BATCH_NO,
                           TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS')
                               START_DATE,
                           TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS')
                               END_DATE,
                             (  TO_DATE (GBH.ATTRIBUTE16,
                                         'YYYY/MM/DD HH24:MI:SS')
                              - TO_DATE (GBH.ATTRIBUTE15,
                                         'YYYY/MM/DD HH24:MI:SS'))
                           * 24
                               PRODUCTION_TIME,
                           DECODE (GBH.ORGANIZATION_ID,
                                   112, 'PET',
                                   280, 'BOP',
                                   1640, 'PET',
                                   NVL (INVENTORY.SEGMENT2, 'PET'))
                               PRODUCT_TYPE,
                           ICMB.SEGMENT1
                               ITEM_CODE,
                           TO_NUMBER (ICMB.ATTRIBUTE1)
                               MICRON,
                           MTLN.GRADE_CODE,
                           TRUNC (MMT.TRANSACTION_DATE)
                               TRX_DATE,
                           SUM (MMT.TRANSACTION_QUANTITY)
                               TRX_QTY
                      FROM APPS.GME_MATERIAL_DETAILS     GMD,
                           APPS.GME_BATCH_HEADER         GBH,
                           APPS.FM_ROUT_HDR              FRH,
                           APPS.MTL_SYSTEM_ITEMS_B       ICMB,
                           APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN,
                           (SELECT MIC.ORGANIZATION_ID,
                                   MIC.INVENTORY_ITEM_ID,
                                   MCV.SEGMENT2
                              FROM APPS.MTL_ITEM_CATEGORIES MIC,
                                   APPS.MTL_CATEGORY_SETS MCS,
                                   APPS.MTL_CATEGORIES_VL MCV
                             WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID
                                   AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                                   AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                                   AND MCS.CATEGORY_SET_NAME = 'Inventory')
                           INVENTORY
                     WHERE     TRUNC (MMT.TRANSACTION_DATE) BETWEEN TRUNC (
                                                                        :P_DATE_FROM,
                                                                        'MON')
                                                                AND :P_DATE
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
                           AND INVENTORY.INVENTORY_ITEM_ID =
                               ICMB.INVENTORY_ITEM_ID
                           AND INVENTORY.SEGMENT2 = 'BOP'
                  GROUP BY GBH.ORGANIZATION_ID,
                           GBH.BATCH_NO,
                           TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS'),
                           TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS'),
                           DECODE (GBH.ORGANIZATION_ID,
                                   112, 'PET',
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
                 'MET'
                     PROD_TYPE,
                 LAST_DAY (TRX_DATE)
                     TRX_DATE,
                 PRODUCT_TYPE,
                 ITEM_CODE,
                 MICRON,
                 TO_NUMBER (TO_CHAR (LAST_DAY (TRX_DATE), 'DD')) * 24
                     PRODUCTION_TIME,
                 SUM (TRX_QTY)
                     TRX_QTY
            FROM (  SELECT GBH.ORGANIZATION_ID,
                           GBH.BATCH_NO,
                           TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS')
                               START_DATE,
                           TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS')
                               END_DATE,
                             (  TO_DATE (GBH.ATTRIBUTE16,
                                         'YYYY/MM/DD HH24:MI:SS')
                              - TO_DATE (GBH.ATTRIBUTE15,
                                         'YYYY/MM/DD HH24:MI:SS'))
                           * 24
                               PRODUCTION_TIME,
                           DECODE (GBH.ORGANIZATION_ID,
                                   112, 'PET',
                                   280, 'BOP',
                                   1640, 'PET',
                                   NVL (INVENTORY.SEGMENT2, 'PET'))
                               PRODUCT_TYPE,
                           ICMB.SEGMENT1
                               ITEM_CODE,
                           TO_NUMBER (ICMB.ATTRIBUTE1)
                               MICRON,
                           MTLN.GRADE_CODE,
                           TRUNC (MMT.TRANSACTION_DATE)
                               TRX_DATE,
                           SUM (MMT.TRANSACTION_QUANTITY)
                               TRX_QTY
                      FROM APPS.GME_MATERIAL_DETAILS     GMD,
                           APPS.GME_BATCH_HEADER         GBH,
                           APPS.FM_ROUT_HDR              FRH,
                           APPS.MTL_SYSTEM_ITEMS_B       ICMB,
                           APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN,
                           (SELECT MIC.ORGANIZATION_ID,
                                   MIC.INVENTORY_ITEM_ID,
                                   MCV.SEGMENT2
                              FROM APPS.MTL_ITEM_CATEGORIES MIC,
                                   APPS.MTL_CATEGORY_SETS MCS,
                                   APPS.MTL_CATEGORIES_VL MCV
                             WHERE     MIC.ORGANIZATION_ID = :P_ORGANIZATION_ID
                                   AND MIC.CATEGORY_SET_ID = MCS.CATEGORY_SET_ID
                                   AND MIC.CATEGORY_ID = MCV.CATEGORY_ID
                                   AND MCS.CATEGORY_SET_NAME = 'Inventory')
                           INVENTORY
                     WHERE     TRUNC (MMT.TRANSACTION_DATE) BETWEEN TRUNC (
                                                                        :P_DATE_FROM,
                                                                        'MON')
                                                                AND :P_DATE
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
                           AND INVENTORY.INVENTORY_ITEM_ID =
                               ICMB.INVENTORY_ITEM_ID
                           AND INVENTORY.SEGMENT2 = 'BOP'
                  GROUP BY GBH.ORGANIZATION_ID,
                           GBH.BATCH_NO,
                           TO_DATE (GBH.ATTRIBUTE15, 'YYYY/MM/DD HH24:MI:SS'),
                           TO_DATE (GBH.ATTRIBUTE16, 'YYYY/MM/DD HH24:MI:SS'),
                           DECODE (GBH.ORGANIZATION_ID,
                                   112, 'PET',
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
                 LAST_DAY (TRX_DATE));









                 -------------








                 --INSERT INTO XXSRF.PFB_STAGING_DATA (ORGANIZATION_ID,--
--                                    RECIPE_NO,
--                                    RECIPE_VERSION,
--                                    FORMULA_NO,
--                                    FORMULA_VERS,
--                                    FG_ITEM_CODE,--
--                                    JUMBO_ITEM_CODE,--
--                                    MET_FILM,
--                                    TRX_DATE,--
--                                    PERCENTAGE,
--                                    RM_CUR_VALUE,
--                                    HOMOPOLYMER_COST,
--                                    PROD_TYPE,                   
--                                    PRODUCT_TYPE,
--                                    ITEM_CODE,
--                                    MICRON,
--                                    PROD_TIME,
--                                    PROD_QTY,
--                                    INPUT_QTY, --                     
--                                    OUTPUT_QTY,--
--                                    BYPRODUCT_QTY,--
--                                    IO_RATIO)--
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
       NULL                                                          AS RECIPE_NO,
       NULL                                                          AS RECIPE_VERSION,
       NULL                                                          AS FORMULA_NO,
       NULL                                                          AS FORMULA_VERS,
       FG_ITEM_CODE,
       JUMBO_ITEM_CODE,
       NULL                                                          AS MET_FILM,
       TRX_DATE,
       NULL                                                          AS PERCENTAGE,
       NULL                                                          AS RM_CUR_VALUE,
       NULL                                                          AS HOMOPOLYMER_COST,
       NULL                                                          AS PROD_TYPE,
       NULL                                                          AS PRODUCT_TYPE,
       NULL                                                          AS ITEM_CODE,
       NULL                                                          AS MICRON,
       NULL                                                          AS PROD_TIME,
       NULL                                                          AS PROD_QTY,
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





             ok so im giving you two codes io ratio and for production in 
production query i want you to add logic of io ratio code in 
production the tables that we have used 
are also present in prodctuion query carefully 
add the io script in production so that when i'll
be fecthing or ruuning the select statement of prodcution 
data i'll be seeing that toooooo of io ratio 
