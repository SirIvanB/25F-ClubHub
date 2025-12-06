DROP DATABASE IF EXISTS ClubHub;
CREATE DATABASE ClubHub;
USE ClubHub;


-- Students Table
CREATE TABLE Students (
   studentID INT PRIMARY KEY,
   email VARCHAR(100) UNIQUE NOT NULL,
   firstName VARCHAR(50) NOT NULL,
   lastName VARCHAR(50) NOT NULL
);


-- Majors Table
CREATE TABLE Majors (
   majorID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL
);


-- Minors Table
CREATE TABLE Minors (
   minorID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL
);


-- Categories Table (must be created before Clubs due to foreign key)
CREATE TABLE Categories (
   categoryID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL
);


-- Clubs Table
CREATE TABLE Clubs (
   clubID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   email VARCHAR(100),
   adviser VARCHAR(100),
   categoryID INT,
   FOREIGN KEY (categoryID) REFERENCES Categories(categoryID)
);


-- Events Table
CREATE TABLE Events (
   eventID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   description TEXT,
   searchDescription TEXT,
   startDateTime DATETIME NOT NULL,
   endDateTime DATETIME,
   authID INT,
   clubID INT,
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID)
);


-- Locations Table
CREATE TABLE Locations (
   locationID INT PRIMARY KEY,
   capacity INT,
   buildingName VARCHAR(100),
   buildingNumber VARCHAR(20),
   floorNumber INT
);


-- Servers Table
CREATE TABLE Servers (
   serverID INT PRIMARY KEY,
   status VARCHAR(50),
   ipAddress VARCHAR(45),
   lastUpdated DATETIME
);


-- Keywords Table
CREATE TABLE Keywords (
   keywordID INT PRIMARY KEY,
   keyword VARCHAR(100) NOT NULL
);


-- EventLog Table
CREATE TABLE EventLog (
   logID INT PRIMARY KEY,
   logTimestamp DATETIME NOT NULL,
   status VARCHAR(50),
   severity VARCHAR(50),
   serverID INT,
   FOREIGN KEY (serverID) REFERENCES Servers(serverID)
);


-- Administrators Table
CREATE TABLE Administrators (
   adminID INT PRIMARY KEY,
   email VARCHAR(100) UNIQUE NOT NULL,
   firstName VARCHAR(50),
   lastName VARCHAR(50)
);


-- Students-Majors (Many-to-Many)
CREATE TABLE Students_Major_Attends (
   studentID INT NOT NULL,
   majorID INT NOT NULL,
   PRIMARY KEY (studentID, majorID),
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE,
   FOREIGN KEY (majorID) REFERENCES Majors(majorID) ON DELETE CASCADE
);


-- Students-Minors (Many-to-Many)
CREATE TABLE Students_Minor_Attends (
   studentID INT NOT NULL,
   minorID INT NOT NULL,
   PRIMARY KEY (studentID, minorID),
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE,
   FOREIGN KEY (minorID) REFERENCES Minors(minorID) ON DELETE CASCADE
);


-- Students-Export Results
CREATE TABLE Students_Export_Results (
   studentID INT NOT NULL,
   exportID INT NOT NULL,
   PRIMARY KEY (studentID, exportID),
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE
);


-- Students-Event Attendees (Many-to-Many)
CREATE TABLE Students_Event_Attendees (
   attendanceID INT PRIMARY KEY AUTO_INCREMENT,
   studentID INT NOT NULL,
   eventID INT NOT NULL,
   status VARCHAR(50),
   timestamp DATETIME,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   UNIQUE KEY unique_attendance (studentID, eventID)
);


-- Events-Event Keywords (Many-to-Many)
CREATE TABLE Events_Event_Keywords (
   eventID INT NOT NULL,
   keywordID INT NOT NULL,
   PRIMARY KEY (eventID, keywordID),
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (keywordID) REFERENCES Keywords(keywordID) ON DELETE CASCADE
);


-- Schedule Changes (weak entity dependent on Locations and Events)
CREATE TABLE Schedule_Changes (
   changeID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   oldLocation VARCHAR(100),
   newLocation VARCHAR(100),
   locationID INT NOT NULL,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (locationID) REFERENCES Locations(locationID) ON DELETE CASCADE
);


-- Rankings (weak entity dependent on Clubs)
CREATE TABLE Rankings (
   rankID INT PRIMARY KEY AUTO_INCREMENT,
   clubID INT NOT NULL,
   rankingValue DECIMAL(5,2),
   rankingType VARCHAR(50),
   rankingYear INT,
   rankingQuarter INT,
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE
);


-- Collaborations (weak entity dependent on Events)
CREATE TABLE Collaborations (
   collaborationID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   status VARCHAR(50),
   clubID INT,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE
);


-- Alerts (weak entity dependent on Events)
CREATE TABLE Alerts (
   alertID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   studentID INT,
   alertType VARCHAR(50),
   isSolved BOOLEAN DEFAULT FALSE,
   description TEXT,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE
);


-- Major (multivalued attribute)
CREATE TABLE Major (
   id INT PRIMARY KEY AUTO_INCREMENT,
   majorID INT NOT NULL,
   studentID INT NOT NULL,
   FOREIGN KEY (majorID) REFERENCES Majors(majorID) ON DELETE CASCADE,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE
);


-- Minor (multivalued attribute)
CREATE TABLE Minor (
   id INT PRIMARY KEY AUTO_INCREMENT,
   minorID INT NOT NULL,
   studentID INT NOT NULL,
   FOREIGN KEY (minorID) REFERENCES Minors(minorID) ON DELETE CASCADE,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE
);

-- Event Invitations (entity)
CREATE TABLE event_invitations (
    invitation_id INT PRIMARY KEY,
    event_id INT NOT NULL,
    sender_student_id INT NOT NULL,
    recipient_student_id INT NOT NULL,
    invitation_status VARCHAR(20) NOT NULL,
    sent_datetime DATETIME NOT NULL,
      FOREIGN KEY (event_id) REFERENCES Events(eventID)
        ON DELETE CASCADE,
    FOREIGN KEY (sender_student_id) REFERENCES Students(studentID)
        ON DELETE CASCADE,
    FOREIGN KEY (recipient_student_id) REFERENCES Students(studentID)
        ON DELETE CASCADE);