import sqlite3
import time

db_path = "../data/_DB/"


# check if this code is in the master data
def check_code_availability(bu_name, code_name):
    db_fullname = db_path + bu_name + "_Master_Data.db"
    filename = bu_name + "_Master_Data"
    conn = sqlite3.connect(db_fullname)
    sql_cmd = "SELECT count(Material) from " + filename + " WHERE Material = \'" + code_name + "\'"
    c = conn.cursor()
    c.execute(sql_cmd)
    trigger = False if c.fetchall()[0][0] == 0 else True
    return trigger


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
    # upload to database
    db_fullname = db_path + bu_name + "_MI.db"
    filename = bu_name + "_MI_" + time.strftime("%Y%m", time.localtime())
    conn = sqlite3.connect(db_fullname)
    c = conn.cursor()
    c.executemany("INSERT INTO " + filename + " VALUES(?, ?, ?, ?, ?)", final_list)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # upload_mi_data("440.834", "TU", [["201909", 100], ["202001", -15], ["202002", 35], ["201909", 40]])
    pass
