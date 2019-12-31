#imports sqlite
import sqlite3

#connects it to the books-collection database
conn = sqlite3.connect('game-records.db')

#creates the cursor
c = conn.cursor()

#execute the query which creates the table called books with id and name
#as the columns
# c.execute('''
#           DROP TABLE book;''')

c.execute('''
          CREATE TABLE game
          (id INTEGER PRIMARY KEY ASC,
	      board varchar(400) NOT NULL,
          answers varchar(1000) NOT NULL,
          solved varchar(100) DEFAULT "[0,9]",
          active varchar(100) DEFAULT "[1,8]",
          letters_active INTEGER DEFAULT 0,
          letters_other INTEGER DEFAULT 0,
          choice INTEGER DEFAULT 0,
          turn INTEGER DEFAULT 1,
          finished INTEGER DEFAULT 0);
          ''')

#executes the query which inserts values in the table
c.execute("INSERT INTO game VALUES(1, '[dinner, time, machine, learning, experience, required, reading, material, world, peace]', '', '[0, 9]', '[1, 8]', 0, 0, 0, 1, 0)")

#commits the executions
conn.commit()

#closes the connection
conn.close()