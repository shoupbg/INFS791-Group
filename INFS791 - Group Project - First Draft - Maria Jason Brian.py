# INFS 791 - Group Project - Maria, Jason, Brian - October 23, 2021

# This program uses historical airline flight data to help a user choose a time of day
#   day [possible add on: and day of the week] to fly to minimize flight delays

import pandas as pd
import numpy as np
from statistics import *
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Access airport data file and create a list of valid airport codes from the flight data file
airport_data = pd.read_csv('airport_data.csv')
flight_data = pd.concat(map(pd.read_csv, ['2020DecemberIllinoisFlights.csv', '2019DecemberIllinoisFlights.csv','2018DecemberIllinoisFlights.csv', '2017DecemberIllinoisFlights.csv']))

flight_data['DEP_HOUR'] = flight_data.CRS_DEP_TIME / 100
flight_data['TimeOfDay'] = np.where(flight_data['DEP_HOUR'] <= 12, 'Morning', 
                      np.where(flight_data['DEP_HOUR'] >= 17, 'Evening', 'Afternoon'))



flight_data_filtered = flight_data.query("ORIGIN == 'ORD' or ORIGIN == 'MDW'")
# Line below was original code, only using 2019 flight data.  Line above combines 4 CSV files with December data for 2020, 2019, 2018 & 2017
# flight_data = pd.read_csv('December2019Flights.csv')
airports_served = flight_data.DEST.unique()
airports_served_list = airports_served.tolist()

# NTD:  we need to remove ORD and MDW from the available_airports list

# Filter airport code list to include only airports served by Chicago airports

available_airports = airport_data.query("Code == @airports_served_list")

# Ask user to enter city name or use lookup tool

print ("\nAre you planning to travel over winter break?")
print ("\nThis program will help you choose a flight in order to minimize delays.")
# Note to Jason & Maria - we could expand the flight data to more months or all months - would give us more data to analyze


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

# Checks whether airport code entered is a valid code actually served by a Chicago airport; starts lookup loop again if needed

while destination_question.upper() not in airports_served_list:
    print("\nThat is not a valid entry")
    destination_question = input("\nPlease try again.  Please enter a three-letter airport code or type 'lookup':  ")
    if destination_question.lower() == "lookup":
        destination_question = lookup()
else:
    print(f"\n[Now we have a valid destination and we can start analysis]" +destination_question)


# Once we have a valid airport destination code, we query the data to see if there are flights between O'Hare and/or Midway and the destination

destination_flights = flight_data.query("DEST == @destination_question.upper()")
num_dest = destination_flights['DEST'].count()

# Following are calculations for total O'Hare flights
ORD_origin = destination_flights.query("ORIGIN == 'ORD'")
ORD_origin_count = ORD_origin['ORIGIN'].count()
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
ORD_morning_delay_length = round(ORD_morning_delays['ARR_DELAY_NEW'].mean())

ORD_origin_afternoon = ORD_origin.query("TimeOfDay == 'Afternoon'")
ORD_afternoon_count = ORD_origin_afternoon['ORIGIN'].count()
ORD_afternoon_delays = ORD_origin_afternoon.query("ARR_DELAY_NEW > 0")
ORD_afternoon_delays_count = ORD_afternoon_delays['ORIGIN'].count()
ORD_afternoon_delays_percent = round(ORD_afternoon_delays_count / ORD_afternoon_count * 100,1)
ORD_afternoon_delay_length = round(ORD_afternoon_delays['ARR_DELAY_NEW'].mean())


ORD_origin_evening = ORD_origin.query("TimeOfDay == 'Evening'")
ORD_evening_count = ORD_origin_evening['ORIGIN'].count()
ORD_evening_delays = ORD_origin_evening.query("ARR_DELAY_NEW > 0")
ORD_evening_delays_count = ORD_evening_delays['ORIGIN'].count()
ORD_evening_delays_percent = round(ORD_evening_delays_count / ORD_evening_count * 100,1)
ORD_evening_delay_length = round(ORD_evening_delays['ARR_DELAY_NEW'].mean())



# Following are calculations for total Midway flights
MDW_origin = destination_flights.query("ORIGIN == 'MDW'")
MDW_origin_count = MDW_origin['ORIGIN'].count()
MDW_delays = MDW_origin.query("ARR_DELAY_NEW > 0")
MDW_delays_count = MDW_delays['ORIGIN'].count()
MDW_delay_percent = round(MDW_delays_count / MDW_origin_count * 100,1)
MDW_delay_length = round(MDW_delays['ARR_DELAY_NEW'].mean())


print(f"\nThere were {num_dest} flights from Chicago to {destination_question.upper()} in December 2017, 2018, 2019 & 2020")

# Following are calculations for Midway flights by time of day
MDW_origin_morning = MDW_origin.query("TimeOfDay == 'Morning'")
MDW_morning_count = MDW_origin_morning['ORIGIN'].count()
MDW_morning_delays = MDW_origin_morning.query("ARR_DELAY_NEW > 0")
MDW_morning_delays_count = MDW_morning_delays['ORIGIN'].count()
MDW_morning_delays_percent = round(MDW_morning_delays_count / MDW_morning_count * 100,1)
MDW_morning_delay_length = round(MDW_morning_delays['ARR_DELAY_NEW'].mean())

