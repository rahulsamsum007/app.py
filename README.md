---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------FREIGHT_DATA-----------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
WITH
    FREIGHT_DATA
    AS
        (SELECT 
        GCC.SEGMENT1 BUSINESS_UNIT,
        CASE
            WHEN TO_NUMBER(GCC.SEGMENT6) BETWEEN 15000 AND 15999 THEN 'BOPP'
            WHEN (TO_NUMBER(GCC.SEGMENT6) NOT BETWEEN 10101 AND 10111)
                 AND TO_NUMBER(GCC.SEGMENT6) < 14999 THEN 'BOPET'
        END PROD,
        CASE
            WHEN GCC.SEGMENT3 = '414501' THEN 'COMMISSION'
            ELSE 'OTHER'
        END CATEGORY,
        NVL(SUM(ACCOUNTED_DR), 0) - NVL(SUM(ACCOUNTED_CR), 0) L_TOT_FREGHT_AMT
    FROM 
    GL_JE_LINES GJL,
    GL_JE_HEADERS GJH,
    GL_LEDGERS GLL,
    GL_CODE_COMBINATIONS_KFV GCC,
    GL_PERIODS GP,
    HR_OPERATING_UNITS HOU
WHERE 
    GJL.JE_HEADER_ID = GJH.JE_HEADER_ID
    AND GJH.LEDGER_ID = HOU.SET_OF_BOOKS_ID
    AND HOU.ORGANIZATION_ID = :P_ORG_ID
    AND GJL.PERIOD_NAME = GJH.PERIOD_NAME
    AND GJL.LEDGER_ID = GLL.LEDGER_ID
    AND GLL.LEDGER_CATEGORY_CODE(+) = 'PRIMARY'
    AND GJL.CODE_COMBINATION_ID = GCC.CODE_COMBINATION_ID
    AND GJH.PERIOD_NAME = GP.PERIOD_NAME
    AND UPPER(GJH.PERIOD_NAME) IN
        (SELECT UPPER(PERIOD_NAME)
         FROM GL_PERIODS
         WHERE ADJUSTMENT_PERIOD_FLAG = 'Y'
           AND TO_CHAR(START_DATE, 'MON-RR') = UPPER(:P_PERIOD)
         UNION ALL
         SELECT UPPER(PERIOD_NAME)
         FROM GL_PERIODS
         WHERE 1 = 1
           AND UPPER(PERIOD_NAME) = UPPER(:P_PERIOD))
    AND GCC.SEGMENT3 IN ('414501', '414601', '414603')
    GROUP BY 
        GCC.SEGMENT1,
        CASE
            WHEN TO_NUMBER(GCC.SEGMENT6) BETWEEN 15000 AND 15999 THEN 'BOPP'
            WHEN (TO_NUMBER(GCC.SEGMENT6) NOT BETWEEN 10101 AND 10111)
                 AND TO_NUMBER(GCC.SEGMENT6) < 14999 THEN 'BOPET'
        END,
        CASE
            WHEN GCC.SEGMENT3 = '414501' THEN 'COMMISSION'
            ELSE 'OTHER'
        END),
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------VOLUME_DATA-----------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   VOLUME_DATA
    AS
        (SELECT GCC.SEGMENT1 BUSINESS_UNIT,
                CASE
                    WHEN TO_NUMBER(GCC.SEGMENT6) BETWEEN 15000 AND 15999 THEN 'BOPP'
                    WHEN (TO_NUMBER(GCC.SEGMENT6) NOT BETWEEN 10101 AND 10111)
                         AND TO_NUMBER(GCC.SEGMENT6) < 14999 THEN 'BOPET'
                END PROD,
                NVL(SUM(ACCOUNTED_DR), 0) - NVL(SUM(ACCOUNTED_CR), 0) L_OTHERTHAN_FREGHT_AMT
         FROM GL_JE_LINES GJL,
              GL_JE_HEADERS GJH,
              GL_LEDGERS GLL,
              GL_CODE_COMBINATIONS_KFV GCC,
              GL_PERIODS GP,
              HR_OPERATING_UNITS HOU
         WHERE GJL.JE_HEADER_ID = GJH.JE_HEADER_ID
           AND GJH.LEDGER_ID = HOU.SET_OF_BOOKS_ID
           AND HOU.ORGANIZATION_ID = :P_ORG_ID
           AND GJL.PERIOD_NAME = GJH.PERIOD_NAME
           AND GJL.LEDGER_ID = GLL.LEDGER_ID
           AND GLL.LEDGER_CATEGORY_CODE(+) = 'PRIMARY'
           AND GJL.CODE_COMBINATION_ID = GCC.CODE_COMBINATION_ID
           AND GJH.PERIOD_NAME = GP.PERIOD_NAME
           AND UPPER(GJH.PERIOD_NAME) IN
               (SELECT UPPER(PERIOD_NAME)
                FROM GL_PERIODS
                WHERE ADJUSTMENT_PERIOD_FLAG = 'Y'
                  AND TO_CHAR(START_DATE, 'MON-RR') = UPPER(:P_PERIOD)
                UNION ALL
                SELECT UPPER(PERIOD_NAME)
                FROM GL_PERIODS
                WHERE 1 = 1
                  AND UPPER(PERIOD_NAME) = UPPER(:P_PERIOD))
           AND GCC.SEGMENT5 <> '2161'
           AND GCC.SEGMENT3 IN ('311111', '311112', '311118', '311119')
         GROUP BY GCC.SEGMENT1,
                  CASE
                      WHEN TO_NUMBER(GCC.SEGMENT6) BETWEEN 15000 AND 15999 THEN 'BOPP'
                      WHEN (TO_NUMBER(GCC.SEGMENT6) NOT BETWEEN 10101 AND 10111)
                           AND TO_NUMBER(GCC.SEGMENT6) < 14999 THEN 'BOPET'
                  END),
