CREATE OR REPLACE PROCEDURE XXSRF.PRO_PFB_MIS_REPORT (P_DATE_FROM   IN DATE,
                                                      P_WHSE_LOC    IN CHAR)
AS
BEGIN
    DELETE FROM XXSRF.PFB_MIS_REPORT_TEMP
          WHERE ORG = P_WHSE_LOC;

    COMMIT;

    INSERT INTO XXSRF.PFB_MIS_REPORT_TEMP
          SELECT SEQ,
                 STAGE,
                 --   decode(Line, 'I', 'L-1', 'J', 'L-2', Line) Line,
                 CASE
                     WHEN (P_WHSE_LOC = 112 AND LINE = '3')
                     THEN 'L-1'
                     ELSE DECODE (LINE, '1', 'L-1',
                                        '2', 'L-2',
                                        '3', 'L-3',
                                        'W', 'L-3', LINE)
                 END                         LINE,
                 LOC_GROUP,
                 CATEGORY,
                 ROUND (SUM (QTY), 2)        SUM_QTY,
                 ROUND (SUM (TOT_QTY), 2)    TOT_QTY,
                 'T',
                 P_WHSE_LOC
            FROM (  SELECT SEQ,-------------------------------------------------------------------Opening WIP
                           STAGE,
                           LINE,
                           LOC_GROUP,
                           CATEGORY,
                           SUM (QTY)         QTY,
                           SUM (TOT_QTY)     TOT_QTY
                      FROM (  SELECT 1                     SEQ,
                                     'Opening WIP'         STAGE,
                                     CASE
                                         WHEN (    P_WHSE_LOC = 240
                                               AND LOT_NUMBER NOT LIKE 'N%'
                                               AND LOT_NUMBER NOT LIKE '%L'
                                               AND LOT_NUMBER NOT LIKE 'O%'
                                               AND LOT_NUMBER NOT LIKE 'RO%')
                                         THEN '1'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'N%' OR LOT_NUMBER LIKE '%L')
                                         THEN '2'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'O%' OR LOT_NUMBER LIKE 'RO%')
                                         THEN '3'
                                         ELSE DECODE (P_WHSE_LOC, 114, '1', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                     END                   LINE,
                                     SUBINVENTORY_CODE     LOC_GROUP,
                                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                        'AL', 'Al Wire',
                                                        'WIP', 'FILM', ITEM_TYPE)    CATEGORY,
                                     NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0) / 1000                QTY,
                                     NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0) / 1000                TOT_QTY
                                FROM APPS.GMF_PERIOD_BALANCES A,
                                     APPS.MTL_SYSTEM_ITEMS_B ICMB,
                                     PFB_LOC_GROUP       LOC
                               WHERE     A.ORGANIZATION_ID = P_WHSE_LOC
                                     AND ACCT_PERIOD_ID IN
                                             (SELECT ACCT_PERIOD_ID
                                                FROM APPS.ORG_ACCT_PERIODS
                                               WHERE     ORGANIZATION_ID = P_WHSE_LOC
                                                     AND SUBINVENTORY_CODE IN ('JMB', 'JMB1', 'JMB2', 'JMB3',
                                                                               'SLT', 'SLT1', 'SLT2', 'SLT3',
                                                                               'PKG', 'PKG1', 'PKG2', 'PKG3',
                                                                               'RTP', 'RTP1', 'RTP2', 'RTP3',
                                                                               'MET', 'MET1', 'MET2', 'MET3',
                                                                               'REC', 'REC1', 'REC2', 'REC3')
                                                     AND UPPER (PERIOD_NAME) = TO_CHAR ((ADD_MONTHS (P_DATE_FROM, -1)), 'MON-RR'))
                                     AND A.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                                     AND A.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                                     AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                                     AND A.ORGANIZATION_ID = P_WHSE_LOC
                                     AND ITEM_TYPE IN ('CHIP', 'FILM', 'REFILM')
                            GROUP BY SUBSTR (SUBINVENTORY_CODE, -1, 1),
                                     SUBINVENTORY_CODE,
                                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                        'AL', 'Al Wire',
                                                        'WIP', 'FILM', ITEM_TYPE),
                                     LOT_NUMBER)
                  GROUP BY SEQ,
                           STAGE,
                           LINE,
                           LOC_GROUP,
                           CATEGORY
                  UNION ALL
                    SELECT 1                                                                SEQ,
                           'Opening WIP'                                                    STAGE,
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                                            'RSN', 'RSN1',
                                                                                            'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1)) LINE,
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM',
                                              ITEM_TYPE) CATEGORY,
                           NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0) / 1000                QTY,
                           NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0) / 1000                TOT_QTY
                      FROM APPS.GMF_PERIOD_BALANCES A,
                           APPS.MTL_SYSTEM_ITEMS_B ICMB,
                           PFB_LOC_GROUP         LOC
                     WHERE     A.ORGANIZATION_ID = P_WHSE_LOC
                           AND ACCT_PERIOD_ID IN
                                   (SELECT ACCT_PERIOD_ID
                                      FROM APPS.ORG_ACCT_PERIODS
                                     WHERE     ORGANIZATION_ID = P_WHSE_LOC
                                           AND SUBINVENTORY_CODE IN ('FED', 'FED1', 'FED2', 'FED3')
                                           AND UPPER (PERIOD_NAME) = TO_CHAR ((ADD_MONTHS (P_DATE_FROM, -1)), 'MON-RR'))
                           AND A.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND A.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND A.ORGANIZATION_ID = P_WHSE_LOC
                           AND SEGMENT1 IN ('RE-CHIP', 'RE-CHIP-2', 'BOP-RE-CHIP')
                  GROUP BY SUBSTR (SUBINVENTORY_CODE, -1, 1),
                           SUBINVENTORY_CODE,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE)-------------------------------------------------------------------END Opening WIP
                  UNION ALL
                    SELECT 2,-------------------------------------------------------------------INPUT
                           'Input',
                           DECODE (P_WHSE_LOC, 114, '1',
                                   SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                      'RSN', 'RSN1',
                                                                      'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) --,substr(icmb.description,1,100)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TRANSACTION_SOURCE_ID IN
                                   (SELECT BATCH_ID
                                      FROM APPS.GME_BATCH_HEADER GBH,
                                           APPS.FM_ROUT_HDR   FRH
                                     WHERE GBH.ROUTING_ID = FRH.ROUTING_ID
                                       AND (FRH.ROUTING_NO LIKE '%J1' OR FRH.ROUTING_NO LIKE '%J2' OR FRH.ROUTING_NO LIKE '%J3'))
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND SUBINVENTORY_CODE IN ('RML', 'FED', 'FED1', 'FED2', 'FED3', 'RSN', 'RFED')
                           AND MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND ITEM_TYPE IN ('AL', 'CHIP')
                           AND SEGMENT1 NOT IN ('RE-CHIP', 'RE-CHIP-2', 'BOP-RE-CHIP') --and p_whse_loc <>112
                           --and substr(icmb.description,1,100) <>'Semi PET Film-Imported'
                           AND P_WHSE_LOC = 240
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                              'RSN', 'RSN1',
                                                              'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE         --,substr(icmb.description,1,100)
                  UNION ALL
                    SELECT 2,
                           'Input',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) --,substr(icmb.description,1,100)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND -- subinventory_code in  ('RML') and
                               MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND SUBINVENTORY_CODE <> 'RFED'
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND ITEM_TYPE IN ('CHEM', 'AL')
                           AND ICMB.SEGMENT1 <> 'COPET'
                           AND SUBSTR (ICMB.DESCRIPTION, 1, 100) <> 'Semi PET Film-Imported'
                           AND P_WHSE_LOC = 240
                  -- and segment1 not in ('RE-CHIP','ROFGFLMI001') and p_whse_loc =112
                  --and icmb.segment1 in ('C100011006', 'C100011016')
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE         --,substr(icmb.description,1,100)
                  UNION ALL
                    SELECT 2,
                           'Input',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND SUBINVENTORY_CODE IN ('RML', 'FED', 'FED1', 'FED2', 'FED3', 'REC3')
                           AND MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND ITEM_TYPE IN ('AL', 'CHIP')
                           AND SEGMENT1 NOT IN ('RE-CHIP', 'RE-CHIP-2') --and p_whse_loc <>112
                           AND P_WHSE_LOC <> 240
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE
                  UNION ALL
                    SELECT 2,
                           'Input',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND -- subinventory_code in  ('RML') and
                               MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND SUBINVENTORY_CODE <> 'RFED'
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND ITEM_TYPE IN ('CHEM')
                           AND ICMB.SEGMENT1 <> 'COPET'
                           AND P_WHSE_LOC <> 240
                  -- and segment1 not in ('RE-CHIP','ROFGFLMI001') and p_whse_loc =112
                  --and icmb.segment1 in ('C100011006', 'C100011016')
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE
                  UNION ALL
                  /*PRODUCED RECHIP TRANSFERED TO RFEED */
                  SELECT 2,
                           'Input',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           'CHIP' REC_CATEGORY,
                           -1 * ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           -1 * ABS (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64, 51, 32, 33)
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           --  AND b.transfer_organization_id = ood.organization_id
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND B.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND SEGMENT1 IN ('RE-CHIP', 'RE-CHIP-2', 'BOP-RE-CHIP')
                           AND P_WHSE_LOC = 240
                           AND B.SUBINVENTORY_CODE IN ('JMB1', 'JMB2', 'JMB3') /*from inventory */
                           AND UPPER (B.TRANSFER_SUBINVENTORY) IN ('RFED', 'STAGING', 'FGL')  -- to inventory
                  --         AND transaction_quantity < 0
                  GROUP BY SUBINVENTORY_CODE------------------------------------------------------------------- END INPUT
                  UNION ALL
                    SELECT SEQ,-------------------------------------------------------------------------------Return from FG
                           STAGE,
                           LINE,
                           LOC_GROUP,
                           CATEGORY,
                           SUM (RET_QTY)     QTY,
                           SUM (TOT_QTY)     TOT_QTY
                      FROM (  SELECT 3 SEQ,
                                     'Return from FG' STAGE,
                                     CASE
                                         WHEN (    P_WHSE_LOC = 240
                                               AND LOT_NUMBER NOT LIKE 'N%'
                                               AND LOT_NUMBER NOT LIKE '%L'
                                               AND LOT_NUMBER NOT LIKE 'O%'
                                               AND LOT_NUMBER NOT LIKE 'RO%')
                                         THEN '1'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'N%' OR LOT_NUMBER LIKE '%L')
                                         THEN '2'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'O%' OR LOT_NUMBER LIKE 'RO%')
                                         THEN '3'
                                         ELSE DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1))
                                     END LINE,
                                     -- decode(:p_whse_loc,114,'1',SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1)),
                                     --loc_group,
                                     SUBSTR (B.TRANSFER_SUBINVENTORY, 1, LENGTH (B.TRANSFER_SUBINVENTORY) - 1) LOC_GROUP,
                                     'FILM' CATEGORY,
                                     ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000 RET_QTY,
                                     ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000 TOT_QTY
                                FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                                     APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                                     APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN
                               --  apps.org_organization_definitions ood
                               WHERE     B.TRANSACTION_TYPE_ID IN (2, 64, 51) --  ('Move Order Transfer' , 'Subinventory Transfer ',''Backflush Transfer')
                                     AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                                     AND MTLN.TRANSACTION_ID = B.TRANSACTION_ID
                                     AND MTLN.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                                     AND B.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                                     AND B.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                                     --     AND b.organization_id = ood.organization_id
                                     AND TO_CHAR (B.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                                     AND B.ORGANIZATION_ID = P_WHSE_LOC
                                     AND DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                            'AL', 'Al Wire',
                                                            'WIP', 'FILM', ITEM_TYPE) = 'FILM'
                                     AND B.TRANSACTION_QUANTITY < 0
                                     AND B.SUBINVENTORY_CODE = 'FGL' /*from inventory */
                                     AND B.TRANSFER_SUBINVENTORY IN ('SLT', 'SLT1', 'SLT2', 'SLT3',
                                                                     'MET', 'MET1', 'MET2', 'MET3',
                                                                     'PKG', 'PKG1', 'PKG2', 'PKG3') -- to inventory
                            GROUP BY SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1),
                                     SUBSTR (B.TRANSFER_SUBINVENTORY, 1, LENGTH (B.TRANSFER_SUBINVENTORY) - 1),
                                     --loc_group,
                                     ICMB.ITEM_TYPE,
                                     LOT_NUMBER
                            UNION ALL
                              SELECT 3,
                                     'Return from FG',
                                     CASE
                                         WHEN (    P_WHSE_LOC = 240
                                               AND LOT_NUMBER NOT LIKE 'N%'
                                               AND LOT_NUMBER NOT LIKE '%L'
                                               AND LOT_NUMBER NOT LIKE 'O%'
                                               AND LOT_NUMBER NOT LIKE 'RO%')
                                         THEN '1'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'N%' OR LOT_NUMBER LIKE '%L')
                                         THEN '2'
                                         WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'O%' OR LOT_NUMBER LIKE 'RO%')
                                         THEN '3'
                                         ELSE DECODE (P_WHSE_LOC, 114, '1', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                     END LINE,
                                     SUBINVENTORY_CODE LOC_GROUP,
                                     'FILM',
                                     ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                                     ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                                FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                                     APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                                     PFB_LOC_GROUP               LOC,
                                     APPS.MTL_TXN_SOURCE_TYPES   MTST,
                                     APPS.MTL_TRANSACTION_TYPES  MTT,
                                     APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN
                               WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                                     AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                                     AND MTLN.TRANSACTION_ID = MMT.TRANSACTION_ID
                                     AND MTLN.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                                     AND MMT.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                                     AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                                     AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                                     AND DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                            'AL', 'Al Wire',
                                                            'WIP', 'FILM', ITEM_TYPE) = 'FILM'
                                     AND TO_CHAR (MMT.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                                     AND SUBINVENTORY_CODE = 'FGL'
                                     AND MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                                     AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                                     AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                                     AND MMT.ORGANIZATION_ID = P_WHSE_LOC --and item_type in ('AL','CHIP','CHEM')
                            --and mmt.transaction_quantity<0
                            GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'FGL', 'FGL1', SUBINVENTORY_CODE), -1, 1),
                                     SUBINVENTORY_CODE,
                                     ITEM_TYPE,
                                     LOT_NUMBER)
                  GROUP BY SEQ,
                           STAGE,
                           LINE,
                           LOC_GROUP,
                           CATEGORY-----------------------------------------------------------------------------------END Return from FG
                  UNION ALL
                    SELECT 4,
                           'Rec from Other Unit/Outside',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1)),
                           ITEM_TYPE,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                           APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                     --xxsrf.pfb_loc_group loc    Commented By path team
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64)
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.TRANSFER_ORGANIZATION_ID = OOD.ORGANIZATION_ID
                           -- AND b.subinventory_code = TRIM (loc.location)   Commented By path team
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND OOD.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND ((ICMB.SEGMENT1 LIKE 'RSFIPET%') OR (ICMB.SEGMENT1 IN ('PETAMBD001', 'RSFIPETD001', 'ROFGFLMI001')))
                           AND B.SUBINVENTORY_CODE = 'RML' /*from inventory */
                           AND B.TRANSFER_SUBINVENTORY IN ('FED', 'FED1', 'FED2', 'FED3') -- to inventory
                           AND TRANSACTION_QUANTITY < 0
                           AND P_DATE_FROM < '01-jun-2015'
                  GROUP BY SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1), ITEM_TYPE
                  UNION ALL
                    SELECT 4,
                           'Rec from Other Unit/Outside',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1)),
                           ITEM_TYPE,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                           APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                     --xxsrf.pfb_loc_group loc    Commented By path team
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64)
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.TRANSFER_ORGANIZATION_ID = OOD.ORGANIZATION_ID
                           -- AND b.subinventory_code = TRIM (loc.location)   Commented By path team
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND OOD.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND ((ICMB.SEGMENT1 LIKE 'RSFIPET%') OR (ICMB.SEGMENT1 IN ('PETAMBD001', 'RSFIPETD001', 'RE-FILM')))
                           AND B.SUBINVENTORY_CODE = 'RML' /*from inventory */
                           AND B.TRANSFER_SUBINVENTORY IN ('FED', 'FED1', 'FED2', 'FED3', 'REC3') -- to inventory
                           AND TRANSACTION_QUANTITY < 0
                           AND P_DATE_FROM >= '01-jun-2015'
                  GROUP BY SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1), ITEM_TYPE
                  UNION ALL
                    SELECT 4,
                           'Rec from Other Unit/Outside',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1)),
                           ITEM_TYPE,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                           APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                     --xxsrf.pfb_loc_group loc    Commented By path team
                     WHERE                 -- B.TRANSACTION_TYPE_ID IN (2, 64)
                               --AND
                               B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND P_WHSE_LOC = 240
                           -- AND b.subinventory_code = TRIM (loc.location)   Commented By path team
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND OOD.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND (ICMB.SEGMENT1 LIKE 'RSFIPET%')
                  --  AND b.subinventory_code = 'RML'     /*from inventory */
                  -- AND B.TRANSFER_SUBINVENTORY IN ('FED','FED1','FED2','FED3','REC3') -- to inventory
                  -- and P_DATE_FROM >='01-jun-2015'
                  GROUP BY SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1), ITEM_TYPE
                  UNION ALL
                    SELECT 2,
                           'Rec from Other Unit/Outside',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND SUBINVENTORY_CODE IN ('RML')
                           AND MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND P_WHSE_LOC = 112
                           AND (ICMB.SEGMENT1 IN ('PETAMBD001', 'RPETFLKD001', 'ROFGFLMI001'))
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE
                  UNION ALL
                    SELECT 4,
                           'Trasfer to Other Unit/Outside',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1)),
                           ITEM_TYPE,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B        ICMB,
                           APPS.ORG_ORGANIZATION_DEFINITIONS OOD
                     --xxsrf.pfb_loc_group loc    Commented By path team
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64)
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.TRANSFER_ORGANIZATION_ID = OOD.ORGANIZATION_ID
                           -- AND b.subinventory_code = TRIM (loc.location)   Commented By path team
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND OOD.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND ((ICMB.SEGMENT1 LIKE 'RSFIPET%') OR (ICMB.SEGMENT1 IN ('PETAMBD001', 'RSFIPETD001', 'RE-FILM')))
                           AND B.SUBINVENTORY_CODE IN ('REC1', 'REC2', 'REC3') /*from inventory */
                           AND B.TRANSFER_SUBINVENTORY IN ('FGL', 'Staging', 'STAGING') -- to inventory
                           AND TRANSACTION_QUANTITY < 0
                           AND P_DATE_FROM >= '01-jun-2015'
                  GROUP BY SUBSTR (B.TRANSFER_SUBINVENTORY, -1, 1), ITEM_TYPE
                  UNION ALL
                    SELECT 2,
                           'POLYMER Waste',
                           DECODE ( P_WHSE_LOC, 114, '1', SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID =
                               MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND --  subinventory_code in  ('RML') and
                               MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND P_WHSE_LOC = 112
                           AND (ICMB.SEGMENT1 IN ('RWBPL', 'RWCPL', 'PWSG-RESIN'))
                           AND MMT.TRANSACTION_TYPE_ID IN (35, 43)
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE
                  UNION ALL
                    SELECT 2,
                           'POLYMER Cons-FILM',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR ( DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1)),
                           SUBINVENTORY_CODE LOC_GROUP,
                           DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                              'AL', 'Al Wire',
                                              'WIP', 'FILM', ITEM_TYPE),
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000) QTY,
                           ABS (SUM (MMT.TRANSACTION_QUANTITY) / 1000)
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           PFB_LOC_GROUP               LOC,
                           APPS.MTL_TXN_SOURCE_TYPES   MTST,
                           APPS.MTL_TRANSACTION_TYPES  MTT
                     WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND MTST.TRANSACTION_SOURCE_TYPE_ID = MMT.TRANSACTION_SOURCE_TYPE_ID
                           AND MTT.TRANSACTION_TYPE_ID = MMT.TRANSACTION_TYPE_ID
                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND --  subinventory_code in  ('RML') and
                               MMT.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND SUBINVENTORY_CODE = TRIM (LOC.LOCATION)
                           AND MMT.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND MMT.ORGANIZATION_ID = P_WHSE_LOC
                           AND P_WHSE_LOC = 112
                           AND ICMB.SEGMENT1 LIKE 'PW%IDR'
                           AND MMT.TRANSACTION_TYPE_ID IN (35, 43)
                  GROUP BY SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1', SUBINVENTORY_CODE), -1, 1),
                           SUBINVENTORY_CODE,
                           ITEM_TYPE
                  UNION ALL
                  SELECT 4,
                         'Rec from Other Unit/Outside',
                         DECODE (P_WHSE_LOC, 112, '2', 1036, '3', 240, '1', '280', '1'),
                         NULL,
                         'FILM',
                         0,
                         0
                    FROM DUAL
                  UNION ALL
                  SELECT 4,
                         'Rec from Other Unit/Outside',
                         '2',
                         NULL,
                         'FILM',
                         0,
                         0
                    FROM DUAL
                  UNION ALL
                  SELECT 4,
                         'Rec from Other Unit/Outside',
                         '3',
                         NULL,
                         'FILM',
                         0,
                         0
                    FROM DUAL
                  UNION ALL
                    SELECT 5,-----------------------------------------------------------------------------------------------PACKED
                           'Packed',
                           DECODE (P_WHSE_LOC, 114, '1', 240, CASE
                                                                  WHEN SUBSTR (MTLN.LOT_NUMBER, 1, 1) = 'T'
                                                                  THEN '1'
                                                                  WHEN SUBSTR (MTLN.LOT_NUMBER, 1, 1) = 'N'
                                                                  THEN '2'
                                                                  WHEN SUBSTR (MTLN.LOT_NUMBER, 1, 1) = 'O'
                                                                  THEN '3'
                                                                  ELSE '1'
                                                              END, SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           NULL,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           -1 * ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B       ICMB,
                           APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN
                     --  apps.org_organization_definitions ood
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64, 51)
                           AND MTLN.TRANSACTION_ID = B.TRANSACTION_ID
                           AND MTLN.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           -- AND b.transfer_organization_id = ood.organization_id
                           AND TO_CHAR (B.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND B.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                  'AL', 'Al Wire',
                                                  'WIP', 'FILM', ITEM_TYPE) = 'FILM'
                           AND B.SUBINVENTORY_CODE IN ('PKG', 'PKG1', 'PKG2', 'PKG3') /*from inventory */
                           AND B.TRANSFER_SUBINVENTORY = 'FGL' -- to inventory
                           AND B.TRANSACTION_QUANTITY < 0
                           AND MTLN.LOT_NUMBER NOT LIKE '%T'
                  --AND MTLN.LOT_NUMBER NOT Like 'O%'
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1),
                           SUBSTR (MTLN.LOT_NUMBER, 1, 1)
                  UNION ALL
                    SELECT 5,
                           'Packed with Trade',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           NULL,
                           'FILM' REC_CATEGORY,
                           ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           -1 * ABS (SUM (B.TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B       ICMB,
                           APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN
                     --  apps.org_organization_definitions ood
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64, 51)
                           AND MTLN.TRANSACTION_ID = B.TRANSACTION_ID
                           AND MTLN.ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           AND B.INVENTORY_ITEM_ID = MTLN.INVENTORY_ITEM_ID
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           -- AND b.transfer_organization_id = ood.organization_id
                           AND TO_CHAR (B.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND B.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                                  'AL', 'Al Wire',
                                                  'WIP', 'FILM', ITEM_TYPE) = 'FILM'
                           AND B.SUBINVENTORY_CODE IN ('PKG', 'PKG1', 'PKG2', 'PKG3') /*from inventory */
                           AND B.TRANSFER_SUBINVENTORY = 'FGL' -- to inventory
                           AND B.TRANSACTION_QUANTITY < 0
                           AND MTLN.LOT_NUMBER LIKE '%T'
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)-----------------------------------------------------------------------END PACKED
                  UNION ALL
                    --         SELECT 5, 'Packed', '2', NULL, 'FILM', 0, 0
                    --           FROM DUAL
                    --         UNION ALL
                    --         SELECT 5, 'Packed', '1', NULL, 'FILM', 0, 0
                    --           FROM DUAL
                    --          union all
                    SELECT 6,-----------------------------------------------------------------------------------==========================-----NRW Gen
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', DECODE (SUBSTR (ROUTING_NO, -1, 1), 4, 3, SUBSTR (ROUTING_NO, -1, 1))),
                           'NRW' LOC_GROUP,
                           'Moisture Loss' CATEGORY,
                           ROUND (SUM (GMD.ACTUAL_QTY - (GMD.ACTUAL_QTY / (1 + GMD.SCRAP_FACTOR))) / 1000, 4) SCRAP_QTY,
                           -1 * ROUND (SUM (GMD.ACTUAL_QTY - (GMD.ACTUAL_QTY / (1 + GMD.SCRAP_FACTOR))) / 1000, 4) DIFF
                      FROM APPS.GME_MATERIAL_DETAILS GMD,
                           APPS.GME_BATCH_HEADER  GBH,
                           APPS.FM_ROUT_HDR       FRH
                     WHERE     GMD.BATCH_ID = GBH.BATCH_ID
                           AND LINE_TYPE = -1
                           AND GBH.ROUTING_ID = FRH.ROUTING_ID
                           --   AND GBH.ORGANIZATION_ID = OOD.ORGANIZATION_ID
                           AND GBH.ORGANIZATION_ID = P_WHSE_LOC
                           AND FRH.ROUTING_NO LIKE ('%J%')
                           AND FRH.ROUTING_NO <> 'JRND'
                           AND TO_CHAR (TRUNC (GBH.ACTUAL_CMPLT_DATE), 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND NVL (GMD.SCRAP_FACTOR, 0) <> 0
                           AND GBH.BATCH_STATUS IN (3, 4)
                  GROUP BY ROUTING_NO
                  UNION ALL
                    SELECT 6,
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           'NRW' LOC_GROUP,
                           'Bare Waste' CATEGORY,
                           SUM (TRANSACTION_QUANTITY) / 1000 NRW_QTY,
                           -1 * SUM (TRANSACTION_QUANTITY) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           -- xxsrf.pfb_loc_group          loc,
                           APPS.GME_MATERIAL_DETAILS   GMD
                     WHERE     GMD.BATCH_ID = B.TRANSACTION_SOURCE_ID
                           AND GMD.MATERIAL_DETAIL_ID = B.TRX_SOURCE_LINE_ID
                           AND GMD.LINE_TYPE IN (2, -1)
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           --  AND b.organization_id = ood.organization_id
                           AND B.SUBINVENTORY_CODE IN ('NRW', 'NRW1', 'NRW2', 'NRW3')
                           AND ITEM_TYPE = 'NRW'
                           AND SUBSTR (ICMB.SEGMENT1, 1, 3) <> 'MET'
                           AND ICMB.SEGMENT1 NOT IN ('WASTE-ALUM-SLUDGE',
                                                     'WASTE-ALUM-WIRE-PCS',
                                                     'RE-CHIP-1',
                                                     'PWSS-RESIN',
                                                     'RWBPL',
                                                     'RWCPL')
                           --   AND icmb.segment1 IN
                           --      ('PWSS-IDR', 'PWSC-IDR', 'PWSD-IDR', 'PWSG-IDR', 'LUMPS')
                           AND ICMB.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                           AND ICMB.ORGANIZATION_ID = B.ORGANIZATION_ID
                           --     AND transaction_quantity > 0
                           AND B.ORGANIZATION_ID = P_WHSE_LOC
                           AND P_WHSE_LOC <> 112
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                  --  AND NVL(B.SOURCE_LINE_ID,-99) = -99
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)
                  UNION ALL
                    SELECT 6,
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           'NRW' LOC_GROUP,
                           'Bare Waste' CATEGORY,
                           SUM (TRANSACTION_QUANTITY) / 1000 NRW_QTY,
                           -1 * SUM (TRANSACTION_QUANTITY) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           -- xxsrf.pfb_loc_group          loc,
                           APPS.GME_MATERIAL_DETAILS   GMD
                     WHERE     GMD.BATCH_ID = B.TRANSACTION_SOURCE_ID
                           AND GMD.MATERIAL_DETAIL_ID = B.TRX_SOURCE_LINE_ID
                           AND GMD.LINE_TYPE IN (2)
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           --  AND b.organization_id = ood.organization_id
                           AND B.SUBINVENTORY_CODE IN ('NRW', 'NRW1', 'NRW2', 'NRW3')
                           AND ITEM_TYPE = 'NRW'
                           AND SUBSTR (ICMB.SEGMENT1, 1, 3) <> 'MET'
                           AND ICMB.SEGMENT1 NOT IN ('WASTE-ALUM-SLUDGE',
                                                     'WASTE-ALUM-WIRE-PCS',
                                                     'RE-CHIP-1',
                                                     'PWSS-RESIN',
                                                     'RWBPL',
                                                     'RWCPL',
                                                     'PWSG-RESIN')
                           --   AND icmb.segment1 IN
                           --      ('PWSS-IDR', 'PWSC-IDR', 'PWSD-IDR', 'PWSG-IDR', 'LUMPS')
                           AND ICMB.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                           AND ICMB.ORGANIZATION_ID = B.ORGANIZATION_ID
                           AND P_WHSE_LOC = 112
                           --     AND transaction_quantity > 0
                           AND B.ORGANIZATION_ID = P_WHSE_LOC
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                  --  AND NVL(B.SOURCE_LINE_ID,-99) = -99
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)
                  UNION ALL
                  SELECT 6,
                         'NRW Gen',
                         DECODE (P_WHSE_LOC, 112, '2', 1036, '3', 240, '1', '280', '1'),
                         NULL,
                         'Bare Waste',
                         0,
                         0
                    FROM DUAL
                  --            UNION ALL
                  --            SELECT   6,
                  --                     'NRW Gen',
                  --                     '1',
                  --                     NULL,
                  --                     'Bare Waste',
                  --                     0,
                  --                     0
                  --              FROM   DUAL
                  UNION ALL
                    SELECT 6,
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           'NRW' LOC_GROUP,
                           'Met PET Waste' CATEGORY,
                           SUM (TRANSACTION_QUANTITY) / 1000 NRW_QTY,
                           -1 * SUM (TRANSACTION_QUANTITY) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           -- xxsrf.pfb_loc_group          loc,
                           APPS.GME_MATERIAL_DETAILS   GMD
                     WHERE     GMD.BATCH_ID = B.TRANSACTION_SOURCE_ID
                           AND GMD.MATERIAL_DETAIL_ID = B.TRX_SOURCE_LINE_ID
                           AND GMD.LINE_TYPE IN (1, 2)
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           --      AND b.organization_id = ood.organization_id
                           AND B.SUBINVENTORY_CODE IN ('NRW', 'NRW1', 'NRW2', 'NRW3')
                           AND SUBSTR (ICMB.SEGMENT1, 1, 3) = 'MET'
                           AND ITEM_TYPE = 'NRW'
                           AND P_WHSE_LOC NOT IN (112, 1036)
                           AND ICMB.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                           AND ICMB.ORGANIZATION_ID = B.ORGANIZATION_ID
                           --                  AND transaction_quantity > 0
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND B.ORGANIZATION_ID = P_WHSE_LOC
                           AND NVL (B.SOURCE_LINE_ID, -99) = -99
                           AND NOT EXISTS
                                   (SELECT '1'
                                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT
                                     WHERE     MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                                           AND MMT.SOURCE_LINE_ID = B.TRANSACTION_ID
                                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                                           AND B.ORGANIZATION_ID = MMT.ORGANIZATION_ID --added by rsl
                                           AND B.INVENTORY_ITEM_ID = MMT.INVENTORY_ITEM_ID --added by rsk
                                           AND B.TRANSACTION_DATE BETWEEN MMT.TRANSACTION_DATE - 60
                                                                      AND MMT.TRANSACTION_DATE + 60)
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)
                  UNION ALL
                    SELECT 6,
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           'NRW' LOC_GROUP,
                           'Met PET Waste' CATEGORY,
                           SUM (TRANSACTION_QUANTITY) / 1000 NRW_QTY,
                           -1 * SUM (TRANSACTION_QUANTITY) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           -- xxsrf.pfb_loc_group          loc,
                           APPS.GME_MATERIAL_DETAILS   GMD
                     WHERE     GMD.BATCH_ID = B.TRANSACTION_SOURCE_ID
                           AND GMD.MATERIAL_DETAIL_ID = B.TRX_SOURCE_LINE_ID
                           AND GMD.LINE_TYPE IN (1, 2)
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           --    AND b.organization_id = ood.organization_id
                           AND B.SUBINVENTORY_CODE IN ('NRW', 'NRW1', 'NRW2', 'NRW3')
                           AND SUBSTR (ICMB.SEGMENT1, 1, 3) = 'MET'
                           AND ICMB.SEGMENT1 <> 'MET-FILM'
                           AND ITEM_TYPE = 'NRW'
                           AND P_WHSE_LOC IN (112, 1036)
                           AND ICMB.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                           AND ICMB.ORGANIZATION_ID = B.ORGANIZATION_ID
                           --                  AND transaction_quantity > 0
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND B.ORGANIZATION_ID = P_WHSE_LOC
                           AND NVL (B.SOURCE_LINE_ID, -99) = -99
                           AND NOT EXISTS
                                   (SELECT '1'
                                      FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT
                                     WHERE     MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                                           AND MMT.SOURCE_LINE_ID = B.TRANSACTION_ID
                                           AND MMT.TRANSACTION_SOURCE_TYPE_ID = 5
                                           AND B.ORGANIZATION_ID = MMT.ORGANIZATION_ID --added by rsl
                                           AND B.INVENTORY_ITEM_ID = MMT.INVENTORY_ITEM_ID --added by rsk
                                           AND B.TRANSACTION_DATE BETWEEN MMT.TRANSACTION_DATE - 60
                                                                      AND MMT.TRANSACTION_DATE + 60)
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)
                  UNION ALL
                  SELECT 6,
                         'NRW Gen',
                         DECODE (P_WHSE_LOC, 112, '2', 1036, '3', 240, '1', '280', '1'),
                         NULL,
                         'Met PET Waste',
                         0,
                         0
                    FROM DUAL
                  /*UNION ALL
                  SELECT   6,
                           'NRW Gen',
                           '1',
                           NULL,
                           'Met PET Waste',
                           0,
                           0
                    FROM   DUAL*/
                  UNION ALL
                    SELECT 6,
                           'NRW Gen',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           'NRW' LOC_GROUP,
                           'Al Sludge and Leftover wire' CATEGORY,
                           SUM (TRANSACTION_QUANTITY) / 1000 NRW_QTY,
                           -1 * SUM (TRANSACTION_QUANTITY) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB,
                           -- xxsrf.pfb_loc_group          loc,
                           APPS.GME_MATERIAL_DETAILS   GMD
                     WHERE     GMD.BATCH_ID = B.TRANSACTION_SOURCE_ID
                           AND GMD.MATERIAL_DETAIL_ID = B.TRX_SOURCE_LINE_ID
                           AND GMD.LINE_TYPE = 2
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           -- AND b.organization_id = ood.organization_id
                           AND B.SUBINVENTORY_CODE IN ('NRW', 'NRW1', 'NRW2', 'NRW3')
                           AND ICMB.SEGMENT1 IN ('WASTE-ALUM-SLUDGE', 'WASTE-ALUM-WIRE-PCS')
                           AND ICMB.INVENTORY_ITEM_ID = B.INVENTORY_ITEM_ID
                           AND ICMB.ORGANIZATION_ID = B.ORGANIZATION_ID
                           --AND transaction_quantity > 0
                           AND B.TRANSACTION_SOURCE_TYPE_ID = 5
                           AND NVL (B.SOURCE_LINE_ID, -99) = -99
                           AND B.ORGANIZATION_ID = P_WHSE_LOC
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1)
                  UNION ALL
                  SELECT 6,
                         'NRW Gen',
                         DECODE (P_WHSE_LOC, 112, '2', 1036, '3', 240, '1', '280', '1'),
                         NULL,
                         'Al Sludge and Leftover wire',
                         0,
                         0
                    FROM DUAL
                  --            UNION ALL
                  --            SELECT   6,
                  --                     'NRW Gen',
                  --                     '1',
                  --                     NULL,
                  --                     'Al Sludge and Leftover wire',
                  --                     0,
                  --                     0
                  --              FROM   DUAL
                  UNION ALL
                    SELECT 7,
                           'RE-CHIP to Resin_Other unit',
                           DECODE (P_WHSE_LOC, 114, '1', SUBSTR (B.SUBINVENTORY_CODE, -1, 1)),
                           NULL,
                           'CHIP' REC_CATEGORY,
                           -1 * ABS (SUM (TRANSACTION_QUANTITY)) / 1000 REC_QTY,
                           -1 * ABS (SUM (TRANSACTION_QUANTITY)) / 1000
                      FROM APPS.MTL_MATERIAL_TRANSACTIONS B,
                           APPS.MTL_SYSTEM_ITEMS_B     ICMB
                     WHERE     B.TRANSACTION_TYPE_ID IN (2, 64, 51, 32, 33)
                           AND B.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                           AND B.TRANSFER_ORGANIZATION_ID = ICMB.ORGANIZATION_ID
                           --  AND b.transfer_organization_id = ood.organization_id
                           AND TO_CHAR (TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                           AND B.ORGANIZATION_ID IN (P_WHSE_LOC)
                           AND SEGMENT1 IN ('RE-CHIP', 'RE-CHIP-2', 'BOP-RE-CHIP')
                           --  AND decode(item_type,'PFB ITEMS','FILM','AL','Al Wire','WIP','FILM',item_type) = 'FILM'
                           AND B.SUBINVENTORY_CODE IN ('FED1', 'FED2', 'FED3') /*from inventory */
                           AND UPPER (B.TRANSFER_SUBINVENTORY) IN ('STAGING', 'FGL')  -- to inventory
                  --         AND transaction_quantity < 0
                  GROUP BY SUBSTR (B.SUBINVENTORY_CODE, -1, 1))----------------------------------------------------------------------------------END-NRW Gen
        GROUP BY SEQ,
                 STAGE,
                 --  DECODE (Line, '1', 'L-1', '2', 'L-2','3','L-3','W','L-3', Line),
                 LOC_GROUP,
                 CASE
                     WHEN (P_WHSE_LOC = 112 AND LINE = '3')
                     THEN 'L-1'
                     ELSE DECODE (LINE, '1', 'L-1',
                                        '2', 'L-2',
                                        '3', 'L-3',
                                        'W', 'L-3', LINE)
                 END,
                 CATEGORY;

    BEGIN
        INSERT INTO XXSRF.PFB_MIS_REPORT_TEMP
              SELECT 1,--------------------------------------------------------------------------------------------------CLOSING
                     'Closing',
                     DECODE (P_WHSE_LOC, 114, 'L-1', LINE)    LINE,
                     DECODE (CASE
                                 WHEN P_WHSE_LOC = 112 AND A.LOC_GROUP = 'REC'
                                 THEN 'RE-CHIP-2'
                                 ELSE TRIM (LOC.LOC_GROUP)
                             END,
                         'Slitting', LOC.LOC_GROUP || '-' || MLN.ATTRIBUTE11,
                         'Packing',  LOC.LOC_GROUP || CASE
                                                          WHEN SUBSTR (ICMB.SEGMENT1, 1, 3) = 'SMA'
                                                          THEN '-Bare'
                                                          ELSE CASE
                                                                   WHEN INSTR (ICMB.SEGMENT1, 'M') = 0
                                                                   THEN '-Bare'
                                                                   ELSE '-MET'
                                                               END
                                                      END,
                         LOC.LOC_GROUP)                       TYP,
                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                        'AL', 'Al Wire',
                                        'WIP', 'FILM', ITEM_TYPE)   CLS_CATEGORY,
                     SUM (QTY) / 1000                               CLS_WIP_QTY,
                     0,
                     'C',
                     P_WHSE_LOC
                FROM (  SELECT CASE
                                   WHEN P_WHSE_LOC = 112
                                   THEN DECODE (SUBSTR (SUBINVENTORY_CODE, -1, 1), '1', 'L-1',
                                                                                   '2', 'L-2',
                                                                                   '3', 'L-2', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                   WHEN (    P_WHSE_LOC = 240
                                         AND LOT_NUMBER NOT LIKE 'N%'
                                         AND LOT_NUMBER NOT LIKE '%L'
                                         AND LOT_NUMBER NOT LIKE 'O%'
                                         AND LOT_NUMBER NOT LIKE 'RO%')
                                   THEN 'L-1'
                                   WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'N%' OR LOT_NUMBER LIKE '%L')
                                   THEN 'L-2'
                                   WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'O%' OR LOT_NUMBER LIKE 'RO%')
                                   THEN 'L-3'
                                   ELSE DECODE (SUBSTR (SUBINVENTORY_CODE, -1, 1), '1', 'L-1',
                                                                                   '2', 'L-2',
                                                                                   '3', 'L-3', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                               END                                           LINE,
                               SUBINVENTORY_CODE                             LOC_GROUP,
                               INVENTORY_ITEM_ID,
                               LOT_NUMBER,
                               NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0)    QTY
                          FROM APPS.GMF_PERIOD_BALANCES
                         WHERE     ORGANIZATION_ID = P_WHSE_LOC
                               AND ACCT_PERIOD_ID IN
                                       (SELECT ACCT_PERIOD_ID
                                          FROM APPS.ORG_ACCT_PERIODS
                                         WHERE     ORGANIZATION_ID = P_WHSE_LOC
                                               AND SUBINVENTORY_CODE IN ('JMB', 'JMB1', 'JMB2', 'JMB3',
                                                                         'SLT', 'SLT1', 'SLT2', 'SLT3',
                                                                         'PKG', 'PKG1', 'PKG2', 'PKG3',
                                                                         'RTP', 'RTP1', 'RTP2', 'RTP3',
                                                                         'MET', 'MET1', 'MET2', 'MET3',                                                                         
                                                                         'REC', 'REC1', 'REC2', 'REC3')
                                               AND UPPER (PERIOD_NAME) = TO_CHAR ((ADD_MONTHS (P_DATE_FROM, -1)), 'MON-RR'))
                      GROUP BY INVENTORY_ITEM_ID,
                               SUBINVENTORY_CODE,
                               SUBSTR (SUBINVENTORY_CODE, 1, LENGTH (SUBINVENTORY_CODE) - 1),
                               LOT_NUMBER
                      UNION ALL
                        SELECT CASE
                                   WHEN P_WHSE_LOC = 112
                                   THEN DECODE (SUBSTR (SUBINVENTORY_CODE, -1, 1), '1', 'L-1',
                                                                                   '2', 'L-2',
                                                                                   '3', 'L-2', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                   WHEN (    P_WHSE_LOC = 240
                                         AND LOT_NUMBER NOT LIKE 'N%'
                                         AND LOT_NUMBER NOT LIKE '%L'
                                         AND LOT_NUMBER NOT LIKE 'O%'
                                         AND LOT_NUMBER NOT LIKE 'RO%')
                                   THEN 'L-1'
                                   WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'N%' OR LOT_NUMBER LIKE '%L')
                                   THEN 'L-2'
                                   WHEN (P_WHSE_LOC = 240 AND LOT_NUMBER LIKE 'O%' OR LOT_NUMBER LIKE 'RO%')
                                   THEN 'L-3'
                                   ELSE DECODE (SUBSTR (SUBINVENTORY_CODE, -1, 1), '1', 'L-1',
                                                                                   '2', 'L-2',
                                                                                   '3', 'L-3', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                               END                               LINE,
                               SUBINVENTORY_CODE,
                               MMT.INVENTORY_ITEM_ID,
                               LOT_NUMBER,
                               SUM (MMT.TRANSACTION_QUANTITY)    TRANS_QTY
                          FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT,
                               APPS.MTL_TRANSACTION_LOT_NUMBERS MTLN
                         WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                               AND MMT.TRANSACTION_ID = MTLN.TRANSACTION_ID(+)
                               AND TO_CHAR (MMT.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
                               AND SUBINVENTORY_CODE IN ('JMB', 'JMB1', 'JMB2', 'JMB3',
                                                         'SLT', 'SLT1', 'SLT2', 'SLT3',
                                                         'PKG', 'PKG1', 'PKG2', 'PKG3',
                                                         'RTP', 'RTP1', 'RTP2', 'RTP3',
                                                         'MET', 'MET1', 'MET2', 'MET3',
                                                         'REC', 'REC1', 'REC2', 'REC3')
                      GROUP BY MMT.INVENTORY_ITEM_ID,
                               SUBSTR (SUBINVENTORY_CODE, -1, 1),
                               SUBINVENTORY_CODE,
                               LOT_NUMBER) A,
                     APPS.MTL_SYSTEM_ITEMS_B ICMB,
                     PFB_LOC_GROUP          LOC,
                     APPS.MTL_LOT_NUMBERS   MLN
               WHERE     A.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                     AND A.LOT_NUMBER = MLN.LOT_NUMBER(+)
                     AND A.INVENTORY_ITEM_ID = MLN.INVENTORY_ITEM_ID(+)
                     AND A.LOC_GROUP = TRIM (LOC.LOCATION)
                     AND ITEM_TYPE IN ('CHIP', 'FILM', 'REFILM')
                     AND ICMB.ORGANIZATION_ID = P_WHSE_LOC
            GROUP BY LINE,
                     DECODE (CASE
                                 WHEN P_WHSE_LOC = 112 AND A.LOC_GROUP = 'REC'
                                 THEN 'RE-CHIP-2'
                                 ELSE TRIM (LOC.LOC_GROUP)
                             END,
                         'Slitting', LOC.LOC_GROUP || '-' || MLN.ATTRIBUTE11,
                         'Packing',  LOC.LOC_GROUP || CASE
                                                          WHEN SUBSTR (ICMB.SEGMENT1, 1, 3) = 'SMA'
                                                          THEN '-Bare'
                                                          ELSE
                                                              CASE
                                                                   WHEN INSTR (ICMB.SEGMENT1, 'M') = 0
                                                                   THEN '-Bare'
                                                                   ELSE '-MET'
                                                              END
                                                      END,
                         LOC.LOC_GROUP),
                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                        'AL', 'Al Wire',
                                        'WIP', 'FILM', ITEM_TYPE)
            UNION ALL
              SELECT 1,
                     'Closing',
                     LINE,
                     LOC.LOC_GROUP,
                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                        'AL', 'Al Wire',
                                        'WIP', 'FILM', ITEM_TYPE)    CLS_CATEGORY,
                     SUM (QTY) / 1000      CLS_WIP_QTY,
                     0,
                     'C',
                     P_WHSE_LOC
                FROM (  SELECT CASE
                                   WHEN P_WHSE_LOC = 112
                                   THEN DECODE (SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                                   'RSN', 'RSN1',
                                                                                   'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1), 
                                                        '1', 'L-1',
                                                        '2', 'L-2',
                                                        '3', 'L-2', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                   ELSE DECODE (SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                                   'RSN', 'RSN1',
                                                                                   'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1), 
                                                        '1', 'L-1',
                                                        '2', 'L-2',
                                                        '3', 'L-3', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                               END                                           LINE,
                               SUBINVENTORY_CODE                             LOC_GROUP,
                               INVENTORY_ITEM_ID,
                               NVL (ROUND (SUM (PRIMARY_QUANTITY), 2), 0)    QTY
                          FROM APPS.GMF_PERIOD_BALANCES
                         WHERE     ORGANIZATION_ID = P_WHSE_LOC
                               AND ACCT_PERIOD_ID IN
                                       (SELECT ACCT_PERIOD_ID
                                          FROM APPS.ORG_ACCT_PERIODS
                                         WHERE     ORGANIZATION_ID = P_WHSE_LOC
                                               AND SUBINVENTORY_CODE IN ('FED', 'FED1', 'FED2', 'FED3')
                                               AND UPPER (PERIOD_NAME) = TO_CHAR ((ADD_MONTHS (P_DATE_FROM, -1)), 'MON-RR'))
                      GROUP BY INVENTORY_ITEM_ID,
                               SUBINVENTORY_CODE,
                               SUBSTR (SUBINVENTORY_CODE, 1, LENGTH (SUBINVENTORY_CODE) - 1)
                      UNION ALL
                        SELECT CASE
                                   WHEN P_WHSE_LOC = 112
                                   THEN DECODE (SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                                   'RSN', 'RSN1',
                                                                                   'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1), 
                                                        '1', 'L-1',
                                                        '2', 'L-2',
                                                        '3', 'L-2', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                                   ELSE DECODE (SUBSTR (DECODE (SUBINVENTORY_CODE, 'RML', 'RML1',
                                                                                   'RSN', 'RSN1',
                                                                                   'RFED', 'RFED1', SUBINVENTORY_CODE), -1, 1), 
                                                        '1', 'L-1',
                                                        '2', 'L-2',
                                                        '3', 'L-3', SUBSTR (SUBINVENTORY_CODE, -1, 1))
                               END                               LINE,
                               SUBINVENTORY_CODE,
                               INVENTORY_ITEM_ID,
                               SUM (MMT.TRANSACTION_QUANTITY)    TRANS_QTY
                          FROM APPS.MTL_MATERIAL_TRANSACTIONS MMT
                         WHERE     MMT.ORGANIZATION_ID = P_WHSE_LOC
                               AND TO_CHAR (MMT.TRANSACTION_DATE, 'MON-YYYY') = TO_CHAR (P_DATE_FROM, 'MON-YYYY')
--                               AND TRANSACTION_SOURCE_TYPE_ID <> 5
                               AND SUBINVENTORY_CODE IN ('FED', 'FED1', 'FED2', 'FED3')
                      GROUP BY INVENTORY_ITEM_ID,
                               SUBSTR (SUBINVENTORY_CODE, -1, 1),
                               SUBINVENTORY_CODE) A,
                     APPS.MTL_SYSTEM_ITEMS_B ICMB,
                     PFB_LOC_GROUP          LOC
               WHERE     A.INVENTORY_ITEM_ID = ICMB.INVENTORY_ITEM_ID
                     AND A.LOC_GROUP = TRIM (LOC.LOCATION)
                     AND ICMB.SEGMENT1 IN ('RE-CHIP', 'RE-CHIP-2', 'BOP-RE-CHIP')
                     AND ORGANIZATION_ID = P_WHSE_LOC
            GROUP BY LINE,
                     LOC.LOC_GROUP,
                     DECODE (ITEM_TYPE, 'PFB ITEMS', 'FILM',
                                        'AL', 'Al Wire',
                                        'WIP', 'FILM', ITEM_TYPE);-----------------------------------------------------------END CLOSING
    END;
END;
/
