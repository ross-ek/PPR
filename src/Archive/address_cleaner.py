import datetime as dt
import pandas as pd
import json
import sys
import re

# CONFIGURATION
with open('conf\\config.json') as f:
     config = json.load(f)

dir_input = config['dir_input']
dir_output = config['dir_output']



def import_towns(f):
    town_info = pd.read_csv(f, dtype=str)
    town_info2 = town_info[['name','county','eircode']]
    
    town_info2['name'] = town_info2['name'].str.upper()
    town_info2['county'] = town_info2['county'].str.upper()

    print(town_info2.head(10))


def import_ppr(f):
   
    df = pd.read_csv(f, dtype=str)
   
    df.columns = ['Date_Sale', 'Address', 'Post_Code', 'County', 'Price'
                    , 'Not_Full_Market_Price', 'VAT_Exclusive'
                    , 'Description_of_Property', 'Property_Size_Description']
   
    df = df.drop(['Not_Full_Market_Price', 'VAT_Exclusive'
                , 'Property_Size_Description'], axis=1)
   
    df['Description_of_Property'] = df['Description_of_Property'].apply(property_age)
    df['Price'] = pd.np.floor(df['Price'].replace('[€,]', '', regex=True).astype(float))
   
    # Dublin Eircode first pass
    df['Post_Code'] = df['Post_Code'].apply(lambda x: x if 'Bhaineann' not in str(x) else pd.np.nan)
    df['Post_Code'] = df['Post_Code'].replace('[^0-9Ww]', '', regex=True)
    
    df['Post_Code'].replace('^.*x|x.*', pd.np.nan, regex=True)
    
    df['Post_Code'] = df['Post_Code'].apply(lambda x: 'D' + str(x).zfill(2) if not pd.isnull(x)  else pd.np.nan)
    df['Post_Code2'] = df['Address'].apply(get_dub_eircode_from_addr)
    df['Post_Code'] = df['Post_Code'].fillna(df['Post_Code2'])

    df = df.drop(['Post_Code2'], axis=1)

    # General Clean Up, backup address col first
    df['Address2'] = df['Address'].str.upper()
    df['Address2'] = df['Address2'].str.strip()           # trim leading trailing spaces
    df['Address2'] = df['Address2'].str.replace('\s',' ', regex=True) # double spaces
    df['Address2'] = df['Address2'].str.replace(', ',',') # comma spaces

    # Towns - Remove trailing "county/co/ co.  whatever" or "dublin 1-24". 

    

    # Remove digits, Apt etc

    # Loop thru a bunch of regexes??
    
    # ['APT(\s|)[0-9]([A-Z]|\s)', 'FLAT(\s|)[0-9]([A-Z]|\s)', 

    list_o_regexes = [r', ', r'[0-9]', r'^APT', r'^APARTMENT', r'^APPARTMENT' , r'^FLAT', '[(.| )]$'
                      , r'(TOP|BOTTOM|ST|RD|ND)(\s|)(FLOOR|FL)' 
                      ,r'(^NO|^NUMBER|^NUM|^N)(\.|\s|\S)([0-9]{1,2}|)' # no. 1 etc
                      ,r'\([A-Z].*\)'  # anything in brackets
                      ,r'(,| )COUNTY.*$|(,| )CO[.{1}| {1}].*$|(,| )DUBLIN [0-9]{1,2}$|(,| )DUBLIN$|DUBLIN 6W' # county whatever, dublin x, etc
                      ,r'[-_!#£$%~\*=+@&\'().\[\]\{\}\\/]' # certain punct
                      ]
                      # BLOCK A ETC

