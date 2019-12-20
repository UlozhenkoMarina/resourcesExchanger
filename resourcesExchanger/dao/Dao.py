import psycopg2


def create(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS public.logins (id integer NOT NULL , username VARCHAR(20) NOT NULL, password integer NOT NULL,  PRIMARY KEY (id));")
    cur.execute("CREATE TABLE IF NOT EXISTS public.resources(id integer NOT NULL, title VARCHAR(20) NOT NULL, keywords VARCHAR(20) NOT NULL, location VARCHAR(20) NOT NULL, author_id integer, PRIMARY KEY (id), FOREIGN KEY (author_id) REFERENCES public.logins (id)  )")
    cur.close()
    conn.commit()


def addUser(conn,username,password):
    cur = conn.cursor()
    cur.execute("SELECT id FROM public.logins")
    i = cur.fetchone()
    if i :
        i = i[len(i)-1] + 1
    else:
        i = 0
    cur.execute("INSERT INTO public.logins VALUES("+str(i)+",\'"+username+"\',"+str(password)+")")
    cur.execute("SELECT * FROM public.logins")
    print(cur.fetchone())
    cur.close()
    conn.commit()


def getUsers(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.logins")
    row = cur.fetchone()
    #row = cur.fetchall
    s = {"admin" : 1}
    while row is not None:
        print(row[0])
        s[row[1]]=row[2]
        row = cur.fetchone()
    # for i in [cur.fetchone()]:
    #     #print(i[])
    #     s[i[1]] = i[2]
    #     #s = s + {i['username']: i['password']}
    #     #s.update(i['username'],i['password'])
    return s


def addResource(conn, title, keywords, author):
    cur = conn.cursor()
    print("add "+author)
    cur.execute("SELECT max(id) FROM public.resources")
    i = cur.fetchone()
    if i:
        i = i[len(i) - 1] + 1
    else:
        i = 0
    cur.execute("SELECT id FROM public.logins WHERE username = \'"+author+"\'")
    j = cur.fetchone()
    j=j[0]
    print(j)
    print(title)
    print(keywords)
    print(author)
    cur.execute("INSERT INTO public.resources VALUES ("+str(i)+",\'"+title+"\',\'"+str(keywords)+"\',\'location\',\' "+str(j)+"\')")
    cur.close()
    conn.commit()


def getResourcesTitles(conn, keywords):
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.resources")
    s = []
    row = cur.fetchone()
    for i in keywords:
        if row[2].find(i)!=-1:
            s.append(row[1])
    while row is not None:
        counter=0
        for i in keywords:
            if i in row[2]:
                counter+=1
        if counter > 0:
                s.append(row[1])
        row = cur.fetchone()
    return s

def isResourceInDb(conn, title):
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.resources WHERE title="+title)
    if cur.fetchone() is not None:
        return True
    else:
        return False

def isAuthorInDb(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.logins WHERE username="+username)
    if cur.fetchone() is not None:
        return True
    else:
        return False