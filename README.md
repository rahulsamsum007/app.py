The `ORA-01475: divisor is equal to zero` error occurs because there is a division operation where the divisor can be zero. To avoid this, we need to add checks to ensure the divisor is not zero before performing the division. Here's the revised query with the necessary checks:

```sql
SELECT :P_ORG_ID Org_id,
       inv.bsv,
       inv.organization_code,
       inv.product_segment,
       inv.period_name,
       inv.mis_category,
       inv.market_type,
       inv.item,
       inv.customer_name,  -- New column added
       ROUND(SUM((NVL(inv.invoice_qty, 0) - NVL(cm.quantity, 0)) / 1000), 2) sales_qty_mt,
       ROUND(SUM((NVL(inv.basic_amt, 0) - NVL(cm.basic_amt, 0))), 2) SALE_VALUE,
       ROUND(
         SUM(
           (NVL(inv.basic_amt, 0) + NVL(inv.tax_amount, 0) - (NVL(cm.basic_amt, 0) + NVL(cm.tax_amount, 0)))
         ) / NULLIF(SUM((NVL(inv.invoice_qty, 0) - NVL(cm.quantity, 0))), 0), 2
       ) GROSS_NPR
FROM (
    SELECT gcc.segment1 bsv,
           mp.organization_code,
           NVL(ott.attribute8, 'BOPET') product_segment,
           TO_CHAR(gp.gl_date, 'MON-RR') period_name,
           CASE
              WHEN UPPER(ctt.name) LIKE '%WDA%' AND rct.org_id = 238 THEN
                   'B-Grade ' || CASE
                                    WHEN UPPER(msi.attribute9) LIKE '%METAL%' THEN 'Metallized'
                                    ELSE 'Plain'
                                 END
              WHEN UPPER(ctt.name) LIKE '%WDA%' AND rct.org_id <> 238 THEN
                   'B-Grade ' || msi.attribute9
              ELSE msi.attribute9
           END mis_category,
           ctt.attribute10 market_type,
           msi.segment1 item, -- New column added
           rc.customer_name,  -- New column added
           SUM(rctl.quantity_invoiced) invoice_qty,
           ROUND(SUM(rctl.extended_amount * NVL(rct.EXCHANGE_RATE, 1)), 2) basic_amt,
           0 tax_amount,
           msi.inventory_item_id,
           rctl.customer_trx_id
    FROM ra_customer_trx_all rct,
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
         gl_code_combinations gcc,
         (SELECT TRUNC(MAX(gl_date)) gl_date,
                 customer_trx_id
          FROM ra_cust_trx_line_gl_dist_all
          WHERE 1 = 1
                AND account_class = 'REC'
                AND org_id = :P_ORG_ID
                AND :P_ORG_ID <> 87
                AND latest_rec_flag = 'Y'
          GROUP BY customer_trx_id) gp
    WHERE rct.org_id = :P_ORG_ID
          AND :P_ORG_ID <> 87
          AND rc.customer_id = rct.bill_to_customer_id
          AND rc.customer_id = hcasa.cust_account_id
          AND rctl.customer_trx_id = rct.customer_trx_id
          AND ctt.cust_trx_type_id = rct.cust_trx_type_id
          AND msi.inventory_item_id = rctl.inventory_item_id
          AND oeh.order_type_id = ott.transaction_type_id
          AND ott.cust_trx_type_id = ctt.cust_trx_type_id
          AND NVL(ott.attribute4, 'N') = 'N'
          AND NVL(ctt.attribute8, 'N') = 'Y'
          AND rctl.warehouse_id = msi.organization_id
          AND rctl.sales_order = TO_CHAR(oeh.order_number)
          AND hpz.location_id = hzl.location_id
          AND oeh.header_id = oel.header_id
          AND oel.line_id = TO_NUMBER(rctl.interface_line_attribute6)
          AND TO_CHAR(gp.gl_date, 'MON-RR') = UPPER(:P_PERIOD)
          AND rct.customer_trx_id = gp.customer_trx_id
          AND rct.trx_number IS NOT NULL
          AND rctl.line_type = 'LINE'
          AND NVL(ctt.attribute10, 'XX') = CASE
                                              WHEN ctt.org_id = 1397 THEN 'Domestic Sales'
                                              ELSE NVL(ctt.attribute10, 'XX')
                                           END
          AND hpz.party_site_id = hcasa.party_site_id
          AND hcus.site_use_id = rct.bill_to_site_use_id
          AND hcasa.cust_acct_site_id = hcus.cust_acct_site_id
          AND hcasa.cust_account_id = rct.bill_to_customer_id
          AND msi.organization_id = mp.organization_id
          AND mp.material_account = gcc.code_combination_id
    GROUP BY gcc.segment1,
             mp.organization_code,
             msi.attribute9,
             msi.inventory_item_id,
             msi.segment1,
             rctl.customer_trx_id,
             ctt.name,
             rct.org_id,
             ctt.attribute10,
             NVL(ott.attribute8, 'BOPET'),
             TO_CHAR(gp.gl_date, 'MON-RR'),
             rc.customer_name  -- New column added
) inv,
(
    SELECT rctlo.customer_trx_id,
           rctl.inventory_item_id,
           ABS(SUM(rctl.extended_amount * NVL(rcta.EXCHANGE_RATE, 1))) basic_amt,
           ABS(SUM(rctl.quantity_credited)) quantity,
           0 tax_amount
    FROM ra_cust_trx_types_all ctt,
         ra_customer_trx_all rcta,
         ra_customer_trx_lines_all rctl,
         ra_customer_trx_lines_all rctlo,
         oe_order_lines_all ool,
         (SELECT TRUNC(MAX(gl_date)) gl_date,
                 customer_trx_id
          FROM ra_cust_trx_line_gl_dist_all
          WHERE 1 = 1
                AND account_class = 'REC'
                AND org_id = :P_ORG_ID
                AND :P_ORG_ID <> 87
                AND latest_rec_flag = 'Y'
          GROUP BY customer_trx_id) gp
    WHERE 1 = 1
          AND rcta.cust_trx_type_id = ctt.cust_trx_type_id
          AND rcta.org_id = rctl.org_id
          AND rcta.customer_trx_id = rctl.customer_trx_id
          AND rcta.customer_trx_id = gp.customer_trx_id
          AND TO_CHAR(gp.gl_date, 'MON-RR') = UPPER(:P_PERIOD)
          AND rctl.line_type = 'LINE'
          AND rcta.org_id = :P_ORG_ID
          AND :P_ORG_ID <> 87
          AND ctt.TYPE = 'CM'
          AND rctl.previous_customer_trx_id = rctlo.customer_trx_id
          AND rctl.previous_customer_trx_line_id = rctlo.customer_trx_line_id
          AND ool.line_id = rctlo.interface_line_attribute6
          AND EXISTS (
              SELECT 1
              FROM ra_cust_trx_types_all rctt
              WHERE NVL(rctt.attribute8, 'N') = 'Y'
                    AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                    AND rctt.org_id = ctt.org_id
                    AND NVL(rctt.attribute10, 'XX') = CASE
                                                        WHEN rctt.org_id = 1397 THEN 'Domestic Sales'
                                                        ELSE NVL(ctt.attribute10, 'XX')
                                                     END)
    GROUP BY rctlo.customer_trx_id,
             rctl.inventory_item_id
    UNION ALL
    SELECT rctlo.customer_trx_id,
           rctl.inventory_item_id,
           ABS(SUM(rctl.extended_amount * NVL(rcta.EXCHANGE_RATE, 1))) basic_amt,
           ABS(SUM(rctl.quantity_credited)) quantity,
           0 tax_amount
    FROM ra_cust_trx_types_all ctt,
         ra_customer_trx_all rcta,
         ra_customer_trx_lines_all rctl,
         ra_customer_trx_lines_all rctlo,
         oe_order_lines_all ool,
         (SELECT TRUNC(MAX(gl_date)) gl_date,
                 customer_trx_id
          FROM ra_cust_trx_line_gl_dist_all
          WHERE 1 = 1
                AND account_class = 'REC'
                AND org_id = :P_ORG_ID
                AND :P_ORG_ID <> 87
                AND latest_rec_flag = 'Y'
          GROUP BY customer_trx_id) gp
    WHERE 1 = 1
          AND rcta.cust_trx_type_id = ctt.cust_trx_type_id
          AND rcta.org_id = rctl.org_id
          AND rcta.customer_trx_id = rctl.customer_trx_id
          AND rcta.customer_trx_id = gp.customer_trx_id
          AND TO_CHAR(gp.gl_date, 'MON-RR') = U




```sql
          AND TO_CHAR(gp.gl_date, 'MON-RR') = UPPER(:P_PERIOD)
          AND rctl.line_type = 'LINE'
          AND rcta.org_id = :P_ORG_ID
          AND :P_ORG_ID <> 87
          AND ctt.TYPE = 'CM'
          AND rctl.previous_customer_trx_id IS NULL
          AND ool.return_attribute1 = rctlo.customer_trx_id
          AND ool.return_attribute2 = rctlo.customer_trx_line_id
          AND ool.line_id = rctl.interface_line_attribute6
          AND EXISTS (
              SELECT 1
              FROM ra_cust_trx_types_all rctt
              WHERE NVL(rctt.attribute8, 'N') = 'Y'
                    AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                    AND rctt.org_id = ctt.org_id
                    AND NVL(rctt.attribute10, 'XX') = CASE
                                                        WHEN rctt.org_id = 1397 THEN 'Domestic Sales'
                                                        ELSE NVL(ctt.attribute10, 'XX')
                                                     END)
    GROUP BY rctlo.customer_trx_id,
             rctl.inventory_item_id
) cm
WHERE inv.customer_trx_id = cm.customer_trx_id(+)
     AND inv.inventory_item_id = cm.inventory_item_id(+)
