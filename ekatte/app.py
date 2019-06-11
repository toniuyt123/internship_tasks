 # -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import psycopg2, psycopg2.extras
from config import config
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search', methods = ['POST'])
def search():
    data = []
    query = request.get_json()['query']
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        conn.set_client_encoding('UTF-8')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(""" SELECT v.ekatte, v.t_v_m, v.name, m.name, m.code, r.name, r.code FROM Villages v
                        LEFT JOIN Minicapilities m ON m.id = v.minicapilityId
                        LEFT JOIN Regions r ON r.id = m.regionId 
                        WHERE v.name LIKE %s;""", ('%'+query+'%',))
        columns = (
            'ekatte', 't_v_m', 'name', 'm_name', 'm_code', 'r_name', 'r_code'
        )
        for row in cur:
            data.append(dict(zip(columns, row)))
        json_result = json.dumps(data, indent=2)
        json_result = json_result.encode('utf-8').decode('unicode_escape')
        json_result = str.replace(json_result,'\n','')
        cur.close()
        conn.commit()

        return json_result
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    app.run()