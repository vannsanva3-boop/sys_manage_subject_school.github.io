PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Classes (
    ClassID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClassName TEXT NOT NULL UNIQUE CHECK (length(ClassName) <= 50),
    CreatedAt TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS Students (
    StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClassID INTEGER NOT NULL,
    StudentCode TEXT NOT NULL UNIQUE CHECK (length(StudentCode) <= 30),
    StudentName TEXT NOT NULL CHECK (length(StudentName) <= 100),
    Gender TEXT NOT NULL CHECK (Gender IN ('Male', 'Female', 'Other')),
    CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

CREATE TABLE IF NOT EXISTS Attendance (
    AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER NOT NULL,
    AttendanceDate TEXT NOT NULL,
    Status TEXT NOT NULL CHECK (Status IN ('Present', 'Permission', 'Absent')),
    CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    UNIQUE (StudentID, AttendanceDate)
);

CREATE INDEX IF NOT EXISTS IX_Students_ClassID ON Students(ClassID);
CREATE INDEX IF NOT EXISTS IX_Students_StudentName ON Students(StudentName);
CREATE INDEX IF NOT EXISTS IX_Attendance_Date ON Attendance(AttendanceDate);
