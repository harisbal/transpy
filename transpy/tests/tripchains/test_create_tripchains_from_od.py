import pandas as pd
import transpy as tpy

#infilepath_od = r'od_purpose_mode_timeperiod_noExtToExt.csv'

print('Reading...')
odtemp = pd.read_csv(infilepath_od, nrows=10)

dtypes_keys = list(odtemp.columns)
dtypes_vals = ['category', 'category', 'category',
               'category', 'category', 'float']

dtypes = dict(zip(dtypes_keys, dtypes_vals))

od = pd.read_csv(infilepath_od, index_col=list(range(0, 5)))
# od.sort_index(inplace=True)

d_grp_purp = {'HBW': 'HB', 'HBO': 'HB', 'NHB': 'NHB'}
grp_keys = [None, None, d_grp_purp, None, None]

odg = od.groupby(grp_keys, level=od.index.names).sum()

odg.reset_index(inplace=True)
odg.Purpose = odg.Purpose.astype('category')

odg.set_index(['OrigID', 'DestID', 'Purpose', 'Mode', 'TimePeriod'], inplace=True)

od_car = odg.xs('CarDriver', level='Mode')
od_car.reset_index(inplace=True)

# Reduce
od_car_reduced = od_car[od_car.Trips >= trips_threshold]
# Remove intrazonals
od_car_reduced = od_car_reduced[od_car_reduced.OrigID != od_car_reduced.DestID]
# Round
od_car_reduced = od_car_reduced.round()

# Export OD
od_car_reduced.to_csv('tripchains_od.csv')

# Encode the df