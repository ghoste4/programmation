create table rate(
	user_id text,
	isbn text, 
	rate numeric(2,0),
	primary key (user_id,isbn),
	foreign key (user_id) references users(user_id),
	foreign key (isbn) references books(isbn)
	);
