CREATE TABLE IF NOT EXISTS salesperson (
	id serial PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	modified TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE
);