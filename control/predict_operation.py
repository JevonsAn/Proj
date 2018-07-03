import numpy as np
from scipy import log
from scipy.optimize import curve_fit
from database.sqlquery import get_one_year_user_number, get_many_year_user_number
from control.gas_index_opeartion import get_weather_in_times_from_database, get_user_gasIndex_year_and_month


def logfit(x, y, p):
    def func(x, a, b):
        y = a * log(x) + b
        return y

    popt, pcov = curve_fit(func, x, y)

    yhat = func(p, popt[0], popt[1])  # or [p(z) for z in x]

    return yhat


def polyfit(x, y, degree=2):
    coeffs = np.polyfit(x, y, degree)
    return coeffs


def polyval(co, params):
    return np.polyval(co, params)


def grey_predict(X, Ys, P):
    def Identification_Algorithm(x):  # 辨识算法
        B = np.array([[1] * 2] * (len(x) - 1))
        tmp = np.cumsum(x)
        for i in range(len(x) - 1):
            B[i][0] = (tmp[i] + tmp[i + 1]) * (-1.0) / 2
        Y = np.transpose(x[1:])
        BT = np.transpose(B)
        a = np.linalg.inv(np.dot(BT, B))
        a = np.dot(a, BT)
        a = np.dot(a, Y)
        a = np.transpose(a)
        return a

    def GM_Model(X0, a, tmp):  # GM(1,1)模型
        # print(X0, a, tmp)
        A = np.ones(len(tmp))
        for i in range(len(A)):
            A[i] = a[1] / a[0] + (X0[0] - a[1] / a[0]) * np.exp(a[0] * (tmp[i] - 1) * (-1))
            if A[i] == np.NAN or A[i] == np.nan or np.isnan(A[i]):
                A[i] = X0[0]
                # print(A[i])

        return A

    # real_x = X
    # tmp = np.array([X[i] - X[0] + 1 for i in range(len(X))])
    data = np.array(Ys)
    X0 = data

    # X1 = np.cumsum(X0)

    a = Identification_Algorithm(data)

    t_P = [P[0] - X[0]] + [P[i] - X[0] + 1 for i in range(len(P))]
    XK = GM_Model(X0, a, t_P)
    results = [XK[i] - XK[i - 1] for i in range(1, len(XK))]
    return results
    # print(P)
    # # print(XK)
    # print(results)


def double_smooth(alpha, x, y, p):
    def exponential_smoothing(alpha, s):
        '''
        一次指数平滑
        :param alpha:  平滑系数
        :param s:      数据序列， list
        :return:       返回一次指数平滑模型参数， list
        '''
        s_temp = [0 for i in range(len(s))]
        s_temp[0] = (s[0] + s[1] + s[2]) / 3
        for i in range(1, len(s)):
            s_temp[i] = alpha * s[i] + (1 - alpha) * s_temp[i - 1]
        return s_temp

    def compute_single(alpha, s):
        '''
        一次指数平滑
        :param alpha:  平滑系数
        :param s:      数据序列， list
        :return:       返回一次指数平滑模型参数， list
        '''
        return exponential_smoothing(alpha, s)

    def compute_double(alpha, s):
        '''
        二次指数平滑
        :param alpha:  平滑系数
        :param s:      数据序列， list
        :return:       返回二次指数平滑模型参数a, b， list
        '''
        s_single = compute_single(alpha, s)
        s_double = compute_single(alpha, s_single)

        a_double = [0 for i in range(len(s))]
        b_double = [0 for i in range(len(s))]

        for i in range(len(s)):
            a_double[i] = 2 * s_single[i] - s_double[i]  # 计算二次指数平滑的a
            b_double[i] = (alpha / (1 - alpha)) * (s_single[i] - s_double[i])  # 计算二次指数平滑的b

        return a_double, b_double

    a, b = compute_double(alpha, y)
    results = []
    for t in p:
        s = t - x[-1]
        results.append(a[-1] + b[-1] * s)
    return results


def human_predict_userNum(user_id, start_year, stop_year, high, mid, low):
    res = [True, ""]
    last_num = get_one_year_user_number(user_id, start_year - 1)
    if last_num == 0:
        res[0] = False
        res[1] = "预测开始年份的上一年数据缺失"
    else:
        high_dict = [int(last_num * (1 + high) ** (y - start_year)) for y in range(start_year, stop_year + 1)]
        mid_dict = [int(last_num * (1 + mid) ** (y - start_year)) for y in range(start_year, stop_year + 1)]
        low_dict = [int(last_num * (1 + low) ** (y - start_year)) for y in range(start_year, stop_year + 1)]
        res[1] = (high_dict, mid_dict, low_dict)
    return res


