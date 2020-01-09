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

# c.execute('''
#           CREATE TABLE game
#           (id INTEGER PRIMARY KEY ASC,
# 	      board varchar(400) NOT NULL,
#           answers varchar(1000) NOT NULL,
#           solved varchar(100) DEFAULT "[0,9]",
#           active varchar(100) DEFAULT "[1,8]",
#           preview_top INTEGER DEFAULT 0,
#           preview_bottom INTEGER DEFAULT 0,
#           choice INTEGER DEFAULT 0,
#           turn INTEGER DEFAULT 1,
#           finished INTEGER DEFAULT 0,
#           score1 INTEGER DEFAULT 0, 
#           score2 INTEGER DEFAULT 0);
#           ''')
# c.execute('''
#           CREATE TABLE turn (
#           id INTEGER PRIMARY KEY ASC,
#           game_id INTEGER NOT NULL,
#           player INTEGER DEFAULT 0,
#           start_score INTEGER DEFAULT 0,
#           active VARCHAR(20) DEFAULT "[1,8]",
#           choice INTEGER DEFAULT 0,
#           word VARCHAR(30), DEFAULT " ",
#           preview INTEGER DEFAULT 1,
#           num_guess INTEGER DEFAULT 0,
#           clue_above VARCHAR(30) DEFAULT " ",
#           clue_below VARCHAR(30) DEFAULT " ",
#           turn_count INTEGER DEFAULT 1,
#           answer VARCHAR(30), DEFAULT " ",
#           correct INTEGER DEFAULT 0,
#           points INTEGER DEFAULT 0,
#           FOREIGN KEY(game_id) REFERENCES game(id));
#           ''')

#executes the query which inserts values in the table
c.execute("INSERT INTO game VALUES( 1, '[dinner, time, machine, learning, experience, required, reading, material, world, peace]', '', '[0, 9]', '[1, 8]', 0, 0, 0, 1, 0, 0, 0)")
c.execute("INSERT INTO turn VALUES( 1, 1, 1, 1, '[0,0]', 0, '', 1, 0, '', '', 1, '', 0, 0 )")
#commits the executions
conn.commit()

#closes the connection
conn.close()