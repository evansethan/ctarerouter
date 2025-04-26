from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import webbrowser
import threading
from station import call_function

app = Flask(__name__)

DB_FILE = 'stations_routes.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE stations (station_id INTEGER PRIMARY KEY, lat REAL, lng REAL)')
    c.execute('CREATE TABLE routes (route_id INTEGER PRIMARY KEY AUTOINCREMENT, s_id1 INTEGER, s_id2 INTEGER)')
    
    for s in data['stations']:
        c.execute('INSERT INTO stations (station_id, lat, lng) VALUES (?, ?, ?)', (s['id'], s['lat'], s['lng']))
    for r in data['routes']:
        c.execute('INSERT INTO routes (s_id1, s_id2) VALUES (?, ?)', (r['s_id1'], r['s_id2']))
    
    conn.commit()
    conn.close()
    num = call_function()
    return jsonify({'message': 'Saved!', 'number': num})

@app.route('/load', methods=['GET'])
def load():
    if not os.path.exists(DB_FILE):
        return jsonify({'stations': [], 'routes': []})

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT station_id, lat, lng FROM stations')
    stations = [{'id': sid, 'lat': lat, 'lng': lng} for sid, lat, lng in c.fetchall()]
    c.execute('SELECT s_id1, s_id2 FROM routes')
    routes = [{'s_id1': s1, 's_id2': s2} for s1, s2 in c.fetchall()]
    conn.close()
    return jsonify({'stations': stations, 'routes': routes})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run()