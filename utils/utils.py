# -*- coding: utf-8 -*-

import sys
import logging
import random
import requests

from datetime import datetime, timedelta
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

from utils.region import region_dict


TIMEOUT = 20
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36'
HEADERS = {
    'authority': 'weibo.com',
    'method': 'GET',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'Host':'weibo.com',
    'referer': 'https://weibo.com/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}


# 防止抓取失败，最多重试3次
@retry(
    stop=stop_after_attempt(3),
    wait=wait_random(min=30, max=60),
    retry=retry_if_exception_type(),
    before=before_log(logging.getLogger(__name__), logging.INFO),
)
def make_request(url: str, params: dict={}, headers: dict=HEADERS) -> requests.Response:
    r = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r


def convert_weibo_type(weibo_type):
    """将微博类型转换成字符串"""
    if weibo_type == 0:
        return '&typeall=1'
    elif weibo_type == 1:
        return '&scope=ori'
    elif weibo_type == 2:
        return '&xsort=hot'
    elif weibo_type == 3:
        return '&atten=1'
    elif weibo_type == 4:
        return '&vip=1'
    elif weibo_type == 5:
        return '&category=4'
    elif weibo_type == 6:
        return '&viewpoint=1'
    return '&scope=ori'


def convert_contain_type(contain_type):
    """将包含类型转换成字符串"""
    if contain_type == 0:
        return '&suball=1'
    elif contain_type == 1:
        return '&haspic=1'
    elif contain_type == 2:
        return '&hasvideo=1'
    elif contain_type == 3:
        return '&hasmusic=1'
    elif contain_type == 4:
        return '&haslink=1'
    return '&suball=1'


def get_keyword_list(file_name):
    """获取文件中的关键词列表"""
    with open(file_name, 'rb') as f:
        try:
            lines = f.read().splitlines()
            lines = [line.decode('utf-8-sig') for line in lines]
        except UnicodeDecodeError:
            print(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序', file_name)
            sys.exit()
        keyword_list = []
        for line in lines:
            if line:
                keyword_list.append(line)
    return keyword_list


def get_regions(region):
    """根据区域筛选条件返回符合要求的region"""
    new_region = {}
    if region:
        for key in region:
            if region_dict.get(key):
                new_region[key] = region_dict[key]
    if not new_region:
        new_region = region_dict
    return new_region


def standardize_date(created_at):
    """标准化微博发布时间"""
    if "刚刚" in created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    elif "秒" in created_at:
        second = created_at[:created_at.find(u"秒")]
        second = timedelta(seconds=int(second))
        created_at = (datetime.now() - second).strftime("%Y-%m-%d %H:%M")
    elif "分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime("%Y-%m-%d %H:%M")
    elif "小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime("%Y-%m-%d %H:%M")
    elif "今天" in created_at:
        today = datetime.now().strftime('%Y-%m-%d')
        created_at = today + ' ' + created_at[2:]
    elif '年' not in created_at:
        year = datetime.now().strftime("%Y")
        month = created_at[:2]
        day = created_at[3:5]
        time = created_at[6:]
        created_at = year + '-' + month + '-' + day + ' ' + time
    else:
        year = created_at[:4]
        month = created_at[5:7]
        day = created_at[8:10]
        time = created_at[11:]
        created_at = year + '-' + month + '-' + day + ' ' + time
    return created_at


def str_to_time(text):
    """将字符串转换成时间类型"""
    result = datetime.strptime(text, '%Y-%m-%d')
    return result
