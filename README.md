-- Create table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    class INT,
    total_marks INT,
    max_marks INT,
    rank INT
);

-- Insert sample data with Indian names and rank
INSERT INTO students (name, class, total_marks, max_marks, rank) VALUES
('Aarav', 8, 450, 500, 1),
('Aarav', 9, 470, 500, 1),
('Aadya', 8, 480, 500, 2),
('Advik', 9, 430, 500, 2),
('Diya', 9, 470, 500, 3),
('Ishaan', 8, 490, 500, 4),
('Mira', 9, 450, 500, 5);
