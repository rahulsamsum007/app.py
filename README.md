-- Create table Student
CREATE TABLE Student (
    Sid INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentName VARCHAR(255),
    DateOfAdmission DATE DEFAULT CURRENT_DATE,
    EnrollmentClass VARCHAR(50),
    ContactNumber VARCHAR(15)
);

-- Create table ExamResult
CREATE TABLE ExamResult (
    Eid INTEGER PRIMARY KEY AUTOINCREMENT,
    Sid INTEGER,
    FOREIGN KEY (Sid) REFERENCES Student(Sid),
    Class VARCHAR(50),
    Subject VARCHAR(255),
    MaxMarks INTEGER DEFAULT 100,
    ScoredMarks INTEGER
);
