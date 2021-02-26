import os
import pandas as pd
import numpy as np
import re
from pyecharts.charts import WordCloud
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from pyecharts.charts import Map, Geo
from pyecharts import options as opts

collection_name = "poker"
folder_boardgames = os.path.join("..", "data", collection_name)

# Wczytanie danych z csv
Users = pd.read_csv(os.path.join(folder_boardgames, "Users.xml.csv"))

print("Sprawdzimy ilu użytkowników ma ustawioną lokalizację...")
location = Users["Location"]
not_nan = location.count()
percenage = not_nan / location.shape[0] * 100
print("Użytkowników tego serwisu jest {}. \nAle tylko {} z nich ma ustawioną lokalizację co daje {:.2f}%"
      .format(location.shape[0], not_nan, percenage))

print("Odrzucamy wartości z Nan i wyświetlamy początek naszego zbioru:")
location = location.dropna()
print(location.head(10))

on_earth = location[location == "Earth"].count()
print("Mamy {} obywatelów ziemi".format(on_earth))

print("Stworzymy teraz dataset z krajami:")
country = location.map(lambda x: x.split(', ')[-1])
country = pd.DataFrame(country.reset_index(drop=True))

country.loc[country["Location"] == "UK", "Location"] = "United Kingdom"
country.loc[country["Location"] == "USA", "Location"] = "United States"

regex_two_capitals = re.compile("[A-Z]{2}$")
regex_us = re.compile("United States")

states_id = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona",
               "California", "Colorado", "Connecticut", "District ", "of Columbia",
               "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho",
               "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts",
               "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi",
               "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire",
               "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
               "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina",
               "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands",
               "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]


def regex_apply_states(val):
    if val and (
            bool(regex_two_capitals.match(val) and val in states_id) or regex_us.findall(val) or val in state_names):
        return 'United States'
    else:
        return val


country['Location'] = country['Location'].apply(regex_apply_states)

country.loc[country["Location"] == "Deutschland", "Location"] = "Germany"

print("Przygotujmy ładną ramkę daych:")

df = pd.DataFrame(country['Location'].value_counts().reset_index())
df.columns = ["CountryName", "TotalUsers"]

print("Forever alone:")
print(df[df.TotalUsers == 1])

df = df.head(20)


def write_cloud_of_names(df):
    """Wyrenderowanie chmury słownej"""
    name = list(df.CountryName)
    value = [int(i / 10) * 100 for i in df.TotalUsers]
    wordcloud = WordCloud()
    wordcloud.add("Popular Countries", list(zip(name, value)), word_size_range=None)
    wordcloud.render("cloud_{}.html".format(collection_name))


write_cloud_of_names(df)


def get_continent(col):
    """Znalezienie kontynentu dla podanego kraju."""
    try:
        cn_a2_code = country_name_to_country_alpha2(col)
    except:
        cn_a2_code = 'Unknown'
    try:
        cn_continent = country_alpha2_to_continent_code(cn_a2_code)
    except:
        cn_continent = 'Unknown'
    return cn_a2_code, cn_continent


def get_countries_codes(df):
    """Przypisanie kodów do poszczególnych krajów."""

    df['Codes'] = df['CountryName'].apply(get_continent)
    df['Country'] = df['Codes'].apply(lambda x: x[0])
    df['Continet'] = df['Codes'].apply(lambda x: x[1])
    return df


df = get_countries_codes(df)


def draw_map(dataframe, name):
    """Wyrenderowanie mapy świata dla podanych krajów i ilości użytkowników."""

    df1 = dataframe[dataframe.Country != "Unknown"]

    countries = list(df1['CountryName'])
    totalnumber = list(df1['TotalUsers'])

    data_list = [[countries[i], totalnumber[i]] for i in range(len(countries))]
    map_1 = Map(init_opts=opts.InitOpts(width="1000px", height="460px"))
    map_1.add('Number of users', data_list, maptype='world', is_map_symbol_show=False)
    map_1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    map_1.set_global_opts(visualmap_opts=opts.VisualMapOpts(max_=1100000, is_piecewise=True,
                                                            pieces=[
                                                                {"min": 0, "max": 100},
                                                                {"min": 100, "max": 200},
                                                                {"min": 200, "max": 300},
                                                                {"min": 300, "max": 400},
                                                                {"min": 400, "max": 500},
                                                                {"min": 500, "max": 600},
                                                                {"min": 600, "max": 700},
                                                                {"min": 700, "max": 800},
                                                                {"min": 800, "max": 900},
                                                                {"min": 900, "max": 1000},
                                                                {"min": 1000, "max": 1500},
                                                                {"min": 1500, "max": 2000},
                                                                {"min": 2000, "max": 2500},
                                                                {"min": 3000},
                                                            ]),
                          title_opts=opts.TitleOpts(title='Users of {0}'.format(name),
                                                    subtitle='Top 20 countries',
                                                    pos_left='center',
                                                    padding=0,
                                                    item_gap=2,
                                                    title_textstyle_opts=opts.TextStyleOpts(color='darkblue',
                                                                                            font_weight='bold',
                                                                                            font_family='Courier New',
                                                                                            font_size=30),
                                                    subtitle_textstyle_opts=opts.TextStyleOpts(color='grey',
                                                                                               font_weight='bold',
                                                                                               font_family='Courier New',
                                                                                               font_size=13)),
                          legend_opts=opts.LegendOpts(is_show=False))

    map_1.render("map_{0}.html".format(name))


draw_map(df, collection_name)


df.to_csv("locations_{0}.csv".format(collection_name))

