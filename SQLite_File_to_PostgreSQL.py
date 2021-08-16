import psycopg2, sqlite3, sys, re

path = '/Users/pongabha/Dropbox/Workspace/AEROTHAI Data Analytics/NavData/simtoolkitpro_native_2108/'

sqdb = path + 'navdata.s3db'
sqlike = '%'
pgdb = 'airac_2021_08_simtoolkit'
pguser = 'postgres'
pgpswd = 'password'
pghost = 'localhost'
pgport = '5432'
pgschema = ''

consq = sqlite3.connect(sqdb)
cursq = consq.cursor()

tabnames = []

cursq.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%s'" % sqlike)
tabgrab = cursq.fetchall()
#print(tabgrab)

for item in tabgrab:
    tabnames.append(item[0])
#print(tabnames)

for table in tabnames:
    cursq.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name = ?;", (table,))
    create = cursq.fetchone()[0]
    create = create.replace("[", "")
    create = create.replace("]", "")
    create = create.replace("double", "double precision")
    create = create.replace("DOUBLE", "double precision")


    create = re.sub(r"""\bTEXT\b""", "VARCHAR", create)
    create = re.sub(r"""(\(\d+\))""", "", create)

    cursq.execute("SELECT * FROM %s;" % table)
    rows = cursq.fetchall()
    colcount = len(rows[0])
    pholder = '%s,' * colcount
    newholder = pholder[:-1]

    try:

        conpg = psycopg2.connect(database=pgdb, user=pguser, password=pgpswd,
                                 host=pghost, port=pgport)
        curpg = conpg.cursor()
        #curpg.execute("SET search_path TO %s;" % pgschema)
        curpg.execute("DROP TABLE IF EXISTS %s;" % table)
        #print(create)

        curpg.execute(create)
        curpg.executemany("INSERT INTO %s VALUES (%s);" % (table, newholder), rows)
        conpg.commit()
        print('Created', table)

    except psycopg2.DatabaseError as e:
        print('Error %s' % e)
        sys.exit(1)

    finally:

        if conpg:
            conpg.close()

consq.close()
