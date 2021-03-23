init_db_sql="""create table pass(
id INTEGER  ,
site varchar(128),
username varchar(128),
password varchar(128),
PRIMARY KEY("id" AUTOINCREMENT),
unique ("site", "username")
);"""