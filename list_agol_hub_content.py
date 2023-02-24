# Import necessary libraries
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.features import FeatureSet
from collections import defaultdict
import pandas as pd
import os

print('Getting login information')
try:
    # Grab username and password from config file when running locally
    import config
    agol_username = config.USER_NAME
    agol_password = config.PASSWORD
except:
    # Get username and password from environment when running on github actions
    agol_username = os.environ['USER_NAME']
    agol_password = os.environ['PASSWORD']

# Connect to the BC MapHub
print('Connecting to the BC Map Hub')
ago_gis = GIS(url="https://governmentofbc.maps.arcgis.com/home", username=agol_username, password=agol_password)

# Select the Thompson Okanagan Region Hub Content Group
hub_group = ago_gis.groups.search('title:Thompson Okanagan Region Hub Content')[0]

# Create a dictionary object of the integer type to store counts
dict_types = defaultdict(int)

print('Searching through content group and incrementing counters')

# Loop through the hub content group add counts where applicable based on content type
for group_item in hub_group.content():
    if group_item.type in ['Service Definition', 'Hub Page']:
        continue
    if group_item.type in ['Web Map']:
        dict_types['Web Maps'] += 1
    elif group_item.type in ['Web Mapping Application', 'Dashboard', 'StoryMap']:
        dict_types['Applications'] += 1
    elif group_item.type in ['Feature Service']:
        dict_types['Datasets'] += 1
    elif group_item.type in ['PDF']:
        dict_types['Documents'] += 1
    else:
        dict_types['Other'] += 1
print(dict_types)

# Create a pandas dataframe object from the type dictionary
df = pd.DataFrame(sorted(dict_types.items()), columns=['TYPE', 'NUMBER_FILES'])
print(df)

# Reference the csv file hosted on ArcGIS Online
tbl = FeatureLayer('https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/hub_inventory/FeatureServer/0', gis=ago_gis)

# Remove all rows from the table
print('Removing all rows from existing hub inventory table')
tbl.manager.truncate()

# Create a featureset from the dataframe
add_tbl = FeatureSet.from_dataframe(df=df)
print('Created table from dataframe')

# Append the newly created featureset to the csv file
tbl.edit_features(adds=add_tbl)
print('Values added successfully to hub inventory table')