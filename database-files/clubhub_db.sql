DROP DATABASE IF EXISTS ClubHub;
CREATE DATABASE ClubHub;
USE ClubHub;

-- Students Table (with year and major from teammate's version)
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

-- Categories Table
CREATE TABLE Categories (
   categoryID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL
);

-- Clubs Table (MERGED: budget + competitiveness_level + type)
CREATE TABLE Clubs (
   clubID INT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   email VARCHAR(100),
   adviser VARCHAR(100),
   categoryID INT,
   type VARCHAR(50),
   budget DECIMAL(10,2),
   competitiveness_level INT,
   FOREIGN KEY (categoryID) REFERENCES Categories(categoryID)
);

-- Events Table (teammate's more complete version)
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

-- Club Memberships Table (ADDED from your version)
CREATE TABLE club_memberships (
   membership_id INT PRIMARY KEY AUTO_INCREMENT,
   club_id INT NOT NULL,
   student_id INT NOT NULL,
   join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (club_id) REFERENCES Clubs(clubID) ON DELETE CASCADE,
   FOREIGN KEY (student_id) REFERENCES Students(studentID) ON DELETE CASCADE,
   UNIQUE KEY unique_membership (club_id, student_id)
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

-- Schedule Changes
CREATE TABLE Schedule_Changes (
   changeID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   oldLocation VARCHAR(100),
   newLocation VARCHAR(100),
   locationID INT NOT NULL,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (locationID) REFERENCES Locations(locationID) ON DELETE CASCADE
);

-- Rankings
CREATE TABLE Rankings (
   rankID INT PRIMARY KEY AUTO_INCREMENT,
   clubID INT NOT NULL,
   rankingValue DECIMAL(5,2),
   rankingType VARCHAR(50),
   rankingYear INT,
   rankingQuarter INT,
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE
);

-- Collaborations
CREATE TABLE Collaborations (
   collaborationID INT PRIMARY KEY AUTO_INCREMENT,
   eventID INT NOT NULL,
   status VARCHAR(50),
   clubID INT,
   FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE
);

-- Alerts
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

-- RSVP Table (from teammate's version)
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

-- Event Invitations (merged table names)
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

-- Feedback Table (from teammate's version)
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

-- Venues Table (from teammate's version)
CREATE TABLE Venues (
   venueID INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   building VARCHAR(100),
   capacity INT,
   locationID INT,
   FOREIGN KEY (locationID) REFERENCES Locations(locationID) ON DELETE SET NULL
);

-- Audit Logs Table (from teammate's version)
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

-- Search Logs Table (from teammate's version)
CREATE TABLE Search_Logs (
   searchLogID INT PRIMARY KEY AUTO_INCREMENT,
   studentID INT,
   searchQuery VARCHAR(255) NOT NULL,
   resultsCount INT DEFAULT 0,
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (studentID) REFERENCES Students(studentID) ON DELETE SET NULL
);

-- System Metrics Table (from teammate's version)
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

-- System Alerts Table (from teammate's version)
CREATE TABLE System_Alerts (
   alertID INT PRIMARY KEY AUTO_INCREMENT,
   alertType VARCHAR(50) NOT NULL,
   severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
   message TEXT,
   triggeredAt DATETIME DEFAULT CURRENT_TIMESTAMP,
   resolved BOOLEAN DEFAULT FALSE,
   resolvedAt DATETIME
);

-- Documentation Table (from teammate's version)
CREATE TABLE Documentation (
   documentID INT PRIMARY KEY AUTO_INCREMENT,
   title VARCHAR(200) NOT NULL,
   category VARCHAR(50),
   version VARCHAR(20),
   content TEXT,
   lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP,
   updatedByUserID INT
);

-- Engagement Reports Table (from teammate's version)
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

-- Club Categories Junction Table (from teammate's version)
CREATE TABLE Club_Categories (
   clubID INT NOT NULL,
   categoryID INT NOT NULL,
   PRIMARY KEY (clubID, categoryID),
   FOREIGN KEY (clubID) REFERENCES Clubs(clubID) ON DELETE CASCADE,
   FOREIGN KEY (categoryID) REFERENCES Categories(categoryID) ON DELETE CASCADE
);

-- ========================================
-- MOCK DATA
-- ========================================

-- Insert Students
INSERT INTO Students (studentID, email, firstName, lastName, year, major) VALUES
(10000001, 'sarah.chen@northeastern.edu', 'Sarah', 'Chen', 2, 'Computer Science'),
(10000002, 'michael.patel@northeastern.edu', 'Michael', 'Patel', 3, 'Business Administration'),
(10000003, 'emma.johnson@northeastern.edu', 'Emma', 'Johnson', 1, 'Computer Science'),
(10000004, 'david.kim@northeastern.edu', 'David', 'Kim', 4, 'Mechanical Engineering'),
(10000005, 'olivia.garcia@northeastern.edu', 'Olivia', 'Garcia', 2, 'Biology'),
(10000006, 'james.wilson@northeastern.edu', 'James', 'Wilson', 3, 'Business Administration'),
(10000007, 'sophia.martinez@northeastern.edu', 'Sophia', 'Martinez', 2, 'Communications'),
(10000008, 'ethan.brown@northeastern.edu', 'Ethan', 'Brown', 1, 'Computer Science'),
(10000009, 'ava.davis@northeastern.edu', 'Ava', 'Davis', 3, 'Psychology'),
(10000010, 'noah.rodriguez@northeastern.edu', 'Noah', 'Rodriguez', 4, 'Political Science'),
(10000011, 'isabella.lee@northeastern.edu', 'Isabella', 'Lee', 2, 'Data Science'),
(10000012, 'lucas.anderson@northeastern.edu', 'Lucas', 'Anderson', 3, 'Mechanical Engineering'),
(10000013, 'mia.thomas@northeastern.edu', 'Mia', 'Thomas', 1, 'Biology'),
(10000014, 'william.jackson@northeastern.edu', 'William', 'Jackson', 4, 'Mathematics'),
(10000015, 'amelia.white@northeastern.edu', 'Amelia', 'White', 2, 'Environmental Science');

-- Insert Majors
INSERT INTO Majors (majorID, name) VALUES
(20000001, 'Computer Science'),
(20000002, 'Business Administration'),
(20000003, 'Mechanical Engineering'),
(20000004, 'Biology'),
(20000005, 'Psychology'),
(20000006, 'Data Science'),
(20000007, 'Political Science'),
(20000008, 'Communications'),
(20000009, 'Mathematics'),
(20000010, 'Environmental Science');

-- Insert Minors
INSERT INTO Minors (minorID, name) VALUES
(30000001, 'Entrepreneurship'),
(30000002, 'Statistics'),
(30000003, 'Music'),
(30000004, 'Spanish'),
(30000005, 'Philosophy'),
(30000006, 'Sustainability'),
(30000007, 'Art History'),
(30000008, 'Economics'),
(30000009, 'Public Health'),
(30000010, 'Creative Writing');

-- Insert Categories
INSERT INTO Categories (categoryID, name) VALUES
(40000001, 'Technology'),
(40000002, 'Sports & Recreation'),
(40000003, 'Arts & Culture'),
(40000004, 'Academic'),
(40000005, 'Community Service'),
(40000006, 'Professional Development'),
(40000007, 'Social'),
(40000008, 'Special Interest');

-- Insert Clubs (WITH budget, competitiveness_level, and type)
INSERT INTO Clubs (clubID, name, email, adviser, categoryID, type, budget, competitiveness_level) VALUES
(50000001, 'Husky Hackers', 'huskyhackers@northeastern.edu', 'Dr. Robert Chen', 40000001, 'Academic', 12000.00, 8),
(50000002, 'Northeastern Dance Collective', 'nudance@northeastern.edu', 'Prof. Maria Santos', 40000003, 'Arts', 8500.00, 6),
(50000003, 'Investment Club', 'investmentclub@northeastern.edu', 'Dr. James Peterson', 40000006, 'Professional', 15000.00, 9),
(50000004, 'Environmental Action Group', 'eag@northeastern.edu', 'Dr. Sarah Green', 40000005, 'Service', 6000.00, 4),
(50000005, 'Debate Society', 'debate@northeastern.edu', 'Prof. Michael Brown', 40000004, 'Academic', 7500.00, 7),
(50000006, 'Intramural Soccer League', 'soccer@northeastern.edu', 'Coach David Miller', 40000002, 'Sports', 5000.00, 5),
(50000007, 'Photography Club', 'photoclub@northeastern.edu', 'Prof. Lisa Wong', 40000003, 'Arts', 4000.00, 3),
(50000008, 'Pre-Med Society', 'premed@northeastern.edu', 'Dr. Amanda Lee', 40000006, 'Professional', 10000.00, 8),
(50000009, 'International Students Association', 'isa@northeastern.edu', 'Dr. Carlos Rodriguez', 40000007, 'Social', 9000.00, 6),
(50000010, 'Robotics Team', 'robotics@northeastern.edu', 'Prof. Emily Zhang', 40000001, 'Academic', 18000.00, 10);

-- Insert Club Memberships
INSERT INTO club_memberships (club_id, student_id) VALUES
-- Husky Hackers: 5 members
(50000001, 10000001), (50000001, 10000003), (50000001, 10000008), (50000001, 10000011), (50000001, 10000014),
-- Dance Collective: 2 members  
(50000002, 10000007), (50000002, 10000009),
-- Investment Club: 3 members
(50000003, 10000002), (50000003, 10000006), (50000003, 10000012),
-- Environmental Action: 3 members
(50000004, 10000004), (50000004, 10000005), (50000004, 10000015),
-- Debate Society: 1 member
(50000005, 10000010),
-- Soccer League: 1 member
(50000006, 10000006),
-- Photography Club: 1 member
(50000007, 10000007),
-- Pre-Med Society: 2 members
(50000008, 10000005), (50000008, 10000013),
-- ISA: 1 member
(50000009, 10000009),
-- Robotics Team: 2 members
(50000010, 10000004), (50000010, 10000012);

-- Insert Locations
INSERT INTO Locations (locationID, capacity, buildingName, buildingNumber, floorNumber) VALUES
(60000001, 150, 'Curry Student Center', 'CSC', 4),
(60000002, 50, 'Snell Library', 'SNL', 2),
(60000003, 200, 'West Village H', 'WVH', 1),
(60000004, 75, 'Dodge Hall', 'DH', 3),
(60000005, 100, 'Richards Hall', 'RH', 2),
(60000006, 300, 'Cabot Cage', 'CC', 1),
(60000007, 40, 'Ell Hall', 'EH', 4),
(60000008, 80, 'Churchill Hall', 'CH', 1),
(60000009, 120, 'Forsyth Building', 'FB', 5),
(60000010, 60, 'Ryder Hall', 'RY', 2);

-- Insert Events (with all fields)
INSERT INTO Events (eventID, name, description, searchDescription, startDateTime, endDateTime, authID, clubID, capacity, location, buildingName, roomNumber) VALUES
(70000001, 'Intro to Web Development Workshop', 'Learn the basics of HTML, CSS, and JavaScript', 'web development html css javascript workshop coding', '2024-12-10 18:00:00', '2024-12-10 20:00:00', 10000001, 50000001, 80, 'West Village H 210', 'West Village H', '210'),
(70000002, 'Winter Dance Showcase', 'Annual performance featuring various dance styles', 'dance performance showcase contemporary hip-hop ballet', '2024-12-15 19:00:00', '2024-12-15 21:30:00', 10000002, 50000002, 200, 'Curry Student Center Ballroom', 'Curry Student Center', 'Ballroom'),
(70000003, 'Portfolio Management Seminar', 'Expert insights on building an investment portfolio', 'investment finance stocks portfolio wealth management', '2024-12-12 17:00:00', '2024-12-12 19:00:00', 10000003, 50000003, 60, 'Dodge Hall 301', 'Dodge Hall', '301'),
(70000004, 'Beach Cleanup Day', 'Community service event at Revere Beach', 'environment cleanup volunteer service community beach', '2024-12-08 09:00:00', '2024-12-08 13:00:00', 10000004, 50000004, 50, 'Revere Beach', 'N/A', 'Outdoor'),
(70000005, 'Debate Tournament Finals', 'Championship round of fall debate competition', 'debate tournament competition public speaking argumentation', '2024-12-14 15:00:00', '2024-12-14 18:00:00', 10000005, 50000005, 100, 'Richards Hall 150', 'Richards Hall', '150'),
(70000006, 'Soccer Tournament Kickoff', 'First matches of the winter intramural season', 'soccer sports tournament intramural athletics competition', '2024-12-09 14:00:00', '2024-12-09 17:00:00', 10000006, 50000006, 300, 'Cabot Cage Field', 'Cabot Cage', 'Field'),
(70000007, 'Night Photography Walk', 'Guided tour for capturing Boston at night', 'photography camera night urban cityscape tutorial', '2024-12-11 20:00:00', '2024-12-11 22:30:00', 10000007, 50000007, 25, 'Meet at Snell Library', 'Snell Library', 'Lobby'),
(70000008, 'MCAT Prep Session', 'Study strategies and practice questions', 'mcat medicine premed medical school test preparation', '2024-12-13 16:00:00', '2024-12-13 18:00:00', 10000008, 50000008, 40, 'Churchill Hall 105', 'Churchill Hall', '105'),
(70000009, 'Cultural Food Festival', 'Celebrate diversity through international cuisine', 'international culture food diversity festival multicultural', '2024-12-16 12:00:00', '2024-12-16 16:00:00', 10000009, 50000009, 150, 'Ell Hall Plaza', 'Ell Hall', 'Plaza'),
(70000010, 'Robotics Competition Prep', 'Final preparation for regional competition', 'robotics engineering competition programming stem technology', '2024-12-07 10:00:00', '2024-12-07 14:00:00', 10000010, 50000010, 50, 'Forsyth Building Lab', 'Forsyth Building', '301'),
(70000011, 'Hackathon 2024', '24-hour coding competition with prizes', 'hackathon coding programming competition innovation software', '2024-12-20 09:00:00', '2024-12-21 09:00:00', 10000001, 50000001, 100, 'West Village H Commons', 'West Village H', 'Commons'),
(70000012, 'Investment Panel Discussion', 'Alumni share career insights in finance', 'finance career alumni networking investment banking', '2024-12-18 18:30:00', '2024-12-18 20:00:00', 10000003, 50000003, 75, 'Ryder Hall 155', 'Ryder Hall', '155');

-- Insert Servers
INSERT INTO Servers (serverID, status, ipAddress, lastUpdated) VALUES
(80000001, 'active', '192.168.1.10', '2024-12-06 08:00:00'),
(80000002, 'active', '192.168.1.11', '2024-12-06 08:00:00'),
(80000003, 'maintenance', '192.168.1.12', '2024-12-05 14:30:00'),
(80000004, 'active', '192.168.1.13', '2024-12-06 07:45:00'),
(80000005, 'inactive', '192.168.1.14', '2024-12-04 16:20:00');

-- Insert Keywords
INSERT INTO Keywords (keywordID, keyword) VALUES
(90000001, 'technology'),
(90000002, 'coding'),
(90000003, 'dance'),
(90000004, 'finance'),
(90000005, 'environment'),
(90000006, 'debate'),
(90000007, 'sports'),
(90000008, 'photography'),
(90000009, 'medicine'),
(90000010, 'culture'),
(90000011, 'robotics'),
(90000012, 'networking'),
(90000013, 'competition'),
(90000014, 'workshop'),
(90000015, 'volunteer');

-- Insert EventLog
INSERT INTO EventLog (logID, logTimestamp, status, severity, serverID) VALUES
(11000001, '2024-12-06 07:15:00', 'Server started successfully', 'info', 80000001),
(11000002, '2024-12-06 07:20:00', 'Database connection established', 'info', 80000001),
(11000003, '2024-12-06 07:45:00', 'High CPU usage detected', 'warning', 80000002),
(11000004, '2024-12-05 14:30:00', 'Scheduled maintenance initiated', 'info', 80000003),
(11000005, '2024-12-05 14:45:00', 'System update in progress', 'warning', 80000003),
(11000006, '2024-12-04 16:20:00', 'Connection timeout error', 'error', 80000005),
(11000007, '2024-12-06 08:00:00', 'Backup completed successfully', 'info', 80000004),
(11000008, '2024-12-06 06:30:00', 'Login attempt failed', 'warning', 80000001);

-- Insert Administrators
INSERT INTO Administrators (adminID, email, firstName, lastName) VALUES
(12000001, 'admin.thompson@northeastern.edu', 'Jennifer', 'Thompson'),
(12000002, 'admin.nguyen@northeastern.edu', 'Kevin', 'Nguyen'),
(12000003, 'admin.patel@northeastern.edu', 'Priya', 'Patel'),
(12000004, 'admin.santos@northeastern.edu', 'Marco', 'Santos'),
(12000005, 'admin.washington@northeastern.edu', 'Alicia', 'Washington');

-- Insert Students_Major_Attends
INSERT INTO Students_Major_Attends (studentID, majorID) VALUES
(10000001, 20000001), (10000001, 20000006),
(10000002, 20000002),
(10000003, 20000001),
(10000004, 20000003),
(10000005, 20000004), (10000005, 20000009),
(10000006, 20000002),
(10000007, 20000008),
(10000008, 20000001),
(10000009, 20000005),
(10000010, 20000007),
(10000011, 20000006),
(10000012, 20000003),
(10000013, 20000004),
(10000014, 20000009),
(10000015, 20000010);

-- Insert Students_Minor_Attends
INSERT INTO Students_Minor_Attends (studentID, minorID) VALUES
(10000001, 30000001),
(10000002, 30000008),
(10000003, 30000002),
(10000004, 30000006),
(10000005, 30000009),
(10000006, 30000001),
(10000007, 30000003),
(10000008, 30000002),
(10000009, 30000005),
(10000010, 30000008),
(10000011, 30000001),
(10000012, 30000006),
(10000013, 30000009),
(10000014, 30000002),
(10000015, 30000004);

-- Insert Students_Event_Attendees
INSERT INTO Students_Event_Attendees (studentID, eventID, status, timestamp) VALUES
(10000001, 70000001, 'confirmed', '2024-12-06 10:00:00'),
(10000001, 70000011, 'confirmed', '2024-12-06 10:30:00'),
(10000002, 70000003, 'confirmed', '2024-12-06 09:00:00'),
(10000003, 70000001, 'confirmed', '2024-12-06 11:00:00'),
(10000003, 70000011, 'waitlisted', '2024-12-06 12:00:00'),
(10000004, 70000010, 'confirmed', '2024-12-05 15:00:00'),
(10000005, 70000008, 'confirmed', '2024-12-06 08:00:00'),
(10000005, 70000004, 'confirmed', '2024-12-05 14:00:00'),
(10000006, 70000006, 'confirmed', '2024-12-06 13:00:00'),
(10000007, 70000002, 'confirmed', '2024-12-06 10:00:00'),
(10000007, 70000009, 'confirmed', '2024-12-06 11:30:00'),
(10000008, 70000001, 'cancelled', '2024-12-06 09:30:00'),
(10000009, 70000009, 'confirmed', '2024-12-06 10:00:00'),
(10000010, 70000005, 'confirmed', '2024-12-06 14:00:00'),
(10000011, 70000001, 'confirmed', '2024-12-06 11:00:00'),
(10000012, 70000010, 'confirmed', '2024-12-05 16:00:00'),
(10000013, 70000008, 'confirmed', '2024-12-06 09:00:00'),
(10000014, 70000011, 'confirmed', '2024-12-06 13:00:00'),
(10000015, 70000004, 'confirmed', '2024-12-05 15:00:00');

-- Insert Events_Event_Keywords
INSERT INTO Events_Event_Keywords (eventID, keywordID) VALUES
(70000001, 90000001), (70000001, 90000002), (70000001, 90000014),
(70000002, 90000003),
(70000003, 90000004), (70000003, 90000012),
(70000004, 90000005), (70000004, 90000015),
(70000005, 90000006), (70000005, 90000013),
(70000006, 90000007), (70000006, 90000013),
(70000007, 90000008), (70000007, 90000014),
(70000008, 90000009), (70000008, 90000014),
(70000009, 90000010),
(70000010, 90000011), (70000010, 90000013),
(70000011, 90000001), (70000011, 90000002), (70000011, 90000013),
(70000012, 90000004), (70000012, 90000012);

-- Insert Schedule_Changes
INSERT INTO Schedule_Changes (eventID, oldLocation, newLocation, locationID) VALUES
(70000001, 'WVH 108', 'WVH 210', 60000003),
(70000005, 'Dodge Hall 201', 'Richards Hall 150', 60000005),
(70000009, 'Curry Student Center Ballroom A', 'Curry Student Center Grand Ballroom', 60000001);

-- Insert Rankings
INSERT INTO Rankings (clubID, rankingValue, rankingType, rankingYear, rankingQuarter) VALUES
(50000001, 4.8, 'Student Engagement', 2024, 4),
(50000002, 4.5, 'Student Engagement', 2024, 4),
(50000003, 4.7, 'Student Engagement', 2024, 4),
(50000004, 4.6, 'Community Impact', 2024, 4),
(50000005, 4.3, 'Academic Excellence', 2024, 4),
(50000006, 4.4, 'Student Engagement', 2024, 4),
(50000007, 4.2, 'Student Engagement', 2024, 4),
(50000008, 4.9, 'Academic Excellence', 2024, 4),
(50000009, 4.7, 'Diversity & Inclusion', 2024, 4),
(50000010, 4.8, 'Innovation', 2024, 4);

-- Insert Collaborations
INSERT INTO Collaborations (eventID, status, clubID) VALUES
(70000001, 'confirmed', 50000010),
(70000009, 'confirmed', 50000002),
(70000009, 'confirmed', 50000007),
(70000011, 'pending', 50000003),
(70000012, 'confirmed', 50000008);

-- Insert Alerts
INSERT INTO Alerts (eventID, studentID, alertType, isSolved, description) VALUES
(70000001, 10000001, 'room_change', TRUE, 'Event location changed from WVH 108 to WVH 210'),
(70000005, 10000010, 'room_change', TRUE, 'Debate finals moved to larger venue'),
(70000008, 10000005, 'cancellation_risk', FALSE, 'Low registration numbers, event may be cancelled'),
(70000011, 10000003, 'waitlist', FALSE, 'You are currently on the waitlist for Hackathon 2024'),
(70000009, 10000007, 'reminder', TRUE, 'Event starts in 24 hours');

-- Insert Major (multivalued attribute table)
INSERT INTO Major (majorID, studentID) VALUES
(20000001, 10000001), (20000006, 10000001),
(20000002, 10000002),
(20000001, 10000003),
(20000003, 10000004),
(20000004, 10000005), (20000009, 10000005),
(20000002, 10000006),
(20000008, 10000007),
(20000001, 10000008),
(20000005, 10000009),
(20000007, 10000010),
(20000006, 10000011),
(20000003, 10000012),
(20000004, 10000013),
(20000009, 10000014),
(20000010, 10000015);

-- Insert Minor (multivalued attribute table)
INSERT INTO Minor (minorID, studentID) VALUES
(30000001, 10000001),
(30000008, 10000002),
(30000002, 10000003),
(30000006, 10000004),
(30000009, 10000005),
(30000001, 10000006),
(30000003, 10000007),
(30000002, 10000008),
(30000005, 10000009),
(30000008, 10000010),
(30000001, 10000011),
(30000006, 10000012),
(30000009, 10000013),
(30000002, 10000014),
(30000004, 10000015);

-- Insert Event Invitations (using new table name)
INSERT INTO Event_Invitations (eventID, senderStudentID, recipientStudentID, status, sentAt) VALUES
(70000001, 10000001, 10000003, 'accepted', '2024-12-05 14:00:00'),
(70000001, 10000001, 10000011, 'accepted', '2024-12-05 14:15:00'),
(70000002, 10000007, 10000009, 'accepted', '2024-12-04 16:00:00'),
(70000003, 10000002, 10000006, 'pending', '2024-12-06 09:00:00'),
(70000004, 10000005, 10000015, 'accepted', '2024-12-04 10:00:00'),
(70000006, 10000006, 10000007, 'declined', '2024-12-05 13:00:00'),
(70000008, 10000005, 10000013, 'accepted', '2024-12-05 11:00:00'),
(70000009, 10000007, 10000009, 'accepted', '2024-12-05 15:00:00'),
(70000011, 10000001, 10000014, 'accepted', '2024-12-06 08:00:00'),
(70000011, 10000003, 10000008, 'pending', '2024-12-06 10:00:00');