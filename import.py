import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    "postgres://dglqnypjhfbhjp:1c95406fa7528f7651e4c01a2628984ab039c3d81ce318580dbf7327e9317ddc@ec2-75-101-128-10.compute-1.amazonaws.com:5432/d10fqudidns4ap")
db = scoped_session(sessionmaker(bind=engine))

# Open book.csv file and import into DB
f = open("books.csv")
reader = csv.reader(f)
counter = 0
next(reader)
for isbn, title, author, year in reader:
    intyear = int(year)
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title, "author": author, "year": intyear})
    counter += 1
    print(f"Added book {title} to database. {counter} out of 5000.")
db.commit()