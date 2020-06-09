import sqlite3
import time
import json
from tabulate import tabulate
import pandas as pd

db_path = "../data/_DB/"


# check if this code is in the master data
def check_code_availability(bu_name, code_name):
    db_fullname = db_path + "Master_Data.db"
    conn = sqlite3.connect(db_fullname)
    sql_cmd = "SELECT count(Material) from MATERIAL_MASTER WHERE Material = \'" + code_name + \
              "\' AND Business_Unit = \'" + bu_name + "\'"
    c = conn.cursor()
    c.execute(sql_cmd)
    trigger = False if c.fetchall()[0][0] == 0 else True
    return trigger


# get current month
def get_current_month():
    return time.strftime("%Y-%m", time.localtime())


# check if right future month item
def check_future_month(month_item, month_quantity):
    current_year = int(time.strftime("%Y", time.localtime()))
    current_month = int(time.strftime("%m", time.localtime()))
    forecast_month_list = []
    for i in range(0, month_quantity):
        t = (current_year, current_month + i, 17, 17, 3, 38, 1, 48, 0)
        secs = time.mktime(t)
        time_1 = time.strftime("%Y%m", time.localtime(secs))
        forecast_month_list.append(time_1)
    return True if month_item in forecast_month_list else False


# Add Index column to a 2 dimension table
def add_table_index(lst_data, lst_index):
    lst_length = len(lst_data)
    for i in range(lst_length):
        lst_data[i].insert(0, lst_index[i])
    return lst_data


# generate exception list for multi-function
def get_exception_list(bu_name, calculation_type):
    exception_list = []
    if calculation_type == "Aging_Backorder":
        if bu_name == "TU":
            exception_list = ["INV20200330", "INV20200331"]
        elif bu_name == "PT":
            exception_list = ["INV20200327", "INV20200330", "INV20200331", "INV20200401"]
        elif bu_name == "CMF":
            exception_list = ["INV20200325", "INV20200326", "INV20200327", "INV20200330", "INV20200331", "INV20200401",
                              "INV20200402"]
        else:
            pass
    else:
        pass
    return exception_list


def get_available_h5_name(h5_name, bu_name):
    h5_output = get_available_h5_list(h5_name, bu_name)
    # 如果返回是空结果
    if len(h5_output) == 0:
        print("No related H5 name, please check.")
        h5_result = "NULL"
    # 如果返回是单值
    elif len(h5_output) == 1:
        h5_result = h5_output[0]
    # 如果有多个返回值
    else:
        print("More than 1 similar output as below：")
        item = iter(h5_output)
        for i in range(1, len(h5_output) + 1):
            print(i, " - ", next(item))
        index_no = input("Plz input the NO of H5 you need：")
        if index_no.isnumeric() and int(index_no) <= len(h5_output):
            h5_result = h5_output[int(index_no) - 1]
        else:
            print("Wrong No, Please re-input！")
            h5_result = "NULL"
    return h5_result


def get_available_h5_list(h5_name, bu_name):
    db_fullname = db_path + "Master_Data.db"
    conn = sqlite3.connect(db_fullname)
    c = conn.cursor()
    str_cmd = "SELECT distinct Hierarchy_5 COLLATE NOCASE from MATERIAL_MASTER WHERE Hierarchy_5 LIKE \'%" + \
              h5_name + "%\' AND Business_Unit = \'" + bu_name + "\' COLLATE NOCASE ORDER BY Hierarchy_5"
    c.execute(str_cmd)
    result = c.fetchall()
    h5_output = [item[0] for item in result]
    conn.close()
    return h5_output


def get_full_h5_list(bu_name):
    db_fullname = db_path + bu_name + '_Master_Data.db'
    table_name = bu_name + '_Master_Data'
    conn = sqlite3.connect(db_fullname)
    c = conn.cursor()
    str_cmd = 'SELECT DISTINCT Hierarchy_5 COLLATE NOCASE from ' + table_name
    c.execute(str_cmd)
    result = c.fetchall()
    conn.close()
    return [item[0] for item in result]


# read the command list from json file
def display_command_list(command_type):
    # read json file
    file_fullname = db_path + "command_list.json"
    try:
        with open(file_fullname, "r", encoding='utf8') as f:
            command_list_file = json.load(f)
    except FileNotFoundError:
        print("!Error, file missing. Please check if the data file is in the data folder.")
        return
    command_list = command_list_file[command_type].items()
    print("====<Commands List>====")
    print(tabulate(command_list, tablefmt="psql", headers="firstrow", colalign=("left", "left")))


# input MI data to database, data format [[YYYYMM, Qty],]
def upload_mi_data(code_name, bu_name, lst_data):
    # remove duplicate value
    lst_month = []
    lst_qty = []
    for mi_item in lst_data:
        temp_month = mi_item[0][0:4] + "-" + mi_item[0][4:]
        temp_qty = mi_item[1]
        # if no duplicate
        if temp_month not in lst_month:
            lst_month.append(temp_month)
            lst_qty.append(temp_qty)
        # if yes, overwrite
        else:
            lst_qty[lst_month.index(temp_month)] = temp_qty
    # get h5 and sap price
    db_fullname = db_path + bu_name + "_Master_Data.db"
    filename = bu_name + "_Master_Data"
    conn = sqlite3.connect(db_fullname)
    sql_cmd = "SELECT Hierarchy_5, SAP_Price from " + filename + " WHERE Material = \'" + code_name + "\'"
    c = conn.cursor()
    c.execute(sql_cmd)
    h5, sap_price = c.fetchall()[0]
    # generate input list
    j = 0
    final_list = []
    while j < len(lst_qty):
        final_list.append([code_name, h5, lst_month[j], lst_qty[j], lst_qty[j] * sap_price])
        j += 1
    conn.commit()
    conn.close()
    # upload to database
    db_fullname = db_path + bu_name + "_MI.db"
    filename = bu_name + "_MI_" + time.strftime("%Y%m", time.localtime())
    conn = sqlite3.connect(db_fullname)
    c = conn.cursor()
    # judge if the mi file for this month exist or not
    sql_cmd = "SELECT count(*) FROM sqlite_master WHERE type=\"table\" AND name = \"" + filename + "\""
    c.execute(sql_cmd)
    table_exit_result = c.fetchall()[0][0]
    # if no such table
    if table_exit_result == 0:
        sql_cmd = '''CREATE TABLE ''' + filename + '''
                        (Material TEXT NOT NULL,
                        Hierarchy_5 TEXT NOT NULL,
                        Month TEXT NOT NULL,
                        Quantity INTEGER NOT NULL,
                        Value_SAP_Price REAL NOT NULL
                        )'''
        c.execute(sql_cmd)
        conn.commit()
    c.executemany("INSERT INTO " + filename + " VALUES(?, ?, ?, ?, ?)", final_list)
    conn.commit()
    conn.close()


# show ascii graph
def display_ascii_graph(title):
    file_fullname = db_path + "graph_" + title + ".txt"
    f = open(file_fullname, encoding='utf8')
    line = f.readline()
    while line:
        print(line,end="")
        line = f.readline()
    pass


if __name__ == '__main__':
    print(get_full_h5_list('SPINE'))
    pass
