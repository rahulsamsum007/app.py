DECLARE
    v_student_name VARCHAR2(50) := 'Aarav';
    v_class students.class%TYPE;
    v_total_marks students.total_marks%TYPE;
    v_max_marks students.max_marks%TYPE;
    v_rank students.rank%TYPE;
    v_percentage NUMBER;

    CURSOR student_cursor IS
        SELECT name, class, total_marks, max_marks, rank
        FROM students
        WHERE name = v_student_name;
BEGIN
    OPEN student_cursor;
    LOOP
        FETCH student_cursor INTO v_student_name, v_class, v_total_marks, v_max_marks, v_rank;
        EXIT WHEN student_cursor%NOTFOUND;
        
        -- Calculate percentage
        v_percentage := (v_total_marks / v_max_marks) * 100;
        
        -- Display result
        DBMS_OUTPUT.PUT_LINE(v_student_name || ' scored ' || v_total_marks || ' total marks out of ' || v_max_marks || 
                             ' and scored ' || v_rank || ' position in class ' || v_class || 
                             '. Percentage: ' || v_percentage || '%');
    END LOOP;
    CLOSE student_cursor;
END;
/
