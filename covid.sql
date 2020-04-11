create database covid;
use covid;

create table users(
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    first_name varchar(255) NOT NULL,
    last_name varchar(255) NOT NULL,
    email varchar(255) NOT NULL unique,
    pass varchar(255) NOT NULL
);

show tables;

ALTER TABLE users
ADD usertype int NOT NULL
DEFAULT 2;

create table usertypes(
	type_id int PRIMARY KEY NOT NULL,
    type_name varchar(25) NOT NULL
);

INSERT INTO userTypes (type_id, type_name) VALUES (1, "Admin");
INSERT INTO userTypes (type_id, type_name) VALUES (2, "Customer");

INSERT INTO users (first_name, last_name, email, pass, usertype)
VALUES ("adminFirst","adminLast","admin@gmail.com","admin", 1);

create table orgs(
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL unique,
    pass varchar(255) NOT NULL
);

UPDATE users
SET usertype = 1
WHERE id = 1;

SELECT * FROM usertypes;
SELECT * FROM users;