create table Medicine(
idx int primary key auto_increment,   #index
product varchar(100), 	#제품명
ingredient varchar(3000),  #함유량
heavy_intake varchar(3000) #중금속 함유량
);

create table Word (
id INT primary key NOT NULL AUTO_INCREMENT,
name VARCHAR(300) NULL,
upper_bound float
);