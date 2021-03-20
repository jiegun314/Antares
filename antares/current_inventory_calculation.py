import sqlite3
import numpy as np
import draw_chart as chart
import os
import pandas as pd


class CurrentInventoryCalculation:
    oneclick_path = '//jnjcnckapdfs11.ap.jnj.com/jnjcnmpdfsroot/COMPASS/Oneclick Inventory Report/Output/'
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    update_file_path = "../data/_Update/"
    oneclick_database = db_path + 'oneclick_dps_inventory.db'
    currency_rate = 6.9233
    _sync_days = 0
    _exception_list = []

    def __int__(self):
        pass

    @property
    def sync_days(self):
        return self._sync_days

    @sync_days.setter
    def sync_days(self, sync_days_input):
        self._sync_days = sync_days_input

    @property
    def exception_list(self):
        return self._exception_list

    @exception_list.setter
    def exception_list(self, exception_list_input):
        self._exception_list = exception_list_input

    # import all dps inventory data to database
    def import_dps_oneclick_inventory(self, str_date):
        data_file_fullname = self.oneclick_path + str_date + "\\OneClick_Inventory_Projection_Report _" \
                             + str_date + ".csv"
        try:
            df = pd.read_csv(data_file_fullname, sep='|', encoding='gbk', index_col='Material')
        except FileNotFoundError:
            return -1
        # combine dps spine and synthes spine
        df.loc[df['Business_Unit'] == 'SP', 'Business_Unit'] = 'Spine'
        df.loc[df['Business_Unit'] == 'SPINE', 'Business_Unit'] = 'Spine'
        # select dps products
        df_dps = df.loc[(df['Business_Group'] == 'Orthopedics') & (df['Loc'] == "Total")]
        # map with JT local Hierarchy
        sql_cmd = 'SELECT Material, Local_Hierarchy FROM JT_Local_Hierarchy'
        _conn = sqlite3.connect(self.db_path + 'JT_Master_Data.db')
        df_local_hierarchy = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Material')
        df_dps = df_dps.join(df_local_hierarchy)
        df_dps.loc[df_dps['Local_Hierarchy'].notnull(), 'Hierarchy_5'] = df_dps['Local_Hierarchy']
        df_dps.drop(columns=['Local_Hierarchy'], inplace=True)
        df_dps.reset_index(inplace=True)
        # add date to first column
        df_dps.insert(0, 'Date', str_date)
        # export to database
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        df_dps.to_sql('oneclick_inventory', con=_conn, if_exists="append", index=False)
        print('%s was imported.' % str_date)
        return 1

    # synchronize inventory data with oneclick
    def start_synchronize(self) -> list:
        lst_folder_temp = []
        import_success_count, import_fail_count = 0, 0
        # read folder list in share folder
        try:
            for file_name in os.listdir(self.oneclick_path):
                if os.path.isdir(self.oneclick_path + file_name):
                    lst_folder_temp.append(file_name)
        except FileNotFoundError:
            return 0
        lst_folder_temp.sort()
        lst_folder_sharepoint = lst_folder_temp[0 - self._sync_days:]
        # get local data
        lst_current_database = self.get_local_inventory_date_list()
        # start to sync
        # delete outdated data
        for item in lst_current_database:
            if item not in lst_folder_sharepoint:
                self.delete_local_inventory_item(item)
                lst_current_database.remove(item)
        # import new data
        for item in lst_folder_sharepoint:
            if (item not in lst_current_database) and (item not in self._exception_list):
                import_result = self.import_dps_oneclick_inventory(item)
                if import_result == 1:
                    import_success_count += 1
                else:
                    import_fail_count += 1
        most_updated_table = self.get_local_inventory_date_list()[-1][0]
        return [import_success_count, import_fail_count, most_updated_table]

    def get_local_inventory_date_list(self) -> list:
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        c = _conn.cursor()
        c.execute('SELECT DISTINCT(Date) FROM oneclick_inventory ORDER BY Date')
        result = c.fetchall()
        date_list = [item[0] for item in result]
        return date_list

    # inventory_data: YYYYMMDD
    def delete_local_inventory_item(self, inventory_date):
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        c = _conn.cursor()
        sql_cmd = 'DELETE FROM oneclick_inventory WHERE Date = \"%s\"' % inventory_date
        c.execute(sql_cmd)
        _conn.commit()
        _conn.close()

    # check if this date exist (date format YYYYMMDD)
    def check_date_availability(self, str_date_input):
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        c.execute('SELECT count(Material) FROM oneclick_inventory WHERE Date = \"%s\"' % str_date_input)
        result = c.fetchone()[0]
        return True if result else False

    def get_newest_date(self) -> str:
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        c.execute('SELECT DISTINCT(Date) FROM oneclick_inventory ORDER BY Date DESC LIMIT 1')
        str_newest_date = c.fetchone()[0]
        return str_newest_date


if __name__ == "__main__":
    sync_test = CurrentInventoryCalculation()
    sync_test.sync_days = 90
    sync_test.exception_list = []
    sync_test.start_synchronize()
    pass
