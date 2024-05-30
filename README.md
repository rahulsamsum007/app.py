Here is the modified query with the inclusion of `customer_name`:

```sql
UNION
SELECT :P_ORG_ID Org_id,
      gcc.segment1 bsv,
      mp.organization_code,
      NVL(
         CTT.attribute11,
         MAX((SELECT NVL(ott.attribute8, 'BOPET')
              FROM ra_cust_trx_types_all rctt,
                   oe_transaction_types_all ott
              WHERE NVL(rctt.attribute8, 'N') = 'Y'
                    AND NVL(ott.attribute4, 'N') = 'N'
                    AND rctt.cust_trx_type_id = ott.cust_trx_type_id
                    AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                    AND ORDER_CATEGORY_CODE <> 'RETURN'
                    AND rctt.org_id = ctt.org_id
              GROUP BY NVL(ott.attribute8, 'BOPET'))))
         product_segment,
      TO_CHAR(gpc.gl_date, 'MON-RR') period_name,
      'Sales Return' mis_category,
      rctto.attribute10 market_type,
      msi.segment1 item, -- Added msi.segment1 for the new column
      SUM(rctl.quantity_credited) / 1000 quantity,
      ROUND(
         SUM((rctl.quantity_credited * rctl.unit_selling_price)
             * NVL(rcta.EXCHANGE_RATE, 1)),
         2
      ) SALE_VALUE,
      ROUND(
         (SUM(rctl.quantity_credited * rctl.unit_selling_price)
          / NULLIF(SUM(rctl.quantity_credited), 0)),
         2
      ) npr_rs_kg,
      rc.customer_name -- New column added
FROM ra_cust_trx_types_all ctt,
    ra_customer_trx_all rcta,
    ra_customer_trx_lines_all rctl,
    ra_customer_trx_lines_all rctlo,
    ra_customer_trx_all rcto,
    oe_order_lines_all ool,
    mtl_system_items msi, -- Added join with mtl_system_items for the new column
    ra_cust_trx_types_all rctto,
    mtl_parameters mp,
    gl_code_combinations gcc,
    ar_customers rc, -- Added join with ar_customers for customer_name
    (SELECT TRUNC(MAX(gl_date)) gl_date, customer_trx_id
     FROM ra_cust_trx_line_gl_dist_all
     WHERE 1 = 1
           AND account_class = 'REC'
           AND org_id = :P_ORG_ID
           AND :P_ORG_ID <> 87
           AND latest_rec_flag = 'Y'
     GROUP BY customer_trx_id) gpo,
    (SELECT TRUNC(MAX(gl_date)) gl_date, customer_trx_id
     FROM ra_cust_trx_line_gl_dist_all
     WHERE 1 = 1
           AND account_class = 'REC'
           AND org_id = :P_ORG_ID
           AND :P_ORG_ID <> 87
           AND latest_rec_flag = 'Y'
     GROUP BY customer_trx_id) gpc
WHERE 1 = 1
     AND rcta.cust_trx_type_id = ctt.cust_trx_type_id
     AND rcta.org_id = rctl.org_id
     AND rcta.customer_trx_id = rctl.customer_trx_id
     AND rcto.cust_trx_type_id = rctto.cust_trx_type_id
     AND rcta.customer_trx_id = gpc.customer_trx_id
     AND TO_CHAR(gpc.gl_date, 'MON-RR') = UPPER(:P_PERIOD)
     AND rcto.customer_trx_id = gpo.customer_trx_id
     AND rctl.line_type = 'LINE'
     AND ctt.TYPE = 'CM'
     AND rctl.previous_customer_trx_id = rctlo.customer_trx_id
     AND rctlo.customer_trx_id = rcto.customer_trx_id
     AND TO_CHAR(gpc.gl_date, 'MON-RR') <> TO_CHAR(gpo.gl_date, 'MON-RR')
     AND rctl.previous_customer_trx_line_id = rctlo.customer_trx_line_id
     AND rctl.previous_customer_trx_line_id IS NOT NULL
     AND ool.line_id = rctlo.interface_line_attribute6
     AND ool.ship_from_org_id = msi.organization_id -- Join condition added
     AND rctl.inventory_item_id = msi.inventory_item_id -- Join condition added
     AND mp.organization_id = msi.organization_id
     AND gcc.code_combination_id = mp.material_account
     AND rcta.org_id = :P_ORG_ID
     AND :P_ORG_ID <> 87
     AND rcta.bill_to_customer_id = rc.customer_id -- Join condition for customer_name
     AND EXISTS
           (SELECT 1
            FROM ra_cust_trx_types_all rctt,
                 oe_transaction_types_all ott
            WHERE NVL(rctt.attribute8, 'N') = 'Y'
                  AND NVL(ott.attribute4, 'N') = 'N'
                  AND rctt.cust_trx_type_id = ott.cust_trx_type_id
                  AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                  AND ORDER_CATEGORY_CODE <> 'RETURN'
                  AND rctt.org_id = ctt.org_id
                  AND NVL(rctt.attribute10, 'XX') = CASE
                                                      WHEN rctt.org_id = 1397 THEN 'Domestic Sales'
                                                      ELSE NVL(ctt.attribute10, 'XX')
                                                   END)
GROUP BY msi.organization_id,
         TO_CHAR(gpc.gl_date, 'MON-RR'),
         gcc.segment1,
         rctto.attribute10,
         mp.organization_code,
         CTT.attribute11,
         msi.segment1, -- Added msi.segment1 to the GROUP BY clause
         rc.customer_name -- Added customer_name to the GROUP BY clause
UNION
SELECT :P_ORG_ID Org_id,
      gcc.segment1 bsv,
      mp.organization_code,
      NVL(
         CTT.attribute11,
         MAX((SELECT NVL(ott.attribute8, 'BOPET')
              FROM ra_cust_trx_types_all rctt,
                   oe_transaction_types_all ott
              WHERE NVL(rctt.attribute8, 'N') = 'Y'
                    AND NVL(ott.attribute4, 'N') = 'N'
                    AND rctt.cust_trx_type_id = ott.cust_trx_type_id
                    AND ORDER_CATEGORY_CODE <> 'RETURN'
                    AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                    AND rctt.org_id = ctt.org_id
              GROUP BY NVL(ott.attribute8, 'BOPET'))))
         product_segment,
      TO_CHAR(gpc.gl_date, 'MON-RR') period_name,
      'Sales Return' mis_category,
      rctto.attribute10 market_type,
      msi.segment1 item, -- Added msi.segment1 for the new column
      SUM(rctl.quantity_credited) / 1000 quantity,
      ROUND(
         SUM((rctl.quantity_credited * rctl.unit_selling_price)
             * NVL(rcta.EXCHANGE_RATE, 1)),
         2
      ) SALE_VALUE,
      ROUND(
         (SUM(rctl.quantity_credited * rctl.unit_selling_price)
          / NULLIF(SUM(rctl.quantity_credited), 0)),
         2
      ) npr_rs_kg,
      rc.customer_name -- New column added
FROM ra_cust_trx_types_all ctt,
    ra_customer_trx_all rcta,
    ra_customer_trx_lines_all rctl,
    ra_customer_trx_lines_all rctlo,
    ra_customer_trx_all rcto,
    oe_order_lines_all ool,
    mtl_system_items_b msi, -- Changed to mtl_system_items_b for the new column
    ra_cust_trx_types_all rctto,
    mtl_parameters mp,
    gl_code_combinations gcc,
    ar_customers rc, -- Added join with ar_customers for customer_name
    (SELECT TRUNC(MAX(gl_date)) gl_date, customer_trx_id
     FROM ra_cust_trx_line_gl_dist_all
     WHERE 1 = 1
           AND account_class = 'REC'
           AND org_id = :P_ORG_ID
           AND :P_ORG_ID <> 87
           AND latest_rec_flag = 'Y'
     GROUP BY customer_trx_id) gpo,
    (SELECT TRUNC(MAX(gl_date)) gl_date, customer_trx_id
     FROM ra_cust_trx_line_gl_dist_all
     WHERE 1 = 1
           AND account_class = 'REC'
           AND org_id = :P_ORG_ID
           AND :P_ORG_ID <> 87
           AND latest_rec_flag = 'Y'
     GROUP BY customer_trx_id) gpc
WHERE 1 = 1
      AND rcta.cust_trx_type_id = ctt.cust_trx_type_id
      AND rcta.org_id = rctl.org_id
      AND rcta.customer_trx_id = rctl.customer_trx_id
      AND rcto.cust_trx_type_id = rctto.cust_trx_type_id
      AND rcta.customer_trx_id = gpc.customer_trx_id
      AND TO_CHAR(gpc.gl_date, 'MON-RR') = UPPER(:P_PERIOD)
      AND rcto.customer_trx_id = gpo.customer_trx_id
      AND rctl.line_type = 'LINE'
```sql
      AND ctt.TYPE = 'CM'
      AND ool.return_attribute1 = rctlo.customer_trx_id
      AND rctlo.customer_trx_id = rcto.customer_trx_id
      AND TO_CHAR(gpc.gl_date, 'MON-RR') <> TO_CHAR(gpo.gl_date, 'MON-RR')
      AND ool.return_attribute2 = rctlo.customer_trx_line_id
      AND ool.line_id = rctl.interface_line_attribute6
      AND ool.ship_from_org_id = msi.organization_id
      AND rctl.inventory_item_id = msi.inventory_item_id
      AND mp.organization_id = msi.organization_id
      AND gcc.code_combination_id = mp.material_account
      AND rctl.previous_customer_trx_line_id IS NULL
      AND rcta.org_id = :P_ORG_ID
      AND :P_ORG_ID <> 87
      AND rcta.bill_to_customer_id = rc.customer_id -- Join condition for customer_name
      AND EXISTS
            (SELECT 1
             FROM ra_cust_trx_types_all rctt,
                  oe_transaction_types_all ott
             WHERE NVL(rctt.attribute8, 'N') = 'Y'
                   AND NVL(ott.attribute4, 'N') = 'N'
                   AND rctt.cust_trx_type_id = ott.cust_trx_type_id
                   AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                   AND rctt.org_id = ctt.org_id
                   AND ORDER_CATEGORY_CODE <> 'RETURN'
                   AND NVL(rctt.attribute10, 'XX') =
                          CASE
                             WHEN rctt.org_id = 1397
                             THEN 'Domestic Sales'
                             ELSE NVL(ctt.attribute10, 'XX')
                          END)
