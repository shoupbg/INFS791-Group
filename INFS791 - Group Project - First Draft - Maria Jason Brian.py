# INFS 791 - Group Project - Maria, Jason, Brian - October 23, 2021

# This program uses historical airline flight data to help a user choose a time of day
#   day [possible add on: and day of the week] to fly to minimize flight delays

import pandas as pd
import numpy as np
from statistics import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf

# Access airport data file and create a list of valid airport codes from the flight data file
airport_data = pd.read_csv('airport_data.csv')
flight_data = pd.concat(map(pd.read_csv, ['2020DecemberIllinoisFlights.csv', '2019DecemberIllinoisFlights.csv','2018DecemberIllinoisFlights.csv', '2017DecemberIllinoisFlights.csv']))

flight_data['TimeOfDay'] = np.where(flight_data['CRS_DEP_TIME'] <= 1200, 'Morning', 
                      np.where(flight_data['CRS_DEP_TIME'] >= 1700, 'Evening', 'Afternoon'))


# Filters flight data to include only flights originating at ORD or MDW
flight_data["ARR_DELAY_NEW"]= flight_data["ARR_DELAY_NEW"].fillna(0).astype(int)

flight_data_cleaned = flight_data[flight_data['ARR_DELAY_NEW'].notnull()]
flight_data_filtered = flight_data_cleaned.query("ORIGIN == 'ORD' or ORIGIN == 'MDW'")

# Creates list of valid destinations from ORD or MDW
airports_served = flight_data_filtered.DEST.unique()
airports_served_list = airports_served.tolist()
available_airports = airport_data.query("Code == @airports_served_list")

# Ask user to enter city name or use lookup tool

codes = airport_data.Code.to_list()
descriptions = airport_data.Description.to_list()

codesdescriptions = dict(zip(codes, descriptions))

airport_data["Code"] = airport_data["Description"].map(codesdescriptions)


print ("\nAre you planning to travel over winter break?")
print ("\nThis program will help you choose a flight in order to minimize delays.")
print ("\nFirst, we need to know where you're going.")
print ("If you know the three-letter code for the airport you're flying to, enter it now.")
destination_question = input ("If you don't know the code, type 'lookup': ").upper()






# Starts lookup loop if applicable and ends with entry of airport code
# new line

# Define lookup function
def lookup():
    city = input("\nPlease enter a city name to look up its airport code:  ")
    possible_airport_codes = available_airports.loc[available_airports['Description'].str.contains(city, case=False)]

    while possible_airport_codes.empty == True:
        print("\nThat city is not directly served by a Chicago airport.")
        city = input("\nPlease enter another city name to look up its airport code:  ")
        possible_airport_codes = available_airports.loc[
            available_airports['Description'].str.contains(city, case=False)]
    else:
        print("\nBelow are airports in the selected city served by airports in Chicago:")
        print("\n", possible_airport_codes.to_string(index=False))
        destination_question = input("\nPlease enter the three-letter code of the airport you're flying to:  ")
    return destcode


if destination_question.lower() == "lookup":
    destination_question  = lookup()


"""
print(airport_data['Description'].where(airport_data['Code']==destination_question))
"""

"""
airport_data['Code Name'] = airport_data['Code']+airport_data['Description']

print()
"""

#Need to fix this - shouldn't be hard to retrieve the Description from the airport_data.csv file based on the "destination_question" value

"""

# Lookup name of city that destination airport (code) is located in

destination_dict = {row[0]: row[1] for row in available_airports.values}

destination_airport_city = available_airports[destination_question]

print(destination_airport_city)
"""

# Checks whether airport code entered is a valid code actually served by a Chicago airport; starts lookup loop again if needed

while destination_question.upper() not in airports_served_list:
    print("\nThat is not a valid entry")
    destination_question = input("\nPlease try again.  Please enter a three-letter airport code or type 'lookup':  ")
    if destination_question.lower() == "lookup":
        destination_question = lookup()
else:
    print(f"\nWe will analyze the delay history of flights from Chicago to ", codesdescriptions[destination_question])


# Once we have a valid airport destination code, we query the data to see if there are flights between O'Hare and/or Midway and the destination

destination_flights = flight_data_filtered.query("DEST == @destination_question.upper()")
num_dest = destination_flights['DEST'].count()

print(f"\nThere were {num_dest} flights from Chicago to {codesdescriptions[destination_question]} in December 2017, 2018, 2019 & 2020")

# Data frame Total count of flights by origin
count_by_origin = destination_flights.groupby('ORIGIN').agg({'ARR_DELAY_NEW': 'count'})
group_delay_origin = destination_flights.query("ARR_DELAY_NEW > 0").groupby('ORIGIN')
count_delay_by_origin = group_delay_origin.agg({'ARR_DELAY_NEW': 'count'})
total_and_delay = count_by_origin.join(count_delay_by_origin, how = 'left', lsuffix = '_total', rsuffix = '_delay')
# total_and_delay.rename({'ARR_DELAY_NEW':'total count of flights'})

# Data frame Total count of flights by origin and time of day
count_by_origin_time = destination_flights.groupby(['ORIGIN','TimeOfDay']).agg({'ARR_DELAY_NEW': 'count'})
group_delay_time = destination_flights.query("ARR_DELAY_NEW > 0").groupby(['ORIGIN','TimeOfDay'])
count_delay_by_origin_time = group_delay_time.agg({'ARR_DELAY_NEW': 'count'})
total_and_delay_by_time = count_by_origin_time.join(count_delay_by_origin_time, how = 'left', lsuffix = '_total', rsuffix = '_delay')

