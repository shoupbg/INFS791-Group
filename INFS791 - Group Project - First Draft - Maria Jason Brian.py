# INFS 791 - Group Project - Maria, Jason, Brian - Created October 23, 2021 - Last modified 10/31/2021

"""
This Python program uses historical airline flight data from The US Department of Transportation
(https://www.transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=FGJ) that includes all flights departing
from O’Hare or Midway in December 2017, 2018, 2019 and 2020 to suggest the user an airport, weekday and time
of day that they should flight depending on the destination to reduce the potential delay, predicting
which flights from Chicago are more likely to arrive on-time for the upcoming winter break

After asking a user for a destination airport, we would analyze actual flight data for that route for multiple
years and inform the user the best and worst times (e.g., day of the week & morning/afternoon/evening)
to fly that route to minimize the risk of delays.
"""

# import Python packages needed
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Access airport data file and create a list of valid airport codes from the flight data file
airport_data = pd.read_csv('airport_data.csv')
flight_data = pd.concat(map(pd.read_csv, ['2020DecemberIllinoisFlights.csv', '2019DecemberIllinoisFlights.csv',
                                          '2018DecemberIllinoisFlights.csv', '2017DecemberIllinoisFlights.csv']))

# Addition of TimeOfDay column depending on the time of departure column to analyse according to the
# departure's time of day (morning/afternoon/evening)
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

# Map airport codes in flight_data with descriptions in airport_data
codes = airport_data.Code.to_list()
descriptions = airport_data.Description.to_list()

codesdescriptions = dict(zip(codes, descriptions))

airport_data["Code"] = airport_data["Description"].map(codesdescriptions)

# Program starts with introduction to the user
print ("\nAre you planning to travel over winter break?")
print ("\nThis program will help you choose a flight in order to minimize delays.")
print ("\nFirst, we need to know where you're going.")

# Ask the user what is the airport code for the destination or provide help if needed (lookup)
print ("If you know the three-letter code for the airport you're flying to, enter it now.")
destination_question = input ("If you don't know the code, type 'lookup': ").upper()

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
    return destination_question.upper()

# If the input from the user is equal to lookup, call the function lookup()
if destination_question.lower() == "lookup":
    destination_question  = lookup()


# Checks whether airport code entered is a valid code actually served by a Chicago airport; starts lookup loop again if needed
while destination_question.upper() not in airports_served_list:
    print("\nThat is not a valid entry")
    destination_question = input("\nPlease try again.  Please enter a three-letter airport code or type 'lookup':  ")
    if destination_question.lower() == "lookup":
        destination_question = lookup()
else:
    destination_question = destination_question.upper()


# Once we have a valid airport destination code, we query the data to see if there are flights between O'Hare
# and/or Midway and the destination

destination_flights = flight_data_filtered.query("DEST == @destination_question.upper()")
num_dest = destination_flights['DEST'].count()

print(f"\nWe counted {num_dest} flights from Chicago to {codesdescriptions[destination_question]}")

# Dictionary to print O'Hare or Midway instead of ORD or MDW
ChicagoAirports = {
    "MDW" : "Midway",
    "ORD" : "O'Hare"
    }

# Data frame Total count of flights by origin
count_by_origin = destination_flights.groupby('ORIGIN').agg({'ARR_DELAY_NEW': 'count'})
group_delay_origin = destination_flights.query("ARR_DELAY_NEW > 0").groupby('ORIGIN')
count_delay_by_origin = group_delay_origin.agg({'ARR_DELAY_NEW': 'count'})
total_and_delay = count_by_origin.join(count_delay_by_origin, how = 'left', lsuffix = '_total', rsuffix = '_delay')

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

# Report count of flights from both origins
for index, row in count_by_origin.iterrows():
    if len(count_by_origin) > 1:
        print(f"{row['ARR_DELAY_NEW']} of those flights were from {ChicagoAirports[index]}")
    elif len(count_by_origin) == 0:
        print(f"\nNo airport go to {destination_question}.")
    else:
        print(f"All flights of those flights were from {ChicagoAirports[index]} to {codesdescriptions[destination_question]}.")
print()

#STATISTICS
# Report percentage of delays and mean of the airport with the min delay
i = 0
min_percent = 0
min_airport = ""
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
    print(f"{delay_percent}% of the {ChicagoAirports[index]} flights were delayed")
else:
    mean = group_delay_origin.agg({'ARR_DELAY_NEW': 'mean'})
    print(f"Overall, {ChicagoAirports[min_airport]} is a better option for this route because fewer flights are delayed.")
    print(f"Average delay for delayed flights from {ChicagoAirports[min_airport]} to {codesdescriptions[destination_question]} is {round(mean['ARR_DELAY_NEW'][min_airport],1)} minutes")

# Report percentage of delays and mean of the airport and time of day with the min delay
i = 0
min_percent = 0
min_time = ""
print('\n{:<10s}{:<12s}{:<12s}{:<12s}'.format("Airport", "Time", "Flights", "Delays (%)"))
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
        print('{:<10s}{:<12s}{:<12s}{:<12s}'.format(str(ChicagoAirports[index[0]]), str(index[1]), str(row['ARR_DELAY_NEW_total']), str(time_delay)))

else:
    mean = group_delay_time.agg({'ARR_DELAY_NEW': 'mean'})
    print(f"{min_time} is the best time to depart {ChicagoAirports[min_airport]} on this route to minimize delays.")
    print(f"Average delay for delayed flights from {ChicagoAirports[min_airport]} to {codesdescriptions[destination_question]} in the {min_time} is {round(mean['ARR_DELAY_NEW'][min_airport][min_time],1)} minutes")

