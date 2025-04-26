from flask import Flask, request, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()

    if os.path.exists('stations_routes.db'):
        os.remove('stations_routes.db')

    conn = sqlite3.connect('stations_routes.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE stations (
            station_id INTEGER PRIMARY KEY,
            lat REAL,
            lng REAL
        )
    ''')

    c.execute('''
        CREATE TABLE routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            s_id1 INTEGER,
            s_id2 INTEGER,
            FOREIGN KEY (s_id1) REFERENCES stations(station_id),
            FOREIGN KEY (s_id2) REFERENCES stations(station_id)
        )
    ''')

    for station in data['stations']:
        c.execute('INSERT INTO stations (station_id, lat, lng) VALUES (?, ?, ?)',
                  (station['id'], station['lat'], station['lng']))

    for route in data['routes']:
        c.execute('INSERT INTO routes (s_id1, s_id2) VALUES (?, ?)',
                  (route['s_id1'], route['s_id2']))

    conn.commit()
    conn.close()

    return 'Saved!', 200

@app.route('/load', methods=['GET'])
def load():
    if not os.path.exists('stations_routes.db'):
        return jsonify({'stations': [], 'routes': []})

    conn = sqlite3.connect('stations_routes.db')
    c = conn.cursor()

    c.execute('SELECT station_id, lat, lng FROM stations')
    stations = [{'id': row[0], 'lat': row[1], 'lng': row[2]} for row in c.fetchall()]

    c.execute('SELECT s_id1, s_id2 FROM routes')
    routes = [{'s_id1': row[0], 's_id2': row[1]} for row in c.fetchall()]

    conn.close()

    return jsonify({'stations': stations, 'routes': routes})

if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask, request, render_template, send_file
# import sqlite3
# import os

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/load', methods=['GET'])
# def load():
#     if not os.path.exists('stations_routes.db'):
#         return {'stations': [], 'routes': []}

#     conn = sqlite3.connect('stations_routes.db')
#     c = conn.cursor()

#     c.execute('SELECT station_id, lat, lng FROM stations')
#     stations = [{'id': row[0], 'lat': row[1], 'lng': row[2]} for row in c.fetchall()]

#     c.execute('SELECT s_id1, s_id2 FROM routes')
#     routes = [{'s_id1': row[0], 's_id2': row[1]} for row in c.fetchall()]

#     conn.close()

#     return {'stations': stations, 'routes': routes}

# @app.route('/save', methods=['POST'])
# def save():
#     data = request.get_json()

#     if os.path.exists('stations_routes.db'):
#         os.remove('stations_routes.db')

#     conn = sqlite3.connect('stations_routes.db')
#     c = conn.cursor()

#     # Create tables
#     c.execute('''
#         CREATE TABLE stations (
#             station_id INTEGER PRIMARY KEY,
#             lat REAL,
#             lng REAL
#         )
#     ''')

#     c.execute('''
#         CREATE TABLE routes (
#             route_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             s_id1 INTEGER,
#             s_id2 INTEGER,
#             FOREIGN KEY (s_id1) REFERENCES stations(station_id),
#             FOREIGN KEY (s_id2) REFERENCES stations(station_id)
#         )
#     ''')

#     # Insert stations
#     for station in data['stations']:
#         c.execute('INSERT INTO stations (station_id, lat, lng) VALUES (?, ?, ?)',
#                   (station['id'], station['lat'], station['lng']))

#     # Insert routes
#     for route in data['routes']:
#         c.execute('INSERT INTO routes (s_id1, s_id2) VALUES (?, ?)',
#                   (route['s_id1'], route['s_id2']))

#     conn.commit()
#     conn.close()

#     return 'Saved!', 200

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, render_template, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# # Setup the SQLite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///connections.db'
# db = SQLAlchemy(app)

# # --- Database Models ---

# class Station(db.Model):
#     station_id = db.Column(db.Integer, primary_key=True)
#     lat = db.Column(db.Float, nullable=False)
#     lng = db.Column(db.Float, nullable=False)

# class Route(db.Model):
#     route_id = db.Column(db.Integer, primary_key=True)
#     station_from_id = db.Column(db.Integer, db.ForeignKey('station.station_id'), nullable=False)
#     station_to_id = db.Column(db.Integer, db.ForeignKey('station.station_id'), nullable=False)

# # --- Create Tables ---
# with app.app_context():
#     db.create_all()

# @app.route('/')
# def index():
#     return render_template('map.html')

# @app.route('/save', methods=['POST'])
# def save():
#     data = request.get_json()
#     print("Received data:", data)

#     # Clear existing data (optional)
#     Route.query.delete()
#     Station.query.delete()
#     db.session.commit()

#     # In-memory lookup to avoid inserting duplicate stations
#     station_lookup = {}
#     station_counter = 1

#     # First, go through all connections and add unique stations
#     for conn in data:
#         from_key = (conn['from']['lat'], conn['from']['lng'])
#         to_key = (conn['to']['lat'], conn['to']['lng'])

#         if from_key not in station_lookup:
#             station = Station(station_id=station_counter, lat=from_key[0], lng=from_key[1])
#             db.session.add(station)
#             station_lookup[from_key] = station_counter
#             station_counter += 1

#         if to_key not in station_lookup:
#             station = Station(station_id=station_counter, lat=to_key[0], lng=to_key[1])
#             db.session.add(station)
#             station_lookup[to_key] = station_counter
#             station_counter += 1

#     db.session.commit()

#     # Now create routes using the station IDs
#     for conn in data:
#         from_key = (conn['from']['lat'], conn['from']['lng'])
#         to_key = (conn['to']['lat'], conn['to']['lng'])

#         route = Route(
#             station_from_id=station_lookup[from_key],
#             station_to_id=station_lookup[to_key]
#         )
#         db.session.add(route)

#     db.session.commit()

#     return jsonify({"status": "success"})

# @app.route('/connections', methods=['GET'])
# def get_connections():
#     # Fetch routes and reconstruct connections
#     routes = Route.query.all()
#     connections = []

#     for route in routes:
#         from_station = Station.query.get(route.station_from_id)
#         to_station = Station.query.get(route.station_to_id)

#         connections.append({
#             "from": {"lat": from_station.lat, "lng": from_station.lng},
#             "to": {"lat": to_station.lat, "lng": to_station.lng}
#         })

#     return jsonify(connections)

# if __name__ == '__main__':
#     app.run(debug=True)