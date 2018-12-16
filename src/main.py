import sys
import pandas as pd
import json
import re
import datetime as dt
from fuzzywuzzy import process

ppr_url = 'https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/$FILE/PPR-ALL.zip'

# Load that config
with open('conf\\config.json') as f:
     config = json.load(f)

with open('conf\\street_abbr.json') as f:
     street_abbr = json.load(f)

with open('conf\\county_towns.json') as f:
     county_towns = json.load(f)

dir_input = config['dir_input']
dir_output = config['dir_output']


def import_eircodes(f):
    df_eirc = pd.read_csv(f)
    df_eirc = df_eirc[['name', 'postal_town', 'county', 'eircode','province',
                       'nuts3_region']].drop_duplicates()
    
    for i in df_eirc:
        df_eirc[i] = df_eirc[i].str.upper()

    return df_eirc


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


def get_post_code(df):
    ''' extract post code from address string and combine 

    :param df: pandas dataframe
    :return: pandas dataframe
    
    '''
   
    rgx_dub = re.compile(r'DUBLIN [0-9]{1,2}')
    df['Post_Code2'] = df['Address'].apply(lambda x: rgx_dub.findall(x)[0] if rgx_dub.search(x) else pd.np.nan )
    df['Post_Code2'] = pd.np.where(df['Address'].str.contains('DUBLIN 6W'), 'DUBLIN 6W', df['Post_Code2'])
    df['Post_Code'] = pd.np.where(df['Post_Code'].isnull(), df['Post_Code2'],df['Post_Code']) #combine post code cols
    df['Post_Code'] = df['Post_Code'].str.upper()
    df['Post_Code'] = df['Post_Code'].str.replace('BAILE .THA CLIATH','DUBLIN', regex=True)
    df['Post_Code'] = df['Post_Code'].str.replace('N. BHAINEANN','', regex=True)
    df['Post_Code'] = df['Post_Code'].str.replace('[^0-9]','')
    df['Post_Code'] = df['Post_Code'].apply(lambda x: 'D' + str(x).zfill(2) if not pd.isnull(x) else '')
    df = df.drop(['Post_Code2'], axis=1)

    return df


def is_apartment(s):
    '''Check string for keyword regex match indicating that address is an appartment
    :param s: string
    :return: string
    '''
   
    is_apt = 'No'
    #^|\s|[0-9]|[,.-_()]
    apt_synomyns = [r'(^|\s|[0-9]|[-_().,])(FLAT|FLT|FL)([0-9]|\s|S|[,.])',
                    r'(^|\s|[0-9]|[-_().,])(FLOOR|FLR|FL)([0-9]|\s|S|[,.])',
                    r'(^|\s|[0-9]|[-_().,])(APPARTMENT|APARTMENT|APPART|APART|APT|APP|AP)([0-9]|\s|S|[,.])',
                    r'^APART|^APPART']

    for i in apt_synomyns:
        if bool(re.search(i, s)):
            is_apt = 'Yes'

    return is_apt


def remove_cnty(addr, cnty):

    x = addr
    
    if addr[-len(cnty):].upper() == cnty.upper():

        x = addr[:-len(cnty)]
        x = re.sub(',$','',x)
        x.strip()
    
    return x

def add_cnty_town(town, cnty):

    x = town
    
    if x == '' or pd.isnull(x):
        x = county_towns[cnty]

    return x


def simple_addr(s):

    re_county = '[,.\s](COUNTY|CO)[,.\s].*$'
    re_dublin = '[,.\s]DUBLIN$'
    x = re.sub(re_county, '', s)
    x = re.sub('[0-9][A-Z]','', x)
    x = re.sub('[^A-Z,\s]', '', x)
    x = re.sub('  ', ' ', x)
    x = x.strip()
    x = re.sub(re_dublin, '', x)
    x = re.sub('^,', '', x)
    x = re.sub('^APART.*,|^APT.*,|^APPT.*,|^APPAR.*,|^NO ','', x)
    x = re.sub('PO$|P O$|', '' ,x) # post office town (ATHLONE PO)
    x = re.sub('^[A-Z](\s|,)', '', x)
    x = re.sub('^,', '', x)
    x = x.strip()
    

    for i in street_abbr:
        x = x.replace(i, street_abbr[i])

    return x


