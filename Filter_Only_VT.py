import psycopg2.extras

# Try to connect to the local PostGresSQL database in which we will store our flight trajectories coupled with FPL data.
from autoprocess_simtoolkit import db_name, airac,schema_name

conn_postgres = psycopg2.connect(
    user='postgres', password='password',
    host='127.0.0.1', port='5432',
    database=db_name,
    options="-c search_path=dbo," + schema_name
)
with conn_postgres:
    cursor_postgres = conn_postgres.cursor(cursor_factory=psycopg2.extras.DictCursor)

    postgres_sql_text = f" CREATE SCHEMA IF NOT EXISTS {schema_name}_vt; " \
                        " SELECT tablename FROM pg_tables " \
                        f" WHERE schemaname = '{schema_name}' " \
                        " AND NOT(tablename like 'sbas%');"

    print(postgres_sql_text)
    cursor_postgres.execute(postgres_sql_text)
    table_name_list = cursor_postgres.fetchall()
    for table_name in table_name_list:
        print(table_name[0])
        postgres_sql_text = f" SELECT * " \
                            f" INTO {schema_name}_vt.{table_name[0]}" \
                            f" FROM {schema_name}.{table_name[0]}" \
                            f" WHERE public.ST_Intersects(geom," \
                            f" (SELECT public.ST_Buffer(geom,10) " \
                            f" FROM airspace.fir " \
                            f" WHERE name like 'BANGKOK%'));" # \
                            # f" DROP TABLE {schema_name}_vt.{table_name[0]};" \
                            # f" ALTER TABLE {schema_name}_vt.{table_name[0]}_vt RENAME TO {table_name[0]};"
        print(postgres_sql_text)
        cursor_postgres.execute(postgres_sql_text)
        conn_postgres.commit()
