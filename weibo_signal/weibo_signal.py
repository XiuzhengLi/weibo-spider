# -*- coding: utf-8 -*-

import re
import time
import logging
import random

from datetime import datetime
from utils.utils import make_request, USER_AGENT, standardize_date
from user_info import UserProfileClient

BLOG_ATTITUDES_API = 'https://m.weibo.cn/api/attitudes/show'
BLOG_COMMENTS_API = 'https://m.weibo.cn/comments/hotflow'
BLOG_SECONDARY_COMMENTS_API = 'https://m.weibo.cn/comments/hotFlowChild'
BLOG_REPOSTS_API = 'https://m.weibo.cn/api/statuses/repostTimeline'

REGEX = re.compile(r'^转发微博$|//@.*')

# 获取用户个人基本信息
class WeiboSignalClient:
    def __init__(self, cookie: str='') -> None:
        self.headers = {
            'User-Agent': USER_AGENT,
            'Cookie': cookie
        }
        self.user_info_client = UserProfileClient(cookie)

    # 获取点赞信息
    def get_attitudes(self, blog_id: str, page: int=1) -> dict:
        params = {
            'id': blog_id,
            'page': page
        }
        resp = make_request(url=BLOG_ATTITUDES_API, params=params, headers=self.headers)
        return resp.json()

    # 获取所有点赞信息
    def get_all_attitudes(self, blog_id: str) -> list:
        page_num = 1
        res = self.get_attitudes(blog_id, page_num)
        while res['ok'] == 1:
            data_list = res['data']['data']
            for data in data_list:
                attitude = {
                    'mid': blog_id,
                    'attitude_id': data['id'],
                    'attitude_user_id': data['user']['id'],
                    'attitude_user_screen_name': data['user']['screen_name'],
                    'attitude_create_at': standardize_date(data['created_at'])
                }
                yield attitude
            logging.info(f'Finish fetch attitudes, id={blog_id}, page={page_num}')
            page_num += 1
            # 随机sleep3～7秒
            time.sleep(random.randint(3,7))
            res = self.get_attitudes(blog_id, page_num)

    # 获取评论信息
    def get_comments(self, blog_id: str, max_id: int=0, max_id_type: int=0) -> dict:
        params = {
            'id': blog_id,
            'mid': blog_id,
            'max_id': max_id,
            'max_id_type': max_id_type
        }
        resp = make_request(url=BLOG_COMMENTS_API, params=params, headers=self.headers)
        return resp.json()

    # 获取评论信息
    def get_secondary_comments(self, comment_id: str, max_id: int=0, max_id_type: int=0) -> dict:
        params = {
            'cid': comment_id,
            'max_id': max_id,
            'max_id_type': max_id_type
        }
        resp = make_request(url=BLOG_SECONDARY_COMMENTS_API, params=params, headers=self.headers)
        return resp.json()

    # 获取所有评论信息
    def get_all_comments(self, blog_id: str) -> list:
        page_num = 1
        res = self.get_comments(blog_id)
        while 'data' in res:
            data_list = res['data']['data']
            for data in data_list:
                created_at_date = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                created_at = created_at_date.strftime('%Y-%m-%d %H:%M')
                text = data['text']
                pic_urls = re.findall(r'src=(.*?) ', text)
                has_pic = 1 if len(pic_urls) > 0 else 0
                alts = ''.join(re.findall(r'alt="?(.*?)"? ', text))
                # sub替换掉标签内容
                # 需要替换的内容，替换之后的内容，替换对象
                text = re.sub('<span.*?</span>', alts, text)
                comment = {
                    'mid': blog_id,
                    'comment_id': data['mid'],
                    'comment_user_id': data['user']['id'],
                    'comment_user_screen_name': data['user']['screen_name'],
                    'comment_text': text,
                    'comment_created_at': created_at,
                    'comment_has_pic': has_pic,
                    'has_secondary_comments': 1 if data['total_number'] > 0 else 0,
                    'secondary_comments_num': data['total_number']
                }
                yield comment
            logging.info(f'Finish fetch comments, id={blog_id}, page={page_num}')
            page_num += 1
            # 提取翻页的max_id
            max_id = res['data']['max_id']
            if max_id == 0:
                break
            # 提取翻页的max_id_type
            max_id_type = res['data']['max_id_type']
            # 随机sleep3～7秒
            time.sleep(random.randint(3,7))
            res = self.get_comments(blog_id, max_id, max_id_type)

    # 获取所有二级评论信息
    def get_all_secondary_comments(self, comment_id: str) -> list:
        page_num = 1
        res = self.get_secondary_comments(comment_id)
        while 'data' in res:
            data_list = res['data']
            for data in data_list:
                created_at_date = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                created_at = created_at_date.strftime('%Y-%m-%d %H:%M')
                text = data['text']
                pic_urls = re.findall(r'src=(.*?) ', text)
                has_pic = 1 if len(pic_urls) > 0 else 0
                alts = ''.join(re.findall(r'alt="?(.*?)"? ', text))
                at_text = ''.join(re.findall(r'@[^<]*', text))
                # sub替换掉标签内容
                # 需要替换的内容，替换之后的内容，替换对象
                text = re.sub('<span.*?</span>', alts, text)
                # 删掉a标签
                text = re.sub('<a.*?</a>', at_text, text)
                comment = {
                    'comment_id': comment_id,
                    'secondary_comment_id': data['mid'],
                    'secondary_comment_user_id': data['user']['id'],
                    'secondary_comment_user_screen_name': data['user']['screen_name'],
                    'secondary_comment_text': text,
                    'secondary_comment_created_at': created_at,
                    'secondary_comment_has_pic': has_pic
                }
                yield comment
            logging.info(f'Finish fetch secondary comments, id={comment_id}, page={page_num}')
            page_num += 1
            # 提取翻页的max_id
            max_id = res['max_id']
            if max_id == 0:
                break
            # 提取翻页的max_id_type
            max_id_type = res['max_id_type']
            # 随机sleep3～7秒
            time.sleep(random.randint(3,7))
            res = self.get_secondary_comments(comment_id, max_id, max_id_type)

    # 获取所有评论和二级评论
    def get_all_comments_and_secondary_comments(self, blog_id: str) -> list:
        for comment in self.get_all_comments(blog_id):
            if comment['has_secondary_comments']:
                for secondary_comment in self.get_all_secondary_comments(comment['comment_id']):
                    new_comment = comment.copy()
                    new_comment.update(secondary_comment)
                    yield new_comment
            else:
                comment['secondary_comment_id'] = ''
                comment['secondary_comment_user_id'] = ''
                comment['secondary_comment_user_screen_name'] = ''
                comment['secondary_comment_text'] = ''
                comment['secondary_comment_created_at'] = ''
                comment['secondary_comment_has_pic'] = ''
                yield comment
                    
        
    # 获取转发信息
    def get_reposts(self, blog_id: str, page: int=1) -> dict:
        params = {
            'id': blog_id,
            'page': page
        }
        resp = make_request(url=BLOG_REPOSTS_API, params=params, headers=self.headers)
        return resp.json()

    # 获取所有转发信息
    def get_all_reposts(self, blog_id: str) -> list:
        page_num = 1
        res = self.get_reposts(blog_id, page_num)
        while res['ok'] == 1:
            data_list = res['data']['data']
            for data in data_list:
                created_at_date = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                created_at = created_at_date.strftime('%Y-%m-%d %H:%M')
                text = data['text']
                at_users = []
                at_user_ids = []
                for r in re.findall(r"href='/n/[^']*", text):
                    at_user_screen_name = r[9:]
                    if at_user_screen_name not in at_users:
                        at_users.append(at_user_screen_name)
                        user_info = self.user_info_client.get_info(screen_name=at_user_screen_name)
                        at_user_ids.append(user_info['data']['user']['idstr'])
                        # 随机sleep1～5秒
                        time.sleep(random.randint(1,5))
                raw_text = data['raw_text']
                is_secondary_transmit = 1 if raw_text.find('//@') != -1 else 0
                raw_text = REGEX.sub('', raw_text)
                repost = {
                    'mid': blog_id,
                    'transmit_id': data['id'],
                    'transmit_user_id': data['user']['id'],
                    'transmit_user_screen_name': data['user']['screen_name'],
                    'transmit_text': raw_text,
                    'is_secondary_transmit': is_secondary_transmit,
                    'transmit_time': created_at,
                    'transmit_at_users': ','.join(at_users),
                    'transmit_at_user_ids': ','.join(at_user_ids),
                    'transmit_at_user_num': len(at_users)
                }
                yield repost
            logging.info(f'Finish fetch reposts, id={blog_id}, page={page_num}')
            page_num += 1
            # 随机sleep3～7秒
            time.sleep(random.randint(3,7))
            res = self.get_reposts(blog_id, page_num)
        

if __name__ == '__main__':
    import sys

    import fire

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
    )

    cookie = 'SCF=Au9Ep4Q_3LaiwFfetD52ihhPIbQuSk1xVe9e-yH36h4mOT0fsMcmdphzFLnvHs-pUftjkrcSF737PiGWw3K_-oc.; SUB=_2A25JIIzBDeRhGeNO4lIW-S_IwjmIHXVq6hSJrDV6PUJbktAGLWblkW1NTt9RazVXQFEd29XvnghuArB-YGNOUZGZ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFZG1TMGEjxieh0wOZUKqdu5NHD95Qfeh.7S0.pSh.fWs4Dqcjci--NiK.Xi-2Ri--ciKL2i-2fi--ci-zfiKyFi--Ri-8siK.fi--Ni-2RiKyFi--fi-iWiKys; _T_WM=83172227019; WEIBOCN_FROM=1110006030; MLOGIN=1; XSRF-TOKEN=82b6a8; mweibo_short_token=a3266e0e5c; M_WEIBOCN_PARAMS=luicode=20000174&uicode=20000174'
    fire.Fire(WeiboSignalClient(cookie=cookie))