MDW_origin_afternoon = MDW_origin.query("TimeOfDay == 'Afternoon'")
MDW_afternoon_count = MDW_origin_afternoon['ORIGIN'].count()
MDW_afternoon_delays = MDW_origin_afternoon.query("ARR_DELAY_NEW > 0")
MDW_afternoon_delays_count = MDW_afternoon_delays['ORIGIN'].count()
MDW_afternoon_delays_percent = round(MDW_afternoon_delays_count / MDW_afternoon_count * 100,1)
MDW_afternoon_delay_length = round(MDW_afternoon_delays['ARR_DELAY_NEW'].mean())

MDW_origin_evening = MDW_origin.query("TimeOfDay == 'Evening'")
MDW_evening_count = MDW_origin_evening['ORIGIN'].count()
MDW_evening_delays = MDW_origin_evening.query("ARR_DELAY_NEW > 0")
MDW_evening_delays_count = MDW_evening_delays['ORIGIN'].count()
MDW_evening_delays_percent = round(MDW_evening_delays_count / MDW_evening_count * 100,1)
MDW_evening_delay_length = round(MDW_evening_delays['ARR_DELAY_NEW'].mean())



print(f"\nThere were {num_dest} flights from Chicago to {destination_question} in December 2017, 2018, 2019 & 2020")
print(f"Of those flights, {ORD_origin_count} were from O'Hare and {MDW_origin_count} were from Midway")
print(f"\n{ORD_delay_percent}% of the O'Hare flights were delayed")
print(f"{ORD_morning_count} of the O'Hare flights were in the morning, {ORD_afternoon_count} were in the afternoon and {ORD_evening_count} were in the evening")
print(f"O'Hare flights delayed were:  Morning {ORD_morning_delays_percent}%, Afternoon {ORD_afternoon_delays_percent}% and Evening {ORD_evening_delays_percent}%")
print(f"Average length of delay for delayed flights was:  Morning {ORD_morning_delay_length}, Afternoon {ORD_afternoon_delay_length}, Evening {ORD_evening_delay_length}")
print(f"\n{MDW_delay_percent}% of the Midway flights were delayed")
print(f"{MDW_morning_count} of the Midway flights were in the morning, {MDW_afternoon_count} were in the afternoon and {MDW_evening_count} were in the evening")
print(f"Midway flights delayed were as follows:  Morning {MDW_morning_delays_percent}%, Afternoon {MDW_afternoon_delays_percent}% and Evening {MDW_evening_delays_percent}%")
print(f"Average length of delay for delayed flights was:  Morning {MDW_morning_delay_length}, Afternoon {MDW_afternoon_delay_length}, Evening {MDW_evening_delay_length}")

print(f"\nOf those flights, {ORD_origin_count} were from O'Hare and {MDW_origin_count} were from Midway")



# Possible outcomes:
# 1) There are directly from ORD only or from MDW only
#     - provide that feedback together with other statistics
# 2) There are direct flights from both ORD and MDW
#     - provide that feedback with statistics for both Chicago airports

# Statistics we could provide from the data:
# - number of flights per week
# - % of on-time (or late) flights
# - average delay (in minutes) for late flights
# - Best time of day to fly to avoid delays (morning, afternoon, evening), based on incidence of delays by time of day
# - whether to travel from ORD or MDW, if flights to that destination are available from both


#Statistics
without_delay = destination_flights.query("ARR_DELAY_NEW == 0").ARR_DELAY_NEW.count()
with_delay = destination_flights.query("ARR_DELAY_NEW > 0").ARR_DELAY_NEW.count()
print("Count of flights without delay ", without_delay)
print("Count of flights with delay ", with_delay)

print(destination_flights['ARR_DELAY_NEW'].dtypes)
print(destination_flights['ARR_DELAY_NEW'].sum())
print(destination_flights['ARR_DELAY_NEW'].describe())

#this is not working with package


print("mean value: ", round(np.nanmean(destination_flights['ARR_DELAY_NEW']), 2))
print("median value: ", np.nanmedian(destination_flights.ARR_DELAY_NEW))
try:
    print("mode value: ", stats.mode(destination_flights.ARR_DELAY_NEW)[0])
except StatisticsError:
    print("** Data does not have a unique mode **")
print("sample standard deviation: ", \
      round(np.std(destination_flights.ARR_DELAY_NEW), 2))


#if we do correlation I need variables to correlate
"""
new_trips_df=trips_df[['fare','trip_miles','trip_seconds']].copy()
print("\n",new_trips_df.describe())
print("\n",new_trips_df.columns)

# The following line prints the correlation matrix
print("\n",new_trips_df.corr())
"""

# Bar chart

# Change data type of pickup_community_area to integer
# trips_df = trips_df.astype({'pickup_community_area':int})

# trips_df = trips_df.set_index('pickup_community_area')
destination_flights = destination_flights.set_index('DEST')


# Create DataFrame groupby object with count of pickups by area
# delay = destination_flights.groupby('ORIGIN').count()
delay = destination_flights.groupby('ORIGIN').apply(lambda x:
                                                 100 * x / float(x.sum()))
print(delay)

x_labels = pd.Series(delay.index.values)
y_values = pd.Series(delay['MONTH'].values)

# Create an array of the number of categories to use in the histogram
bars = np.array(range(len(x_labels)))

# Use xticks method to specify actual values of pickup locations
plt.xticks(bars, x_labels)

plt.bar(bars, y_values)

plt.title('Delay by month')
plt.xlabel('Origin')
plt.ylabel('Frequency')
plt.show()

# what place and time

