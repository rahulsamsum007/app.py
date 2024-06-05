CREATE OR REPLACE PROCEDURE APPS.XXSRF_PFB_NPR_VALUES_TAB_PR (
   ERRBUF           OUT VARCHAR2,
   RETCODE          OUT VARCHAR2,
   P_ORG_ID      IN     NUMBER,
   P_DATE_FROM   IN     VARCHAR2
)
AS
   L_DATE                   DATE;

   
   CURSOR C2 (
      P_ORG_ID                 NUMBER,
      P_PERIOD                 VARCHAR2
   )
   IS
        SELECT   ledger_id,
                 business_unit,
                 prod,
                 SUM (gl_balance) gl_balance
          FROM   (  SELECT   gjh.ledger_id,
                             gcc.segment1 business_unit,
                             CASE
                                WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                  AND  15999
                                THEN
                                   'BOPP'
                                WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                       AND  10111)
                                     AND TO_NUMBER (gcc.segment6) < 14999
                                THEN
                                   'BOPET'
                             END
                                prod,
                             NVL (SUM (accounted_dr), 0)
                             - NVL (SUM (accounted_cr), 0)
                                gl_balance
                      FROM   gl_je_lines gjl,
                             gl_je_headers gjh,
                             gl_ledgers gll,
                             gl_code_combinations_kfv gcc,
                             gl_periods gp,
                             hr_operating_units hou,
                             pfbcustom.pfb_key_flash_gl_master glm
                     WHERE       gjl.je_header_id = gjh.je_header_id
                             AND gjh.ledger_id = hou.set_of_books_id
                             AND hou.organization_id = p_org_id
                             AND gjl.period_name = gjh.period_name
                             AND gjl.ledger_id = gll.ledger_id
                             AND gll.ledger_category_code(+) = 'PRIMARY'
                             AND gjl.code_combination_id =
                                   gcc.code_combination_id
                             AND gjh.period_name = gp.period_name
                             AND UPPER (gjh.period_name) IN
                                      (SELECT   UPPER (period_name)
                                         FROM   gl_periods
                                        WHERE   adjustment_period_flag = 'Y'
                                                AND TO_CHAR (start_date,
                                                             'MON-RR') = p_period
                                       UNION ALL
                                       SELECT   UPPER (period_name)
                                         FROM   gl_periods
                                        WHERE   1 = 1
                                                AND UPPER (period_name) =
                                                      p_period)
                             AND gcc.segment3 = glm.account_number
                             AND gcc.segment5 =
                                   NVL (glm.cost_center_like, gcc.segment5)
                             AND gcc.segment5 <>
                                   NVL (glm.cost_center_not_like, '00')
                             AND glm.sales_flag = 'YES'
                             AND glm.market = 'DOMESTIC'
                  GROUP BY   gjh.ledger_id,
                             gcc.segment1,
                             CASE
                                WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                  AND  15999
                                THEN
                                   'BOPP'
                                WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                       AND  10111)
                                     AND TO_NUMBER (gcc.segment6) < 14999
                                THEN
                                   'BOPET'
                             END)
      GROUP BY   ledger_id, business_unit, prod;

   L_TOT_SALES              NUMBER;
   L_EXP_KG                 NUMBER;
   L_FEXP_KG                NUMBER;
   L_NPR_ALLOC_EXP          NUMBER;
   L_NPR_QTY                NUMBER;
   L_NPR_SALE_VALUE         NUMBER;
   L_TADING_QTY             NUMBER;
   L_TRA_FREIGHT_AMT        NUMBER;
   L_TOT_FREGHT_AMT         NUMBER;
   L_OTHERTHAN_FREGHT_AMT   NUMBER;
   L_DM_AMT                 NUMBER;
   L_DM_AMT_KG              NUMBER;
   L_INTER_COM_SALES        NUMBER;
