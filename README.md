CREATE OR REPLACE FUNCTION PFBCUSTOM.f_getarrow (product_i VARCHAR2)
   RETURN VARCHAR2
IS
   arrow    VARCHAR2 (1);
   prdstr   VARCHAR2 (1);
   prdstr1  VARCHAR2 (1);
BEGIN
   SELECT   SUBSTR (product_i, INSTR (product_i, '-') + 2, 1),SUBSTR (product_i, INSTR (product_i, '-') + 1, 1)
     INTO   prdstr,prdstr1
     FROM   DUAL;

   SELECT   CASE
               WHEN (prdstr = 'I' OR prdstr1 = 'I') THEN 'U'
               WHEN (prdstr = 'O' OR prdstr1 = 'O') THEN 'D'
               ELSE '-'
            END
     INTO   arrow
     FROM   DUAL;

   RETURN arrow;
EXCEPTION
   WHEN OTHERS
   THEN
      arrow := '-';
      RETURN arrow;
END;
/
