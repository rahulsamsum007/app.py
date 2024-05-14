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
