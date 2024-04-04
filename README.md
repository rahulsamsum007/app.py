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

-- Query to get student names ordered by class and rank using JOIN
SELECT 
    sd.student_name,
    sd.class,
    DENSE_RANK() OVER (PARTITION BY sd.class ORDER BY sd.score_marks DESC) AS rank_within_class
FROM 
    student_data sd
JOIN 
    (SELECT 
         class,
         MAX(score_marks) AS max_score
     FROM 
         student_data
     GROUP BY 
         class) max_scores
ON 
    sd.class = max_scores.class
ORDER BY 
    sd.class, 
    rank_within_class, 
    sd.student_name;
