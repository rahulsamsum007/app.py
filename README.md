-- Step 1: Create the student table
CREATE TABLE student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(50),
    class VARCHAR(10),
    total_marks INT,
    scored_marks INT
);

-- Step 2: Create the calculate_rank function
DELIMITER //

CREATE FUNCTION calculate_rank(scored_marks_percentage FLOAT) RETURNS VARCHAR(20)
BEGIN
    DECLARE rank_value VARCHAR(20);
    
    IF scored_marks_percentage >= 90 THEN
        SET rank_value = 'A+';
    ELSEIF scored_marks_percentage >= 80 THEN
        SET rank_value = 'A';
    ELSEIF scored_marks_percentage >= 70 THEN
        SET rank_value = 'B+';
    ELSEIF scored_marks_percentage >= 60 THEN
        SET rank_value = 'B';
    ELSEIF scored_marks_percentage >= 50 THEN
        SET rank_value = 'C';
    ELSE
        SET rank_value = 'D';
    END IF;
    
    RETURN rank_value;
END //

DELIMITER ;

-- Step 3: Create the student_name table
CREATE TABLE student_name (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(50),
    class VARCHAR(10)
);

-- Step 4: Insert values into the student table
INSERT INTO student (student_name, class, total_marks, scored_marks)
VALUES ('John Doe', '12A', 500, 450),
       ('Alice Smith', '11B', 500, 480),
       ('Bob Johnson', '10C', 500, 400);

-- Step 5: Insert values into the student_name table
INSERT INTO student_name (student_id, student_name, class)
SELECT student_id, student_name, class
FROM student;

-- Step 6: Query the final exam result
SELECT sn.student_name, sn.class, calculate_rank(s.scored_marks/s.total_marks * 100) AS rank
FROM student s
JOIN student_name sn ON s.student_id = sn.student_id
ORDER BY sn.class, rank;