BEGIN
   SELECT   TO_DATE(TO_CHAR (
                       DECODE (
                          INSTR (P_DATE_FROM, '-'),
                          0,
                          DECODE (
                             INSTR (P_DATE_FROM, '/'),
                             5,
                             TO_DATE (P_DATE_FROM, 'YYYY/MM/DD HH24:MI:SS'),
                             NULL
                          ),
                          1,
                          NULL,
                          TO_DATE (P_DATE_FROM, 'DD-MON-RRRR')
                       ),
                       'DD-MON-RRRR'
                    ))
     INTO   L_DATE
     FROM   DUAL;


   FND_FILE.PUT_LINE (
      FND_FILE.LOG,
      'NPR Calculation Period : ' || TO_CHAR (L_DATE, 'MON-RR')
   );

   DELETE FROM   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
         WHERE       ORG_ID = P_ORG_ID
                 AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                 AND SALE_TYPE = 'Domestic';

   DELETE FROM   XXSRF.XXSRF_PFB_SCRAP_SALES_DTL
         WHERE   ORG_ID = P_ORG_ID
                 AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR');

   COMMIT;

   

      FOR J IN C2 (P_ORG_ID, TO_CHAR (L_DATE, 'MON-RR'))
      LOOP
         IF P_ORG_ID = 278
         THEN
            L_TOT_SALES := 0;
            L_EXP_KG := 0;

            BEGIN
               SELECT   SUM (gl_balance)
                 INTO   L_TOT_FREGHT_AMT
                 FROM   (  SELECT   gjh.ledger_id,
                                    gcc.segment1 business_unit,
                                    CASE
                                       WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                         AND  15999
                                       THEN
                                          'BOPP'
                                       WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                              AND  10111)
                                            AND TO_NUMBER (gcc.segment6) <
                                                  14999
                                       THEN
                                          'BOPET'
                                    END
                                       PROD,
                                    NVL (SUM (accounted_dr), 0)
                                    - NVL (SUM (accounted_cr), 0)
                                       gl_balance
                             FROM   gl_je_lines gjl,
                                    gl_je_headers gjh,
                                    gl_ledgers gll,
                                    gl_code_combinations_kfv gcc,
                                    gl_periods gp,
                                    hr_operating_units hou
                            WHERE       gjl.je_header_id = gjh.je_header_id
                                    AND gjh.ledger_id = hou.SET_OF_BOOKS_ID
                                    AND hou.organization_id = P_ORG_ID
                                    AND gjl.period_name = gjh.period_name
                                    AND gjl.ledger_id = gll.ledger_id
                                    AND gll.ledger_category_code(+) = 'PRIMARY'
                                    AND gjl.code_combination_id =
                                          gcc.code_combination_id
                                    AND gjh.period_name = gp.period_name
                                    AND UPPER (gjh.period_name) IN
                                             (SELECT   UPPER (PERIOD_NAME)
                                                FROM   GL_PERIODS
                                               WHERE   ADJUSTMENT_PERIOD_FLAG =
                                                          'Y'
                                                       AND TO_CHAR (START_DATE,
                                                                    'MON-RR') =
                                                             TO_CHAR (L_DATE,
                                                                      'MON-RR')
                                              UNION ALL
                                              SELECT   UPPER (PERIOD_NAME)
                                                FROM   GL_PERIODS
                                               WHERE   1 = 1
                                                       AND UPPER (PERIOD_NAME) =
                                                             TO_CHAR (L_DATE,
                                                                      'MON-RR'))
                                    AND gcc.segment3 IN
                                             ('414601', '414603', '414609')
                         GROUP BY   gjh.ledger_id,
                                    gcc.segment1,
                                    CASE
                                       WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                         AND  15999
                                       THEN
                                          'BOPP'
                                       WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                              AND  10111)
                                            AND TO_NUMBER (gcc.segment6) <
                                                  14999
                                       THEN
                                          'BOPET'
                                    END)
                WHERE   BUSINESS_UNIT = J.BUSINESS_UNIT AND PROD = J.PROD;
            EXCEPTION
               WHEN OTHERS
               THEN
                  L_TOT_FREGHT_AMT := 0;
            END;


            BEGIN
               SELECT   SUM (gl_balance)
                 INTO   L_OTHERTHAN_FREGHT_AMT
                 FROM   (  SELECT   gjh.ledger_id,
                                    gcc.segment1 business_unit,
                                    CASE
                                       WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                         AND  15999
                                       THEN
                                          'BOPP'
                                       WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                              AND  10111)
                                            AND TO_NUMBER (gcc.segment6) <
                                                  14999
                                       THEN
                                          'BOPET'
                                    END
                                       PROD,
                                    NVL (SUM (accounted_dr), 0)
                                    - NVL (SUM (accounted_cr), 0)
                                       gl_balance
                             FROM   gl_je_lines gjl,
                                    gl_je_headers gjh,
                                    gl_ledgers gll,
                                    gl_code_combinations_kfv gcc,
                                    gl_periods gp,
                                    hr_operating_units hou
                            WHERE       gjl.je_header_id = gjh.je_header_id
                                    AND gjh.ledger_id = hou.SET_OF_BOOKS_ID
                                    AND hou.organization_id = P_ORG_ID
                                    AND gjl.period_name = gjh.period_name
                                    AND gjl.ledger_id = gll.ledger_id
                                    AND gll.ledger_category_code(+) = 'PRIMARY'
                                    AND gjl.code_combination_id =
                                          gcc.code_combination_id
                                    AND gjh.period_name = gp.period_name
                                    AND UPPER (gjh.period_name) IN
                                             (SELECT   UPPER (PERIOD_NAME)
                                                FROM   GL_PERIODS
                                               WHERE   ADJUSTMENT_PERIOD_FLAG =
                                                          'Y'
                                                       AND TO_CHAR (START_DATE,
                                                                    'MON-RR') =
                                                             TO_CHAR (L_DATE,
                                                                      'MON-RR')
                                              UNION ALL
                                              SELECT   UPPER (PERIOD_NAME)
                                                FROM   GL_PERIODS
                                               WHERE   1 = 1
                                                       AND UPPER (PERIOD_NAME) =
                                                             TO_CHAR (L_DATE,
                                                                      'MON-RR'))
                                    AND gcc.segment5 <> '2161'
                                    AND gcc.segment3 IN
                                             ('414605',
                                              '414608',
                                              '311111',
                                              '423429',
                                              '414501',
                                              '311112',
                                              '311118',
                                              '311119')
                         GROUP BY   gjh.ledger_id,
                                    gcc.segment1,
                                    CASE
                                       WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                         AND  15999
                                       THEN
                                          'BOPP'
                                       WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                              AND  10111)
                                            AND TO_NUMBER (gcc.segment6) <
                                                  14999
                                       THEN
                                          'BOPET'
                                    END)
                WHERE   BUSINESS_UNIT = J.BUSINESS_UNIT AND PROD = J.PROD;
            EXCEPTION
               WHEN OTHERS
               THEN
                  L_OTHERTHAN_FREGHT_AMT := 0;
            END;

            SELECT   SUM (SALES_QTY_MT)
              INTO   L_TOT_SALES
              FROM   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
             WHERE       BSV = J.BUSINESS_UNIT
                     AND PRODUCT_SEGMENT = J.PROD
                     AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                     AND SALE_TYPE = 'Domestic';

            BEGIN
               SELECT   SUM (SALES_QTY_MT)
                 INTO   L_INTER_COM_SALES
                 FROM   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
                WHERE       BSV = J.BUSINESS_UNIT
                        AND PRODUCT_SEGMENT = J.PROD
                        AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                        AND MARKET_TYPE = 'Inter Company-DOM' --'Inter Company Sales'
                        AND SALE_TYPE = 'Domestic';
            EXCEPTION
               WHEN OTHERS
               THEN
                  L_INTER_COM_SALES := 0;
            END;

            FND_FILE.PUT_LINE (FND_FILE.LOG,
                               'NPR Business Unit : ' || J.BUSINESS_UNIT);

            FND_FILE.PUT_LINE (FND_FILE.LOG, 'NPR Product Type : ' || J.PROD);

            FND_FILE.PUT_LINE (
               FND_FILE.LOG,
               'NPR Allocation Expences(Other Than freight) : '
               || L_OTHERTHAN_FREGHT_AMT
            );

            FND_FILE.PUT_LINE (
               FND_FILE.LOG,
               'NPR Total Freight Expences : ' || L_TOT_FREGHT_AMT
            );

            FND_FILE.PUT_LINE (
               FND_FILE.LOG,
               'Total Intercompany Sales : ' || L_INTER_COM_SALES
            );

            FND_FILE.PUT_LINE (FND_FILE.LOG, 'Total Sales : ' || L_TOT_SALES);


            L_EXP_KG :=
               (L_OTHERTHAN_FREGHT_AMT / (L_TOT_SALES - L_INTER_COM_SALES))
               / 1000;

            L_FEXP_KG := (L_TOT_FREGHT_AMT / L_TOT_SALES) / 1000;

            FND_FILE.PUT_LINE (FND_FILE.LOG,
                               'Freight Expences Per kg : ' || L_FEXP_KG);

            FND_FILE.PUT_LINE (FND_FILE.LOG,
                               'Other Expences Per kg : ' || L_EXP_KG);

            UPDATE   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
               SET   TOTAL_EXPENSES = J.GL_BALANCE,
                     NET_NPR =
                        ROUND ( (GROSS_NPR - (L_EXP_KG + L_FEXP_KG)), 2)
             WHERE       BSV = J.BUSINESS_UNIT
                     AND PRODUCT_SEGMENT = J.PROD
                     AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                     AND SALE_TYPE = 'Domestic'
                     AND MARKET_TYPE <> 'Inter Company-DOM' --'Inter Company Sales'
                                                           ;

            UPDATE   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
               SET   TOTAL_EXPENSES = J.GL_BALANCE,
                     NET_NPR = ROUND ( (GROSS_NPR - L_FEXP_KG), 2)
             WHERE       BSV = J.BUSINESS_UNIT
                     AND PRODUCT_SEGMENT = J.PROD
                     AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                     AND SALE_TYPE = 'Domestic'
                     AND MARKET_TYPE = 'Inter Company-DOM' --'Inter Company Sales'
                                                          ;

            COMMIT;
         ELSE
            L_TOT_SALES := 0;
            L_EXP_KG := 0;

            SELECT   SUM (SALES_QTY_MT)
              INTO   L_TOT_SALES
              FROM   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
             WHERE       BSV = J.BUSINESS_UNIT
                     AND PRODUCT_SEGMENT = J.PROD
                     AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                     AND SALE_TYPE = 'Domestic';



            L_EXP_KG := (J.GL_BALANCE / L_TOT_SALES) / 1000;

            UPDATE   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
               SET   TOTAL_EXPENSES = J.GL_BALANCE,
                     NET_NPR = ROUND ( (GROSS_NPR - L_EXP_KG), 2)
             WHERE       BSV = J.BUSINESS_UNIT
                     AND PRODUCT_SEGMENT = J.PROD
                     AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                     AND SALE_TYPE = 'Domestic';

            COMMIT;
         END IF;
      END LOOP;
  

      FOR J IN C2 (P_ORG_ID, TO_CHAR (L_DATE, 'MON-RR'))
      LOOP
         L_TOT_SALES := 0;
         L_EXP_KG := 0;
         L_NPR_ALLOC_EXP := 0;
         L_NPR_QTY := 0;
         L_NPR_SALE_VALUE := 0;
         L_TRA_FREIGHT_AMT := 0;
         L_TOT_FREGHT_AMT := 0;
         L_TADING_QTY := 0;
         L_DM_AMT := 0;
         L_DM_AMT_KG := 0;


         BEGIN
            SELECT   ROUND (SUM ( (RATE_PER_KG - NPR) * nfd.inv_quantity), 2)
                        ALLOC_VALUE,
                     SUM (nfd.inv_quantity) QTY,
                     ROUND (SUM (RATE_PER_KG * nfd.inv_quantity)) SALE_VALUE
              INTO   L_NPR_ALLOC_EXP, L_NPR_QTY, L_NPR_SALE_VALUE
              FROM   xxsrf.xxsrf_pfb_npr_details nfd,
                     xxsrf_pfb_npr_headers fnh,
                     ra_cust_trx_types_all rct,
                     mtl_parameters mp,
                     gl_code_combinations gcc,
                     fnd_lookup_values flv
             WHERE   1 = 1
                     AND TO_CHAR (nfd.trx_date, 'MON-RR') =
                           UPPER (TO_CHAR (L_DATE, 'MON-RR'))
                     AND fnh.npr_header_id = nfd.npr_header_id
                     AND fnh.organization_id = mp.organization_id
                     AND mp.material_account = gcc.code_combination_id
                     AND rct.name = flv.meaning
                     AND flv.lookup_type = 'XXSRF_PFB_NPR_DTL'
                     AND nfd.customer_trx_type_id = rct.cust_trx_type_id
                     AND fnh.org_id = P_ORG_ID
                     AND NVL (flv.tag, 'BOPET') = J.PROD
                     AND gcc.segment1 = J.BUSINESS_UNIT
                     AND mp.organization_code NOT IN
                              ('P06', 'P23', 'P24', 'P13');
         EXCEPTION
            WHEN OTHERS
            THEN
               L_NPR_ALLOC_EXP := 0;
               L_NPR_QTY := 0;
               L_NPR_SALE_VALUE := 0;
         END;


         BEGIN
            SELECT   SUM (SALES_QTY_MT) QTY
              INTO   L_TADING_QTY
              FROM   (  SELECT   INV.BSV,
                                 INV.PRODUCT_SEGMENT,
                                 ROUND (
                                    SUM( (NVL (INV.invoice_qty, 0)
                                          - NVL (cm.QUANTITY, 0))
                                        / 1000),
                                    2
                                 )
                                    SALES_QTY_MT
                          FROM   (  SELECT   gcc.segment1 BSV,
                                             mp.organization_code,
                                             NVL (ott.ATTRIBUTE8, 'BOPET')
                                                PRODUCT_SEGMENT,
                                             TO_CHAR (rct.trx_date, 'MON-YY')
                                                PERIOD_NAME,
                                             CASE
                                                WHEN UPPER (CTT.NAME) LIKE
                                                        '%WDA%'
                                                THEN
                                                   'B-Grade ' || msi.attribute9
                                                ELSE
                                                   msi.attribute9
                                             END
                                                mis_category,
                                             ctt.attribute10 Market_Type,
                                             SUM (rctl.quantity_invoiced)
                                                invoice_qty,
                                             SUM (rctl.extended_amount) basic_amt,
                                             0 tax_amount,
                                             msi.inventory_item_id,
                                             rctl.customer_trx_id
                                      FROM   ra_customer_trx_all rct,
                                             ar_customers rc,
                                             ra_customer_trx_lines_all rctl,
                                             mtl_system_items_b msi,
                                             oe_order_headers_all oeh,
                                             oe_order_lines_all oel,
                                             hz_cust_acct_sites_all hcasa,
                                             hz_cust_site_uses_all hcus,
                                             hz_party_sites hpz,
                                             hz_locations hzl,
                                             ra_cust_trx_types_all ctt,
                                             oe_transaction_types_all ott,
                                             mtl_parameters mp,
                                             gl_code_combinations gcc
                                     WHERE   rct.org_id = p_org_id
                                             AND rc.customer_id =
                                                   rct.bill_to_customer_id
                                             AND rctl.customer_trx_id =
                                                   rct.customer_trx_id
                                             AND ctt.cust_trx_type_id =
                                                   rct.cust_trx_type_id
                                             AND msi.inventory_item_id =
                                                   rctl.inventory_item_id
                                             AND oeh.order_type_id =
                                                   ott.transaction_type_id
                                             AND ott.cust_trx_type_id =
                                                   ctt.cust_trx_type_id
                                             AND NVL (ott.attribute4, 'N') = 'N'
                                             AND rctl.warehouse_id =
                                                   msi.organization_id
                                             AND rctl.sales_order =
                                                   oeh.order_number
                                             AND hpz.location_id =
                                                   hzl.location_id
                                             AND oeh.header_id = oel.header_id
                                             AND mp.organization_code IN
                                                      ('P06', 'P23', 'P24', 'P13')
                                             AND oel.line_id =
                                                   TO_NUMBER(rctl.interface_line_attribute6)
                                             AND TO_CHAR (rct.trx_date, 'MON-RR') =
                                                   UPPER (
                                                      TO_CHAR (L_DATE, 'MON-RR')
                                                   )
                                             AND rct.trx_number IS NOT NULL
                                             AND rctl.line_type = 'LINE'
                                             AND hpz.party_site_id =
                                                   hcasa.party_site_id
                                             AND rc.customer_id =
                                                   hcasa.cust_account_id
                                             AND hcus.site_use_id =
                                                   rct.bill_to_site_use_id
                                             AND hcasa.cust_acct_site_id =
                                                   hcus.cust_acct_site_id
                                             AND hcasa.cust_account_id =
                                                   rct.bill_to_customer_id
                                             AND msi.organization_id =
                                                   mp.organization_id
                                             AND mp.material_account =
                                                   gcc.code_combination_id
                                  GROUP BY   gcc.segment1,
                                             mp.organization_code,
                                             msi.attribute9,
                                             msi.inventory_item_id,
                                             rctl.customer_trx_id,
                                             CTT.NAME,
                                             ctt.attribute10,
                                             NVL (ott.ATTRIBUTE8, 'BOPET'),
                                             TO_CHAR (rct.trx_date, 'MON-YY'))
                                 INV,
                                 (  SELECT   rctlo.customer_trx_id,
                                             rctl.inventory_item_id,
                                             ABS (SUM (rctl.extended_amount))
                                                basic_amt,
                                             ABS (SUM (rctl.quantity_credited))
                                                quantity,
                                             0 tax_amount
                                      FROM   ra_cust_trx_types_all ctt,
                                             ra_customer_trx_all rcta,
                                             ra_customer_trx_lines_all rctl,
                                             ra_customer_trx_lines_all rctlo,
                                             oe_order_lines_all ool
                                     WHERE   1 = 1
                                             AND rcta.cust_trx_type_id =
                                                   ctt.cust_trx_type_id
                                             AND rcta.org_id = rctl.org_id
                                             AND rcta.customer_trx_id =
                                                   rctl.customer_trx_id
                                             AND TO_CHAR (rcta.trx_date,
                                                          'MON-RR') =
                                                   UPPER (
                                                      TO_CHAR (L_DATE, 'MON-RR')
                                                   )
                                             AND rctl.line_type = 'LINE'
                                             AND rcta.org_id = P_ORG_ID
                                             AND ctt.TYPE = 'CM'
                                             AND rctl.previous_customer_trx_id =
                                                   rctlo.customer_trx_id
                                             AND rctl.previous_customer_trx_line_id =
                                                   rctlo.customer_trx_line_id
                                             AND ool.line_id =
                                                   rctlo.interface_line_attribute6
                                  GROUP BY   rctlo.customer_trx_id,
                                             rctl.inventory_item_id) CM
                         WHERE   INV.customer_trx_id = CM.customer_trx_id(+)
                                 AND INV.inventory_item_id =
                                       CM.inventory_item_id(+)
                      GROUP BY   INV.BSV, INV.PRODUCT_SEGMENT
                      UNION ALL
                        SELECT   gcc.segment1 BSV,
                                 MAX( (  SELECT   NVL (ott.ATTRIBUTE8, 'BOPET')
                                           FROM   ra_cust_trx_types_all rctt,
                                                  oe_transaction_types_all ott
                                          WHERE   NVL (rctt.attribute8, 'N') =
                                                     'Y'
                                                  AND NVL (ott.attribute4, 'N') =
                                                        'N'
                                                  AND rctt.cust_trx_type_id =
                                                        ott.cust_trx_type_id
                                                  AND rctt.credit_memo_type_id =
                                                        ctt.cust_trx_type_id
                                                  AND rctt.org_id = ctt.org_id
                                       GROUP BY   NVL (ott.ATTRIBUTE8, 'BOPET')))
                                    PRODUCT_SEGMENT,
                                 SUM (rctl.quantity_credited) / 1000 quantity
                          FROM   ra_cust_trx_types_all ctt,
                                 ra_customer_trx_all rcta,
                                 ra_customer_trx_lines_all rctl,
                                 ra_customer_trx_lines_all rctlo,
                                 ra_customer_trx_all rcto,
                                 oe_order_lines_all ool,
                                 mtl_system_items msi,
                                 ra_cust_trx_types_all rctto,
                                 mtl_parameters mp,
                                 gl_code_combinations gcc
                         WHERE   1 = 1
                                 AND rcta.cust_trx_type_id =
                                       ctt.cust_trx_type_id
                                 AND rcta.org_id = rctl.org_id
                                 AND rcta.customer_trx_id =
                                       rctl.customer_trx_id
                                 AND rcto.cust_trx_type_id =
                                       rctto.cust_trx_type_id
                                 AND TO_CHAR (rcta.trx_date, 'MON-RR') =
                                       UPPER (TO_CHAR (L_DATE, 'MON-RR'))
                                 AND rctl.line_type = 'LINE'
                                 AND mp.organization_code IN
                                          ('P06', 'P23', 'P24', 'P13')
                                 AND ctt.TYPE = 'CM'
                                 AND rctl.previous_customer_trx_id =
                                       rctlo.customer_trx_id
                                 AND rctlo.customer_trx_id =
                                       rcto.customer_trx_id
                                 AND TO_CHAR (rcta.trx_date, 'MON-YY') <>
                                       TO_CHAR (rcto.trx_date, 'MON-YY')
                                 AND rctl.previous_customer_trx_line_id =
                                       rctlo.customer_trx_line_id
                                 AND ool.line_id =
                                       rctlo.interface_line_attribute6
                                 AND ool.ship_from_org_id = msi.organization_id
                                 AND rctl.inventory_item_id =
                                       msi.inventory_item_id
                                 AND mp.organization_id = msi.organization_id
                                 AND gcc.code_combination_id =
                                       mp.material_account
                                 AND rcta.org_id = P_ORG_ID
                      GROUP BY   msi.organization_id,
                                 TO_CHAR (rcta.trx_date, 'MON-YY'),
                                 gcc.segment1,
                                 rctto.attribute10,
                                 mp.organization_code)
             WHERE   BSV = J.BUSINESS_UNIT AND PRODUCT_SEGMENT = J.PROD;
         EXCEPTION
            WHEN OTHERS
            THEN
               L_TADING_QTY := 0;
         END;


         BEGIN
            SELECT   SUM (gl_balance)
              INTO   L_TOT_FREGHT_AMT
              FROM   (  SELECT   gjh.ledger_id,
                                 gcc.segment1 business_unit,
                                 CASE
                                    WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                      AND  15999
                                    THEN
                                       'BOPP'
                                    WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                           AND  10111)
                                         AND TO_NUMBER (gcc.segment6) < 14999
                                    THEN
                                       'BOPET'
                                 END
                                    PROD,
                                 NVL (SUM (accounted_dr), 0)
                                 - NVL (SUM (accounted_cr), 0)
                                    gl_balance
                          FROM   gl_je_lines gjl,
                                 gl_je_headers gjh,
                                 gl_ledgers gll,
                                 gl_code_combinations_kfv gcc,
                                 gl_periods gp,
                                 hr_operating_units hou
                         WHERE       gjl.je_header_id = gjh.je_header_id
                                 AND gjh.ledger_id = hou.SET_OF_BOOKS_ID
                                 AND hou.organization_id = P_ORG_ID
                                 AND gjl.period_name = gjh.period_name
                                 AND gjl.ledger_id = gll.ledger_id
                                 AND gll.ledger_category_code(+) = 'PRIMARY'
                                 AND gjl.code_combination_id =
                                       gcc.code_combination_id
                                 AND gjh.period_name = gp.period_name
                                 AND UPPER (gjh.period_name) IN
                                          (SELECT   UPPER (PERIOD_NAME)
                                             FROM   GL_PERIODS
                                            WHERE   ADJUSTMENT_PERIOD_FLAG =
                                                       'Y'
                                                    AND TO_CHAR (START_DATE,
                                                                 'MON-RR') =
                                                          TO_CHAR (L_DATE,
                                                                   'MON-RR')
                                           UNION ALL
                                           SELECT   UPPER (PERIOD_NAME)
                                             FROM   GL_PERIODS
                                            WHERE   1 = 1
                                                    AND UPPER (PERIOD_NAME) =
                                                          TO_CHAR (L_DATE,
                                                                   'MON-RR'))
                                 AND gcc.segment3 = '414601'
                      GROUP BY   gjh.ledger_id,
                                 gcc.segment1,
                                 CASE
                                    WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                                      AND  15999
                                    THEN
                                       'BOPP'
                                    WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                           AND  10111)
                                         AND TO_NUMBER (gcc.segment6) < 14999
                                    THEN
                                       'BOPET'
                                 END)
             WHERE   BUSINESS_UNIT = J.BUSINESS_UNIT AND PROD = J.PROD;
         EXCEPTION
            WHEN OTHERS
            THEN
               L_TOT_FREGHT_AMT := 0;
         END;



         SELECT   SUM (SALES_QTY_MT)
           INTO   L_TOT_SALES
           FROM   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
          WHERE       BSV = J.BUSINESS_UNIT
                  AND PRODUCT_SEGMENT = J.PROD
                  AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                  AND SALE_TYPE = 'Domestic';


         BEGIN
            SELECT   NVL (SUM (NVL (AMOUNT, 0) * NVL (rct.EXCHANGE_RATE, 1)),
                          0)
                        DM_AMT
              INTO   L_DM_AMT
              FROM   ra_cust_trx_line_gl_dist_all gpo,
                     gl_code_combinations gcc,
                     ra_cust_trx_types_all rtt,
                     ra_customer_trx_all rct
             WHERE       1 = 1
                     AND gpo.account_class = 'REV'
                     AND rtt.TYPE = 'DM'
                     AND gpo.code_combination_id = gcc.code_combination_id
                     AND rtt.org_id = rct.org_id
                     AND gpo.org_id = rct.org_id
                     AND rtt.cust_trx_type_id = rct.cust_trx_type_id
                     AND rct.customer_trx_id = gpo.customer_trx_id
                     AND gcc.segment3 = '311101'
                     AND TO_CHAR (gpo.gl_date, 'MON-RR') =
                           TO_CHAR (L_DATE, 'MON-RR')
                     AND gpo.org_id = P_ORG_ID
                     AND gcc.segment1 = J.BUSINESS_UNIT
                     AND NVL (
                           LENGTH(TRIM(TRANSLATE (gcc.segment6,
                                                  ' +.0123456789',
                                                  ' '))),
                           0
                        ) = 0
                     AND CASE
                           WHEN TO_NUMBER (gcc.segment6) BETWEEN 15000
                                                             AND  15999
                           THEN
                              'BOPP'
                           WHEN (TO_NUMBER (gcc.segment6) NOT BETWEEN 10101
                                                                  AND  10111)
                                AND TO_NUMBER (gcc.segment6) < 14999
                           THEN
                              'BOPET'
                        END = J.PROD;
         EXCEPTION
            WHEN OTHERS
            THEN
               L_DM_AMT := 0;
         END;



         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'NPR Business Unit : ' || J.BUSINESS_UNIT);

         FND_FILE.PUT_LINE (FND_FILE.LOG, 'NPR Product Type : ' || J.PROD);

         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'NPR Allocation Expences : ' || L_NPR_ALLOC_EXP);



         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'NPR Total Sales Qty (MT) : ' || L_TOT_SALES);

         FND_FILE.PUT_LINE (
            FND_FILE.LOG,
            'NPR Total Trading Sales Qty (MT) : ' || NVL (L_TADING_QTY, 0)
         );
         FND_FILE.PUT_LINE (
            FND_FILE.LOG,
            'NPR Total Freight Expences : ' || L_TOT_FREGHT_AMT
         );

         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'NPR Total Debit Memo Amount : ' || L_DM_AMT);


         L_TRA_FREIGHT_AMT :=
            (L_TOT_FREGHT_AMT / (L_TOT_SALES + NVL (L_TADING_QTY, 0)))
            * L_TADING_QTY;
         FND_FILE.PUT_LINE (
            FND_FILE.LOG,
            'NPR Total Trading Freight Expences : ' || L_TRA_FREIGHT_AMT
         );


         FND_FILE.PUT_LINE (
            FND_FILE.LOG,
            'NPR Total GL Allocation Expences : ' || J.GL_BALANCE
         );


         L_EXP_KG :=
            ( ( (J.GL_BALANCE - NVL (L_TRA_FREIGHT_AMT, 0)) - L_NPR_ALLOC_EXP)
             / L_TOT_SALES)
            / 1000;

         L_DM_AMT_KG := (L_DM_AMT / L_TOT_SALES) / 1000;

         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'NPR Total Expences per KG : ' || L_EXP_KG);

         FND_FILE.PUT_LINE (FND_FILE.LOG,
                            'Debit Memo Expences per KG : ' || L_DM_AMT_KG);


         UPDATE   XXSRF.XXSRF_PFB_NPR_VALUES_TAB
            SET   TOTAL_EXPENSES =
                     ROUND ( (J.GL_BALANCE - NVL (L_TRA_FREIGHT_AMT, 0)), 2),
                  NET_NPR =
                     ROUND (
                        ( (GROSS_NPR - L_EXP_KG) + NVL (L_DM_AMT_KG, 0)),
                        2
                     ),
                  DM_AMOUNT = L_DM_AMT
          WHERE       BSV = J.BUSINESS_UNIT
                  AND PRODUCT_SEGMENT = J.PROD
                  AND PERIOD_NAME = TO_CHAR (L_DATE, 'MON-RR')
                  AND SALE_TYPE = 'Domestic';

         COMMIT;
      END LOOP;
   END IF;
END XXSRF_PFB_NPR_VALUES_TAB_PR;
/


Freight Per KG: Freight GL Expense / Sales Qty – GL codes for domestic freight cost are 414601 & 414603 and for export freight are 414602, 423426, 414605, 414607 & 414604.
Volume Discount per KG: Volume Discount GL Expense / Sales Qty – GL code for discounts are 311111, 311112, 311118 & 311119.
