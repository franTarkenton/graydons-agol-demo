# Import necessary libraries
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from collections import defaultdict
import pandas as pd

ago_gis = GIS("home")

# Select the Thompson Okanagan Region Hub Content Group
hub_group = ago_gis.groups.search('title:Thompson Okanagan Region Hub Content')[0]

# Create a dictionary object of the integer type to store counts
dict_types = defaultdict(int)

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
tbl.manager.truncate()

# Create a featureset from the dataframe
add_tbl = df.spatial.to_featureset()
print(add_tbl)

# Append the newly created featureset to the csv file
tbl.edit_features(adds=add_tbl)