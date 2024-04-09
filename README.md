-- Create table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    class VARCHAR(10),
    total_marks INT,
    max_marks INT
);

-- Insert sample data
INSERT INTO students (name, class, total_marks, max_marks) VALUES
('Alice', 'A', 450, 500),
('Bob', 'A', 480, 500),
('Charlie', 'B', 430, 500),
('David', 'B', 470, 500),
('Emma', 'A', 490, 500),
('Frank', 'B', 450, 500);

-- Add rank column
ALTER TABLE students ADD COLUMN rank INT;

-- Update rank based on total marks within each class
UPDATE students s
JOIN (
    SELECT id, class, total_marks, 
    RANK() OVER (PARTITION BY class ORDER BY total_marks DESC) AS rank
    FROM students
) r ON s.id = r.id
SET s.rank = r.rank;