GROUP BY inv.bsv,
        inv.organization_code,
        inv.product_segment,
        inv.period_name,
        inv.mis_category,
        inv.market_type,
        inv.item,
        inv.customer_name
```

### Explanation of Changes

1. **NULLIF for Division**: To avoid division by zero errors, the `NULLIF` function is used:
   ```sql
   ROUND(
     SUM(
       (NVL(inv.basic_amt, 0) + NVL(inv.tax_amount, 0) - (NVL(cm.basic_amt, 0) + NVL(cm.tax_amount, 0)))
     ) / NULLIF(SUM((NVL(inv.invoice_qty, 0) - NVL(cm.quantity, 0))), 0), 2
   ) GROSS_NPR
   ```

   This ensures that the division only occurs if the divisor is not zero. If the divisor is zero, `NULLIF` will return `NULL`, which prevents the division error.

2. **Customer Name Inclusion**: The customer name is selected and included in the `GROUP BY` clause in both the inner and outer queries:
   - In the inner query:
     ```sql
     SELECT ...
            rc.customer_name,  -- New column added
            ...
     GROUP BY ...
              rc.customer_name  -- New column added
     ```

   - In the outer query:
     ```sql
     SELECT ...
            inv.customer_name,  -- New column added
     GROUP BY ...
              inv.customer_name  -- New column added
     ```

By making these changes, the query now includes the customer name and ensures that there will be no division by zero errors.