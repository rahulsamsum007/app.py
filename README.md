It seems like you want to modify the existing SQL Server function `f_getarrow` to work with Oracle and also retrieve data from the `ArrowTextMaster` table based on certain conditions. Here's the modified function for Oracle:

```sql
CREATE OR REPLACE FUNCTION f_getarrow(p_product VARCHAR2) RETURN VARCHAR2 AS
  v_arrow VARCHAR2(1);
  v_prdstr VARCHAR2(1);
  v_prdstr1 VARCHAR2(1);
BEGIN
  v_prdstr := SUBSTR(p_product, INSTR(p_product, '-') + 2, 1);
  v_prdstr1 := SUBSTR(p_product, INSTR(p_product, '-') + 1, 1);

  SELECT CASE
           WHEN v_prdstr = 'I' OR v_prdstr1 = 'I' THEN 'U'
           WHEN v_prdstr = 'O' OR v_prdstr1 = 'O' THEN 'D'
           ELSE '-'
         END
  INTO v_arrow
  FROM dual;

  RETURN v_arrow;
END;
/
```

And to retrieve data from the `ArrowTextMaster` table based on the direction obtained from the function, you can modify it like this:

```sql
CREATE OR REPLACE FUNCTION f_getarrow(p_product VARCHAR2) RETURN VARCHAR2 AS
  v_arrow VARCHAR2(1);
  v_prdstr VARCHAR2(1);
  v_prdstr1 VARCHAR2(1);
  v_treatment VARCHAR2(10);
BEGIN
  v_prdstr := SUBSTR(p_product, INSTR(p_product, '-') + 2, 1);
  v_prdstr1 := SUBSTR(p_product, INSTR(p_product, '-') + 1, 1);

  SELECT CASE
           WHEN v_prdstr = 'I' OR v_prdstr1 = 'I' THEN 'U'
           WHEN v_prdstr = 'O' OR v_prdstr1 = 'O' THEN 'D'
           ELSE '-'
         END
  INTO v_arrow
  FROM dual;

  -- Retrieve treatmentname based on arrow direction from ArrowTextMaster
  SELECT treatmentname INTO v_treatment
  FROM ArrowTextMaster
  WHERE arrowdirection = v_arrow;

  RETURN v_treatment;
END;
/
```

This version retrieves the `treatmentname` from the `ArrowTextMaster` table based on the arrow direction obtained from the function. Make sure the `ArrowTextMaster` table is properly structured and contains the necessary data.



Sure, here's a single query with a test select query to check if the function is working properly:

```sql
SELECT f_getarrow('PX140-IT/OR') AS arrow_direction
FROM dual;
```

This query will return the arrow direction based on the input `'PX140-IT/OR'`. Make sure to replace `'PX140-IT/OR'` with your actual test input.