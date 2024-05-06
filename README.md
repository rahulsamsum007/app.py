It looks like you're trying to create a function in Oracle that returns an arrow direction based on a product string and then match that with a table called ArrowTextMaster. Here's the corrected function and query:

```sql
CREATE OR REPLACE FUNCTION f_getarrow (p_product VARCHAR2) RETURN VARCHAR2 IS
  v_arrow VARCHAR2(1);
  v_prdstr VARCHAR2(1);
  v_prdstr1 VARCHAR2(1);
BEGIN
  v_prdstr := SUBSTR(p_product, INSTR(p_product, '-') + 2, 1);
  v_prdstr1 := SUBSTR(p_product, INSTR(p_product, '-') + 1, 1);

  SELECT
    CASE
      WHEN v_prdstr = 'I' OR v_prdstr1 = 'I' THEN 'U'
      WHEN v_prdstr = 'O' OR v_prdstr1 = 'O' THEN 'D'
      ELSE '-'
    END
  INTO v_arrow
  FROM DUAL;

  RETURN v_arrow;
END;
/

SELECT f_getarrow('PX140-IT/OR') FROM DUAL;
```

Now, assuming you have a table called ArrowTextMaster with columns ArrowDirection and FrontOrTreatment, you can use a query like this to match the arrow direction with the product and get the corresponding treatment:

```sql
SELECT atm.FrontOrTreatment
FROM ArrowTextMaster atm
WHERE atm.ArrowDirection = f_getarrow('PX140-IT/OR');
```

This query will return the FrontOrTreatment value corresponding to the arrow direction of the given product string.