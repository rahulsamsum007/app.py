To add the `ORGANIZATION_ID` and `TRX_DATE` columns to the query, you need to select these columns and include them in the `GROUP BY` clause. Here’s the modified query:

```sql
SELECT   GCC.SEGMENT1 BSV,
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
         RCTL.CUSTOMER_TRX_ID,
         RCT.ORGANIZATION_ID,
         RCT.TRX_DATE
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
           TO_CHAR (GP.GL_DATE, 'MON-RR'),
           RCT.ORGANIZATION_ID,
           RCT.TRX_DATE
```