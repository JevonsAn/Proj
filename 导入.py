from database.sqlquery import insert_weather, insert_user, insert_user_data
import xlrd
import datetime

# data = xlrd.open_workbook('C:\\Users\\JevonsAn\\Desktop\\测试数据\\天气温度08-16.xls')
# table = data.sheets()[0]
# nrows = table.nrows
# for i in range(1, nrows):
#     row = table.row_values(i)
#     year = int(row[0])
#     month = int(row[1])
#     day = int(row[2])
#     mx = row[3]
#     mn = row[4]
#     avg = row[5]
#     try:
#         insert_weather(datetime.date(year, month, day), mx, mn, avg)
#     except Exception as e:
#         print(datetime.date(year, month, day), mx, mn, avg, e)

# insert_user("居民", "小时", "万立方米", "人")  12
# insert_user("采暖", "用户", "万立方米", "万m2面积") 13
# insert_user("电厂", "郑常庄", "立方米", "kw*h")14
# insert_user("电厂", "751", "立方米", "kw*h")15
# insert_user("电厂", "太阳宫", "立方米", "kw*h")16

# data = xlrd.open_workbook('C:\\Users\\JevonsAn\\Desktop\\测试数据\\采暖日用气量08-16.xlsx')
# table = data.sheets()[0]
# nrows = table.nrows
# for i in range(1, nrows):
#     row = table.row_values(i)
#     # print(row)
#     year = int(row[1])
#     month = int(row[2])
#     day = int(row[3])
#     gas = float(row[-2])
#     userNum = int(row[-1])
#     # print(13, gas, userNum, year, month, day, 0)
#     insert_user_data(13, gas, userNum, year, month, day, 0)


data = xlrd.open_workbook('C:\\Users\\JevonsAn\\Desktop\\测试数据\\2014.1.1居民小时用气量.xlsx')
table = data.sheets()[0]
nrows = table.nrows
for i in range(1, nrows):
    row = table.row_values(i)
    # print(row)
    year = int(row[1])
    month = int(row[2])
    day = int(row[3])
    hour = int(row[4].split("~")[-1])
    gas = float(row[-1])
    userNum = 1
    # print(12, gas, userNum, year, month, day, hour)
    insert_user_data(12, gas, userNum, year, month, day, hour)

# data = xlrd.open_workbook('C:\\Users\\JevonsAn\\Desktop\\测试数据\\电厂日用气量13-16.xlsx')
# table = data.sheets()[0]
# nrows = table.nrows
# n = 0
# for i in range(1, nrows):
#     row = table.row_values(i)
#     # print(row)
#     year = int(row[1])
#     month = int(row[2])
#     day = int(row[3])

#     gas0 = float(row[4])
#     userNum0 = int(row[5])
#     gas1 = float(row[6])
#     userNum1 = int(row[7])
#     gas2 = float(row[8])
#     userNum2 = int(row[9])
#     # print(14, gas0, userNum0, year, month, day, 0, gas1, userNum1, gas2, userNum2)
#     n += 1
#     insert_user_data(14, gas0, userNum0, year, month, day, 0)
#     insert_user_data(15, gas1, userNum1, year, month, day, 0)
#     insert_user_data(16, gas2, userNum2, year, month, day, 0)
# print(n)