def model_predict_userNum(user_id, start_year, stop_year, model_type):
    res = [True, ""]
    year_numbers = get_many_year_user_number(user_id, start_year - 1)
    if not year_numbers:
        res[0] = False
        res[1] = "没有预测开始年份之前的数据"
    else:
        predict_years = list(range(start_year, stop_year + 1))
        last_years = sorted(year_numbers.keys())
        numbers = [year_numbers[x] for x in last_years]
        predict_results = []
        if model_type == 0:  # 线性拟合
            cofes = polyfit(last_years, numbers, 1)
            predict_results = polyval(cofes, predict_years)
        elif model_type == 1:  # 二次多项式拟合
            cofes = polyfit(last_years, numbers)
            predict_results = polyval(cofes, predict_years)
        elif model_type == 2:  # 对数拟合
            predict_results = logfit(last_years, numbers, predict_years)
        elif model_type == 3:  # 灰色模型
            if len(last_years) <= 2:
                res[0] = False
                res[1] = "数据不足，灰色模型至少需要有之前三年的数据。"
                return res
            predict_results = grey_predict(last_years, numbers, predict_years)

        res[1] = [int(x) for x in predict_results]
    return res


def model_predict_gasIndex(user_id, start_year, start_month, stop_year, stop_month, timeType, model_type, param):
    res = [True, ""]
    if timeType == "年":
        year_numbers = get_user_gasIndex_year_and_month(user_id, "年", "2000", "%4d" % (start_year - 1))
        if not year_numbers:
            res[0] = False
            res[1] = "没有预测开始年份之前的数据"
        else:
            predict_years = list(range(start_year, stop_year + 1))
            last_years = [int(x[0]) for x in year_numbers]
            numbers = [float(x[1]) for x in year_numbers]
            predict_results = []
            if model_type == 0:  # 指数平滑
                alpha = float(param)
                # print((alpha, last_years, numbers, predict_years))
                if len(last_years) <= 2:
                    res[0] = False
                    res[1] = "数据不足，二次指数平滑模型至少需要有之前三年的数据。"
                    return res
                predict_results = list(zip(predict_years, double_smooth(alpha, last_years, numbers, predict_years)))
            elif model_type == 2:  # 二次多项式回归
                # weather_list = get_weather_in_times_from_database(timeType, start_year, start_month, 0, stop_year, stop_month, 0)
                cofes = polyfit(last_years, numbers, 1)
                predict_results = list(zip(predict_years, polyval(cofes, predict_years)))

            elif model_type == 1:  # 灰色模型
                if len(last_years) <= 2:
                    res[0] = False
                    res[1] = "数据不足，灰色模型至少需要有之前三年的数据。"
                    return res
                predict_results = list(zip(predict_years, grey_predict(last_years, numbers, predict_years)))

            res[1] = predict_results
        return res
    elif timeType == "月":
        year_numbers = get_user_gasIndex_year_and_month(user_id, "月", "200000", "%4d12" % (start_year - 1))
        weather_list = []
        if not year_numbers:
            res[0] = False
            res[1] = "没有预测开始年份之前的数据"
        else:
            predict_months = [(start_year, m) for m in range(start_month, 13)] \
                             + [(x, m) for x in range(start_year + 1, stop_year) for m in range(1, 13)] \
                             + [(stop_year, m) for m in range(1, stop_month + 1)]
            predict_results = []
            if model_type == 2:  # 二次多项式回归 用温度
                weather_list = get_weather_in_times_from_database("月", start_year, start_month, 0, stop_year,
                                                                  stop_month, 0)
                weather_dict = {x[0].replace("/", "-"): x[3] for x in weather_list if len(x) >= 3}
                last_weather = []
                last_numbers = []
                for t in year_numbers:
                    if t[0] in weather_dict:
                        last_weather.append(weather_dict[t[0]])
                        last_numbers.append(t[1])
                cofes = polyfit(last_weather, last_numbers)
                temprature = float(param)
                r = polyval(cofes, [temprature])
                predict_results.append(["%4d-%d" % (start_year, stop_month), "%.4f" % r[0]])

            elif model_type == 0 or model_type == 1:
                for m in predict_months:
                    this_month = m[1]
                    last_months = []
                    numbers = []
                    for t in year_numbers:
                        if int(t[0].split("-")[-1]) == this_month:
                            last_months.append(int(t[0].split("-")[0]))
                            numbers.append(t[1])

                    if model_type == 0:  # 指数平滑
                        alpha = float(param)
                        if len(last_months) <= 2:
                            res[0] = False
                            res[1] = "数据不足，指数平滑预测至少需要有之前三年的数据。"
                            return res
                        r = double_smooth(alpha, last_months, numbers, [m[0]])
                        predict_results.append(["%4d-%d" % m, "%.4f" % r[0]])
                    elif model_type == 1:  # 灰色模型
                        if len(last_months) <= 2:
                            res[0] = False
                            res[1] = "数据不足，灰色模型至少需要有之前三年的数据。"
                            return res
                        r = grey_predict(last_months, numbers, [m[0]])
                        predict_results.append(["%4d-%d" % m, "%.4f" % r[0]])

            res[1] = predict_results
        return res
