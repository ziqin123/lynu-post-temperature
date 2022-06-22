import os
import requests
import json
import sys
import time
import random

KEY1 = "RPEBZ-J2ZWW-2CIRC-OO3Q2-HH7X2-7GBEJ"  # 请求粗略地点的key
KEY2 = "YIOBZ-J6ZKD-V7G4A-HGJS2-66XOJ-S4F6G"  # 请求精准地点的key


def get_json(js: dict, s: str):
    i = 0
    li = s.split("/")
    while i < len(li):
        js = js.get(li[i])
        if js is None:
            return ""
        # elif not isinstance(js, dict):  # 这段代码保证了在获取到的内容不是字典时可以返回当前层
        #     return js
        else:
            i += 1
    return js


def str_data_to_num(str_data):
    # 格式时间成毫秒
    str_time = time.strptime(str_data, "%Y-%m-%d %H:%M:%S")  # 将时间格式化
    mk_time = int(time.mktime(str_time)*1000)
    return mk_time


def whether_token(account):
    with open("data.json", mode="r") as f:
        js = f.read()
        j = json.loads(js)  # 读出一个字典文件
        ts = j[0].get(account)
        if ts:
            t = ts.get("token_expiration_datetime")
            st = str_data_to_num(t)
            nt = time.time()*1000
            if nt < st:  # 是否大于本地时间
                token = ts.get("token")
                return token
            else:
                return False
        else:
            return False


def requests_token(account, password):
    data = {
        "username": account,
        "password": password,
        "type": ""
    }
    resp = requests.post("https://apii.lynu.edu.cn/v1/accounts/login/", json=data)
    d = resp.json()
    token = d.get("token")
    resp.close()
    if token:
        with open("data.json", mode="r") as f:
            jss = f.read()  # json字符串
            dic = json.loads(jss)  # 格式化后为字典
        with open("data.json", mode="w") as f:
            dic[0][account] = d
            dics = json.dumps(dic)  # 将字典转换为json string
            f.write(dics)
        return token
    else:
        print("账号或密码输入错误")
        return False


def get_token(account):
    if os.path.exists('data.json'):  # 判断是否有文件，如果没有就创建
        pass
    else:
        with open("data.json", mode="w") as f:
            f.write("[{},{}]")  # 创建一个基础层，第0个位置为账号，第1个位置为地点信息

    # 是否有保存token
    token = whether_token(account)
    if token:
        return token
    else:
        password = input("输入密码")
        token = requests_token(account, password)
        return token


def set_sig(lat, lng, sig):
    with open("data.json", mode="r") as f:
        s_data = f.read()
        json_data = json.loads(s_data)
        json_data[1][f"{lat},{lng}"] = sig

    with open("data.json", mode="w") as f:
        s_data = json.dumps(json_data)
        f.write(s_data)


def get_sig(lat, lng):
    if os.path.exists('data.json'):  # 判断是否有文件，如果没有就创建
        pass
    else:
        with open("data.json", mode="w") as f:
            f.write("[{},{}]")  # 创建一个基础层，第0个位置为账号，第1个位置为地点信息

    with open("data.json", mode="r") as f:  # 获取sig
        data = f.read()
        j = json.loads(data)
        sigs = j[1]
        sig = sigs.get(f"{lat},{lng}")
        if sig is None:
            res = input("没有内置数字签名信息，是否设置(y/n)")
            if res == "y" or res == "Y":
                sig = input("输入你当前位置的数字签名(sig)")
                set_sig(lat, lng, sig)
                return sig
            else:
                sys.exit("没有设置数字签名")
        else:
            return sig


def position():  # 获取所在位置
    data1 = {  # 第一个请求的data数据为定值
        "key": KEY1,
        "sig": "7817334a06d1ddb3bac9137847e65b6b"  # sig 可以不填，这里为当前key的sig
    }
    resp1 = requests.get("https://apis.map.qq.com/ws/location/v1/ip", params=data1)
    lat = resp1.json()["result"]["location"]["lat"]
    lng = resp1.json()["result"]["location"]["lng"]
    resp1.close()

    sig = get_sig(lat, lng)
    data2 = {
        "coord_type": "5",
        "get_poi": "0",
        "output": "json",
        "key": KEY2,
        "location": f"{lat},{lng}",
        "sig": sig  # 这里的sig需要抓包获取
    }
    resp2 = requests.get("https://apis.map.qq.com/ws/geocoder/v1/", params=data2)
    resp2.close()

    if resp2.json()['status'] == 111:
        res = input("设置的数字签名(sig)有误,是否重新设置(y/n)")
        if res == "y" or res == "Y":
            sig = input("输入你当前位置的数字签名(sig)")
            set_sig(lat, lng, sig)
            position()
        else:
            sys.exit("没有重新设置数字签名")

    elif resp2.json()['status'] == 0:
        return resp2.json()


def report_data():  # 健康状况登记的数据
    data = {}
    print("健康状况登记代码还没实现，自己去手机上登记")

    return data


def temperature_data():  # 体温打卡的数据
    rest = position()

    data = {
        "code_color": "A",
        "condition": "A",
        "home_condition": "A",
        "high_risk_status": "A",
        "vaccine_status": "F",
        "value": str(36+random.randint(1, 9)*0.1),  # 生成一个随机的体温
        "location": {
            "status": get_json(rest, "status"),
            "lat": get_json(rest, "result/location/lat"),
            "lng": get_json(rest, "result/location/lng"),
            "nation": get_json(rest, "result/ad_info/nation"),
            "nation_code": get_json(rest, "result/ad_info/nation_code"),
            "address": get_json(rest, "result/address"),
            "famous": get_json(rest, "result/address_reference/famous_area/title"),
            "recommend": get_json(rest, "result/formatted_addresses/recommend"),
            "district_code": get_json(rest, "result/ad_info/adcode"),
            "district_name": get_json(rest, "result/ad_info/district"),
            "district_lat": get_json(rest, "result/ad_info/location/lat"),
            "district_lng": get_json(rest, "result/ad_info/location/lng"),
            "town_code": get_json(rest, "result/address_reference/town/id"),
            "town_name": get_json(rest, "result/address_reference/town/title"),
            "town_lat": get_json(rest, "result/address_reference/town/location/lat"),
            "town_lng": get_json(rest, "result/address_reference/town/location/lng"),
        }
    }

    return data


def main(account):
    account = str(account)  # 保证输入的账号是一个字符串
    token = get_token(account)

    headers = {"Authorization": "JWT "+token}
    resp = requests.get("https://apii.lynu.edu.cn/v1/temperatures/allowed/", headers=headers)  # 获取能否打卡
    resp.close()

    if resp.text == "true" or resp.text == "True":
        data = temperature_data()
        # requests.post(url="https://apii.lynu.edu.cn/v1/temperatures/", headers=headers, json=data)

    elif resp.text == "false" or resp.text == "False":
        r_data = report_data()
        data = temperature_data()
        # requests.post(url="https://apii.lynu.edu.cn/v1/wuhan-reports/", headers=headers, json=r_data)
        # requests.post(url="https://apii.lynu.edu.cn/v1/temperatures/", headers=headers, json=data)

    else:
        print("打卡失败")


if __name__ == '__main__':
    Acc = input("输入账号")
    main(Acc)
