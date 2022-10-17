"""
Functions needed for the pandas data cleaning project
October 2022
"""
# GENERAL CLEANING FUNCTIONS

def import_clean (dataset_loc, encod):
    """
    Takes a dataset in csv format and returns a pandas object without blank lines and duplicates
    """
    import pandas as pd
    df = pd.read_csv(dataset_loc, encoding=encod)
    print(f"""Rows: {df.shape[0]}
    Columns: {df.shape[1]}""")
    df.dropna(how="all", inplace=True)
    df = df.drop_duplicates()
    return df

# SHARK SPECIES CLEANING FUNCTIONS

def species_clean(string):
    import re
    '''
    function to clean species column from database https://www.kaggle.com/datasets/teajay/global-shark-attacks
        1) If no value return "unknown shark"
        2) Set all text to lower case
        3) Using regex finds pattern of word 'shark' precided by one or two words, if can find convert to "unknown shark"
        4) Remove "small" string and "a " string
        5) Remove leading and trailing spaces
        6) If "unidentified" return "unknown shark"
        7) Return either shark species or "unknown shark"
        
    '''
    if not isinstance(string, str):
        return "unknown shark"
    string = string.lower()
    if re.match("[A-Za-z]+\s?[A-Za-z]{3,}\ssharks?", string):
        shark = re.match("[A-Za-z]+\s?[A-Za-z]{3,}\ssharks?", string)[0]
        if "small" in shark:
            shark = shark.replace("small", "")
        if "a " in shark:
            shark = shark.replace("a ", "")
        elif "uidentified" in shark:
            return 'unknown shark'
        shark = shark.strip()
        if shark == "shark":
            return 'unknown shark'
        else: 
            return shark
    else:
        return 'unknown shark'

def species_norm(dataframe):

    """
    Specific function to normalize Shark species column
    - Add Unknown Shark to all cases without information
    - Find if Shark Species are metioned in the cases where something is reported
    - Clean and standrize Shark Species reported
    - Find the 8 species most reported and group the others in a Other Sharks category
    - Adding a new column "Shark Identified"
    """
    ## Extracting Shark Species:

    dataframe["Species "] = dataframe["Species "].apply(species_clean)

    ## Groupping Species:

    species_list = substrings_cleaning(list(dataframe["Species "].unique())) ## Finding substrings of strings in the list of species
    dataframe["Species "] = dataframe["Species "].apply(lambda x: clean_categories(x, species_list)) ## Cleaning dtabase with the final list of species

    ## Keep the 8 species with more incidents and group the rest as "Other Sharks"

    top_8 = list(dataframe["Species "].value_counts().index)[:10] ## Extracting the top 8 shark species list
    dataframe["Species "] = dataframe["Species "].apply(lambda x: x.title() if x in top_8 else "Other Sharks" ) ## Gropping not top8 species in a "Other Sharks" category

    ## Adding a new column "Shark Identified"

    dataframe["Shark Identified"] = dataframe["Species "].apply(lambda x: 0 if x == 'Unknown Shark' else 1)

    return dataframe

def substrings_cleaning(list):
    '''
    Removes substrings from a strings list
    '''
    clean_list = list.copy()
    is_sub = False
    for e in list:
        for i in range(0,len(list)):
            if e in list[i] and list[i] in clean_list and e != list[i]:
                clean_list.remove(list[i])
    return clean_list

def clean_categories(element, categories_list):
    '''
    function to clean subcategories (contains any category as a substring) from a categories list
    '''
    if element in categories_list:
            return element
    else:
        for e in categories_list:
            if element in e:
                return e
                break

## SEX CLEANING FUNCTIONS

def sex_clean(dataframe):
    """
    Function to clean and normlize Sex column in sharks database
    """
    sharks_sex = dataframe.copy()
    sharks_sex = sharks_sex.dropna(subset=["Sex "])
    sharks_sex["Sex "] = sharks_sex["Sex "].apply(lambda x: x.strip())
    sharks_sex["Sex "] = sharks_sex["Sex "].apply(lambda x: x if x == "M" or x == "F" else None)
    sharks_sex = sharks_sex.dropna(subset=["Sex "])
    return sharks_sex

## FATAL (Y/N) CLEANING FUNCTIONS

def fatal_clean_function(string):
    if not isinstance(string, str):
        return None
    string = string.upper()
    string = string.strip()
    if string == "Y" or string ==  "N":
        return string
    else:
        return None

def fatal_clean(dataframe):
    dataframe["Fatal (Y/N)"] = dataframe["Fatal (Y/N)"].apply(fatal_clean_function)
    sharks_fatal = dataframe.dropna(subset=["Fatal (Y/N)"])
    return sharks_fatal

## NORMALIZATION FUNCTION

def norm_biase(dataset, to_norm):
    """
    Adjust values for a possible bias in the data sets with boolean varia
    """
    false_norm = dataset["Percentage"][0]/dataset["Percentage"][2]
    true_norm = dataset["Percentage"][1] /dataset["Percentage"][3]
    sharks_fatal4 = to_norm.copy() 
    sharks_fatal4['Percentage'] = sharks_fatal4['Percentage'].mask((sharks_fatal4['Percentage'] < 100) & (sharks_fatal4['Percentage'] > 0) & (sharks_fatal4["Fatal (Y/N)"]=="N"), other=sharks_fatal4['Percentage']*false_norm, axis=0)
    sharks_fatal4['Percentage'] = sharks_fatal4['Percentage'].mask((sharks_fatal4['Percentage'] < 100) & (sharks_fatal4['Percentage'] > 0) & (sharks_fatal4["Fatal (Y/N)"]=="Y"), other=sharks_fatal4['Percentage']*true_norm, axis=0)
    return sharks_fatal4