------------------------------------------------------------INSERT INTO XXSRF.XXSRF_SA_NPR_VALUES-----------------------------------------------------------------------------------------
INSERT INTO XXSRF.XXSRF_SA_NPR_VALUES (
    ORGANIZATION_ID,
    ORG_ID,
    BSV,
    ORGANIZATION_CODE,
    PRODUCT_SEGMENT,
    PERIOD_NAME,
    MIS_CATEGORY,
    TRX_DATE,
    TRX_NUMBER,
    MARKET_TYPE,
    ITEM_CODE,
    CUSTOMER_NAME,
    SALES_QTY_MT,
    SALE_VALUE,
    GROSS_NPR,
    NET_NPR,
    FREIGHT_AND_HANDLING,
    SPL_DISCOUNT
)--------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------NPR_MAIN_QUERY-----------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------         

--npr query was use to be here but i have stored it data in XXSRF.XXSRF_SA_NPR_VALUES
       ROUND(NPR.GROSS_NPR - ((NVL(VD.L_OTHERTHAN_FREGHT_AMT, 0) / NULLIF(SUM(NPR.SALES_QTY_MT), 0)) / 1000
         + (NVL(FD_OTHER.L_TOT_FREGHT_AMT, 0) / NULLIF(SUM(NPR.SALES_QTY_MT), 0)) / 1000), 2) AS NET_NPR,
         also calculate 
                ROUND(NVL(FD_OTHER.L_TOT_FREGHT_AMT, 0) / NULLIF(SUM(NPR.SALES_QTY_MT) OVER () * 1000, 0), 4) AS FREIGHT_AND_HANDLING,
       ROUND(NVL(VD.L_OTHERTHAN_FREGHT_AMT, 0) / NULLIF(SUM(NPR.SALES_QTY_MT) OVER () * 1000, 0), 4) AS SPL_DISCOUNT,
       ROUND(NVL(FD_COMMISSION.L_TOT_FREGHT_AMT, 0) / NULLIF(SUM(NPR.SALES_QTY_MT) OVER () * 1000, 0), 4) AS COMMISSION
       
       HERE MY FD IS FREIGHT DATA QUERY AND VD IS VOLUME DATA QUERY I WANT YOU TO USETHESE AND THEABOVE FREIGHT AND COLUME QUERY AND MAKE UPDATE SATEMENT
       AFTER CALUCALTING UPDATE THIS IN TABLE XXSRF.XXSRF_SA_NPR_VALUES
       RESPECTIVELY WITH OTER DATA i hope you got  me give me full fixed code 
             
             