#,r'[()\\/-\.&]' #any left over punct marks etc comma

    for i in list_o_regexes:
        df['Address2'] = df['Address2'].str.replace(i, '', regex=True)

    

    df['Address2'] = df['Address2'].str.replace('\s',' ', regex=True) # double spaces
    df['Address2'] = df['Address2'].str.replace(', ',',') # comma spaces
    df['Address2'] = df['Address2'].str.replace(r'\sSQUARE(\W|$)',' SQ ', regex=True) #SQUARE
    df['Address2'] = df['Address2'].str.replace(r'\sSTREET(\W|$)',' ST ', regex=True) #STREET
    df['Address2'] = df['Address2'].str.replace(r'\sQUAY(\W|$)',' QY ', regex=True) #STREET
    df['Address2'] = df['Address2'].str.replace(r'\sPLACE(\W|$)',' PL ', regex=True) #STREET
    df['Address2'] = df['Address2'].str.replace(r'\sROAD(\W|$)',' RD ', regex=True) #ROAD
    df['Address2'] = df['Address2'].str.replace(r'\sTERRACE(\W|$)',' TCE ', regex=True) #ROAD
    df['Address2'] = df['Address2'].str.replace(r'\sDRIVE(\W|$)',' DV ', regex=True) #DRIVE
    df['Address2'] = df['Address2'].str.replace(r'\sAVENUE(\W|$)',' AVE ', regex=True) #AVE
    df['Address2'] = df['Address2'].str.replace(r'\sCOURT(\W|$)',' CT ', regex=True) #COURT
    df['Address2'] = df['Address2'].str.replace(r'\sPARK(\W|$)',' PK ', regex=True) #PARK
    df['Address2'] = df['Address2'].str.replace(r'\sLOWER(\W|$)',' LR ', regex=True) #LOWER
    df['Address2'] = df['Address2'].str.replace(r'\sUPPER(\W|$)',' UPR ', regex=True) #UPPER

    df['Address2'] = df['Address2'].str.replace(r'\s',' ', regex=True) # double spaces
    df['Address2'] = df['Address2'].str.strip()
    df['Address2'] = df['Address2'].str.replace(r'^,|^,\s','', regex=True) # begins with comma
    df['Address2'] = df['Address2'].str.replace(r'^[A-Z](\s|,)' ,'', regex=True) # " A " at beginning
    df['Address2'] = df['Address2'].str.strip()
    df['Address2'] = df['Address2'].str.replace(r'^,|^,\s|,$','', regex=True) # begins, ends with comma
    
    for i in list_o_regexes:
        df['Address2'] = df['Address2'].str.replace(i, '', regex=True)

    df['Address2'] = df['Address2'].str.strip()
    df['Address2'] = df['Address2'].str.replace(r'\s',' ', regex=True) # double spaces
    df['Address2'] = df['Address2'].str.strip()
    df['Address2'] = df['Address2'].str.replace(r'^,|^,\s','', regex=True) # begins with comma
    df['Address2'] = df['Address2'].str.replace(r'^[A-Z](\s|,)' ,'', regex=True) # " A " at beginning
    df['Address2'] = df['Address2'].str.strip()
    df['Address2'] = df['Address2'].str.replace(r'^,|^,\s|,$','', regex=True) # begins, ends with comma

    df['Address2'] = df['Address2'].str.strip()

    return df

    


with open('conf\\dub_eircodes.json') as f:
    dub_eircodes = json.load(f)

def get_dub_eircode(x):

    return x['Address']


def get_dub_eircode_from_addr(x):
   
    y = None

    for i in dub_eircodes:
        if str(i) in x.upper():
            y = dub_eircodes[i]
            break

    return y


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


def main():

    #ie_towns = import_towns(dir_input + 'ie-towns.csv')

    df_ppr = import_ppr(dir_input + 'PPR-ALL.csv')

    # print(df_ppr.head(10))
    #print(df_ppr['Post_Code'].unique)

    try:
        now = dt.datetime.now()
        # df_ppr.to_csv(dir_output + 'output-' + format(now.strftime("%Y%m%d-%H%M")) +'.csv', index=False)
        df2 = df_ppr['Address2']
        df2.to_csv(dir_output + 'output-' + format(now.strftime("%Y%m%d-%H%M")) +'.csv', index=False)
    except Exception as e:
        print('close the file')
        print(str(e))


if __name__ == "__main__":
    sys.exit(main())
