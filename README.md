DECLARE
    p_product VARCHAR2(100) := 'HSPA0210-ip/or';
    v_arrow VARCHAR2(1);
    v_prdstr VARCHAR2(100);
    v_treatment_name VARCHAR2(100);
    v_arrow_direction VARCHAR2(1);
    v_count NUMBER;
BEGIN
    IF INSTR(p_product, '/') > 0 THEN
        v_prdstr := SUBSTR(p_product, INSTR(p_product, '-', 1) + 1, INSTR(p_product, '/') - INSTR(p_product, '-') - 1);
    ELSE
        v_prdstr := SUBSTR(p_product, INSTR(p_product, '-', 1) + 1);
    END IF;

    SELECT COUNT(*) INTO v_count
    FROM ArrowTextMaster
    WHERE UPPER(treatmentname) = UPPER(v_prdstr);

    IF v_count > 0 THEN
        BEGIN
            SELECT treatmentname, arrowdirection
            INTO v_treatment_name, v_arrow_direction
            FROM ArrowTextMaster
            WHERE UPPER(treatmentname) = UPPER(v_prdstr);

            DBMS_OUTPUT.PUT_LINE('Name: ' || v_treatment_name);

            IF UPPER(v_treatment_name) LIKE '%I%' THEN
                DBMS_OUTPUT.PUT_LINE('Arrow Direction: U');
            ELSIF UPPER(v_treatment_name) LIKE '%O%' THEN
                DBMS_OUTPUT.PUT_LINE('Arrow Direction: D');
            ELSE
                DBMS_OUTPUT.PUT_LINE('Arrow Direction: ' || v_arrow_direction);
            END IF;
        END;
    ELSE
        v_arrow := CASE
            WHEN SUBSTR(v_prdstr, 1, 1) = 'I' OR SUBSTR(v_prdstr, 2, 1) = 'I' THEN
                'U'
            WHEN SUBSTR(v_prdstr, 1, 1) = 'O' OR SUBSTR(v_prdstr, 2, 1) = 'O' THEN
                'D'
            ELSE
                '-'
        END;

        DBMS_OUTPUT.PUT_LINE('Arrow: ' || v_arrow);
    END IF;
END;
/






























DECLARE
    p_product VARCHAR2(100) := 'HSPA0210-it';
    arrowtxt VARCHAR2(50);
    prdstr VARCHAR2(65);
    treatment_name VARCHAR2(65);
    arrow_direction VARCHAR2(1);
BEGIN
    IF INSTR(p_product, '/') > 0 THEN
        prdstr := SUBSTR(p_product, INSTR(p_product, '-') + 1, INSTR(p_product, '/') - INSTR(p_product, '-') - 1);
    ELSE
        prdstr := SUBSTR(p_product, INSTR(p_product, '-') + 1);
    END IF;

    SELECT COUNT(*)
    INTO arrow_direction
    FROM ArrowTextMaster
    WHERE UPPER(treatmentname) = UPPER(prdstr);

    IF arrow_direction > 0 THEN
        SELECT treatmentname, arrowdirection, arrowdescription
        INTO treatment_name, arrow_direction, arrowtxt
        FROM ArrowTextMaster
        WHERE UPPER(treatmentname) = UPPER(prdstr);
    ELSE
        arrow_direction := CASE
                               WHEN SUBSTR(prdstr, 1, 1) = 'I' OR SUBSTR(prdstr, 2, 1) = 'I' THEN 'U'
                               WHEN SUBSTR(prdstr, 1, 1) = 'O' OR SUBSTR(prdstr, 2, 1) = 'O' THEN 'D'
                               ELSE '-'
                            END;
        arrowtxt := '-';
    END IF;

    IF arrow_direction = 'D' AND arrowtxt = '-' THEN
        SELECT arrowdescription
        INTO arrowtxt
        FROM ArrowTextMaster
        WHERE UPPER(treatmentname) LIKE '%O%'
          AND arrowdirection = 'D';
    ELSIF arrow_direction = 'U' AND arrowtxt = '-' THEN
        SELECT arrowdescription
        INTO arrowtxt
        FROM ArrowTextMaster
        WHERE UPPER(treatmentname) LIKE '%I%'
          AND arrowdirection = 'U';
    END IF;

    DBMS_OUTPUT.PUT_LINE('Arrow Text: ' || arrowtxt);

EXCEPTION
    WHEN OTHERS THEN
        arrowtxt := '-';
        DBMS_OUTPUT.PUT_LINE('Arrow Text: ' || arrowtxt);
END;
/

