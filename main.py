# https://www.coin-or.org/download/binary/CoinAll/CoinAll-1.6.0-win64-intel11.1.zip
import pandas as pd
from pulp import *


# load data from the csv file into Pandas
def load_data(file):
    df = pd.read_csv(file)
    return(df)

#TODO
def cal_score(df):
    df["score"] = 0.5
    df["minimum_order"] = 3
    df["maximum_order"] = 100


if __name__ == '__main__':
    IS_INTEGER = True
    MAX_CAPACITY_CBM = {"20": 33, "40": 66}


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
    status = prob.solve(PULP_CBC_CMD(msg=0, options=['dualSimplex'] ))
    print(LpStatus[status])
    for var in var_id:
        print(var, " = ", value(var))
    print("max profit is " ,value(prob.objective))


