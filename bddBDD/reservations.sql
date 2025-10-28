create table reservations(
	rsv_id text,
	user_id text,
	isbn text,
	rsv_date date,
	status text check (status in ('disponible', 'reserved')),
	primary key (rsv_id),
	foreign key (user_id) references users,
	foreign key (isbn) references books
	);
