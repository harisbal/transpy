
import pandas as pd
import networkx as nx

from itertools import tee


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

# First check if intermediate legs contain NHB trips
def nhb_in_interm_legs(G, node_chain):
    if len(node_chain) > 2:
        mid_node_chain = node_chain[1:-1]

        for a, b in pairwise(mid_node_chain):
            edges = G.get_edge_data(a, b)

            contains_nhb = False
            for k, edge in edges.items():
                if edge['Purpose'] == 'NHB':
                    contains_nhb = True
                    break

            if not contains_nhb:
                return False

        return True

def main():
    infilepath = r'/mnt/sda1/Users/Work/Transport Systems Catapult/MERGE - Documents/Models/MATSim/MATSim/Synthetic Pop/Building/inputs/ODs_purpose_mode_timeperiod.csv'
    #odtemp = pd.read_csv(infilepath, nrows=10)

    """
    dtypes_keys = list(odtemp.columns)
    dtypes_vals = ['category', 'category', 'category',
                   'category', 'category', 'float']

    dtypes = dict(zip(dtypes_keys, dtypes_vals))
    """

    od = pd.read_csv(infilepath, index_col=list(range(0, 5)))

    d_grp_purp = {'HBW': 'HB', 'HBO': 'HB', 'NHB': 'NHB'}
    grp_keys = [None, None, d_grp_purp, None, None]

    odg = od.groupby(grp_keys, level=od.index.names).sum()
    odg.reset_index(inplace=True)
    odg.Purpose = odg.Purpose.astype('category')

    od_car = odg.xs('CarDriver', level='Mode')
    od_car.reset_index(inplace=True)

    # Remove ODs with few trips
    trips_limit = 20
    od_car_red = od_car[od_car.Trips >= trips_limit]

    # Create the Network
    G = nx.from_pandas_dataframe(od_car_red, 'orig_zoneID', 'dest_zoneID',
                                 ['Purpose', 'TimePeriod'], nx.MultiDiGraph())

    potential_cycles = nx.simple_cycles(G, 5)

    # TEMP
    from itertools import takewhile
    l = takewhile(lambda x: x < 10, potential_cycles())


    #node_chain = next(potential_cycles)


if __name__ == '__main__':
    main()
