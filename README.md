Got it, you want to extract the substring between '-' and '/' from the input string, then match it with the `treatmentname` column in the `ArrowTextMaster` table and return the corresponding `arrowdirection` value.

Here's how you can achieve this:

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

  RETURN v_treatment;
END;
/
```

Now, when you run the test query with an example like `'PX140-IT/OR'`:

```sql
SELECT f_getarrow('PX140-IT/OR') AS arrow_direction
FROM dual;
```

It will return the `arrowdirection` value corresponding to `'IT'` from the `ArrowTextMaster` table. 

Assuming in the `ArrowTextMaster` table `'IT'` corresponds to `'I'`, it will return:

```plaintext
| arrow_direction |
|-----------------|
| I               |
```

Is this what you were looking for?