def get_town(s):
    
    x = s.split(',')[-1]
    x = x.strip()

    for i in street_abbr:
        x = re.sub('^.*' + street_abbr[i] + '\s', '', x)
        x = re.sub('^.*' + street_abbr[i] + '$', '', x) # remove anything up to "MAIN RD" etc
    
    x = re.sub('NEAR(\s|$)', '', x)
    x = x.strip()
    x = re.sub('\sTOWN$', '', x)

    return x


def import_ppr(f):

    df = pd.read_csv(f, dtype=str)
    df.columns = ['Date_Sale', 'Address', 'Post_Code', 'County', 'Price', 'Not_Full_Market_Price',
                  'VAT_Exclusive', 'Description_of_Property', 'Property_Size_Description']

    df['Description_of_Property'] = df['Description_of_Property'].apply(property_age)
    df['Property_Size_Description'] = df['Property_Size_Description'].fillna('')
    df['Property_Size_Description'] = df['Property_Size_Description'].apply(property_size)
    df['Price'] = df['Price'].replace('[€,]', '', regex=True).astype(float)

    # General Address Clean Up
    df['County'] = df['County'].str.upper()
    df['Address'] = df['Address'].str.upper()
    df['Address'] = df['Address'].str.strip()           # trim leading trailing spaces
    df['Address'] = df['Address'].str.replace('  ',' ') # double spaces
    df['Address'] = df['Address'].str.replace(', ',',') # comma spaces
   
    df = get_post_code(df)

    df['Simple_Address'] = df['Address'].apply(simple_addr)
    df['Simple_Address'] = df.apply(lambda x: remove_cnty(x['Simple_Address'], x['County']), axis=1)
    df['Is_Apartment'] = df['Address'].apply(is_apartment)
    df['Town'] = df['Simple_Address'].apply(get_town)
    df['Town'] = df.apply(lambda x: add_cnty_town(x['Town'], x['County']), axis=1)

    return df


def match_by_county(df_ppr, df_eircode, county):

    '''
    split left and right dfs by county for quicker, more accurate matches
    '''

    df_ppr = df_ppr[df_ppr['County'] == county]
    df_eircode = df_eircode[df_eircode['county'] == county]
    #df_ppr['Town2'] = df_ppr['Town'].apply(lambda x: process.extractOne(x, df_eircode['name'])[0])

    unique_towns = df_ppr['Town'].to_frame()
    list_of_towns_df = unique_towns.drop_duplicates()

    #list_of_towns_df = pd.DataFrame.from_records(list_of_towns_df)
    list_of_towns_df['best_matched_town'] = list_of_towns_df['Town'].apply(lambda x: process.extractOne(x, df_eircode['name'])[0])

    df_ppr = df_ppr.merge(list_of_towns_df, left_on='Town', right_on='Town', how='left')
    df_ppr = df_ppr.merge(df_eircode, left_on='best_matched_town', right_on='name', how='left')

    return df_ppr




def main():
   
    print(str(dt.datetime.now()) + ' STARTED')
    
    df_ppr = import_ppr(dir_input + 'PPR-ALL.csv')
    df_ppr.to_csv(dir_output + 'ppr-' + format(dt.datetime.now().strftime("%Y%m%d-%H%M")) +'.csv', index=False)

    df_eirc = import_eircodes(dir_input + 'ie-towns.csv')
    df_eirc.to_csv(dir_output + 'eircode-' + format(dt.datetime.now().strftime("%Y%m%d-%H%M")) +'.csv', index=False)

    df_out = pd.DataFrame()

    for i in county_towns:
        print(str(dt.datetime.now()) + ' ' + i)
        df_x = match_by_county(df_ppr, df_eirc, i)
        df_out = df_out.append(df_x)

    df_out['eircode_pass2'] = df_out['Post_Code'] + df_out['eircode']
    df_out['eircode_pass2'] = df_out['eircode_pass2'].str[:3]

    df_out.to_csv(dir_output + 'matched-' + format(dt.datetime.now().strftime("%Y%m%d-%H%M")) +'.csv', index=False)
    
    print(str(dt.datetime.now()) + ' ' + i)

if __name__ == "__main__":
    sys.exit(main())
    