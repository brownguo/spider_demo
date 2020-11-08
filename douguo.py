import json
import requests
from multiprocessing import Queue
from data_to_mongodb import mongo_info
from concurrent.futures import ThreadPoolExecutor

#搞个队列出来
queue_list = Queue()

def handle_request(url,data):
    header = {
        # "Cookie": "duid=66470293",
        "client": "4",
        "version": "6969.2",
        "device": "Mate 10 Pro",
        "sdk": "23,6.0.1",
        "channel": "zhuzhan",
        "resolution": "1664*936",
        "display-resolution": "1664*936",
        "dpi": "1.95",
        "pseudo-id": "ZX1G42CPJD",
        "brand": "HUAWEI",
        "scale": "1.95",
        "timezone": "28800",
        "language": "zh",
        "cns": "0",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; Mate 10 Pro Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36",
        # "act-code": "1604665470",
        # "act-timestamp": "1604665470",
        "uuid": "7fd8e17d-6468-4472-9a87-39b61688c735",
        "battery-level": "0.80",
        "battery-state": "2",
        "terms-accepted": "1",
        "newbie": "1",
        "reach": "1",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "session-info": "zZ9ob7xjJtQKWPylkgRuVfav6oYfr/592WIbAYZMTC7xgWiRAjFtcw8Ib3WwMK7y+e2Adbut7T5/lm+nyUTzYo/ADnEBi3LRldGjjfD/IlagOuAapBssp5efr48MDP4d",
        "Host": "api.douguo.net",
        # "Content-Length": "132",
    }

    response = requests.post(url=url,headers=header,data=data,)
    return response

#app首页
def handle_index():
    url = 'https://api.douguo.net/recipe/flatcatalogs'
    data = {
        "client": "4",
        # "_session": "1604668110839422220439897398",
        # "v": "1604661038",
        "_vs": "2305",
        # "sign_ran": "932b6b4556d4bae26528fb5b80d2c13b",
        # "code": "4737adb6ddc966da",
    }
    repsonse = handle_request(url,data)
    index_dict = json.loads(repsonse.text)

    for category_items in index_dict['result']['cs']:
        for items1 in category_items['cs']:
            for items2 in items1['cs']:
                data2 = {
                    "client": "4",
                    # "_session": "1604668110839422220439897398",
                    "keyword": items2['name'],
                    "order": "0",
                    "_vs": "400",
                    "type": "0",
                    "auto_play_mode": "2",
                    # "sign_ran": "5a673cd6548166b231e5fef876fd5a9d",
                    # "code": "fa018e2128dc3eec",
                }
                queue_list.put(data2)  #往队列里追加

#菜谱
def handle_menu(data):
    print("handle_menu:",data['keyword'])
    url = 'https://api.douguo.net/recipe/v2/search/0/20'
    response = handle_request(url=url, data=data)
    response_dict = json.loads(response.text)
    for items in response_dict['result']['list']:
        menu_info = {}
        menu_info['food_name'] = data['keyword']
        if items['type'] == 13:
            menu_info['food_id'] = items['r']['id']
            menu_info['anthor'] = items['r']['an']
            menu_info['desc'] = items['r']['cookstory']
            menu_info['img'] = items['r']['img']
            menu_info['recommendation_tag'] = items['r']['recommendation_tag']
            detail_url = 'https://api.douguo.net/recipe/v2/detail/'+str(menu_info['food_id'])
            detail_request_data = {
                "client": "4",
                # "_session": "1604668110839422220439897398",
                "author_id": "0",
                "_vs": "11104",
                "_ext": '{"query":{"kw":'+menu_info['food_name']+',"src":"11104","idx":"1","type":"13","id":'+str(menu_info['food_id'])+'}}',
                "is_new_user": "1",
                # "sign_ran": "51a0bfeec80cc25fc58a1e757bb2b3d8",
                # "code": "fe03ecee4dcb3596",
            }
            detail_response = handle_request(url=detail_url,data=detail_request_data)
            detail_response_dict = json.loads(detail_response.text)
            menu_info['tips'] = detail_response_dict['result']['recipe']['tips']
            menu_info['cookstep'] = detail_response_dict['result']['recipe']['cookstep']
            print('当前入库:',menu_info['food_name'])
            # mongo_info.insert_item(menu_info)
        else:
            continue
if __name__ == '__main__':
    handle_index()
    pool = ThreadPoolExecutor(max_workers=20)
    while queue_list.empty() != True:
        pool.submit(handle_menu,queue_list.get())
