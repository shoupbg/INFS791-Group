# INFS 791 - Group Project - Maria, Jason, Brian - October 23, 2021

# This program uses historical airline flight data to help a user choose a time of day
#   day [possible add on: and day of the week] to fly to minimize flight delays

import pandas as pd
import numpy as np
from statistics import *
import matplotlib.pyplot as plt
import numpy as np

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

print ("\nAre you planning to travel over winter break?")
print ("\nThis program will help you choose a flight in order to minimize delays.")
print ("\nFirst, we need to know where you're going.")
print ("If you know the three-letter code for the airport you're flying to, enter it now.")
destination_question = input ("If you don't know the code, type 'lookup': ")


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
    return destination_question


if destination_question.lower() == "lookup":
    destination_question  = lookup()

"""
Need to fix this - shouldn't be hard to retrieve the Description from the airport_data.csv file based on the "destination_question" value

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
    print(f"\nWe will analyze the delay history of flights from Chicago to " +destination_question)


# Once we have a valid airport destination code, we query the data to see if there are flights between O'Hare and/or Midway and the destination

destination_flights = flight_data_filtered.query("DEST == @destination_question.upper()")
num_dest = destination_flights['DEST'].count()

print(f"\nThere were {num_dest} flights from Chicago to {destination_question} in December 2017, 2018, 2019 & 2020")

ORD_origin = destination_flights.query("ORIGIN == 'ORD'")
ORD_origin_count = ORD_origin['ORIGIN'].count()
MDW_origin = destination_flights.query("ORIGIN == 'MDW'")
MDW_origin_count = MDW_origin['ORIGIN'].count()
if ORD_origin_count < 1:
    print(f"\nThere were no flights from O'Hare to {destination_question}, so we'll focus on flights from Midway.")
if MDW_origin_count <1:
    print(f"\nThere were no flights from Midway to {destination_question}, so we'll focus on flights from O'Hare.")
if ORD_origin_count > 0 and MDW_origin_count > 0:
   print(f"Of those flights, {ORD_origin_count} were from O'Hare and {MDW_origin_count} were from Midway") 

if ORD_origin_count > 0:

    # Following are calculations for total O'Hare flights    
    ORD_delays = ORD_origin.query("ARR_DELAY_NEW > 0")
    ORD_delays_count = ORD_delays['ORIGIN'].count()
    ORD_delay_percent = round(ORD_delays_count / ORD_origin_count * 100,1)
    ORD_delay_length = round(ORD_delays['ARR_DELAY_NEW'].mean())


    # Following are calculations for O'Hare flights by time of day
    ORD_origin_morning = ORD_origin.query("TimeOfDay == 'Morning'")
    ORD_morning_count = ORD_origin_morning['ORIGIN'].count()
    ORD_morning_delays = ORD_origin_morning.query("ARR_DELAY_NEW > 0")
    ORD_morning_delays_count = ORD_morning_delays['ORIGIN'].count()
    ORD_morning_delays_percent = round(ORD_morning_delays_count / ORD_morning_count * 100,1)
    if ORD_morning_delays_count == 0:
        ORD_morning_delay_length = 0
    else:
        ORD_morning_delay_length = round(ORD_morning_delays['ARR_DELAY_NEW'].mean())

    ORD_origin_afternoon = ORD_origin.query("TimeOfDay == 'Afternoon'")
    ORD_afternoon_count = ORD_origin_afternoon['ORIGIN'].count()
    ORD_afternoon_delays = ORD_origin_afternoon.query("ARR_DELAY_NEW > 0")
    ORD_afternoon_delays_count = ORD_afternoon_delays['ORIGIN'].count()
    ORD_afternoon_delays_percent = round(ORD_afternoon_delays_count / ORD_afternoon_count * 100,1)
    if ORD_afternoon_delays_count == 0:
        ORD_afternoon_delay_length = 0
    else:
        ORD_afternoon_delay_length = round(ORD_afternoon_delays['ARR_DELAY_NEW'].mean())



    ORD_origin_evening = ORD_origin.query("TimeOfDay == 'Evening'")
    ORD_evening_count = ORD_origin_evening['ORIGIN'].count()
    ORD_evening_delays = ORD_origin_evening.query("ARR_DELAY_NEW > 0")
    ORD_evening_delays_count = ORD_evening_delays['ORIGIN'].count()
    ORD_evening_delays_percent = round(ORD_evening_delays_count / ORD_evening_count * 100,1)
    if ORD_evening_delays_count > 0:
        ORD_evening_delay_length = round(ORD_evening_delays['ARR_DELAY_NEW'].mean())
    else:
        ORD_evening_delay_length = 0


    print(f"\n{ORD_delay_percent}% of the O'Hare flights were delayed")
    print(f"{ORD_morning_count} of the O'Hare flights were in the morning, {ORD_afternoon_count} were in the afternoon and {ORD_evening_count} were in the evening")
    print(f"O'Hare flights delayed were:  Morning {ORD_morning_delays_percent}%, Afternoon {ORD_afternoon_delays_percent}% and Evening {ORD_evening_delays_percent}%")
    print(f"Average length of delay for delayed flights was:  Morning {ORD_morning_delay_length}, Afternoon {ORD_afternoon_delay_length}, Evening {ORD_evening_delay_length}")



if MDW_origin_count > 0:

    # Following are calculations for total Midway flights
    MDW_delays = MDW_origin.query("ARR_DELAY_NEW > 0")
    MDW_delays_count = MDW_delays['ORIGIN'].count()
    MDW_delay_percent = round(MDW_delays_count / MDW_origin_count * 100,1)
    MDW_delay_length = round(MDW_delays['ARR_DELAY_NEW'].mean())


    # Following are calculations for Midway flights by time of day
    MDW_origin_morning = MDW_origin.query("TimeOfDay == 'Morning'")
    MDW_morning_count = MDW_origin_morning['ORIGIN'].count()
    MDW_morning_delays = MDW_origin_morning.query("ARR_DELAY_NEW > 0")  
    MDW_morning_delays_count = MDW_morning_delays['ORIGIN'].count()
    MDW_morning_delays_percent = round(MDW_morning_delays_count / MDW_morning_count * 100,1)
    if MDW_morning_delays_count == 0:
        MDW_morning_delay_length = 0
    else:
        MDW_morning_delay_length = round(MDW_morning_delays['ARR_DELAY_NEW'].mean())

    MDW_origin_afternoon = MDW_origin.query("TimeOfDay == 'Afternoon'")
    MDW_afternoon_count = MDW_origin_afternoon['ORIGIN'].count()
    MDW_afternoon_delays = MDW_origin_afternoon.query("ARR_DELAY_NEW > 0")
    MDW_afternoon_delays_count = MDW_afternoon_delays['ORIGIN'].count()
    MDW_afternoon_delays_percent = round(MDW_afternoon_delays_count / MDW_afternoon_count * 100,1)
    if MDW_afternoon_delays_count == 0:
        MDW_afternoon_delay_length = 0
    else:
        MDW_afternoon_delay_length = round(MDW_afternoon_delays['ARR_DELAY_NEW'].mean())



    MDW_origin_evening = MDW_origin.query("TimeOfDay == 'Evening'")
    MDW_evening_count = MDW_origin_evening['ORIGIN'].count()
    MDW_evening_delays = MDW_origin_evening.query("ARR_DELAY_NEW > 0")
    MDW_evening_delays_count = MDW_evening_delays['ORIGIN'].count()
    MDW_evening_delays_percent = round(MDW_evening_delays_count / MDW_evening_count * 100,1)
    if MDW_evening_delays_count > 0:
        MDW_evening_delay_length = round(MDW_evening_delays['ARR_DELAY_NEW'].mean())
    else:
        MDW_evening_delay_length = 0



    print(f"\n{MDW_delay_percent}% of the Midway flights were delayed")
    print(f"{MDW_morning_count} of the Midway flights were in the morning, {MDW_afternoon_count} were in the afternoon and {MDW_evening_count} were in the evening")
    print(f"Midway flights delayed were as follows:  Morning {MDW_morning_delays_percent}%, Afternoon {MDW_afternoon_delays_percent}% and Evening {MDW_evening_delays_percent}%")
    print(f"Average length of delay for delayed flights was:  Morning {MDW_morning_delay_length}, Afternoon {MDW_afternoon_delay_length}, Evening {MDW_evening_delay_length}")


if ORD_origin_count > 0 and MDW_origin_count > 0:
    if ORD_delay_percent < MDW_delay_percent:
        print(f"\nOverall, O'Hare is a better option for this route because fewer flights are delayed.")
        if ORD_morning_delays_percent < ORD_afternoon_delays_percent:
            if ORD_morning_delays_percent < ORD_evening_delays_percent:
                print(f"\nMorning is the best time to depart O'Hare on this route to minimize delays.")
            else:
                print(f"\nEvening is the best time to depart O'Hare on this route to minimize delays.")
        elif ORD_afternoon_delays_percent < ORD_evening_delays_percent:
                print(f"\nAfternoon is the best time to depart O'Hare on this route to minimize delays.")
        else:
            print(f"\nEvening is the best time to depart O'Hare on this route to minimize delays.")
    else:
        print(f"\nOverall, Midway is a better option for this route because fewer flights are delayed.")
        if MDW_morning_delays_percent < MDW_afternoon_delays_percent:
            if MDW_morning_delays_percent < MDW_evening_delays_percent:
                print(f"\nMorning is the best time to depart Midway on this route to minimize delays.")
            else:
                print(f"\nEvening is the best time to depart Midway on this route to minimize delays.")
        elif MDW_afternoon_delays_percent < MDW_evening_delays_percent:
            print(f"\nAfternoon is the best time to depart Midway on this route to minimize delays.")
        else:
            print(f"\nEvening is the best time to depart Midway on this route to minimize delays.")

if ORD_origin_count > 0 and MDW_origin_count < 1:
    if ORD_morning_delays_percent < ORD_afternoon_delays_percent:
        if ORD_morning_delays_percent < ORD_evening_delays_percent:
            print(f"\nMorning is the best time to depart O'Hare on this route to minimize delays.")
        else:
            print(f"\nEvening is the best time to depart O'Hare on this route to minimize delays.")
    elif ORD_afternoon_delays_percent < ORD_evening_delays_percent:
            print(f"\nAfternoon is the best time to depart O'Hare on this route to minimize delays.")
    else:
        print(f"\nEvening is the best time to depart O'Hare on this route to minimize delays.")

if ORD_origin_count < 1 and MDW_origin_count > 0:
    if MDW_morning_delays_percent < MDW_afternoon_delays_percent:
        if MDW_morning_delays_percent < MDW_evening_delays_percent:
            print(f"\nMorning is the best time to depart Midway on this route to minimize delays.")
        else:
            print(f"\nEvening is the best time to depart Midway on this route to minimize delays.")
    elif MDW_afternoon_delays_percent < MDW_evening_delays_percent:
        print(f"\nAfternoon is the best time to depart Midway on this route to minimize delays.")
    else:
        print(f"\nEvening is the best time to depart Midway on this route to minimize delays.")







# Statistics - I think this works now, not sure the data is meaningful
"""
without_delay = destination_flights.query("ARR_DELAY_NEW == 0").ARR_DELAY_NEW.count()
with_delay = destination_flights.query("ARR_DELAY_NEW > 0").ARR_DELAY_NEW.count()
print("\nCount of flights without delay ", without_delay)
print("\nCount of flights with delay ", with_delay)

