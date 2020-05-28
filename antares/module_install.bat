@echo off
::等号中间没有空格
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
set moudle=numpy scipy matplotlib pandas seaborn tabulate wxPython xlrd xlswriter openpyxl notebook pyecharts
echo 1/3 The following modules would be installed
for %%j in (%moudle%) do echo %%j
echo 2/3 Start to install
for %%i in (%moudle%) do pip install %%i
echo 3/3 List all installed module
pip list
pause