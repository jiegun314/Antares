# Project Antares

该项目用于DPS产品的基本数据存储和分析，用于常规的数据查询，预测计算以及预测调整。

## 文件结构

### antares

   所有代码源文件

### data

   1. _Charter

      所有利用echarts模块生成的图片保存在该文件夹下

   2. _DB

      所有文件数据库，文件名称格式BU名称+下划线+数据库种类

   3. _Output

      生成Stantistical FCST以及SNOP文件保存位置

   4. _Source_Data

      数据原始导入文件，excel格式

   5. _Update

      每月更新文件，excel格式
      
## 命令集合
### 主界面
#### 111 - 命令查询

#### 3XX - Hierarchy _5 层级运算

##### 销量查询

| 311     | 312          | 313     | 314              |
| ------- | ------------ | ------- | ---------------- |
| 查询GTS | 查询LP Sales | 查询IMS | 查询所有销售记录 |

##### 库存查询

| 321      | 322      | 324      |
| -------- | -------- | -------- |
| 强生库存 | 平台库存 | 所有库存 |

##### 综合查询

| 300          | 300g                   |
| ------------ | ---------------------- |
| 综合信息查询 | 综合销量库存量图形显示 |

#### 4XX - 单个代码信息汇总

##### 销售查询

| 411     | 412          | 413     |
| ------- | ------------ | ------- |
| 查询GTS | 查询LP Sales | 查询IMS |

##### 库存查询

| 412          | 422      | 424      |
| ------------ | -------- | -------- |
| 强生库存查询 | 平台库存 | 所有库存 |

##### Forecast查询

| 427                             |      |
| ------------------------------- | ---- |
| 未来24个月的Statistical Forcast |      |

##### ESO查询

| 450     |
| ------- |
| ESO查询 |

##### 汇总查询

| 400                  | 400g                     |
| -------------------- | ------------------------ |
| 单个代码所有信息汇总 | 单个代码销量库存信息汇总 |

#### 888 - 生成Statistical Forecast

#### 999 - 设置MI

| code                                               | h5              | submit                               | reset      | bpdp                     | exit       |
| -------------------------------------------------- | --------------- | ------------------------------------ | ---------- | ------------------------ | ---------- |
| 进入单个代码的调整，可以在code后加空格直接输入代码 | 进入by H5的调整 | 提交当前调整，将MI合并到FInal FCST中 | 清空所有MI | 查看当前整个BU的bpdp情况 | 退出MI模式 |

Note：单代码调整的连续输入格式 YYYYMM:数量，分号分隔可以连续输入，确认输入键入save，自动保存在MI数据库

#### 90X - 数据更新

| 900  | 901     | 902         | 903     | 905         | 906        | 909        | 900     |
| ------- | ----------- | ------- | ----------- | ---------- | ---------- | ---------- | ---------- |
| 更新BU层级Master Data | 更新GTS | 更新LPSales | 更新IMS | 更新JNJ INV | 更新LP INV | 更新ESO     | 更新Master Data |

Note：

1. 除了JNJ INV之外，所有的更新文件均放置在Data/_Update目录下，文件命名 [BU_Name]__InfomationType
2. JNJ INV可以选择当前从Oneclick已经导入的数据中的任意一天自动导入

#### 000 - Oneclick Pro

| inv                                      | bo                                                 | pending                     | check                           | trend                      | bu_trend                                        |
| ---------------------------------------- | -------------------------------------------------- | --------------------------- | ------------------------------- | -------------------------- | ----------------------------------------------- |
| 查询当前最新一天库存情况，by Hierarchy_5 | 查询当前back order情况                             | 查询pending库存的趋势       | 查询单个代码的基本库存，GIT情况 | 查询单个代码的基本库存趋势 | 查询某个H5的库存趋势，输入all查询整个bu库存趋势 |
| **h5_detail**                            | **inv_export**                                     | **bo_export**               | **sync**                        | **cmd**                    | **exit**                                        |
| 查询某个Hierarchy_5的库存情况            | 导出某天的库存数据（仅包含有库存或者有缺货订单的） | 给NED提供现有的缺货信息汇总 | 与L盘同步，获取最新的库存信息   | 查询命令清单               | 退回到Dragon主界面                              |

#####  退出命令 ：exit