print("\n",destination_flights['ARR_DELAY_NEW'].dtypes)
print("\n",destination_flights['ARR_DELAY_NEW'].sum())
print("\n",destination_flights['ARR_DELAY_NEW'].describe())




print("mean value: ", round(mean(destination_flights['ARR_DELAY_NEW']), 2))
print("median value: ", median(destination_flights.ARR_DELAY_NEW))
try:
    print("mode value: ", mode(destination_flights.ARR_DELAY_NEW))
except StatisticsError:
    print("** Data does not have a unique mode **")
print("sample standard deviation: ", \
      round(stdev(destination_flights.ARR_DELAY_NEW), 2))
print("population standard deviation: ", \
      round(pstdev(destination_flights.ARR_DELAY_NEW), 2))
"""
"""
# For correlation, can we only use columns that are numeric?  Here's a correlation that runs, but I'm not sure the data is meaningful

corr_delays=destination_flights[['ARR_DELAY_NEW','DAY_OF_WEEK','CRS_DEP_TIME','DEP_DELAY_NEW']]
print("\n",corr_delays.describe())
print("\n",corr_delays.columns)

# The following line prints the correlation matrix
print("\n",corr_delays.corr())
"""

"""
# Bar chart

# Change data type of pickup_community_area to integer
# trips_df = trips_df.astype({'pickup_community_area':int})

