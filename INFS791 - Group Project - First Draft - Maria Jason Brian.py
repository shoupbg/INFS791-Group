# INFS 791 - Group Project - First Draft - Maria, Jason, Brian - September 22, 2021

# This program uses historical airline flight data to help a user choose a time of day
#   day [possible add on: and day of the week] to fly to minimize flight delays

import pandas as pd
import numpy as np

# Access airport data file and create a list of valid airport codes from the flight data file
airport_data = pd.read_csv('airport_data.csv')
flight_data = pd.concat(map(pd.read_csv, ['2020DecemberIllinoisFlights.csv', '2019DecemberIllinoisFlights.csv','2018DecemberIllinoisFlights.csv', '2017DecemberIllinoisFlights.csv']))
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
    print(f"\n[Now we have a valid destination and we can start analysis]")


# Once we have a valid airport destination code, we query the data to see if there are flights between O'Hare and/or Midway and the destination

destination_flights = flight_data_filtered.query("DEST == @destination_question")
num_dest = destination_flights['DEST'].count()
ORD_origin = destination_flights.query("ORIGIN == 'ORD'")
ORD_origin_count = ORD_origin['ORIGIN'].count()
MDW_origin = destination_flights.query("ORIGIN == 'MDW'")
MDW_origin_count = MDW_origin['ORIGIN'].count()


print()
print(f"There were {num_dest} flights from Chicago to {destination_question} in December 2017, 2018, 2019 & 2020")
print()
print(f"Of those flights, {ORD_origin_count} were from O'Hare and {MDW_origin_count} were from Midway")
print()



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
