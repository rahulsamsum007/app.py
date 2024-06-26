FOR THIS QUERY """
SELECT   :P_ORG_ID ORG_ID,
                 INV.BSV,
                 INV.ORGANIZATION_CODE,
                 INV.PRODUCT_SEGMENT,
                 INV.PERIOD_NAME,
                 INV.MIS_CATEGORY,
                 INV.MARKET_TYPE,
                 ROUND (
                    SUM (
                       (NVL (INV.INVOICE_QTY, 0) - NVL (CM.QUANTITY, 0)) / 1000
                    ),
                    2
                 )
                    SALES_QTY_MT,
                 ROUND (
                    SUM ( (NVL (INV.BASIC_AMT, 0) - NVL (CM.BASIC_AMT, 0))),
                    2
                 )
                    SALE_VALUE,
                 ROUND (
                    SUM( (  NVL (INV.BASIC_AMT, 0)
                          + NVL (INV.TAX_AMOUNT, 0)
                          - ( (NVL (CM.BASIC_AMT, 0) + NVL (CM.TAX_AMOUNT, 0)))))
                    / SUM ( (NVL (INV.INVOICE_QTY, 0) - NVL (CM.QUANTITY, 0))),
                    2
                 )
                    GROSS_NPR
          FROM   (  SELECT   GCC.SEGMENT1 BSV,
                             MP.ORGANIZATION_CODE,
                             NVL (OTT.ATTRIBUTE8, 'BOPET') PRODUCT_SEGMENT,
                             TO_CHAR (GP.GL_DATE, 'MON-RR') PERIOD_NAME,
                             CASE
                                WHEN UPPER (CTT.NAME) LIKE '%WDA%'
                                     AND RCT.ORG_ID = 238
                                THEN
                                   'B-Grade '
                                   || CASE
                                         WHEN UPPER (MSI.ATTRIBUTE9) LIKE
                                                 '%METAL%'
                                         THEN
                                            'Metallized'
                                         ELSE
                                            'Plain'
                                      END
                                WHEN UPPER (CTT.NAME) LIKE '%WDA%'
                                     AND RCT.ORG_ID <> 238
                                THEN
                                   'B-Grade ' || MSI.ATTRIBUTE9
                                ELSE
                                   MSI.ATTRIBUTE9
                             END
                                MIS_CATEGORY,
                             CTT.ATTRIBUTE10 MARKET_TYPE,
                             SUM (RCTL.QUANTITY_INVOICED) INVOICE_QTY,
                             ROUND (
                                SUM(RCTL.EXTENDED_AMOUNT
                                    * NVL (RCT.EXCHANGE_RATE, 1)),
                                2
                             )
                                BASIC_AMT,
                             0 TAX_AMOUNT,
                             MSI.INVENTORY_ITEM_ID,
                             RCTL.CUSTOMER_TRX_ID
                      FROM   RA_CUSTOMER_TRX_ALL RCT,
                             AR_CUSTOMERS RC,
                             RA_CUSTOMER_TRX_LINES_ALL RCTL,
                             MTL_SYSTEM_ITEMS_B MSI,
                             OE_ORDER_HEADERS_ALL OEH,
                             OE_ORDER_LINES_ALL OEL,
                             HZ_CUST_ACCT_SITES_ALL HCASA,
                             HZ_CUST_SITE_USES_ALL HCUS,
                             HZ_PARTY_SITES HPZ,
                             HZ_LOCATIONS HZL,
                             RA_CUST_TRX_TYPES_ALL CTT,
                             OE_TRANSACTION_TYPES_ALL OTT,
                             MTL_PARAMETERS MP,
                             GL_CODE_COMBINATIONS GCC,
                             (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE,
                                         CUSTOMER_TRX_ID
                                  FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                                 WHERE       1 = 1
                                         AND ACCOUNT_CLASS = 'REC'
                                         AND ORG_ID = :P_ORG_ID
                                         AND :P_ORG_ID <> 87
                                         AND LATEST_REC_FLAG = 'Y'
                              GROUP BY   CUSTOMER_TRX_ID) GP
                     WHERE       RCT.ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND RC.CUSTOMER_ID = RCT.BILL_TO_CUSTOMER_ID
                             AND RCTL.CUSTOMER_TRX_ID = RCT.CUSTOMER_TRX_ID
                             AND CTT.CUST_TRX_TYPE_ID = RCT.CUST_TRX_TYPE_ID
                             AND MSI.INVENTORY_ITEM_ID = RCTL.INVENTORY_ITEM_ID
                             AND OEH.ORDER_TYPE_ID = OTT.TRANSACTION_TYPE_ID
                             AND OTT.CUST_TRX_TYPE_ID = CTT.CUST_TRX_TYPE_ID
                             AND NVL (OTT.ATTRIBUTE4, 'N') = 'N'
                             AND NVL (CTT.ATTRIBUTE8, 'N') = 'Y'
                             AND RCTL.WAREHOUSE_ID = MSI.ORGANIZATION_ID
                             AND RCTL.SALES_ORDER = TO_CHAR(OEH.ORDER_NUMBER)
                             AND HPZ.LOCATION_ID = HZL.LOCATION_ID
                             AND OEH.HEADER_ID = OEL.HEADER_ID
                             AND OEL.LINE_ID =
                                   TO_NUMBER (RCTL.INTERFACE_LINE_ATTRIBUTE6)
                             AND TO_CHAR (GP.GL_DATE, 'MON-RR') =
                                   UPPER (:P_PERIOD)
                             AND RCT.CUSTOMER_TRX_ID = GP.CUSTOMER_TRX_ID
                             AND RCT.TRX_NUMBER IS NOT NULL
                             AND RCTL.LINE_TYPE = 'LINE'
                             AND NVL (CTT.ATTRIBUTE10, 'XX') =
                                   CASE
                                      WHEN CTT.ORG_ID = 1397
                                      THEN
                                         'Domestic Sales'
                                      ELSE
                                         NVL (CTT.ATTRIBUTE10, 'XX')
                                   END
                             AND HPZ.PARTY_SITE_ID = HCASA.PARTY_SITE_ID
                             AND RC.CUSTOMER_ID = HCASA.CUST_ACCOUNT_ID
                             AND HCUS.SITE_USE_ID = RCT.BILL_TO_SITE_USE_ID
                             AND HCASA.CUST_ACCT_SITE_ID = HCUS.CUST_ACCT_SITE_ID
                             AND HCASA.CUST_ACCOUNT_ID = RCT.BILL_TO_CUSTOMER_ID
                             AND MSI.ORGANIZATION_ID = MP.ORGANIZATION_ID
                             AND MP.MATERIAL_ACCOUNT = GCC.CODE_COMBINATION_ID
                  GROUP BY   GCC.SEGMENT1,
                             MP.ORGANIZATION_CODE,
                             MSI.ATTRIBUTE9,
                             MSI.INVENTORY_ITEM_ID,
                             RCTL.CUSTOMER_TRX_ID,
                             CTT.NAME,
                             RCT.ORG_ID,
                             CTT.ATTRIBUTE10,
                             NVL (OTT.ATTRIBUTE8, 'BOPET'),
                             TO_CHAR (GP.GL_DATE, 'MON-RR')) INV,
                 (  SELECT   RCTLO.CUSTOMER_TRX_ID,
                             RCTL.INVENTORY_ITEM_ID,
                             ABS(SUM(RCTL.EXTENDED_AMOUNT
                                     * NVL (RCTA.EXCHANGE_RATE, 1)))
                                BASIC_AMT,
                             ABS (SUM (RCTL.QUANTITY_CREDITED)) QUANTITY,
                             0 TAX_AMOUNT
                      FROM   RA_CUST_TRX_TYPES_ALL CTT,
                             RA_CUSTOMER_TRX_ALL RCTA,
                             RA_CUSTOMER_TRX_LINES_ALL RCTL,
                             RA_CUSTOMER_TRX_LINES_ALL RCTLO,
                             OE_ORDER_LINES_ALL OOL,
                             (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE,
                                         CUSTOMER_TRX_ID
                                  FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                                 WHERE       1 = 1
                                         AND ACCOUNT_CLASS = 'REC'
                                         AND ORG_ID = :P_ORG_ID
                                         AND :P_ORG_ID <> 87
                                         AND LATEST_REC_FLAG = 'Y'
                              GROUP BY   CUSTOMER_TRX_ID) GP
                     WHERE       1 = 1
                             AND RCTA.CUST_TRX_TYPE_ID = CTT.CUST_TRX_TYPE_ID
                             AND RCTA.ORG_ID = RCTL.ORG_ID
                             AND RCTA.CUSTOMER_TRX_ID = RCTL.CUSTOMER_TRX_ID
                             AND RCTA.CUSTOMER_TRX_ID = GP.CUSTOMER_TRX_ID
                             AND TO_CHAR (GP.GL_DATE, 'MON-RR') =
                                   UPPER (:P_PERIOD)
                             AND RCTL.LINE_TYPE = 'LINE'
                             AND RCTA.ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND CTT.TYPE = 'CM'
                             AND RCTL.PREVIOUS_CUSTOMER_TRX_ID =
                                   RCTLO.CUSTOMER_TRX_ID
                             AND RCTL.PREVIOUS_CUSTOMER_TRX_LINE_ID =
                                   RCTLO.CUSTOMER_TRX_LINE_ID
                             AND OOL.LINE_ID = RCTLO.INTERFACE_LINE_ATTRIBUTE6
                             AND EXISTS
                                   (SELECT   1
                                      FROM   RA_CUST_TRX_TYPES_ALL RCTT
                                     WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                             AND RCTT.CREDIT_MEMO_TYPE_ID =
                                                   CTT.CUST_TRX_TYPE_ID
                                             AND RCTT.ORG_ID = CTT.ORG_ID
                                             AND NVL (RCTT.ATTRIBUTE10, 'XX') =
                                                   CASE
                                                      WHEN RCTT.ORG_ID = 1397
                                                      THEN
                                                         'Domestic Sales'
                                                      ELSE
                                                         NVL (CTT.ATTRIBUTE10,
                                                              'XX')
                                                   END)
                  GROUP BY   RCTLO.CUSTOMER_TRX_ID, RCTL.INVENTORY_ITEM_ID
                  UNION ALL
                    SELECT   RCTLO.CUSTOMER_TRX_ID,
                             RCTL.INVENTORY_ITEM_ID,
                             ABS(SUM(RCTL.EXTENDED_AMOUNT
                                     * NVL (RCTA.EXCHANGE_RATE, 1)))
                                BASIC_AMT,
                             ABS (SUM (RCTL.QUANTITY_CREDITED)) QUANTITY,
                             0 TAX_AMOUNT
                      FROM   RA_CUST_TRX_TYPES_ALL CTT,
                             RA_CUSTOMER_TRX_ALL RCTA,
                             RA_CUSTOMER_TRX_LINES_ALL RCTL,
                             RA_CUSTOMER_TRX_LINES_ALL RCTLO,
                             OE_ORDER_LINES_ALL OOL,
                             (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE,
                                         CUSTOMER_TRX_ID
                                  FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                                 WHERE       1 = 1
                                         AND ACCOUNT_CLASS = 'REC'
                                         AND ORG_ID = :P_ORG_ID
                                         AND :P_ORG_ID <> 87
                                         AND LATEST_REC_FLAG = 'Y'
                              GROUP BY   CUSTOMER_TRX_ID) GP
                     WHERE       1 = 1
                             AND RCTA.CUST_TRX_TYPE_ID = CTT.CUST_TRX_TYPE_ID
                             AND RCTA.ORG_ID = RCTL.ORG_ID
                             AND RCTA.CUSTOMER_TRX_ID = RCTL.CUSTOMER_TRX_ID
                             AND RCTA.CUSTOMER_TRX_ID = GP.CUSTOMER_TRX_ID
                             AND TO_CHAR (GP.GL_DATE, 'MON-RR') =
                                   UPPER (:P_PERIOD)
                             AND RCTL.LINE_TYPE = 'LINE'
                             AND RCTA.ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND CTT.TYPE = 'CM'
                             AND RCTL.PREVIOUS_CUSTOMER_TRX_ID IS NULL
                             AND OOL.RETURN_ATTRIBUTE1 = RCTLO.CUSTOMER_TRX_ID
                             AND OOL.RETURN_ATTRIBUTE2 =
                                   RCTLO.CUSTOMER_TRX_LINE_ID
                             AND OOL.LINE_ID = RCTL.INTERFACE_LINE_ATTRIBUTE6
                             AND EXISTS
                                   (SELECT   1
                                      FROM   RA_CUST_TRX_TYPES_ALL RCTT
                                     WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                             AND RCTT.CREDIT_MEMO_TYPE_ID =
                                                   CTT.CUST_TRX_TYPE_ID
                                             AND RCTT.ORG_ID = CTT.ORG_ID
                                             AND NVL (RCTT.ATTRIBUTE10, 'XX') =
                                                   CASE
                                                      WHEN RCTT.ORG_ID = 1397
                                                      THEN
                                                         'Domestic Sales'
                                                      ELSE
                                                         NVL (CTT.ATTRIBUTE10,
                                                              'XX')
                                                   END)
                  GROUP BY   RCTLO.CUSTOMER_TRX_ID, RCTL.INVENTORY_ITEM_ID) CM
         WHERE   INV.CUSTOMER_TRX_ID = CM.CUSTOMER_TRX_ID(+)
                 AND INV.INVENTORY_ITEM_ID = CM.INVENTORY_ITEM_ID(+)
      GROUP BY   INV.BSV,
                 INV.ORGANIZATION_CODE,
                 INV.PRODUCT_SEGMENT,
                 INV.PERIOD_NAME,
                 INV.MIS_CATEGORY,
                 INV.MARKET_TYPE
      UNION
        SELECT   :P_ORG_ID ORG_ID,
                 GCC.SEGMENT1 BSV,
                 MP.ORGANIZATION_CODE,
                 NVL (
                    CTT.ATTRIBUTE11,
                    MAX( (  SELECT   NVL (OTT.ATTRIBUTE8, 'BOPET')
                              FROM   RA_CUST_TRX_TYPES_ALL RCTT,
                                     OE_TRANSACTION_TYPES_ALL OTT
                             WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                     AND NVL (OTT.ATTRIBUTE4, 'N') = 'N'
                                     AND RCTT.CUST_TRX_TYPE_ID =
                                           OTT.CUST_TRX_TYPE_ID
                                     AND RCTT.CREDIT_MEMO_TYPE_ID =
                                           CTT.CUST_TRX_TYPE_ID
                                     AND ORDER_CATEGORY_CODE <> 'RETURN'
                                     AND RCTT.ORG_ID = CTT.ORG_ID
                          GROUP BY   NVL (OTT.ATTRIBUTE8, 'BOPET')))
                 )
                    PRODUCT_SEGMENT,
                 TO_CHAR (GPC.GL_DATE, 'MON-RR') PERIOD_NAME,
                 'Sales Return' MIS_CATEGORY,
                 RCTTO.ATTRIBUTE10 MARKET_TYPE,
                 SUM (RCTL.QUANTITY_CREDITED) / 1000 QUANTITY,
                 ROUND (
                    SUM( (RCTL.QUANTITY_CREDITED * RCTL.UNIT_SELLING_PRICE)
                        * NVL (RCTA.EXCHANGE_RATE, 1)),
                    2
                 )
                    SALE_VALUE,
                 ROUND (
                    (SUM (RCTL.QUANTITY_CREDITED * RCTL.UNIT_SELLING_PRICE)
                     / (SUM (RCTL.QUANTITY_CREDITED))),
                    2
                 )
                    NPR_RS_KG
          FROM   RA_CUST_TRX_TYPES_ALL CTT,
                 RA_CUSTOMER_TRX_ALL RCTA,
                 RA_CUSTOMER_TRX_LINES_ALL RCTL,
                 RA_CUSTOMER_TRX_LINES_ALL RCTLO,
                 RA_CUSTOMER_TRX_ALL RCTO,
                 OE_ORDER_LINES_ALL OOL,
                 MTL_SYSTEM_ITEMS MSI,
                 RA_CUST_TRX_TYPES_ALL RCTTO,
                 MTL_PARAMETERS MP,
                 GL_CODE_COMBINATIONS GCC,
                 (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE, CUSTOMER_TRX_ID
                      FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                     WHERE       1 = 1
                             AND ACCOUNT_CLASS = 'REC'
                             AND ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND LATEST_REC_FLAG = 'Y'
                  GROUP BY   CUSTOMER_TRX_ID) GPO,
                 (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE, CUSTOMER_TRX_ID
                      FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                     WHERE       1 = 1
                             AND ACCOUNT_CLASS = 'REC'
                             AND ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND LATEST_REC_FLAG = 'Y'
                  GROUP BY   CUSTOMER_TRX_ID) GPC
         WHERE       1 = 1
                 AND RCTA.CUST_TRX_TYPE_ID = CTT.CUST_TRX_TYPE_ID
                 AND RCTA.ORG_ID = RCTL.ORG_ID
                 AND RCTA.CUSTOMER_TRX_ID = RCTL.CUSTOMER_TRX_ID
                 AND RCTO.CUST_TRX_TYPE_ID = RCTTO.CUST_TRX_TYPE_ID
                 AND RCTA.CUSTOMER_TRX_ID = GPC.CUSTOMER_TRX_ID
                 AND TO_CHAR (GPC.GL_DATE, 'MON-RR') = UPPER (:P_PERIOD)
                 AND RCTO.CUSTOMER_TRX_ID = GPO.CUSTOMER_TRX_ID
                 AND RCTL.LINE_TYPE = 'LINE'
                 AND CTT.TYPE = 'CM'
                 AND RCTL.PREVIOUS_CUSTOMER_TRX_ID = RCTLO.CUSTOMER_TRX_ID
                 AND RCTLO.CUSTOMER_TRX_ID = RCTO.CUSTOMER_TRX_ID
                 AND TO_CHAR (GPC.GL_DATE, 'MON-RR') <>
                       TO_CHAR (GPO.GL_DATE, 'MON-RR')
                 AND RCTL.PREVIOUS_CUSTOMER_TRX_LINE_ID =
                       RCTLO.CUSTOMER_TRX_LINE_ID
                 AND RCTL.PREVIOUS_CUSTOMER_TRX_LINE_ID IS NOT NULL
                 AND OOL.LINE_ID = RCTLO.INTERFACE_LINE_ATTRIBUTE6
                 AND OOL.SHIP_FROM_ORG_ID = MSI.ORGANIZATION_ID
                 AND RCTL.INVENTORY_ITEM_ID = MSI.INVENTORY_ITEM_ID
                 AND MP.ORGANIZATION_ID = MSI.ORGANIZATION_ID
                 AND GCC.CODE_COMBINATION_ID = MP.MATERIAL_ACCOUNT
                 AND RCTA.ORG_ID = :P_ORG_ID
                 AND :P_ORG_ID <> 87
                 AND EXISTS
                       (SELECT   1
                          FROM   RA_CUST_TRX_TYPES_ALL RCTT,
                                 OE_TRANSACTION_TYPES_ALL OTT
                         WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                 AND NVL (OTT.ATTRIBUTE4, 'N') = 'N'
                                 AND RCTT.CUST_TRX_TYPE_ID =
                                       OTT.CUST_TRX_TYPE_ID
                                 AND RCTT.CREDIT_MEMO_TYPE_ID =
                                       CTT.CUST_TRX_TYPE_ID
                                 AND ORDER_CATEGORY_CODE <> 'RETURN'
                                 AND RCTT.ORG_ID = CTT.ORG_ID
                                 AND NVL (RCTT.ATTRIBUTE10, 'XX') =
                                       CASE
                                          WHEN RCTT.ORG_ID = 1397
                                          THEN
                                             'Domestic Sales'
                                          ELSE
                                             NVL (CTT.ATTRIBUTE10, 'XX')
                                       END)
      GROUP BY   MSI.ORGANIZATION_ID,
                 TO_CHAR (GPC.GL_DATE, 'MON-RR'),
                 GCC.SEGMENT1,
                 RCTTO.ATTRIBUTE10,
                 MP.ORGANIZATION_CODE,
                 CTT.ATTRIBUTE11
      UNION
        SELECT   :P_ORG_ID ORG_ID,
                 GCC.SEGMENT1 BSV,
                 MP.ORGANIZATION_CODE,
                 NVL (
                    CTT.ATTRIBUTE11,
                    MAX( (  SELECT   NVL (OTT.ATTRIBUTE8, 'BOPET')
                              FROM   RA_CUST_TRX_TYPES_ALL RCTT,
                                     OE_TRANSACTION_TYPES_ALL OTT
                             WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                     AND NVL (OTT.ATTRIBUTE4, 'N') = 'N'
                                     AND RCTT.CUST_TRX_TYPE_ID =
                                           OTT.CUST_TRX_TYPE_ID
                                     AND ORDER_CATEGORY_CODE <> 'RETURN'
                                     AND RCTT.CREDIT_MEMO_TYPE_ID =
                                           CTT.CUST_TRX_TYPE_ID
                                     AND RCTT.ORG_ID = CTT.ORG_ID
                          GROUP BY   NVL (OTT.ATTRIBUTE8, 'BOPET')))
                 )
                    PRODUCT_SEGMENT,
                 TO_CHAR (GPC.GL_DATE, 'MON-RR') PERIOD_NAME,
                 'Sales Return' MIS_CATEGORY,
                 RCTTO.ATTRIBUTE10 MARKET_TYPE,
                 SUM (RCTL.QUANTITY_CREDITED) / 1000 QUANTITY,
                 ROUND (
                    SUM( (RCTL.QUANTITY_CREDITED * RCTL.UNIT_SELLING_PRICE)
                        * NVL (RCTA.EXCHANGE_RATE, 1)),
                    2
                 )
                    SALE_VALUE,
                 ROUND (
                    (SUM (RCTL.QUANTITY_CREDITED * RCTL.UNIT_SELLING_PRICE)
                     / (SUM (RCTL.QUANTITY_CREDITED))),
                    2
                 )
                    NPR_RS_KG
          FROM   RA_CUST_TRX_TYPES_ALL CTT,
                 RA_CUSTOMER_TRX_ALL RCTA,
                 RA_CUSTOMER_TRX_LINES_ALL RCTL,
                 RA_CUSTOMER_TRX_LINES_ALL RCTLO,
                 RA_CUSTOMER_TRX_ALL RCTO,
                 OE_ORDER_LINES_ALL OOL,
                 MTL_SYSTEM_ITEMS MSI,
                 RA_CUST_TRX_TYPES_ALL RCTTO,
                 MTL_PARAMETERS MP,
                 GL_CODE_COMBINATIONS GCC,
                 (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE, CUSTOMER_TRX_ID
                      FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                     WHERE       1 = 1
                             AND ACCOUNT_CLASS = 'REC'
                             AND ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND LATEST_REC_FLAG = 'Y'
                  GROUP BY   CUSTOMER_TRX_ID) GPO,
                 (  SELECT   TRUNC (MAX (GL_DATE)) GL_DATE, CUSTOMER_TRX_ID
                      FROM   RA_CUST_TRX_LINE_GL_DIST_ALL
                     WHERE       1 = 1
                             AND ACCOUNT_CLASS = 'REC'
                             AND ORG_ID = :P_ORG_ID
                             AND :P_ORG_ID <> 87
                             AND LATEST_REC_FLAG = 'Y'
                  GROUP BY   CUSTOMER_TRX_ID) GPC
         WHERE       1 = 1
                 AND RCTA.CUST_TRX_TYPE_ID = CTT.CUST_TRX_TYPE_ID
                 AND RCTA.ORG_ID = RCTL.ORG_ID
                 AND RCTA.CUSTOMER_TRX_ID = RCTL.CUSTOMER_TRX_ID
                 AND RCTO.CUST_TRX_TYPE_ID = RCTTO.CUST_TRX_TYPE_ID
                 AND RCTA.CUSTOMER_TRX_ID = GPC.CUSTOMER_TRX_ID
                 AND TO_CHAR (GPC.GL_DATE, 'MON-RR') = UPPER (:P_PERIOD)
                 AND RCTO.CUSTOMER_TRX_ID = GPO.CUSTOMER_TRX_ID
                 AND RCTL.LINE_TYPE = 'LINE'
                 AND CTT.TYPE = 'CM'
                 AND OOL.RETURN_ATTRIBUTE1 = RCTLO.CUSTOMER_TRX_ID
                 AND RCTLO.CUSTOMER_TRX_ID = RCTO.CUSTOMER_TRX_ID
                 AND TO_CHAR (GPC.GL_DATE, 'MON-RR') <>
                       TO_CHAR (GPO.GL_DATE, 'MON-RR')
                 AND OOL.RETURN_ATTRIBUTE2 = RCTLO.CUSTOMER_TRX_LINE_ID
                 AND OOL.LINE_ID = RCTL.INTERFACE_LINE_ATTRIBUTE6
                 AND OOL.SHIP_FROM_ORG_ID = MSI.ORGANIZATION_ID
                 AND RCTL.INVENTORY_ITEM_ID = MSI.INVENTORY_ITEM_ID
                 AND MP.ORGANIZATION_ID = MSI.ORGANIZATION_ID
                 AND GCC.CODE_COMBINATION_ID = MP.MATERIAL_ACCOUNT
                 AND RCTL.PREVIOUS_CUSTOMER_TRX_LINE_ID IS NULL
                 AND RCTA.ORG_ID = :P_ORG_ID
                 AND :P_ORG_ID <> 87
                 AND EXISTS
                       (SELECT   1
                          FROM   RA_CUST_TRX_TYPES_ALL RCTT,
                                 OE_TRANSACTION_TYPES_ALL OTT
                         WHERE   NVL (RCTT.ATTRIBUTE8, 'N') = 'Y'
                                 AND NVL (OTT.ATTRIBUTE4, 'N') = 'N'
                                 AND RCTT.CUST_TRX_TYPE_ID =
                                       OTT.CUST_TRX_TYPE_ID
                                 AND RCTT.CREDIT_MEMO_TYPE_ID =
                                       CTT.CUST_TRX_TYPE_ID
                                 AND RCTT.ORG_ID = CTT.ORG_ID
                                 AND ORDER_CATEGORY_CODE <> 'RETURN'
                                 AND NVL (RCTT.ATTRIBUTE10, 'XX') =
                                       CASE
                                          WHEN RCTT.ORG_ID = 1397
                                          THEN
                                             'Domestic Sales'
                                          ELSE
                                             NVL (CTT.ATTRIBUTE10, 'XX')
                                       END)
      GROUP BY   MSI.ORGANIZATION_ID,
                 TO_CHAR (GPC.GL_DATE, 'MON-RR'),
                 GCC.SEGMENT1,
                 RCTTO.ATTRIBUTE10,
                 MP.ORGANIZATION_CODE,
                 CTT.ATTRIBUTE11;
"""
AND TO THIS INSERT FOR I IN C1 (P_ORG_ID, TO_CHAR (L_DATE, 'MON-RR'))
      LOOP
         IF I.ORGANIZATION_CODE <> 'P75'
         THEN
            INSERT INTO XXSRF.XXSRF_PFB_NPR_VALUES_TAB_TEST (ORG_ID,
                                                        BSV,
                                                        ORGANIZATION_CODE,
                                                        PRODUCT_SEGMENT,
                                                        PERIOD_NAME,
                                                        MIS_CATEGORY,
                                                        MARKET_TYPE,
                                                        SALES_QTY_MT,
                                                        SALE_VALUE,
                                                        GROSS_NPR,
                                                        SALE_TYPE)
              VALUES   (I.ORG_ID,
                        I.BSV,
                        I.ORGANIZATION_CODE,
                        I.PRODUCT_SEGMENT,
                        I.PERIOD_NAME,
                        I.MIS_CATEGORY,
                        I.MARKET_TYPE,
                        I.SALES_QTY_MT,
                        I.SALE_VALUE,
                        I.GROSS_NPR,
                        'Domestic'); 
1. I WANT YOU TO ADD ORGANIZATION_IS AND TRX_DATE COLUMN TO THE QUERY 