GROUP BY msi.organization_id,
         TO_CHAR(gpc.gl_date, 'MON-RR'),
         gcc.segment1,
         rctto.attribute10,
         mp.organization_code,
         CTT.attribute11,
         msi.segment1, -- Added msi.segment1 to the GROUP BY clause
         rc.customer_name; -- Added customer_name to the GROUP BY clause
```

### Key Changes:
1. **Added `customer_name` column**: The `customer_name` column is added to the `SELECT` statement.
2. **Joined with `ar_customers` table**: The query includes a join with the `ar_customers` table to get the `customer_name`.
3. **Grouped by `customer_name`**: The `customer_name` is added to the `GROUP BY` clause.
4. **Handled zero divisor in `ROUND` function**: The division operation inside the `ROUND` function now uses `NULLIF` to handle the zero divisor error.

### Complete Code:
```sql
UNION
SELECT :P_ORG_ID Org_id,
      gcc.segment1 bsv,
      mp.organization_code,
      NVL (
         CTT.attribute11,
         MAX( (SELECT NVL (ott.attribute8, 'BOPET')
                FROM ra_cust_trx_types_all rctt,
                     oe_transaction_types_all ott
                WHERE NVL (rctt.attribute8, 'N') = 'Y'
                      AND NVL (ott.attribute4, 'N') = 'N'
                      AND rctt.cust_trx_type_id = ott.cust_trx_type_id
                      AND rctt.credit_memo_type_id = ctt.cust_trx_type_id
                      AND ORDER_CATEGORY_CODE <> 'RETURN'
                      AND rctt.org_id = ctt.org_id
                GROUP BY NVL (ott.attribute8, 'BOPET'))))
         product_segment,
      TO_CHAR (gpc.gl