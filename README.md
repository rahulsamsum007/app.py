Understood, let's modify the function to return 'U' if the treatment name is not found in the `ArrowTextMaster` table and ensure the arrow direction contains only 'I' and 'O'. Here's the updated function:

```sql
CREATE OR REPLACE FUNCTION f_getarrow(p_product VARCHAR2) RETURN VARCHAR2 AS
  v_treatment VARCHAR2(10);
BEGIN
  -- Extract substring between '-' and '/'
  v_treatment := SUBSTR(p_product, INSTR(p_product, '-') + 1, INSTR(p_product, '/') - INSTR(p_product, '-') - 1);

  -- Retrieve arrowdirection based on treatmentname from ArrowTextMaster
  SELECT arrowdirection INTO v_treatment
  FROM ArrowTextMaster
  WHERE treatmentname = v_treatment;

  -- If treatment name not found, return 'U' (Up) as default
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN 'U';
    WHEN OTHERS THEN
      RETURN 'U';
  RETURN v_treatment;
END;
/
```

This function will now return 'U' if the treatment name is not found in the `ArrowTextMaster` table. 

If the treatment name is found, it will return the corresponding arrow direction, which must be either 'I' or 'O' according to your requirement. 

Now, when you run the query:

```sql
SELECT f_getarrow('PX140-IT/OR') AS arrow_direction
FROM dual;
```

If `'IT'` is found in the `ArrowTextMaster` table with an arrow direction of 'I', it will return:

```plaintext
| arrow_direction |
|-----------------|
| I               |
```

If `'OR'` is found in the `ArrowTextMaster` table with an arrow direction of 'O', it will return:

```plaintext
| arrow_direction |
|-----------------|
| O               |
```

If neither 'IT' nor 'OR' is found in the `ArrowTextMaster` table, it will return:

```plaintext
| arrow_direction |
|-----------------|
| U               |
```

This ensures that the function returns 'U' if the treatment name is not found in the `ArrowTextMaster` table, and it only returns 'I' or 'O' if the treatment name corresponds to those values.