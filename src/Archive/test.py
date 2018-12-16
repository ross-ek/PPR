import re
import pandas as pd
import json

with open('conf\\config.json') as f:
     config = json.load(f)

samples = [
            #['LAOIS','ASHEWOOD WK,SUMMERHILL LN,PORTLAOISE'],
            #['DUBLIN 18','ATHGOE DV,SHANKILL'],
            #['DUBLIN','ALLEN PK RD,STILLORGAN'],
            #['CORK','BALLINVARRIG,YOUGHAL'],
            ['KERRY','CURRAGRAIGUE,BLENNERVILLE,TRALEE'],
            #['KILDARE','THE GR MOYGLARE HALL,MOYGLARE RD,MAYNOOTH'],
            #['DUBLIN','UNIT HEATHFIELD PK,HEATHFIELD,CAPPAGH RD FINGLAS'],
            #['CARLOW', 'CLARENCE GATE,KILKENNY RD'],
        ]


df_addr = pd.DataFrame(samples,columns=['county','address'])


df = pd.read_csv(config['dir_input'] + 'ie-towns.csv')

df = df[['name', 'postal_town', 'irish_name', 'county', 'eircode']]

for i in df:
    df[i] = df[i].str.upper()

df['search_string'] = df['name'] + ',' + df['county']

df = df[['search_string', 'eircode']]

df = df.drop_duplicates()

df.to_csv(config['dir_output'] + 'towns_unique.csv')




def whats_my_eircode(l):

    addr = l[1]
    county = l[0]

    s = addr.split(',')[::-1]


    for i in s:
        found = False
        x = i + ',' + county
        
        for row_index,row in df.iterrows():
            
            if df.iloc[row_index,5] == x:
                #print(i, df.iloc[row_index,4] )
                eircode = df.iloc[row_index,4]
                found = True
            
            if found:
                print(i, eircode)
                break
            
            

    # if found:
    #     print(i, df.iloc[row_index,4])
    # else:
    #     print(i)


# for i in samples:

#     whats_my_eircode(i)
