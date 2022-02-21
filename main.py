# https://www.coin-or.org/download/binary/CoinAll/CoinAll-1.6.0-win64-intel11.1.zip
import pandas as pd
from pulp import *


# load data from the csv file into Pandas
def load_data(file):
    df = pd.read_csv(file)
    return(df)

def cal_score(df):
    scores = []
    minimum_order = []
    maximum_order = []
    score = 0
    minimum = 0
    maximum = 0
    # growth rate of 30% will become 1.33 for better calculation
    sales_growth_rate = (SALES_GROWTH_RATE / 100) + 1
    for index, row in df.iterrows():
        score = df.at[index, 'profit'] / df.at[index, 'volume']
        sales_prediction = df.at[index,'sold_last_year'] * sales_growth_rate
        left_in_stock = df.at[index,'amount_availble']
        # PROPER_INVENTORY = True -> means that I verify that I will not import only profitable items, to keep the diversity of inventory.
        minimum = round(df.at[index,'sold_last_year'] / 20)
        # if the item sold out last year now i will oreder 1.5 times more,
        maximum = round(sales_prediction * 1.5 if left_in_stock == 0 else sales_prediction - left_in_stock)
        # verify minimum and maximum greater then 0
        minimum = max(0, minimum)
        maximum = max(0, maximum, minimum)
        scores.append(score)
        minimum_order.append(minimum)
        maximum_order.append(maximum)
    df["score"] = scores
    df["minimum_order"] = minimum_order
    df["maximum_order"] = maximum_order


IS_INTEGER = False
MAX_CAPACITY_CBM = {"20": 33, "40": 66}
# increase of sales rate in %, compare to last year
SALES_GROWTH_RATE = 6

if __name__ == '__main__':

    # load data
    df = load_data("opti-db.csv")

    # adding score to the table
    cal_score(df)
    print(df.to_string())

    # Model:
    prob = LpProblem("sd", LpMaximize)

    # create for each item a variable:
    # every item needs to be above score
    ids = df["id"].tolist()
    var_id = ids.copy()
    minimum_order = df["minimum_order"].tolist()
    maximum_order = df["maximum_order"].tolist()

    i = 0
    for id in ids:
        if IS_INTEGER:
            var_id[i] = LpVariable(id, lowBound=minimum_order[i], upBound=maximum_order[i] ,cat="Integer")
        else:
            var_id[i] = LpVariable(id, lowBound=minimum_order[i], upBound=maximum_order[i])
        i += 1

    # max problem
    profit = df["profit"]
    i = 0
    var_profit = []
    for var in var_id:
        var_profit.append(var * profit[i])
        i += 1
    prob += sum(var_profit)

    #the sum needs to be under the max capactiy of the container
    volume_list = df["volume"]
    i = 0
    var_valume = []
    for var in var_id:
        var_valume.append(var * volume_list[i])
        i += 1
    prob += sum(var_valume) <= MAX_CAPACITY_CBM["20"]


    # TODO check what options we have
    status = prob.solve(PULP_CBC_CMD(msg=0, options=['dualSimplex']))
    print(LpStatus[status])
    for var in var_id:
        print(var, " = ", value(var))
    print("max profit is " ,value(prob.objective))


