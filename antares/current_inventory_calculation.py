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
    currency_rate = 7.0842
    _sync_days = 0
    _exception_list = []

    def __int__(self, bu_input):
        self.__class__.bu_name = bu_input


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
        conn = sqlite3.connect(current_app.config['DATABASE_JOINT_MASTER_DATA'])
        local_hierarchy_datasheet = 'JT_Local_Hierarchy'
        sql_cmd = 'SELECT Material, Local_Hierarchy FROM ' + local_hierarchy_datasheet
        df_local_hierarchy = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        df_dps = df_dps.join(df_local_hierarchy)
        df_dps.loc[df_dps['Local_Hierarchy'].notnull(), 'Hierarchy_5'] = df_dps['Local_Hierarchy']
        df_dps.drop(columns=['Local_Hierarchy'], inplace=True)
        df_dps.reset_index(inplace=True)
        # export to database
        conn = sqlite3.connect(current_app.config['DATABASE_CURRENT_INVENTORY_DPS'])
        df_dps.to_sql("INV" + str_date, con=conn, if_exists="replace", index=False)
        return 1

    # synchronize inventory data with oneclick
    def start_synchronize(self):
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
        lst_db_date = self.get_local_inventory_table_list()
        lst_current_database = [item.lstrip("INV") for item in lst_db_date]
        # start to sync
        # delete outdated data
        for item in lst_current_database:
            if item not in lst_folder_sharepoint:
                self.delete_local_inventory_table(item)
                lst_current_database.remove(item)
        # import new data
        for item in lst_folder_sharepoint:
            if (item not in lst_current_database) and (item not in self._exception_list):
                import_result = self.import_dps_oneclick_inventory(item)
                if import_result == 1:
                    import_success_count += 1
                else:
                    import_fail_count += 1
        most_updated_table = self.get_local_inventory_table_list()[-1]
        return [import_success_count, import_fail_count, most_updated_table]

    @staticmethod
    def get_local_inventory_table_list():
        conn = sqlite3.connect(current_app.config['DATABASE_CURRENT_INVENTORY_DPS'])
        c = conn.cursor()
        c.execute("select name from sqlite_master where type='table' order by name")
        table_list = [item[0] for item in c.fetchall()]
        conn.commit()
        conn.close()
        return table_list

    # inventory_data: YYYYMMDD
    @staticmethod
    def delete_local_inventory_table(inventory_date):
        table_name = 'INV' + inventory_date
        conn = sqlite3.connect(current_app.config['DATABASE_CURRENT_INVENTORY_DPS'])
        c = conn.cursor()
        sql_cmd = "DROP TABLE " + table_name
        c.execute(sql_cmd)
        conn.commit()
        conn.close()