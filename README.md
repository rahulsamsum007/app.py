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


1234567890'