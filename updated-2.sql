CREATE TABLE Customer (
  Customer_ID INT PRIMARY KEY,
  Customer_Name VARCHAR(256),
  Email_ID VARCHAR(256),
  Phone_no BIGINT,
  Age SMALLINT,
  Gender CHAR(1),
  Addr VARCHAR(90)
);

CREATE TABLE CustomerPasswords (
  Customer_ID INT PRIMARY KEY,
   Password_ VARCHAR(20)
) ;

CREATE TABLE Supplier (
  Supplier_ID INT PRIMARY KEY,
  Supplier_Name VARCHAR(128),
  Phone_no BIGINT,
  Email_ID VARCHAR(256),
  Addr VARCHAR(90),
  License_no CHAR(15)
);

CREATE TABLE Medicine (
  Medicine_ID INT PRIMARY KEY,
  Medicine_Name VARCHAR(128),
  Manufacturer VARCHAR(128),
  Date_of_mfg DATE,
  ExpiryDate DATE,
  Batch_no VARCHAR(128),
  Price_per_unit DECIMAL(6,2),
  No_of_units_sold INT,
  Category CHAR(25),
  current_stock INT DEFAULT 5  
);

CREATE TABLE DeliveryPerson (
  DeliveryPerson_ID INT PRIMARY KEY, 
  DeliveryPerson_Name VARCHAR(128),
  Email_ID VARCHAR(256),
  Phone_no BIGINT,
  Aadhar_no BIGINT,
  Driving_license_no CHAR(16),
  Vehicle_no CHAR(12),
  Bank_acc_no VARCHAR(16),
  Rating DECIMAL(2, 1),
  status_ VARCHAR(20) DEFAULT 'pending',
  addition BOOLEAN DEFAULT FALSE
);


CREATE TABLE Requested_Delivery_Partners (
  id SERIAL PRIMARY KEY,
  name_ VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(15),
  aadhaar VARCHAR(12),
  driving_licence VARCHAR(20),
  vehicle_no VARCHAR(15),
  status_ VARCHAR(20) DEFAULT 'Pending'
);



CREATE TABLE Admin (
  Admin_id CHAR(7),
  Password_ CHAR(10),
  Addr VARCHAR(90),
  Manages VARCHAR(90)
);

