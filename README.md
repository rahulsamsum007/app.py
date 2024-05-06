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
SR NO	ITEM_CODE		Arrow Direction	Discription to be print 
65	1HSP0200-IHP/OR	IHP	In Side	HEAT SEAL
107	1HSP0210-IHP/OR	IHP	In Side	HEAT SEAL
![image]
TreatmentName	ArrowDirection
IT	I
IQ	I
IV	I
IX	I
![image](https://github.com/rahulsamsum007/app.py/assets/135415621/f2bbb691-7b1c-4c64-a7b6-ce24c1fb62f7)

(https://github.com/rahulsamsum007/app.py/assets/135415621/a2ecfc8d-6540-4ad1-911d-dc75126bbbb2)

