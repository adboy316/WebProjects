  CREATE TABLE users (
      username VARCHAR NOT NULL PRIMARY KEY UNIQUE,
      firstname VARCHAR NOT NULL,
      lastname VARCHAR NOT NULL,
      password VARCHAR NOT NULL,
      favbook VARCHAR NOT NULL
  );

   CREATE TABLE books (
      isbn VARCHAR NOT NULL PRIMARY KEY UNIQUE,
      title VARCHAR NOT NULL,
      author VARCHAR NOT NULL,
      year INTEGER NOT NULL
  );

    CREATE TABLE reviews (
      id SERIAL PRIMARY KEY,
      review VARCHAR NOT NULL,
      rating INTEGER NOT NULL,
      username VARCHAR REFERENCES users(username),
      isbn VARCHAR REFERENCES books(isbn)
  );


