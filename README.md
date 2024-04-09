CREATE OR REPLACE PROCEDURE get_student_info (
    student_name IN VARCHAR2
) AS
    v_class students.class%TYPE;
    v_total_marks students.total_marks%TYPE;
    v_max_marks students.max_marks%TYPE;
    v_percentage NUMBER;
    CURSOR student_cur IS
        SELECT name, class, total_marks, max_marks
        FROM students
        WHERE name = student_name;
BEGIN
    OPEN student_cur;
    FETCH student_cur INTO student_name, v_class, v_total_marks, v_max_marks;
    CLOSE student_cur;
    
    -- Calculate percentage
    v_percentage := (v_total_marks / v_max_marks) * 100;
    
    -- Output result
    DBMS_OUTPUT.PUT_LINE(student_name || ' scored ' || v_total_marks || ' total marks out of ' || v_max_marks || 
                         ' and scored ' || v_percentage || '%');
    DBMS_OUTPUT.PUT_LINE('and scored 1 position in class ' || v_class);
END;
/
