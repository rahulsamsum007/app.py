-- Create table for student data
CREATE TABLE student_data (
    student_id NUMBER PRIMARY KEY,
    student_name VARCHAR2(50),
    class NUMBER,
    total_marks NUMBER,
    score_marks NUMBER,
    percentage NUMBER
);

-- Insert example values
INSERT INTO student_data (student_id, student_name, class, total_marks, score_marks, percentage)
VALUES
(1, 'John Doe', 10, 500, 450, 90),
(2, 'Jane Smith', 10, 500, 430, 86),
(3, 'Alice Johnson', 10, 500, 490, 98),
(4, 'Bob Williams', 10, 500, 400, 80);

-- Query to get rank based on score marks
SELECT 
    student_id,
    student_name,
    class,
    score_marks,
    percentage,
    DENSE_RANK() OVER (PARTITION BY class ORDER BY score_marks DESC) AS rank_within_class
FROM 
    student_data;

-- Query to get student names ordered by class and rank
SELECT 
    sd.student_name,
    sd.class,
    sd.rank_within_class
FROM 
    (SELECT 
         student_id,
         student_name,
         class,
         DENSE_RANK() OVER (PARTITION BY class ORDER BY score_marks DESC) AS rank_within_class
     FROM 
         student_data) sd
ORDER BY 
    sd.class, 
    sd.rank_within_class, 
    sd.student_name;
