IF DB_ID(N'TanazOfoghiHomework4') IS NULL
BEGIN
    CREATE DATABASE TanazOfoghiHomework4;
END;
GO

USE TanazOfoghiHomework4;
GO

IF OBJECT_ID(N'dbo.Employees', N'U') IS NOT NULL DROP TABLE dbo.Employees;
IF OBJECT_ID(N'dbo.Departments', N'U') IS NOT NULL DROP TABLE dbo.Departments;
GO

CREATE TABLE dbo.Departments
(
    DepartmentID INT NOT NULL PRIMARY KEY,
    DepartmentName NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE dbo.Employees
(
    EmployeeID INT NOT NULL PRIMARY KEY,
    EmployeeName NVARCHAR(100) NOT NULL,
    DepartmentID INT NULL,
    CONSTRAINT FK_Employees_Departments
        FOREIGN KEY (DepartmentID) REFERENCES dbo.Departments(DepartmentID)
);
GO

INSERT INTO dbo.Departments (DepartmentID, DepartmentName)
VALUES
    (1, N'IT'),
    (2, N'Human Resources'),
    (3, N'Finance'),
    (4, N'Research');
GO

INSERT INTO dbo.Employees (EmployeeID, EmployeeName, DepartmentID)
VALUES
    (101, N'Ali', 1),
    (102, N'Sara', 2),
    (103, N'Reza', 1),
    (104, N'Mina', NULL);
GO

SELECT e.EmployeeID, e.EmployeeName, d.DepartmentName
FROM dbo.Employees AS e
INNER JOIN dbo.Departments AS d
    ON e.DepartmentID = d.DepartmentID
ORDER BY e.EmployeeID;
GO

SELECT e.EmployeeID, e.EmployeeName, d.DepartmentName
FROM dbo.Employees AS e
LEFT JOIN dbo.Departments AS d
    ON e.DepartmentID = d.DepartmentID
ORDER BY e.EmployeeID;
GO

SELECT e.EmployeeID, e.EmployeeName, d.DepartmentName
FROM dbo.Employees AS e
RIGHT JOIN dbo.Departments AS d
    ON e.DepartmentID = d.DepartmentID
ORDER BY d.DepartmentID, e.EmployeeID;
GO

SELECT e.EmployeeID, e.EmployeeName, d.DepartmentName
FROM dbo.Employees AS e
FULL OUTER JOIN dbo.Departments AS d
    ON e.DepartmentID = d.DepartmentID
ORDER BY d.DepartmentID, e.EmployeeID;
GO
