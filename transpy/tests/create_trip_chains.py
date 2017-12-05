
import pandas as pd
import networkx as nx

import itertools

def viable_tripchains(G, tripchains):
    
    def filter_edges_purpose(start_node, end_node, purpose):
        edges_data = G.get_edge_data(start_node, end_node)
        filt_edges = [v for k, v in edges_data.items() if v['Purpose'] == purpose]
        
        if filt_edges:
            od_pair = (start_node, end_node)
            return {od_pair: filt_edges}
        else:
            return None
        
    
    def filter_interm_edges(interm_edges):
        filt_interm_edges = []
        for u, v in pairwise(interm_edges):
            filt_edges = filter_edges_purpose(u, v, 'NHB')

            if filt_edges:
                filt_interm_edges.append(filt_edges)
            else:
                return None
        
        return filt_interm_edges

    # Filter edges 
    # Filter intrazonals
    
    viable_tripchains = []
    
    for tc in tripchains:
        # We filter the edges of the tripchain according to purpose
        edges = []
        if len(tc) > 1:
            
            first_edges = filter_edges_purpose(tc[0], tc[1], 'HB')
            last_edges = filter_edges_purpose(tc[-2], tc[-1], 'HB')
            
            # Check if first and last leg fulfil the criteria
            # If they don't function has returned NaN
            if first_edges and last_edges:
                edges.append(first_edges)
                edges.append(last_edges)
            else:
                continue
        
            if len(tc) > 2:
                # The rest can only be NHB trips
                interm_edges = tc[1:-1]
                
                filt_interm_edges = filter_interm_edges(interm_edges)    
                
                if filt_interm_edges:
                    for fie in filt_interm_edges:
                        edges.insert(1, fie)
                else:
                    continue
            
            viable_tripchains.append(edges)
    
    return viable_tripchains

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

"""
infilepath = r'/mnt/sda1/Users/Work/SharedSpace_linux/ODs_purpose_mode_timeperiod.csv'

odtemp = pd.read_csv(infilepath, nrows=10)

dtypes_keys = list(odtemp.columns)
dtypes_vals = ['category', 'category', 'category',
               'category', 'category', 'float']

dtypes = dict(zip(dtypes_keys, dtypes_vals))

od = pd.read_csv(infilepath, index_col=list(range(0, 5)))
#od.sort_index(inplace=True)

d_grp_purp = {'HBW': 'HB', 'HBO': 'HB', 'NHB': 'NHB'}
grp_keys = [None, None, d_grp_purp, None, None]

odg = od.groupby(grp_keys, level=od.index.names).sum()

odg.reset_index(inplace=True)
odg.Purpose = odg.Purpose.astype('category')


odg.set_index(['orig_zoneID', 'dest_zoneID', 'Purpose', 'Mode', 'TimePeriod'], inplace=True)

od_car = odg.xs('CarDriver', level='Mode')

od_car.reset_index(inplace=True)

# Reduce
od_car_reduced = od_car[od_car.Trips >= 50]
# Remove intrazonals
od_car_reduced = od_car_reduced[od_car_reduced.orig_zoneID != od_car_reduced.dest_zoneID]

od_car_reduced.to_csv('tmp.csv')
"""
od_car_reduced = pd.read_csv('tmp.csv')

G = nx.from_pandas_dataframe(od_car_reduced, 'orig_zoneID', 'dest_zoneID',
                             ['Purpose', 'TimePeriod'], nx.MultiDiGraph())

potential_tripchains = nx.trip_chains(G, 5)

vtc = viable_tripchains(G, potential_tripchains)