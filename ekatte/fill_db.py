import psycopg2
import csv
import sys
from config import config

def fill_table(ekatte_dir, table_name):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        with open(ekatte_dir + "/Ek_obl.csv") as regions:
            reg_reader = csv.DictReader(regions, delimiter=',')
            for row in reg_reader:
                cur.execute("""INSERT INTO Regions(name, code) VALUES(%s, %s)
                        ON CONFLICT ON CONSTRAINT regions_code_key
                        DO NOTHING;""", (row['name'], row['oblast']))

            with open(ekatte_dir + "/Ek_obst.csv") as minicapilities:
                min_reader = csv.DictReader(minicapilities, delimiter=',')
                for row in min_reader:
                    regions.seek(0)
                    for reg in reg_reader:
                        if row['obstina'][0:3] == reg['oblast']:
                            cur.execute("SELECT id FROM Regions WHERE code = '%s';" % reg['oblast'])
                            id = cur.fetchone()[0]
                            
                            cur.execute("""INSERT INTO Minicapilities(name, code, regionId) VALUES(%s, %s, %s)
                                ON CONFLICT ON CONSTRAINT uc_minicapilities
                                DO NOTHING;""", (row['name'], row['obstina'], id))

                with open(ekatte_dir + "/Ek_atte.csv") as villages:
                    vil_reader = csv.DictReader(villages, delimiter=',')
                    for row in vil_reader:
                        minicapilities.seek(0)
                        for m in min_reader:
                            if row['obstina'] == m['obstina']:
                                cur.execute("SELECT id FROM Minicapilities WHERE code = '%s';" % m['obstina'])
                                id = cur.fetchone()[0]
                                
                                cur.execute("""INSERT INTO Villages(ekatte, t_v_m, name, minicapilityId) VALUES(%s, %s, %s, %s)
                                    ON CONFLICT ON CONSTRAINT villages_name_minicapilityId_key
                                    DO NOTHING;""", (row['ekatte'], row['t_v_m'], row['name'], id))


        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    fill_table(sys.argv[1], sys.argv[2])