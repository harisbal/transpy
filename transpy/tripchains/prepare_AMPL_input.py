import pandas as pd
import tqdm

def insert_legID(df):
    df['LegID'] = (df.OrigID.map(str) + '_' +
                   df.DestID.map(str) + '_' +
                   df.Purpose.map(str) + '_' +
                   df.TimePeriod.map(str))
    return df

def encode_df(df):
    # Replace names with codes to save space
    for c in df.columns[:-1]:
        df[c] = df[c].astype('category')
        df[c] = df[c].cat.codes
    return df

max_legs = 5

infile_tripchains = r'tripchains_{}legs.csv'.format(max_legs)
infile_od = r'tripchains_od.csv'

#tripchains
tcs = pd.read_csv(infile_tripchains)
od = pd.read_csv(infile_od)

tripchain_ids = tcs.TripChainID.unique().tolist()
od.Trips = od.Trips.astype(int)

od = encode_df(od)
tcs = encode_df(tcs)

# Add the concatenated description of the od/tripchain
od = insert_legID(od)
tcs = insert_legID(tcs)

outfilepath_data = 'data_{}legs_encoded.dat'.format(max_legs)
 
with open(outfilepath_data, 'w') as f:
    print(r'data;', file=f)

    # LINKS part
    print('Preparing LEGS...')
    print('param: LEGS: trips:=', file=f)
    for od_pair in od.itertuples():
        outline = od_pair.LegID + ' ' + str(od_pair.Trips)

        print(outline, file=f)

    print(';', file=f)

    # CHAIN_IDS part
    print('Preparing CHAIN_IDS...')
    print(r'set CHAIN_IDS :=', file=f)
    print(*tripchain_ids, file=f, sep=' ', end=';\n')

    print('Preparing CHAINS...')
    # CHAINS part
    # group for each tripchain_ID
    print('set CHAINS :=', file=f)

    tcsg = tcs.groupby('TripChainID
    for tc, g in tqdm.tqdm(tcsg):
        # List with all the legs included in the tripchain
        legs = []
        for leg in g.itertuples():
            legs.append(leg.LegID)

        print('({},*) '.format(tc),file=f, end='')
        print(*legs, file=f, sep=' ')

    # Add the missing ; at the end
    # Check if works
    print(';', file=f)

print('END')
