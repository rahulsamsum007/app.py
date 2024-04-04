SELECT r.StudentID, r.StudentName, r.EnrolledClass, s.Class, s.ExamDate, s.Subject, s.Marks
FROM result r
JOIN Students s ON r.StudentID = s.StudentID;
