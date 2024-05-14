Sure, here's a query to retrieve the information you need from Oracle ERP:

```sql
SELECT
    h.org_id AS organization_id,
    h.org_id AS org_id,
    c.party_name AS customer_name,
    h.invoice_number,
    h.invoice_date AS date,
    l.item_name AS item,
    l.quantity AS qty,
    l.line_amount AS inv_value
FROM
    ra_customer_trx_all h
    INNER JOIN ra_customer_trx_lines_all l ON h.customer_trx_id = l.customer_trx_id
    INNER JOIN hz_parties c ON h.bill_to_customer_id = c.party_id;
```

This query retrieves organization ID (`org_id`), organization ID (`organization_id`), customer name (`customer_name`), invoice number (`invoice_number`), invoice date (`date`), item name (`item`), quantity (`qty`), and invoice value (`inv_value`). It joins the necessary tables to get this information from Oracle ERP.