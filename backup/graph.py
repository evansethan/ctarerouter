import sqlite3
import networkx as nx
from haversine import haversine

# Connect to your .db file
conn = sqlite3.connect('stations_routes.db')
cursor = conn.cursor()

# Load stations into a dictionary
cursor.execute("SELECT station_id, lat, lng FROM stations")
stations = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

# Create a graph
G = nx.Graph()

# Load routes and add edges
cursor.execute("SELECT route_id, s_id1, s_id2 FROM routes")
for route_id, s_id1, s_id2 in cursor.fetchall():
    if s_id1 in stations and s_id2 in stations:
        coord1 = stations[s_id1]
        coord2 = stations[s_id2]
        distance = haversine(coord1, coord2)  # Distance in kilometers
        G.add_edge(s_id1, s_id2, weight=distance, route_id=route_id)

conn.close()

# Now G is your graph!
print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")