# Data frame Total count of flights by origin and day of the week
count_by_origin_day = destination_flights.groupby(['ORIGIN','DAY_OF_WEEK']).agg({'ARR_DELAY_NEW': 'count'})
group_delay_day = destination_flights.query("ARR_DELAY_NEW > 0").groupby(['ORIGIN','DAY_OF_WEEK'])
count_delay_by_origin_day = group_delay_day.agg({'ARR_DELAY_NEW': 'count'})
total_and_delay_by_day = count_by_origin_day.join(count_delay_by_origin_day, how = 'left', lsuffix = '_total', rsuffix = '_delay')

# eliminates the error of not having flights form origin

for index, row in count_by_origin.iterrows():
    if len(count_by_origin) > 1:
        print(f"Of those flights, {row['ARR_DELAY_NEW']} were from {index}")
    elif len(count_by_origin) == 0:
        print(f"\nNo airport go to {destination_question}.")
    else:
        print(f"\nAll flights are from {index} to {destination_question}.")

i = 0
min_percent = 0
min_airport = ""
origin_delay_mean = group_delay_origin.agg({'ARR_DELAY_NEW': 'mean'})
for index, row in total_and_delay.iterrows():
    delay_percent = round(row['ARR_DELAY_NEW_delay'] / row['ARR_DELAY_NEW_total'] * 100, 1)
    if i == 0:
        min_percent = delay_percent
        min_airport = index
        i+=1
    else:
        if delay_percent<min_percent:
            min_percent = delay_percent
            min_airport = index
    print(f"\n{delay_percent}% of the {index} flights were delayed")
else:
    print(f"\nOverall, {min_airport} is a better option for this route because fewer flights are delayed.")
    # print("--------Mean", group_delay_origin.agg({'ARR_DELAY_NEW': 'mean'}))


i = 0
min_percent = 0
min_time = ""
for index, data in total_and_delay_by_time.iterrows():
    for colname, row in data.to_frame().transpose().iterrows():
        time_delay = round(row['ARR_DELAY_NEW_delay'] / row['ARR_DELAY_NEW_total'] * 100, 1)
        if index[0] == min_airport:
            if i == 0:
                min_percent = time_delay
                min_time = index[1]
                i += 1
            else:
                if time_delay < min_percent:
                    min_percent = time_delay
                    min_time = index[1]
        print(f"{row['ARR_DELAY_NEW_total']} of the {index[0]} flights were in the {index[1]}")
        print(f"{index[0]} flights delayed were:  {index[1]} {time_delay}%")
else:
    print(f"\n{min_time} is the best time to depart {min_airport} on this route to minimize delays.")
    # print("--------Mean", group_delay_time.agg({'ARR_DELAY_NEW': 'mean'}))

i = 0
min_percent = 0
min_day = ""
week_day = {1:"Monday", 2:"Tuesday", 3:"Wednesday", 4:"Thursday", 5:"Friday", 6:"Saturday", 7:"Sunday"}
for index, data in total_and_delay_by_day.iterrows():
    for colname, row in data.to_frame().transpose().iterrows():
        day_delay = round(row['ARR_DELAY_NEW_delay'] / row['ARR_DELAY_NEW_total'] * 100, 1)
        print(f"{row['ARR_DELAY_NEW_total']} of the {index[0]} flights were on {week_day[index[1]]}")
        if index[0] == min_airport:
            if i == 0:
                min_percent = day_delay
                min_day = index[1]
                i += 1
            else:
                if day_delay < min_percent:
                    min_percent = day_delay
                    min_day = index[1]
        print(f"{index[0]} flights delayed were:  {week_day[index[1]]} {day_delay}%")
else:
    print(f"\n{week_day[min_day]} is the best day to depart {min_airport} on this route to minimize delays.")
    # print("--------Mean", group_delay_day.agg({'ARR_DELAY_NEW': 'mean'}))

"""
# Regression

model= smf.logit(formula="ARR_DELAY_NEW ~ TimeOfDay", data= destination_flights).fit()

# Print out the model summary information
print(model.summary())



# Bar chart

# Change data type of pickup_community_area to integer
# trips_df = trips_df.astype({'pickup_community_area':int})

# trips_df = trips_df.set_index('pickup_community_area')
destination_flights = destination_flights.set_index('DEST')


# Create DataFrame groupby object with count of pickups by area
# delay = destination_flights.groupby('TimeOfDay').sum()
delay = destination_flights.groupby('TimeOfDay').agg({'ARR_DELAY_NEW': 'sum'})
delay_percent = delay / delay['ARR_DELAY_NEW'].sum()

count_by_week = destination_flights.groupby(['ORIGIN','DAY_OF_WEEK']).agg({'ARR_DELAY_NEW': 'count'})
delay_by_week = destination_flights.query("DEP_DELAY_NEW > 0").groupby(['ORIGIN','DAY_OF_WEEK']).agg({'ARR_DELAY_NEW': 'count'})

print(type(count_by_week))

print(delay)
print(delay_percent)

print(count_by_week , delay_by_week)

x_labels = pd.Series(delay.index.values)
y_values = pd.Series(delay['ARR_DELAY_NEW'].values)

# Create an array of the number of categories to use in the histogram
bars = np.array(range(len(x_labels)))

# Use xticks method to specify actual values of pickup locations
plt.xticks(bars, x_labels)

plt.bar(bars, y_values)

plt.title('Delay by Time of Day')
plt.xlabel('Time of Day')
plt.ylabel('Delays')
plt.show()

"""