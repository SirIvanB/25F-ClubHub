DROP DATABASE IF EXISTS ClubHub;
CREATE DATABASE ClubHub;
USE ClubHub;


-- Students Table
CREATE TABLE Students (
   studentID INT PRIMARY KEY,
   email VARCHAR(100) UNIQUE NOT NULL,
   firstName VARCHAR(50) NOT NULL,
   lastName VARCHAR(50) NOT NULL,
   year INT,
   major VARCHAR(100)
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
   type VARCHAR(50),
   budget DECIMAL(10,2),
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
   capacity INT,
   location VARCHAR(200),
   buildingName VARCHAR(100),
   roomNumber VARCHAR(20),
   mapCoordinates VARCHAR(100),
   eventType VARCHAR(50),
   lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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

-- RSVP Table (for event registration/reservations)
CREATE TABLE RSVPs (
   rsvpID INT PRIMARY KEY AUTO_INCREMENT,
   studentID INT NOT NULL,
   eventID INT NOT NULL,
   status ENUM('confirmed', 'waitlisted', 'cancelled') DEFAULT 'confirmed',
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   UNIQUE KEY unique_rsvp (studentID, eventID)
);

-- Event Invitations Table
CREATE TABLE Event_Invitations (
   invitationID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   senderStudentID INT NOT NULL,
   recipientStudentID INT NOT NULL,
   status ENUM('pending', 'accepted', 'declined') DEFAULT 'pending',
   sentAt DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (senderStudentID) REFERENCES Students(studentID) ON DELETE CASCADE,
   FOREIGN KEY (recipientStudentID) REFERENCES Students(studentID) ON DELETE CASCADE
);


-- Feedback Table (for event feedback from students)
CREATE TABLE Feedback (
   feedbackID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   studentID INT NOT NULL,
   rating INT CHECK (rating >= 1 AND rating <= 5),
   comments TEXT,
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE CASCADE
);


-- Venues Table (separate from Locations for capacity tracking)
CREATE TABLE Venues (
   venueID INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   building VARCHAR(100),
   capacity INT,
   locationID INT,
   FOREIGN KEY (locationID) REFERENCES Locations(locationID) ON DELETE SET NULL
);


-- Audit Logs Table (for system administrator tracking)
CREATE TABLE Audit_Logs (
   logID INT PRIMARY KEY AUTO_INCREMENT,
   userID INT,
   actionType VARCHAR(50) NOT NULL,
   entityType VARCHAR(50),
   entityID INT,
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   details TEXT,
   ipAddress VARCHAR(45),
   userAgent TEXT,
   status VARCHAR(50)
);


-- Search Logs Table (for data analyst tracking)
CREATE TABLE Search_Logs (
   searchLogID INT PRIMARY KEY AUTO_INCREMENT,
   studentID INT,
   searchQuery VARCHAR(255) NOT NULL,
   resultsCount INT DEFAULT 0,
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE SET NULL
);


-- System Metrics Table (for server monitoring)
CREATE TABLE System_Metrics (
   metricID INT PRIMARY KEY AUTO_INCREMENT,
   metricName VARCHAR(100) NOT NULL,
   metricValue DECIMAL(10,2),
   metricUnit VARCHAR(50),
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   status VARCHAR(50),
   thresholdWarning DECIMAL(10,2),
   thresholdCritical DECIMAL(10,2)
);


-- System Alerts Table (for automated alerts)
CREATE TABLE System_Alerts (
   alertID INT PRIMARY KEY AUTO_INCREMENT,
   alertType VARCHAR(50) NOT NULL,
   severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
   message TEXT,
   triggeredAt DATETIME DEFAULT CURRENT_TIMESTAMP,
   resolved BOOLEAN DEFAULT FALSE,
   resolvedAt DATETIME
);


-- Documentation Table (for system docs and changelogs)
CREATE TABLE Documentation (
   documentID INT PRIMARY KEY AUTO_INCREMENT,
   title VARCHAR(200) NOT NULL,
   category VARCHAR(50),
   version VARCHAR(20),
   content TEXT,
   lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP,
   updatedByUserID INT
);


-- Engagement Reports Table (for weekly/monthly reports)
CREATE TABLE Engagement_Reports (
   reportID INT PRIMARY KEY AUTO_INCREMENT,
   reportPeriodStart DATE NOT NULL,
   reportPeriodEnd DATE NOT NULL,
   totalActiveUsers INT,
   totalEventsCreated INT,
   totalRSVPs INT,
   totalAttendance INT,
   totalSearches INT,
   generatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Club Categories Junction Table (clubs can have multiple categories)
CREATE TABLE Club_Categories (
   clubID INT NOT NULL,
   categoryID INT NOT NULL,
   PRIMARY KEY (clubID, categoryID),
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE,
   FOREIGN KEY (categoryID) REFERENCES Categories(categoryID) ON DELETE CASCADE
);


