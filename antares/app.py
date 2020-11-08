from flask import Flask, render_template, request, url_for, send_from_directory
import webbrowser
import urllib
import os
from werkzeug.utils import secure_filename
import json
import crt_inv_calculation


ALLOWED_EXTENSIONS = set(['xlsx', 'xls', 'txt', 'csv', 'XLSX'])

INDEX_URL = 'http://127.0.0.1:8888'
app = Flask(__name__)


@app.route('/')
def index_page():
    # get current inventory list for test
    calculation_module = crt_inv_calculation.CurrentInventoryCalculation('TU')
    str_newest_date = calculation_module.get_newest_date()
    [lst_total_inventory, lst_summary_data] = calculation_module.get_current_inventory(str_newest_date)
    return render_template('index.html')
    pass


if __name__ == '__main__':
    # start server
    app.run(debug=True)
