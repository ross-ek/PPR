import sys
import pandas as pd
import json
import re
import datetime as dt

ppr_url = 'https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/$FILE/PPR-ALL.zip'

# Load that config
with open('conf\\config.json') as f:
     config = json.load(f)


dir_input = config['dir_input']
dir_output = config['dir_output']


def property_age(x):
    """
    There are two property types. New or Second-hand.
    This function searches text for key words to determine if dwelling is new or second hand.
    """
    if 'NUA' in x.upper() or 'NEW' in x.upper():
        y = 'New'
    else:
        y = 'Second-Hand'

    return y


def property_size(x):
    """
    Determine property size from text descr.
    There are only 3 that I will label S,M and L. Text description is in English or Irish.
    <38, 35-125 and >125 meters sq.
    """

    #if x == pd.np.nan:#
    y = x
    if '38' in x and '125' in x:
        y = 'M'
    elif '38' in x and '125' not in x:
        y = 'S'
    elif '38' not in x and '125' in x:
        y = 'L'

    return y


def import_ppr(f):

    df = pd.read_csv(f, dtype=str)
    df.columns = ['Date_Sale', 'Address', 'Post_Code', 'County', 'Price', 'Not_Full_Market_Price', 'VAT_Exclusive',
                  'Description_of_Property', 'Property_Size_Description']

    df['Description_of_Property'] = df['Description_of_Property'].apply(property_age)
    df['Property_Size_Description'] = df['Property_Size_Description'].fillna('')
    df['Property_Size_Description'] = df['Property_Size_Description'].apply(property_size)
    df['Price'] = df['Price'].replace('[€,]', '', regex=True).astype(float)

    # General Clean Up
    df['Address2'] = df['Address'].str.upper()
    df['Address2'] = df['Address2'].str.strip()           # trim leading trailing spaces
    df['Address2'] = df['Address2'].str.replace('  ',' ') # double spaces
    df['Address2'] = df['Address2'].str.replace(', ',',') # comma spaces
    
    
    # extract post code from address string
    rgx_dub = re.compile(r'DUBLIN [0-9]{1,2}')
    df['Post_Code2'] = df['Address2'].apply(lambda x: rgx_dub.findall(x)[0] 
                                            if rgx_dub.search(x) else pd.np.nan )
    df['Post_Code2'] = pd.np.where(df['Address2'].str.contains('DUBLIN 6W'), 
                                   'DUBLIN 6W', df['Post_Code2'])
    df['Post_Code'] = pd.np.where(df['Post_Code'].isnull(), df['Post_Code2'],
                                  df['Post_Code']) #combine post code cols
    df['Post_Code'] = df['Post_Code'].str.upper()
    df['Post_Code'] = df['Post_Code'].str.replace('BAILE .THA CLIATH','DUBLIN', regex=True)
    df['Post_Code'] = df['Post_Code'].str.replace('N. BHAINEANN','', regex=True)

    # Towns - Remove trailing "county/co/ co.  whatever" or "dublin 1-24". 
    re_last_addr = '(,| )COUNTY.*$|(,| )CO[.{1}| {1}].*$|(,| )DUBLIN [0-9]{1,2}$|(,| )DUBLIN$'
    df['Address2'] = df['Address2' ].str.replace('[(.| )]$', '', regex=True)
    df['Address2'] = df['Address2'].str.replace(re_last_addr, '', regex=True)

    df['Address2'] = df['Address2'].str.replace('(,| )COUNTY.*$|(,| )CO[.{1}| {1}].*$|(,| )DUBLIN [0-9]{1,2}$|(,| )DUBLIN$', '', regex=True)
    df['Address2'] = df['Address2'].str.strip()

    # df['Address2'] = df['Address2'].str.replace(',COUNTY.*$|,CO[.].*$|,DUBLIN [0-9]{1,2}$|,DUBLIN$', '', regex=True)
    # df['Address2'] = df['Address2'].str.replace(' COUNTY.*$| CO[.].*$| DUBLIN [0-9]{1,2}$| DUBLIN$', '', regex=True) # some down't have commas
    
    # Asuming town is last string entry
    df['Town'] = df['Address2'].str.split(',').str[-1]




    #df['Address2'] = df['Address'].str.replace(', CO\. \w+$', '', regex=True)

    # clean up
    df = df.drop(['Post_Code2'], axis=1)

    # print(df['Address'][312711], '\n',df['Address2'][312711], '\n...')
    # print(df['Address'][0], '\n',df['Address2'][0], '\n...')
    # print(df['Address'][19], '\n',df['Address2'][19], '\n...')
    


    return df


def main():
    df_ppr = import_ppr(dir_input + 'PPR-ALL.csv')
    
    try:
        now = dt.datetime.now()
        df_ppr.to_csv(dir_output + 'output-' + format(now.strftime("%Y%m%d-%H%M")) +'.csv', index=False)
    except Exception as e:
        print('close the file')
        print(str(e))
    
    #a = df_ppr['Add2'].unique()

    # print(a)
    # f = open(dir_output + 'output_address.csv', 'a')
    
    # for i in a:
    #     f.write(i + '\n')

    f.close()

if __name__ == "__main__":
    sys.exit(main())

