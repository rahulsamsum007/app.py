-- Creating the student table
CREATE TABLE student (
    Sid INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255),
    date_of_admission DATE DEFAULT CURRENT_DATE,
    enrolment_class VARCHAR(50),
    contact_number VARCHAR(20)
);

-- Creating the exam_result table
CREATE TABLE exam_result (
    eid INT AUTO_INCREMENT PRIMARY KEY,
    Sid INT,
    FOREIGN KEY (Sid) REFERENCES student(Sid),
    class VARCHAR(50),
    subject VARCHAR(255),
    max_marks INT DEFAULT 100,
    scored_marks INT
);


-- Inserting data into the student table
INSERT INTO student (student_name, enrolment_class, contact_number)
VALUES ('John Doe', 'Class A', '1234567890'),
       ('Jane Smith', 'Class B', '9876543210'),
       ('Alice Johnson', 'Class C', '5555555555');

-- Inserting data into the exam_result table
INSERT INTO exam_result (Sid, class, subject, scored_marks)
VALUES (1, 'Class A', 'Mathematics', 85),
       (1, 'Class A', 'Science', 90),
       (2, 'Class B', 'Mathematics', 75),
       (2, 'Class B', 'Science', 80),
       (3, 'Class C', 'Mathematics', 95),
       (3, 'Class C', 'Science', 92);
