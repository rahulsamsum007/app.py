SELECT INPUT.ORGANIZATION_ID,
       INPUT.PROD_TYPE,
       INPUT.TRX_DATE,
       INPUT.JUMBO_ITEM_CODE,
       INPUT.INPUT_ITEM_CODE,
       INPUT.INPUT_QTY,
       OUTPUT.OUTPUT_QTY,
       INPUT.INPUT_QTY / OUTPUT.OUTPUT_QTY     PER_KG_QTY
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
                 INPUT_ITEM_CODE) INPUT,
       (  SELECT ORGANIZATION_ID,
                 PROD_TYPE,
                 LINE_TYPE,
                 TRX_DATE,
                 --         BATCH_NO,
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
                 --         BATCH_NO,
                 ITEM_CODE) OUTPUT
WHERE     INPUT.ORGANIZATION_ID = OUTPUT.ORGANIZATION_ID
       AND INPUT.PROD_TYPE = OUTPUT.PROD_TYPE
       AND INPUT.TRX_DATE = OUTPUT.TRX_DATE
       AND INPUT.JUMBO_ITEM_CODE = OUTPUT.JUMBO_ITEM_CODE
