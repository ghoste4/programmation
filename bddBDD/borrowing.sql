create table borrowing(
	brw_id text,
	user_id text,
	isbn text, 
	brw_date date,
	return_date date,
	primary key (brw_id),
	foreign key(user_id) references users,
	foreign key(isbn) references books
	);