CREATE TABLE CustomerOrder (
  Customer_ID INT,
  Medicine_ID INT,
  Price INT,
  ExpiryDate DATE,
  Medicine_Name VARCHAR(128),
  Order_ID INT,
  Delivery_address VARCHAR(90),
  Medicine_quantity SMALLINT,
  Order_status CHAR(10),
  PRIMARY KEY(Customer_ID, Medicine_ID, Order_ID),
  FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE ShoppingCart (
  Customer_ID INT,
  Medicine_ID INT,
  Price INT,
  ExpiryDate DATE,
  PRIMARY KEY(Customer_ID, Medicine_ID),
  FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Prescription (
  Customer_ID INT,
  Photo_ID INT 
);

CREATE TABLE SupplierRequests (
  Supplier_ID INT,
  Medicine_ID INT,
  Requested_quantity SMALLINT,
  Requested_price INT,
  Answered_quantity SMALLINT NULL,
  Answered_price INT NULL,
  Response_status CHAR(10),
  Request_ID INT,
  PRIMARY KEY(Request_ID, Medicine_ID)
);

CREATE TABLE SupplyOrder (
  Request_ID INT,
  Supplier_ID INT,
  Supplier_Name VARCHAR(128),
  Medicine_ID INT,
  Medicine_Name VARCHAR(128),
  Price_per_unit INT,
  Quantity SMALLINT,
  Order_date DATE NOT NULL DEFAULT CURRENT_DATE,
  Delivery_status CHAR(10),
  PRIMARY KEY(Request_ID, Medicine_ID),
  FOREIGN KEY (Request_ID,  Medicine_ID) REFERENCES SupplierRequests(Request_ID, Medicine_ID)
);


CREATE TABLE ManageOrder (
  DeliveryPerson_ID INT,
  Order_status CHAR(10),
  Order_ID INT PRIMARY KEY,
  Delivery_address VARCHAR(90),
  Customer_ID INT,
  Total_price INT,
  Order_Time TIMESTAMP 
);

CREATE TABLE DeliveredToCustomer (
  Customer_ID INT,
  DeliveryPerson_ID INT,
  Order_ID INT PRIMARY KEY,
  Delivery_Time TIMESTAMP
);

CREATE TABLE DeliveryManReview (
  Order_ID INT,
  DeliveryPerson_ID INT,
  Review VARCHAR(256),
  Rating INT,
  PRIMARY KEY (Order_ID, DeliveryPerson_ID)
);


INSERT INTO Customer (Customer_ID, Customer_Name, Email_ID, Phone_no, Age, Gender, Addr) 
VALUES 
(1, 'Rahul Kumar', 'rahul@example.com', 9876543210, 50,  'M', '23, Gandhi Road' ),
(2, 'Priya Sharma', 'priya@example.com', 8765432109, 30,  'F', '45, Nehru Nagar' ),
(3, 'Amit Patel', 'amit@example.com', 7654321098, 20,  'M', '12, Gandhi Nagar'),
(4, 'Sneha Singh', 'sneha@example.com', 6543210987, 27, 'M', '89, Krisha Street'),
(5, 'Anjali Gupta', 'anjali@example.com', 5432109876, 35, 'F', '34, Rama Road'),
(6, 'Rajesh Khanna', 'rajesh@example.com', 4321098765, 30, 'M', '78, Laxmi Nagar'),
(7, 'Kavita Verma', 'kavita@example.com', 3210987654, 37,  'F', '56, Radha Street'),
(8, 'Manoj Tiwari', 'manoj@example.com', 2109876543, 62,  'F', '90, Shiva Road'),
(9, 'Meena Jain', 'meena@example.com', 1098765432, 41,  'T', '67, Ganesh Nagar'),
(10, 'Sanjay Reddy', 'sanjay@example.com', 1987654325, 51, 'M', '44, Rama Road');

  

INSERT INTO DeliveryPerson (DeliveryPerson_ID, DeliveryPerson_Name, Email_ID, Phone_no, Aadhar_no, Driving_license_no, Vehicle_no, Bank_acc_no, Rating) 
VALUES 
(1, 'Ravi kumar', 'ravi@gmail.com', 9876543210, 265345991234, 'AB47382910564732', 'DL10AB1234', '56000000001', 3.2),
(2, 'Suresh Sharma', 'suresh@gmail.com', 8765432109, 235645982345, 'ZX92038475618394', 'MH12XY5678', '56000000002', 1.1),
(3, 'Vikram Singh', 'vikram@gmail.com', 7654321098, 564212363456, 'MN56473829103485', 'KA03CD9876', '56000000003', 5.0),
(4, 'Prakash Verma', 'prakash@gmail.com', 6543210987, 654987564567, 'KL83746291038475', 'UP16EF5432', '56000000004', 3.6),
(5, 'Amit Tiwari', 'amit@gmail.com', 5432109876, 632612355678, 'PQ19283746573829', 'TN07GH8765', '56000000005', 4.0),
(6, 'Rajesh Jain', 'rajesh@gmail.com', 4321098765, 845900236789, 'XY38475629103847', 'RJ14JK2345', '56000000006', 2.6),
(7, 'Sanjay Reddy', 'sanjay@gmail.com', 3210987654, 987002657890, 'CD74829103746582', 'WB20LM6789', '56000000007', 4.2),
(8, 'Vinod Gupta', 'vinod@gmail.com', 2109876543, 000300158901, 'GH10293847563829', 'GJ05NP4321', '56000000008', 1.6),
(9, 'Anil Patel', 'anil@gmail.com', 1098765432, 111122229012, 'RS56473829103847', 'HR26QR7890', '56000000009', 0.0),
(10, 'Ajay Kumar', 'ajay@gmail.com', 5987654321, 100020000123, 'VW83746592018374', 'PB10ST3456', '56000000010', 3.1);

INSERT INTO Admin (Admin_id, Password_, Addr, Manages) 
VALUES 
('admin', 'admin123', 'IIITD Okhla industrial area phase 3', 'Manages every thing');

INSERT INTO Medicine (Medicine_ID, Medicine_Name, Manufacturer, Date_of_mfg, ExpiryDate, Batch_no, Price_per_unit, No_of_units_sold, Category) 
VALUES 
(201, 'Paracetamol 500mg', 'Cipla', '2024-01-10', '2026-01-10', 'B12345', 2.50, 500, 'Painkiller'),  
(202, 'Amoxicillin 250mg', 'Sun Pharma', '2023-12-05', '2025-12-05', 'A56789', 5.00, 300, 'Antibiotic'),  
(203, 'Cetirizine 200mg', 'Lupin', '2024-02-15', '2026-02-15', 'C23456', 1.75, 400, 'Antihistamine'),  
(204, 'Metformin 10mg', 'Dr. Reddy''s', '2023-11-20', '2025-11-20', 'D98765', 3.00, 600, 'Diabetes'),  
(205, 'Aspirin 500mg', 'Zydus', '2024-03-08', '2026-03-08', 'E34567', 2.00, 700, 'Painkiller'),  
(206, 'Azithromycin', 'Glenmark', '2023-09-12', '2025-09-12', 'F67890', 6.50, 250, 'Antibiotic'),  
(207, 'Ibuprofen', 'Torrent Pharma', '2024-01-25', '2026-01-25', 'G11223', 3.25, 450, 'Painkiller'),  
(208, 'Omeprazole', 'Biocon', '2023-10-30', '2025-10-30', 'H44556', 4.75, 350, 'Gastrointestinal'),  
(209, 'Dolo-650', 'Mankind Pharma', '2024-04-05', '2026-04-05', 'I77889', 2.25, 550, 'Painkiller'),  
(210, 'Atorvastatin', 'Alkem Labs', '2023-08-18', '2025-08-18', 'J99001', 5.50, 380, 'Cardiovascular');



INSERT INTO Supplier (Supplier_ID, Supplier_Name, Phone_no, Email_ID, Addr, License_no) 
VALUES 
(101, 'Sharma Pharmaceuticals', 9876543210, 'sharmapharma@gmail.com', 'okhla industrial area phase 1', 'G7XJ4ZQW2V8MAL9'),
(102, 'Patel Medicals', 8765432109, 'patelpharma@gmail.com', 'faridabad sector 10', 'P3K9T7YXL5VQ2ZJ'),
(103, 'Singh Distributors', 7654321098, 'singhpharma@gmail.com', 'noida sector 37', 'M8Z4WQXJ2V7BKT9'),
(104, 'Gupta Healthcare', 6543210987, 'guptapharma@gmail.com', 'south ex lajpat nagar', 'Y5Q7Z9XJ3WVML2T'),
(105, 'Khanna Enterprises', 5432109876, 'khannapharma@gmail.com', 'hauz khas', 'L8T3Q7V9XJZ2WKM'),
(106, 'Verma Suppliers', 4321098765, 'vermapharma@gmail.com', 'new delhi', 'X2M7Z9VQJ4T5WLB'),
(107, 'Tiwari Pharma', 3210987654, 'tiwaripharma@gmail.com', 'ashram block A', 'B9T3QXJ2W7VML4Z'),
(108, 'Jain Distributors', 2109876543, 'jainpharma@gmail.com', 'greater kailash I', 'J4Z2WQ7X9VMBKLT'),
(109, 'Reddy Pharmaceuticals', 1098765432, 'reddypharma@gmail.com', 'connaught place', 'V7Q9XJ2Z4WMBL3T'),
(110, 'Kumar Medicals',987654321, 'kumarpharma@gmail.com', 'east of kailash', 'T3XJ4Z7VQ9WMBL2');



INSERT INTO SupplierRequests (Supplier_ID, Medicine_ID, Requested_quantity, Requested_price, Answered_quantity, Answered_price, Response_status, Request_ID)
VALUES
(2, 203, 10, 150, NULL, NULL, 'Not seen', 1),
(2, 202, 15, 75, 12, 80, 'Answered', 1),
(2, 204, 20, 30, 25, 30, 'Ordered', 1),
(3, 205, 10, 105, NULL, NULL, 'Not seen', 2),
(1, 206, 5, 50, 6, 60, 'Answered', 3),
(5, 201, 10, 50, 10, 50, 'Ordered', 4);



INSERT INTO SupplyOrder (Request_ID, Supplier_ID, Supplier_Name, Medicine_ID, Medicine_Name, Price_per_unit, Quantity, Order_date, Delivery_status)
VALUES
(1, 101, 'Sharma Pharmaceuticals', 203, 'Cetirizine 200mg', 1.75, 1000, '2025-04-10', 'On The Way'),
(2, 102, 'Patel Medicals', 205, 'Aspirin 500mg', 2.00, 500, '2025-04-11', 'Shipped'),
(3, 103, 'Singh Distributors', 206, 'Azithromycin', 6.50, 800, '2025-04-11', 'Delivered'),
(4, 104, 'Gupta Healthcare', 201, 'Paracetamol 500mg', 2.50, 1200, '2025-04-12', 'Cancelled');


INSERT INTO CustomerOrder (Customer_ID, Medicine_ID, Price, ExpiryDate, Medicine_Name, Order_ID, Delivery_address, Medicine_quantity, Order_status)
VALUES
(2, 201, 100, '2026-02-16', 'Paracetamol', 2, '45, Nehru Nagar', 2, 'Delivered'),
(2, 202, 80, '2027-02-16', 'Amoxicillin', 2, '45, Nehru Nagar', 1, 'Delivered'),
(5, 203, 120, '2025-08-16', 'Omeprazole', 5, '34, Rama Road', 1, 'Delivered'),
(8, 204, 30, '2026-08-16', 'Aspirin', 8, '90, Shiva Road', 1, 'Delivered'),
(1, 205, 200, '2027-08-16', 'Vitamin C', 1, '23, Gandhi Road', 2, 'Pending');

INSERT INTO ShoppingCart (Customer_ID, Medicine_ID, Price, ExpiryDate)
VALUES
(2, 201, 100, '2026-02-16'),
(2, 202, 80, '2027-02-16'),
(5, 203, 120, '2025-08-16'),
(8, 204, 30, '2026-08-16'),
(1, 205, 200, '2027-08-16');

INSERT INTO ManageOrder (DeliveryPerson_ID, Order_status, Order_ID, Delivery_address, Customer_ID, Total_price, Order_Time)
VALUES
(3, 'Delivered', 2, '45, Nehru Nagar', 2, 180, NOW() - INTERVAL '2 DAYS'),
(9, 'Delivered', 5, '34, Rama Road', 5, 120, NOW() - INTERVAL '3 DAYS'),
(6, 'Delivered', 8, '90, Shiva Road', 8, 30, NOW() - INTERVAL '1 DAY'),
(1, 'Pending', 1, '23, Gandhi Road', 1, 200, NOW());

INSERT INTO DeliveredToCustomer(Customer_ID, DeliveryPerson_ID, Order_ID, Delivery_Time)
VALUES
(2, 3, 2, NOW()),
(5, 9, 5, NOW() - INTERVAL '2 HOURS'),
(8, 6, 8, NOW() - INTERVAL '3 HOURS');

INSERT INTO DeliveryManReview (Order_ID, DeliveryPerson_ID, Review, Rating)
VALUES
(2, 3, 'Excellent service!', 4),
(5, 9, 'Very polite and punctual.', 5),
(8, 6, 'Could be more punctual.', 3);

INSERT INTO CustomerPasswords (Customer_ID, Password_) 
VALUES
(1, 'Rahul1'),
(2, 'Priya2'),
(3, 'Amit3'),
(4, 'Sneha4'),
(5, 'Anjali5'),
(6, 'Rajesh6'),
(7, 'Kavita7'),
(8, 'Manoj8'),
(9, 'Meena9'),
(10, 'Sanjay10') ; 