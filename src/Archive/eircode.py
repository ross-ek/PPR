import re
import pandas as pd
import json
# from fuzzywuzzy import fuzz, process
import fuzzymatcher


# a = 'BALLYMUN,DUBLIN'
# b = 'BALLYMUNNY,DUBLIN'

# print(fuzz.ratio(a,b))
# print(fuzz.partial_ratio(a,b))

with open('conf\\config.json') as f:
     config = json.load(f)


samples = [
            #['PORTLAOISE','LAOIS'],
            #['SHANKILL','DUBLIN 18'],
            #['STILLORGAN','DUBLIN'],
            ['ADAMSTON','DUBLIN'],
            #['TRALEE','KERRY'],
            #['MAYNOOTH','KILDARE'],
            #[' FINGLAS','DUBLIN'],
            #['','CARLOW']
        ]

df_addr = pd.DataFrame(samples,columns=['address','county'])
df_addr['search_string'] = df_addr['address'] + ',' + df_addr['county']

df = pd.read_csv(config['dir_input'] + 'ie-towns.csv')
df = df[['name', 'county', 'eircode']].drop_duplicates()
df['search_string'] = df['name'] + ',' +df['county']
df = df[['search_string','eircode']]

for i in df:
    df[i] = df[i].str.upper()


# fuzzy match way

#fuzzymatcher.fuzzy_left_join(df_left, df_right, left_on = "ons_name", right_on = "os_name")

df1 = fuzzymatcher.fuzzy_left_join(df_addr, df, left_on = "search_string", right_on = "search_string")
print(df1)













# subset way

# for index, row in df_addr.iterrows():
   
#     eircode = None
#     result_set = df[(df['county'] == row['county']) & (df['postal_town'] == row['address'])]

#     for z in result_set['eircode']:
#         eircode = str(z)

#     print( row['address'], eircode)



    
    





#------------------------------------------------------
#df.to_csv(config['dir_output'] + 'towns_unique.csv')
# counties = df['county'].drop_duplicates().tolist()









