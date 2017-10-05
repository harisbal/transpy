"""
Functions to cailitate the import of common transport related datasets

Author: Haris Ballis harisballis@gmail.com
02/10/2017
"""
import os
import pandas as pd

def get_nts(nts_tables, infolder_data, infilepath_metadata=None):
    """
    Parameters
    ----------
    infolder_data : str
         The folder where NTS (.tab) files are located
    nts_tables : list(str)
         The NTS available tables
         nts_tables : {trip, individual, day, etc.. }
    infilepath_metadata : str
         filepath of the relevant lookup table
    
    Returns
    nts : dict
        Dictionary with tables specified in nts_tables
    """
    
    def create_lookups(lookup_data):
        lookups = {}
        for i, name in enumerate(lookup_data.sheet_names):
            
            df = lookup_data.parse(i)
            df.fillna(method='ffill', inplace=True)
            lname = name.replace('LUT', '').strip()
            
            # Create a table with the Variable name descriptions and
            # a table with the value descriptions
            lookups[lname] = {}
            
            var = df.drop(['Value', 'Values Description'], axis=1)
            var.drop_duplicates(inplace=True)
            var.set_index(var.columns[0], inplace=True)
            
            lookups[lname]['Variables'] = var.squeeze()
            
            val = df.drop('Description', axis=1)
            val.drop_duplicates(inplace=True)
            val.set_index(list(val.columns[0:2]), inplace=True)
            
            lookups[lname]['Values'] = val.squeeze()
        
        return lookups
    
    def create_categorical_columns(df, categs, replace_vals=False):
        names = categs.index.get_level_values(0)
        for c in df.columns:
            if c in names:
                if replace_vals:
                    new_vals = categs.xs(c, level=0).to_dict()
                    df[c].replace(new_vals, inplace=True)
                df[c] = df[c].astype('category')
        return df
    
    def read_nts(infolder_data):
        # Dictionary to store the relevant data
        nts = {}
        
        for intbl in nts_tables:
            infilepath = os.path.join(infolder_data, 'tab',
                                      '{}eul2015.tab'.format(intbl.lower()))
            df = pd.read_csv(infilepath, sep='\t', na_values=[' '])
            df.set_index('{}ID'.format(intbl.title()), inplace=True)
            # if a column is categorical has been already imported from the xls file
            if infilepath_metadata:
                categ_vars = lookups[intbl]['Values']
                df = create_categorical_columns(df, categ_vars,
                                                replace_vals=True)
            
            nts[intbl] = df
        
        return nts
    

    if infilepath_metadata:
        lookup_data = pd.ExcelFile(infilepath_metadata)
        lookups = create_lookups(lookup_data)    
    
    nts = read_nts(infolder_data)
    
    return nts