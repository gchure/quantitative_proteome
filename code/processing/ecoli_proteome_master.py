"""
This script generates a master list of all genes in ecoli with their associated 
GO terms and gene products.
"""
#%%
import numpy  as np
import pandas as pd 
import tqdm
import glob
#%%
# Load the raw ecocyc master list. 
ecocyc = pd.read_csv('../../data/ecocyc_raw_data/2020-03-04_ecocyc_master.tab',
                    delimiter='\t')

#%%
# Iterate through each gene name and, for each synonym, create a new entry. 
dfs = []
i = 0
for g, d in tqdm.tqdm(ecocyc.groupby(['gene_name'])):
    # Stitch together the go ids. 
    go_ids = d['go_terms'].values[0]
    if str(go_ids) != 'nan':
        go_ids = '; '.join([s.strip() for s in go_ids.split('//')])
    else:
        go_ids = 'no ontology'
    mw = d['mw_kda'].unique()[0]
    if '//' in str(mw):
        mw = float(mw.split('//')[0])
    else:
        mw = float(mw)
    # Generate the base dict. 
    base_dict = {'gene_name':g.lower(),
                'b_number':d['b_number'].unique(), 
                'gene_product':d['gene_product'].unique(),
                'mw_fg': mw * 1.660E-6,
                'go_terms':go_ids}

    # Update the dataframe
    dfs.append(pd.DataFrame(base_dict, index=[0]))

    # Iterate through each synonym
    syn = d['synonyms'].values[0]
    if str(syn) != 'nan':
        syn_split = syn.split('//')
        syns = [s.strip().replace('"', '').lower() for s in syn_split]
        for s in syns:
            base_dict['gene_name'] = s
            dfs.append(pd.DataFrame(base_dict, index=[0]))

df = pd.concat(dfs, sort=False)
print(i, len(ecocyc))
#%%
# Drop duplicate rows
df.drop_duplicates(inplace=True)


# %%
# Load all of the cog lists and collate
cogs = pd.concat([pd.read_csv(f) for f in glob.glob('../../data/cog_data/*.csv')])
cogs.drop(columns=['Unnamed: 4'], axis=1, inplace=True)

# Assign the cog information to the ecocyc df based on the b number
for g, d in df.groupby('b_number'):
    cog = cogs[cogs['b_number']==g]
    if len(cog) == 0:
        df.loc[df['b_number']==g, 'cog_class'] = 'Not Assigned'
        df.loc[df['b_number']==g, 'cog_letter'] = 'Not Assigned'
        df.loc[df['b_number']==g, 'cog_category'] = 'Not Assigned'
        df.loc[df['b_number']==g, 'cog_desc'] = 'Not Assigned'
    else:
        df.loc[df['b_number']==g, 'cog_class'] = cog['cog_class'].values[0]
        df.loc[df['b_number']==g, 'cog_letter'] = cog['cog_letter'].values[0]
        df.loc[df['b_number']==g, 'cog_category'] = cog['cog_category'].values[0]
        df.loc[df['b_number']==g, 'cog_desc'] = cog['cog_desc'].values[0]

# %%
df.to_csv('../../data/ecoli_genelist_master.csv', index=False)

# %%
