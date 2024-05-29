----------------------------------------------------------------------------------------------------------------------------
-------------------------------------------- ITEM WISE IO RATIO	 -----------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
--INSERT INTO XXSRF.PFB_CONTRI_IORATIO_DATA (ORGANIZATION_ID,
--                                           JUMBO_ITEM_CODE,
--                                           FG_ITEM_CODE,
--                                           TRX_DATE,  
--                                           INPUT_QTY,
--                                           OUTPUT_QTY,
--                                           BYPRODUCT_QTY,
--                                           IO_RATIO)
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