# Report percentage of delays and mean of the airport and day of the week with the min delay
i = 0
min_percent = 0
min_day = ""
week_day = {1:"Monday", 2:"Tuesday", 3:"Wednesday", 4:"Thursday", 5:"Friday", 6:"Saturday", 7:"Sunday"}
print('\n{:<10s}{:<12s}{:<12s}{:<12s}'.format("Airport", "Day", "Flights", "Delays (%)"))
for index, data in total_and_delay_by_day.iterrows():
    for colname, row in data.to_frame().transpose().iterrows():
        day_delay = round(row['ARR_DELAY_NEW_delay'] / row['ARR_DELAY_NEW_total'] * 100, 1)
        if index[0] == min_airport:
            if i == 0:
                min_percent = day_delay
                min_day = index[1]
                i += 1
            else:
                if day_delay < min_percent:
                    min_percent = day_delay
                    min_day = index[1]
        print('{:<10s}{:<12s}{:<12s}{:<12s}'.format(str(ChicagoAirports[index[0]]), week_day[index[1]], str(row['ARR_DELAY_NEW_total']), str(day_delay)))
else:
    mean = group_delay_day.agg({'ARR_DELAY_NEW': 'mean'})
    print(f"{week_day[min_day]} is the best day to depart {ChicagoAirports[min_airport]} on this route to minimize delays.")
    print(f"Average delay for delayed flights from {ChicagoAirports[min_airport]} to {codesdescriptions[destination_question]} on {week_day[min_day]}s is {round(mean['ARR_DELAY_NEW'][min_airport][min_day],1)} minutes")

#DATA VISUALIZATION

print("\n----------------------------------------------------")
continue_answer = input("Do you want to see further visual comparison between the two airports? (y/n)").lower()
while continue_answer not in ('y', 'n'):
    print("\nSorry, not valid a answer. Try again.")
    continue_answer = input("Do you want to see further visual comparison between the two airports? (y/n)").lower()


if continue_answer == 'y':

    # Bar chart

    s = "MDW|ORD".split("|")
    df = group_delay_day.agg({'ARR_DELAY_NEW': 'mean'})
    index_graph = np.arange(7)
    bar_width = 0
    fig, ax = plt.subplots()
    for index in reversed(df['ARR_DELAY_NEW'].index.get_level_values('ORIGIN').unique()):
        ax.bar(index_graph + bar_width, df['ARR_DELAY_NEW'][index], 0.35,
               label=ChicagoAirports[index])
        bar_width = 0.35

    ax.set_xlabel('Weekday')
    ax.set_ylabel('Mean Delay')
    ax.set_title('Delay by weekday and airport')
    ax.set_xticks(index_graph + bar_width / 2)
    ax.set_xticklabels(["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"])
    ax.legend()

    plt.show()


    # Heatmap

    heatmap = destination_flights[['TimeOfDay', 'ORIGIN']]

    # Create frequency table using crosstabs function
    delays_freq = pd.crosstab(destination_flights.TimeOfDay, \
                              destination_flights.ORIGIN)

    fig = plt.figure()

    # Create heatmap from frequency table (in DataFrame)
    ax = sns.heatmap(delays_freq)

    plt.show()


print("\n----------------------------------------------------")
continue_answer = input("Do you want to see further visual comparison between delays and time of departure? (y/n)").lower()
while continue_answer not in ('y', 'n'):
    print("\nSorry, not valid a answer. Try again.")
    continue_answer = input("Do you want to see further visual comparison between delays and time of departure? (y/n)").lower()

if continue_answer == 'y':
    # Scatterplot of all ORD/MDW departures with ARR_DELAY_NEW > 0 based on departure time and length of delay
    # Result -> there are notably more long delays for flights that depart later in the day
    all_delayed_flights = flight_data_filtered[['CRS_DEP_TIME', 'ARR_DELAY_NEW']].query('ARR_DELAY_NEW > 15')

    # Create series for each of the two columns to use in scatterplot
    dep_time_series = all_delayed_flights.CRS_DEP_TIME
    delay_series = all_delayed_flights.ARR_DELAY_NEW

    fig = plt.figure()

    # Specify market and line style (here, none) to use
    plt.plot(dep_time_series, delay_series, marker=".", linestyle="none")
    plt.title('Length of Delay by Time of Departure (when delay > 15 min.)')
    plt.xlabel('Time of Departure')
    plt.ylabel('Length of Delay (minutes)')

    plt.show()

    # Report overall mean delay per origin
    total_delay = flight_data_filtered.query("ARR_DELAY_NEW > 0").groupby('ORIGIN')
    print("\nMean delay in minutes by airport:")
    print(round(total_delay.agg({'ARR_DELAY_NEW': 'mean'}).reset_index()\
        .rename(columns={'ARR_DELAY_NEW': 'DELAY MEAN'}),1))


print("\n----------------------------------------------------")

# MACHINE LEARNING PREDICTIONS

flight_data.fillna(0,inplace=True)

arrive_y = flight_data["ARR_DEL15"] 
arrive_x = flight_data[["CANCELLED", "DAY_OF_WEEK", "ARR_DELAY"]]  

x_train, x_test, y_train, y_test = train_test_split(arrive_x, arrive_y,
                                    test_size=0.25, random_state = 30)
y_train = np.ravel(y_train)

# used the SAGA machine learning solver with LogisticRegression to predict flight delays
classifier = LogisticRegression(solver='lbfgs', max_iter=10000).fit(x_train, y_train) 

print("\nTraining score of model: ")
print(round(classifier.score(x_train, y_train), 3), "\n")

print("Testing score of model: ")
print(round(classifier.score(x_test, y_test), 3), "\n")

big_delay = classifier.predict(x_test)

print("Predictions based on test data: ")
print(big_delay)
print("Number predicted to be a big delay: ", sum(big_delay))

print(classification_report(y_test, big_delay))



