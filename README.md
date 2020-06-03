# Project Antares

该项目用于DPS产品的基本数据存储和分析，用于常规的数据查询，预测计算以及预测调整。

## 支持文件安装

### 环境要求

本系统基于Python3.8开发，在Windows10以及Linux 5.5, 5.6 内核(Manjaro)环境下测试通过

### 组件要求及安装

Python安装要求：Python 3.8

组件要求：numpy, scipy, pandas, pyecharts, tabulate, wxpython, xlrd, xlsxwriter, openpyxl，windows环境下可以直接点击module_install.bat安装

## 文件结构

### /antares

   所有代码源文件

### /data

   1. /_Charter

      所有利用echarts模块生成的图片保存在该文件夹下

   2. /_DB

      所有文件数据库，文件名称格式BU名称+下划线+数据库种类

   3. /_Output

      生成Statistical FCST以及SNOP文件保存位置

   4. /_Backorder
   
      导出的缺货文件，发给平台用
   
   5. /_INV_Export
   
      导出的库存文件，发给平台用

   4. /_Source_Data

      数据原始导入文件，excel格式

   5. /_Update

      每月更新文件，excel格式
      
## 命令集合
### 主界面
#### 111 - 命令查询

#### 3XX - Hierarchy _5 层级信息查询

| 命令代码 | 命令内容               |
| -------- | ---------------------- |
| 300      | 综合信息查询           |
| 300g     | 综合销量库存量图形显示 |
| 310      | 查询所有销售记录       |
| 320      | 库存查询               |

Note: 输入all显示整个BU信息

#### 4XX - 单个代码信息查询

| 命令代码 | 命令内容                 |
| -------- | ------------------------ |
| 400      | 单个代码所有信息汇总     |
| 400g     | 单个代码销量库存信息汇总 |
| 410      | 查询代码层级销量         |
| 420      | 查询代码层级库存         |
| 450      | ESO查询                  |

#### 777 - 导出SNOP所需Excel文件

Note：导出会生成2个Excel文件，一个文件包含单个Code的所有内容，另一个包括H5层级关键信息汇总和月度数据汇总

#### 888 - 生成Statistical Forecast

Note：在生成Statistical Forecast时可以选择IMS和LP Sales作为源数据，选择IMS会选择之前36个月数据，选择LP Sales会选择之前24个月数据。

#### 999 - 设置MI

| 命令代码 | 命令内容                                           |
| -------- | -------------------------------------------------- |
| code     | 进入单个代码的调整，可以在code后加空格直接输入代码 |
| h5       | 进入by H5的调整                                    |
| submit   | 提交当前调整，将MI合并到FInal FCST中               |
| reset    | 清空所有MI                                         |
| bpdp     | 查看当前整个BU的bpdp情况                           |
| ext      | 退出MI模式                                         |

Note：单代码调整的连续输入格式 YYYYMM:数量，分号分隔可以连续输入，确认输入键入save，自动保存在MI数据库

#### 9XX - 数据更新

| 命令代码 | 命令内容              |
| -------- | --------------------- |
| 901      | 更新GTS               |
| 902      | 更新LPSales           |
| 903      | 更新IMS               |
| 905      | 更新JNJ INV           |
| 906      | 更新LP INV            |
| 908      | 更新Final Forecast    |
| 909      | 更新ESO               |
| 911      | 更新BU层级master data |
| 915      | 刷新BU_Master_Data    |
| 919      | 更新全局master data   |

**Note：**

1. 除了JNJ INV之外，所有的更新文件均放置在Data/_Update目录下，文件命名 [BU_Name]__InfomationType
2. JNJ INV可以选择当前从Oneclick已经导入的数据中的任意一天自动导入

#### 000 - Oneclick Pro

| 命令代码   | 命令内容                                           |
| ---------- | -------------------------------------------------- |
| inv        | 查询当前最新一天库存情况，by Hierarchy_5           |
| bo         | 查询当前back order情况                             |
| pending    | 查询pending库存的趋势                              |
| check      | 查询单个代码的基本库存，GIT情况                    |
| trend      | 查询单个代码的基本库存趋势                         |
| h5_trend   | 查询某个H5的库存趋势，输入all查询整个bu库存趋势    |
| h5_detail  | 查询某个Hierarchy_5的库存情况                      |
| inv_export | 导出某天的库存数据（仅包含有库存或者有缺货订单的） |
| bo_export  | 给NED提供现有的缺货信息汇总                        |
| sync       | 与L盘同步，获取最新的库存信息                      |
| bo_trend   | 缺货金额趋势图                                     |
| inv_alert  | 显示所有库存低于1个月的AB类产品（仅限Trauma）      |
| exit       | 退回到Dragon主界面                                 |
| help       | 显示所有命令符                                     |

#### 开启GUI图形界面

运行gui_main.py或者点击运行startGUI.bat（windows系统）

####  Dragon系统退出命令 ：exit