
import pandas as pd
import itertools
import collections
import networkx as nx

import itertools


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def is_ascending(lst):
    for i in range(len(lst) - 1):
        if lst[i]>lst[i+1]:
            return False

    return True

def purpose_viable_tripchains(G, tripchain_nodes):

    def filter_edges_purpose(start_node, end_node, purpose):
        edges_data = G.get_edge_data(start_node, end_node)
        filt_edges = [v for k, v in edges_data.items() if v['Purpose'] == purpose]
        
        if filt_edges:
            od_pair = (start_node, end_node)
            return od_pair, filt_edges
        else:
            return None
    
    def filter_interm_edges(interm_edges):
        filt_interm_edges = collections.OrderedDict()
        for u, v in pairwise(interm_edges):
            od, filt_edges = filter_edges_purpose(u, v, 'NHB')

            if filt_edges:
                filt_interm_edges[od] = filt_edges
            else:
                return None
        
        return filt_interm_edges

    viable_tripchains = []
    
    for tcn in tripchain_nodes:
        # We filter the edges of the tripchain according to purpose
        edges = collections.OrderedDict()
        # Filter intrazonals
        if len(tcn) > 1:
            # The tripchain does not include the last leg back to origin
            # Append the last node which is the same as the first
            tcn.append(tcn[0])

            first_od, first_edges = filter_edges_purpose(tcn[0], tcn[1], 'HB')
            last_od, last_edges = filter_edges_purpose(tcn[-2], tcn[-1], 'HB')
            
            # Check if first and last leg fulfil the criteria
            # If they don't function has returned NaN
            if first_edges and last_edges:
                edges[first_od] = first_edges
                edges[last_od] = last_edges
            else:
                continue
        
            if len(tcn) - 1 > 2: # -1 because we manually added the last node of the chain
                # The rest can only be NHB trips
                interm_edges = tcn[1:-1]
                
                filt_interm_edges = filter_interm_edges(interm_edges)
                
                if filt_interm_edges:
                    for k, fie in filt_interm_edges.items():
                        edges[k] = fie
                else:
                    continue

            # The last_od key must be moved to the end
            edges.move_to_end(last_od)

            viable_tripchains.append(edges)
    
    return viable_tripchains


def chronologically_viable_tripchains(tripchains, timeperiod_sequence):

    def sequence_isunique(sequence):
        # Check if entries in sequence unique
        set_sequence = set(sequence)
        if len(set_sequence) == len(sequence):
            return True
        else:
            return False

    if sequence_isunique(timeperiod_sequence):
        pass
    else:
        raise TypeError('timeperiod_sequence is not unique')

    chron_ordered_tripchains = []

    for tc in tripchains:
        leg_timeperiods = {} # dictionary with the available timeperiods for each leg (key=od pair)
        # for each od I create a list of the available timeperiods
        for od, edge_attrs in tc.items():
            leg_timeperiods[od] = []
            for attrs in edge_attrs:
                leg_timeperiod = attrs['TimePeriod']
                # Convert to number from the given sequence
                leg_timeperiod = timeperiod_sequence.index(leg_timeperiod)
                leg_timeperiods[od].append(leg_timeperiod)

        # Here I will create a list with the available timeperiods for each od in the tripchain
        tripchain_leg_timeperiods = [] # e.g. [ [AM, IP, OP], [IP, PM], [PM, OP] ]
        for od, timeperiods in leg_timeperiods.items():
            tripchain_leg_timeperiods.append(timeperiods)

        tripchain_timeperiod_combinations = list(itertools.product(*tripchain_leg_timeperiods))

        for timeperiod_comb in tripchain_timeperiod_combinations:
            # Store the legs of the chronologically ordered tripchains
            legs = {}
            if is_ascending(timeperiod_comb):
                for tp_comb_idx, timeperiod_idx in enumerate(timeperiod_comb):
                    od, edge_attrs = next(itertools.islice(tc.items(), tp_comb_idx, None))
                    # Find the edges that corresponds to the identified timeperiod
                    for attrs in edge_attrs:
                        tp = attrs['TimePeriod']
                        tp_idx = timeperiod_sequence.index(tp)
                        if tp_idx == timeperiod_idx:
                            legs[od] = attrs
                            break

            if legs:
                chron_ordered_tripchains.append(legs)

    return chron_ordered_tripchains

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
print('Reading...')
od_car_reduced = pd.read_csv('tmp.csv')

G = nx.from_pandas_dataframe(od_car_reduced, 'orig_zoneID', 'dest_zoneID',
                             ['Purpose', 'TimePeriod'], nx.MultiDiGraph())

print('Creating Chains...')
potential_tripchains = nx.trip_chains(G, 5)

vtc = purpose_viable_tripchains(G, potential_tripchains)
vtc2 = chronologically_viable_tripchains(vtc, ['AM', 'IP', 'PM', 'OP'])