# trips_df = trips_df.set_index('pickup_community_area')
destination_flights = destination_flights.set_index('TimeOfDay')


# Create DataFrame groupby object with count of pickups by area
delay = destination_flights.groupby('TimeOfDay').count()
print(delay)

x_labels = pd.Series(delay.index.values)
y_values = pd.Series(delay['ORIGIN'].values)

# Create an array of the number of categories to use in the histogram
bars = np.array(range(len(x_labels)))

# Use xticks method to specify actual values of pickup locations
plt.xticks(bars, x_labels)

plt.bar(bars, y_values)

plt.title('Delay by Time of Day')
plt.xlabel('Time of Day')
plt.ylabel('Delays')
plt.show()

# what place and time
"""
# Heatmap

heatmap_data = destination_flights[['TimeOfDay','ORIGIN']]
delays = pd.crosstab(heatmap_data.TimeOfDay,\
     heatmap_data.ORIGIN).stack().\
     reset_index().rename(columns={0:'ARR_DELAY_NEW'})

#delays = trips_freq.query('numtrips>20')
#trips_freq = trips_freq.pivot("pickup_community_area",
#     "dropoff_community_area", "numtrips")
#trips_freq = trips_freq.replace(np.nan, 0)
#trips_freq = trips_freq.astype(int)

fig = plt.figure()

# Change colormap used to range from yellow to green to blue
ax = sns.heatmap(delays, annot = True, fmt = "d", cmap = "YlGnBu")
plt.show()



