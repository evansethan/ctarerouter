import networkx as nx
import geopandas as gpd
import numpy as np
import duckdb
import pathlib
from geopy.distance import geodesic



#locations_db = pathlib.Path(__file__).parent.parent/"instance"/"locations.db"
stations_routes_db = "stations_routes.db"


def call_function(): # call use this function to get the median time
    G = generate_graph()
    calculate_distance(G)
    m_distance = median_distance(G)

    dist = round(m_distance, 2)
    
    return f"median shortest path (km): {dist}"

    
def generate_graph(): # call this function to generate the graph that has all stations
    
    stations_gdf,routes_gdf = read_db_input()
    G = graph_add_node(stations_gdf)
    graph_add_edge(G,routes_gdf)

    return G


def read_db_input():

    #con_1 = duckdb.connect(locations_db)
    con_2 = duckdb.connect(stations_routes_db)

    #stations_gdf = gpd.GeoDataFrame(con.execute("SELECT * FROM stations").df())
    stations_gdf = gpd.GeoDataFrame(con_2.execute("SELECT * FROM stations;").df())
    routes_gdf = gpd.GeoDataFrame(con_2.execute("SELECT * FROM routes;").df())
    print(routes_gdf)

    return stations_gdf, routes_gdf


def graph_add_node(stations_gdf):
    G = nx.Graph()

    for index, row in stations_gdf.iterrows():
        station_name, station_lat, station_lng = row["station_id"], row["lat"],row["lng"]
        G.add_node(station_name,lat = station_lat, lng = station_lng)

    return G

def graph_add_edge(G, routes_gdf):
    for index, row in routes_gdf.iterrows():
        G.add_edge(row["s_id1"], row["s_id2"])

def calculate_distance(G):
    for u,v in G.edges():
        coords_u = (G.nodes[u]['lat'], G.nodes[u]['lng'])
        coords_v = (G.nodes[v]['lat'], G.nodes[v]['lng'])
        G[u][v]['distance'] = geodesic(coords_u, coords_v).km
        G[u][v]['distance_unit'] = 'km'

def median_distance(G):
    distances = []
    all_pairs_distances = nx.floyd_warshall(G, weight="distance")
    for source_node, target_paths in all_pairs_distances.items():
        #print(source_node, target_paths )
        for target_node, distance in target_paths.items():
            if (source_node != target_node) and (distance != float("inf")):  # Skip self-distances
                distances.append(float(distance))
    median_distance = np.median(distances)
    
    return median_distance

if __name__ == '__main__':
    print(call_function())
    
        