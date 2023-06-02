# -*- coding: utf-8 -*-

import os
import csv
import time
import logging
import random

from datetime import datetime

import settings
import utils.utils as utils
from weibo_blogs import WeiboSearchClient
from weibo_signal import WeiboSignalClient
from sentiments_predictor import SentimentsPredictor
from user_info import UserProfileClient

class Writer:
    def __init__(self, file_path:str, headers:str=[]):
        self.headers = headers
        exists = os.path.exists(file_path)
        self.fp = open(file_path, 'a', encoding='utf-8', newline='')
        self.writer = csv.writer(self.fp)
        if not exists:
            self.writer.writerow(headers)
            self.fp.flush()

    def write(self, doc:dict, output_fields:list=[]):
        if len(output_fields) == 0:
            output_fields = self.headers
        row = [doc.get(key, '') for key in output_fields]
        self.writer.writerow(row)
        self.fp.flush()

    def write_row(self, row):
        self.writer.writerow(row)

    def close(self):
        self.fp.close()

class WeiboSpider:
    def __init__(self):
        cookie = settings.COOKIE
        self.search_client = WeiboSearchClient(cookie)
        self.signal_client = WeiboSignalClient(cookie)
        self.user_info_client = UserProfileClient(cookie)

        self.keywords = []
        self.output_path = settings.OUTPUT_PATH
        start_date = settings.START_DATE
        end_date = settings.END_DATE
        self.start_date = start_date
        self.end_date = end_date
        self.weibo_type = utils.convert_weibo_type(settings.WEIBO_TYPE) 
        self.contain_type = utils.convert_contain_type(settings.CONTAIN_TYPE)
        if '全部' in settings.REGION:
            self.regions = []
        else:
            self.regions = utils.get_regions(settings.REGION)
        # 每个keyword search 最大页数
        self.max_page_num = settings.FURTHER_THRESHOLD

        # 选择启用的功能
        self.enable_comment = settings.ENABLE_COMMENT
        self.enable_repost = settings.ENABLE_REPOST
        self.enable_attitude = settings.ENABLE_ATTITUDE

        # 自定义输出字段
        self.blog_output_fields = settings.BLOG_OUTPUT_FIELDS
        self.comment_output_fields = settings.COMMENT_OUTPUT_FIELDS
        self.repost_output_fields = settings.REPOST_OUTPUT_FIELDS
        self.attitude_output_fields = settings.ATTITUDE_OUTPUT_FIELDS
        self.comment_output4_fields = settings.COMMENT_OUTPUT4_FIELDS
        self.repost_output4_fields = settings.REPOST_OUTPUT4_FIELDS
        self.attitude_output4_fields = settings.ATTITUDE_OUTPUT4_FIELDS
        self.user_info_fields = settings.USERINFO_OUTPUT_FIELDS

    def _load_model(self):
        self.predictor = SentimentsPredictor()

    def _load_keywords(self):
        if isinstance(settings.KEYWORD_LIST, list):
            self.keywords = settings.KEYWORD_LIST
        elif os.path.exists(settings.KEYWORD_LIST):
            with open(settings.KEYWORD_LIST, 'r') as fp:
                for line in fp.readlines():
                    self.keywords.append(line.strip())
        else:
            logging.error(f'Fail to load keywords...')


    # 创建输出结果路径
    def _mkdir_output(self):
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        # output1 输出路径
        output1_path = f'{self.output_path}/output1'
        if not os.path.exists(output1_path):
            os.mkdir(output1_path)
        output1_file_path = f'{output1_path}/blogs.csv'
        self.output1_writer = Writer(
            output1_file_path, self.blog_output_fields
        )

        # output2 输出路径
        output2_path = f'{self.output_path}/output2'
        if not os.path.exists(output2_path):
            os.mkdir(output2_path)

        # output3 输出路径
        output3_path = f'{self.output_path}/output3'
        if not os.path.exists(output3_path):
            os.mkdir(output3_path)

        # output4 输出路径
        output4_path = f'{self.output_path}/output4'
        if not os.path.exists(output4_path):
            os.mkdir(output4_path)

        if self.enable_comment:
            output2_comment_file_path = f'{output2_path}/comments.csv'
            self.output2_comment_writer = Writer(
                output2_comment_file_path, self.comment_output_fields
            )
            output3_comment_file_path = f'{output3_path}/comments.csv'
            self.output3_comment_writer = Writer(
                output3_comment_file_path, self.blog_output_fields + self.comment_output_fields[1:]
            )
            output4_comment_file_path = f'{output4_path}/comments.csv'
            self.output4_comment_writer = Writer(
                output4_comment_file_path, self.blog_output_fields + self.comment_output_fields[1:] + self.comment_output4_fields
            )
        if self.enable_repost:
            output2_repost_file_path = f'{output2_path}/reposts.csv'
            self.output2_repost_writer = Writer(
                output2_repost_file_path, self.repost_output_fields
            )
            output3_repost_file_path = f'{output3_path}/reposts.csv'
            self.output3_repost_writer = Writer(
                output3_repost_file_path, self.blog_output_fields + self.repost_output_fields[1:]
            )
            output4_repost_file_path = f'{output4_path}/reposts.csv'
            self.output4_repost_writer = Writer(
                output4_repost_file_path, self.blog_output_fields + self.repost_output_fields[1:] + self.repost_output4_fields
            )
        if self.enable_attitude:
            output2_attitude_file_path = f'{output2_path}/attitudes.csv'
            self.output2_attitude_writer = Writer(
                output2_attitude_file_path, self.attitude_output_fields
            )
            output3_attitude_file_path = f'{output3_path}/attitudes.csv'
            self.output3_attitude_writer = Writer(
                output3_attitude_file_path, self.blog_output_fields + self.attitude_output_fields[1:]
            )
            output4_attitude_file_path = f'{output4_path}/attitudes.csv'
            self.output4_attitude_writer = Writer(
                output4_attitude_file_path, self.blog_output_fields + self.attitude_output_fields[1:] + self.attitude_output4_fields
            )

        # output5 输出路径
        output5_path = f'{self.output_path}/output5'
        if not os.path.exists(output5_path):
            os.mkdir(output5_path)
        output5_user_id_file_path = f'{output5_path}/user_id.csv'
        self.output5_user_id_writer = Writer(
            output5_user_id_file_path, ['user_id', 'has_offensive', 'action', 'period']
        )

    def _close_writers(self):
        self.output1_writer.close()
        if self.enable_comment:
            self.output2_comment_writer.close()
            self.output3_comment_writer.close()
            self.output4_comment_writer.close()
        if self.enable_repost:
            self.output2_repost_writer.close()
            self.output3_repost_writer.close()
            self.output4_repost_writer.close()
        if self.enable_attitude:
            self.output2_attitude_writer.close()
            self.output3_attitude_writer.close()
            self.output4_attitude_writer.close()
        self.output5_user_id_writer.close()

    def fetch_by_keyword_and_region(self, keyword: str, region: str=''):
        for page_num in range(1, self.max_page_num+1):
            logging.info(f'Start to search blogs, keyword={keyword}, region={region}, page={page_num}')
            mblogs = self.search_client.search(keyword, page_num, self.start_date, self.end_date, region, self.weibo_type, self.contain_type)
            for mblog in mblogs:
                mid = mblog['id']
                mblog['text_label'] = self.predictor.predict(mblog['text'])
                self.output5_user_id_writer.write_row([mblog['user_id'], mblog['text_label'], '发帖', utils.get_pried(mblog['created_at'])])
                self.output1_writer.write(mblog)
                if self.enable_comment:
                    try:
                        for comment in self.signal_client.get_all_comments_and_secondary_comments(mid):
                            mblog_with_comment = mblog.copy()
                            mblog_with_comment.update(comment)
                            mblog_with_comment['comment_text_label'] = self.predictor.predict(comment['comment_text'])
                            self.output5_user_id_writer.write_row(
                                [mblog_with_comment['comment_user_id'], mblog_with_comment['comment_text_label'], '评论', utils.get_pried(mblog_with_comment['comment_created_at'])])
                            mblog_with_comment['secondary_comment_text_label'] = self.predictor.predict(comment['secondary_comment_text'])
                            if len(mblog_with_comment['secondary_comment_text']) != 0:
                                self.output5_user_id_writer.write_row(
                                    [
                                        mblog_with_comment['secondary_comment_user_id'],
                                        mblog_with_comment['secondary_comment_text_label'],
                                        '评论',
                                        utils.get_pried(mblog_with_comment['secondary_comment_created_at'])
                                    ]
                                )
                            self.output2_comment_writer.write(comment)
                            self.output3_comment_writer.write(mblog_with_comment)
                            self.output4_comment_writer.write(mblog_with_comment)
                    except Exception as e:
                        logging.error(f'Fail to fetch comments, mid={mid}, err={e}')
                        time.sleep(30)
                if self.enable_repost:
                    try:
                        for repost in self.signal_client.get_all_reposts(mid):
                            mblog_with_repost = mblog.copy()
                            mblog_with_repost.update(repost)
                            mblog_with_repost['transmit_text_label'] = self.predictor.predict(repost['transmit_text'])
                            self.output5_user_id_writer.write_row(
                                [mblog_with_repost['transmit_user_id'], mblog_with_repost['transmit_text_label'], '转发', utils.get_pried(mblog_with_repost['transmit_time'])])
                            self.output2_repost_writer.write(repost)
                            self.output3_repost_writer.write(mblog_with_repost)
                            self.output4_repost_writer.write(mblog_with_repost)
                    except Exception as e:
                        logging.error(f'Fail to fetch reposts, mid={mid}, err={e}')
                        time.sleep(30)
                if self.enable_attitude:
                    try:
                        for attitude in self.signal_client.get_all_attitudes(mid):
                            mblog_with_attitude = mblog.copy()
                            mblog_with_attitude.update(attitude)
                            self.output2_attitude_writer.write(attitude)
                            self.output3_attitude_writer.write(mblog_with_attitude)
                            self.output4_attitude_writer.write(mblog_with_attitude)
                    except Exception as e:
                        logging.error(f'Fail to fetch attitudes, mid={mid}, err={e}')
                        time.sleep(30)
                # 随机sleep1～5秒
                time.sleep(random.randint(1,5))
                

    def fetch_by_keyword(self, keyword):
        if len(self.regions) == 0:
            self.fetch_by_keyword_and_region(keyword)
        else:
            for region in self.regions:
                self.fetch_by_keyword_and_region(keyword, region)

    def fetch_all_keywords(self):
        task_count = len(self.keywords)
        task_num = 1
        for keyword in self.keywords:
            logging.info(f'Start to fetch keyword={keyword}, crawling progress: {task_num} of {task_count}...')
            task_num += 1
            try:
                self.fetch_by_keyword(keyword)
                time.sleep(1)
            except Exception as e:
                logging.error(f'Fail to fetch keyword, keyword={keyword}, err={e}')
            logging.info(f'Success to fetch keyword={keyword}...')
        logging.info('Finish to fetch...')

    def _load_user_ids(self, file_path, row_num:int = 1):
        user_ids = []
        if os.path.exists(file_path):
            index = 0
            with open(file_path, 'r', encoding='utf-8', newline='') as fp:
                for line in fp.readlines():
                    if index >= row_num:
                        sp = line.strip().split(',')
                        if len(sp) < 4:
                            user_ids.append({'id': sp[0]})
                        else:
                            user_id, has_offensive, action, period = sp
                            user_ids.append({
                                'id': user_id,
                                'action': action,
                                'has_offensive': has_offensive,
                                'period': period
                            })
                    index += 1
            logging.info(f'Loaded user_ids, start_num={row_num}, total={index}')
        else:
            logging.error(f'File path not exists, path={file_path}')
        return user_ids

    # 从标准输入读入userid，并抓取用户详细信息
    def fetch_user_info(self, row_num:int = settings.ID_ROW_NUM, file_path:str = ''):
        # 连续错误达到3次认为被反爬
        max_err_num = 3
        err_num = 0
        user_id_file_path = file_path if file_path != '' else f'{self.output_path}/output5/user_id.csv'
        user_info_file_path = f'{self.output_path}/output5/user_info.csv'
        writer = Writer(user_info_file_path, self.user_info_fields)
        for user in self._load_user_ids(user_id_file_path, row_num):
            user_id = user['id']
            logging.info(f'Start to fetch user_info, user_id={user_id}')
            try:
                user_info = self.user_info_client.get_all_info(user_id)
                user.update(user_info)
                writer.write(user)
                # 随机sleep1～5秒
                time.sleep(random.randint(1,5))
                err_num = 0
            except Exception as e:
                err_num += 1
                if err_num >= max_err_num:
                    logging.error(f'连续失败3次，可能触发反爬机制，请稍后重试或更换cookie')
                    break
                logging.error(f'Fail to fetch user_info, user_id={user_id}, err={e}, row_num={row_num}')
                time.sleep(30)
            row_num += 1
                

    # 主要运行函数
    def run(self):
        # 加载关键词
        self._load_keywords()
        # 加载模型
        self._load_model()
        # 创建输出路径
        self._mkdir_output()
        self.fetch_all_keywords()
        self._close_writers()
        self.fetch_user_info()

if __name__ == '__main__':
    import sys
    import fire
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
    )

    spider = WeiboSpider()
    fire.Fire(spider)
    #spider.run()
