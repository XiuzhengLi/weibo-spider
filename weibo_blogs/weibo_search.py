# -*- coding: utf-8 -*-

import logging
import re
import time
import random

from lxml import html, etree
from urllib.parse import unquote

import utils.utils as utils
from user_info import UserProfileClient


WEIBO_SEARCH_URL = "https://s.weibo.com/weibo"
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
}

class WeiboSearchClient:
    def __init__(self, cookie: str) -> None:
        headers = HEADERS.copy()
        headers['cookie'] = cookie
        self.headers = headers
        self.user_info_client = UserProfileClient(cookie)

    def search(self, keyword, page_num: int=1, start_date: str='', end_date:str='', region: str='', weibo_type: int=1, contain_type: int=0):
        url = f'{WEIBO_SEARCH_URL}/q={keyword}&page={page_num}'
        url += utils.convert_weibo_type(weibo_type)
        url += utils.convert_contain_type(contain_type)
        if start_date != '' and end_date != '':
            url += f'&timescope=custom:{start_date}-0:{end_date}-0'
        if region != '':
            url += f'&region=custom:{region}:1000'
        resp = utils.make_request(url=url, headers=self.headers)
        tree = html.fromstring(resp.content)
        for weibo in self.parse_weibo(tree):
            yield weibo

    def parse_weibo(self, response):
        """解析网页中的微博信息"""
        for sel in response.xpath("//div[@class='card-wrap']"):
            info = sel.xpath(
                "div[@class='card']/div[@class='card-feed']/div[@class='content']/div[@class='info']"
            )
            if info:
                weibo = {}
                weibo['id'] = sel.xpath('@mid')[0]
                weibo['bid'] = sel.xpath(
                    './/div[@class="from"]/a[1]/@href')[0].split('/')[-1].split('?')[0]
                weibo['user_id'] = info[0].xpath(
                    'div[2]/a/@href')[0].split('?')[0].split(
                        '/')[-1]
                weibo['screen_name'] = info[0].xpath(
                    'div[2]/a/@nick-name')[0]
                txt_sel = sel.xpath('.//p[@class="txt"]')[0]
                retweet_sel = sel.xpath('.//div[@class="card-comment"]')
                retweet_txt_sel = ''
                if retweet_sel and retweet_sel[0].xpath('.//p[@class="txt"]'):
                    retweet_txt_sel = retweet_sel[0].xpath(
                        './/p[@class="txt"]')[0]
                content_full = sel.xpath(
                    './/p[@node-type="feed_list_content_full"]')
                is_long_weibo = False
                is_long_retweet = False
                if content_full:
                    if not retweet_sel:
                        txt_sel = content_full[0]
                        is_long_weibo = True
                    elif len(content_full) == 2:
                        txt_sel = content_full[0]
                        retweet_txt_sel = content_full[1]
                        is_long_weibo = True
                        is_long_retweet = True
                    elif retweet_sel[0].xpath(
                            './/p[@node-type="feed_list_content_full"]'):
                        retweet_txt_sel = retweet_sel[0].xpath(
                            './/p[@node-type="feed_list_content_full"]')[0]
                        is_long_retweet = True
                    else:
                        txt_sel = content_full[0]
                        is_long_weibo = True
                weibo['text'] = txt_sel.xpath(
                    'string(.)').replace('\u200b', '').replace(
                        '\ue627', '')
                weibo['article_url'] = self.get_article_url(txt_sel)
                weibo['location'] = self.get_location(txt_sel)
                if weibo['location']:
                    weibo['text'] = weibo['text'].replace(
                        '2' + weibo['location'], '')
                weibo['text'] = weibo['text'][2:].replace(' ', '')
                if is_long_weibo:
                    weibo['text'] = weibo['text'][:-4]
                at_users, at_user_ids = self.get_at_users(txt_sel)
                weibo['at_users'] = ','.join(at_users)
                weibo['at_user_ids'] = ','.join(at_user_ids)
                topics = self.get_topics(txt_sel)
                weibo['topics'] = ','.join(topics)
                weibo['topics_num'] = len(topics)
                reposts_count = sel.xpath(
                    './/a[@action-type="feed_list_forward"]/text()')
                reposts_count = "".join(reposts_count)
                try:
                    reposts_count = re.findall(r'\d+.*', reposts_count)
                except TypeError:
                    print(
                        "无法解析转发按钮，可能是 1) 网页布局有改动 2) cookie无效或已过期。\n"
                        "请在 https://github.com/dataabc/weibo-search 查看文档，以解决问题，"
                    )
                    raise CloseSpider()
                weibo['reposts_count'] = reposts_count[
                    0] if reposts_count else '0'
                comments_count = sel.xpath(
                    './/a[@action-type="feed_list_comment"]/text()'
                )[0]
                comments_count = re.findall(r'\d+.*', comments_count)
                weibo['comments_count'] = comments_count[
                    0] if comments_count else '0'
                attitudes_count = sel.xpath(
                    './/a[@action-type="feed_list_like"]/button/span[2]/text()')[0]
                attitudes_count = re.findall(r'\d+.*', attitudes_count)
                weibo['attitudes_count'] = attitudes_count[
                    0] if attitudes_count else '0'
                created_at = sel.xpath(
                    './/div[@class="from"]/a[1]/text()')[0].replace(' ', '').replace('\n', '').split('前')[0]
                weibo['created_at'] = utils.standardize_date(created_at)
                source = sel.xpath('.//div[@class="from"]/a[2]/text()')
                weibo['source'] = source[0] if source else ''
                pics = []
                is_exist_pic = sel.xpath(
                    './/div[@class="media media-piclist"]')
                if is_exist_pic:
                    pics = is_exist_pic[0].xpath('ul[1]/li/img/@src')
                    pics = [pic[8:] for pic in pics]
                    pics = [
                        re.sub(r'/.*?/', '/large/', pic, 1) for pic in pics
                    ]
                    pics = ['https://' + pic for pic in pics]
                video_url = ''
                is_exist_video = sel.xpath(
                    './/div[@class="thumbnail"]//video-player')
                if is_exist_video:
                    video_txt = etree.tostring(is_exist_video[0],encoding='utf-8').decode('utf-8')
                    video_url = re.findall(r'src:\'(.*?)\'', video_txt)[0]
                    video_url = video_url.replace('&amp;', '&')
                    video_url = 'http:' + video_url
                if not retweet_sel:
                    weibo['pics'] = pics
                    weibo['video_url'] = video_url
                else:
                    weibo['pics'] = []
                    weibo['video_url'] = ''
                weibo['has_pic'] = 1 if len(weibo['pics']) > 0 else 0
                weibo['has_video'] = 1 if len(weibo['video_url']) > 0 else 0
                weibo['retweet_id'] = ''
                if retweet_sel and retweet_sel[0].xpath(
                        './/div[@node-type="feed_list_forwardContent"]/a[1]'):
                    retweet = {}
                    retweet['id'] = retweet_sel[0].xpath(
                        './/a[@action-type="feed_list_like"]/@action-data'
                    )[0][4:]
                    retweet['bid'] = retweet_sel[0].xpath(
                        './/p[@class="from"]/a/@href')[0].split(
                            '/')[-1].split('?')[0]
                    info = retweet_sel[0].xpath(
                        './/div[@node-type="feed_list_forwardContent"]/a[1]'
                    )[0]
                    retweet['user_id'] = info.xpath(
                        '@href')[0].split('/')[-1]
                    retweet['screen_name'] = info.xpath(
                        '@nick-name')[0]
                    retweet['text'] = retweet_txt_sel.xpath(
                        'string(.)').replace('\u200b','').replace('\ue627', '')
                    retweet['article_url'] = self.get_article_url(
                        retweet_txt_sel)
                    retweet['location'] = self.get_location(retweet_txt_sel)
                    if retweet['location']:
                        retweet['text'] = retweet['text'].replace(
                            '2' + retweet['location'], '')
                    retweet['text'] = retweet['text'][2:].replace(' ', '')
                    if is_long_retweet:
                        retweet['text'] = retweet['text'][:-4]
                    at_users, at_user_ids = self.get_at_users(retweet_txt_sel)
                    retweet['at_users'] = ','.join(at_users)
                    retweet['at_user_ids'] = ','.join(at_user_ids)
                    topics = self.get_topics(retweet_txt_sel)
                    retweet['topics'] = ','.join(topics)
                    retweet['topics_num'] = len(topics)
                    reposts_count = retweet_sel[0].xpath(
                        './/ul[@class="act s-fr"]/li[1]/a[1]/text()'
                    )[0]
                    reposts_count = re.findall(r'\d+.*', reposts_count)
                    retweet['reposts_count'] = reposts_count[
                        0] if reposts_count else '0'
                    comments_count = retweet_sel[0].xpath(
                        './/ul[@class="act s-fr"]/li[2]/a[1]/text()'
                    )[0]
                    comments_count = re.findall(r'\d+.*', comments_count)
                    retweet['comments_count'] = comments_count[
                        0] if comments_count else '0'
                    attitudes_count = retweet_sel[0].xpath(
                        './/a[@class="woo-box-flex woo-box-alignCenter woo-box-justifyCenter"]//span[@class="woo-like-count"]/text()'
                    )[0]
                    attitudes_count = re.findall(r'\d+.*', attitudes_count)
                    retweet['attitudes_count'] = attitudes_count[
                        0] if attitudes_count else '0'
                    created_at = retweet_sel[0].xpath(
                        './/p[@class="from"]/a[1]/text()')[0].replace(' ', '').replace('\n', '').split('前')[0]
                    retweet['created_at'] = utils.standardize_date(created_at)
                    source = retweet_sel[0].xpath(
                        './/p[@class="from"]/a[2]/text()')
                    retweet['source'] = source[0] if source else ''
                    retweet['pics'] = pics
                    retweet['video_url'] = video_url
                    retweet['retweet_id'] = ''
                    yield retweet
                    weibo['retweet_id'] = retweet['id']
                yield weibo

    def get_article_url(self, selector):
        """获取微博头条文章url"""
        article_url = ''
        text = selector.xpath('string(.)').replace(
            '\u200b', '').replace('\ue627', '').replace('\n',
            '').replace(' ', '')
        if text.startswith('发布了头条文章'):
            urls = selector.xpath('.//a')
            for url in urls:
                if url.xpath(
                        'i[@class="wbicon"]/text()') == 'O':
                    if url.xpath('@href') and url.xpath(
                            '@href').startswith('http://t.cn'):
                        article_url = url.xpath('@href')
                    break
        return article_url

    def get_location(self, selector):
        """获取微博发布位置"""
        a_list = selector.xpath('.//a')
        location = ''
        for a in a_list:
            if a.xpath('./i[@class="wbicon"]') and a.xpath(
                    './i[@class="wbicon"]/text()') == '2':
                location = a.xpath('string(.)')[1:]
                break
        return location

    def get_at_users(self, selector):
        """获取微博中@的用户昵称"""
        a_list = selector.xpath('.//a')
        at_users = []
        at_user_ids = []
        for a in a_list:
            if len(unquote(a.xpath('@href')[0])) > 14 and len(
                    a.xpath('string(.)')) > 1:
                if unquote(a.xpath('@href')[0])[14:] == a.xpath(
                        'string(.)')[1:]:
                    at_user = a.xpath('string(.)')[1:]
                    if at_user not in at_users:
                        at_users.append(at_user)
                        user_info = self.user_info_client.get_info(screen_name=at_user)
                        at_user_ids.append(user_info['data']['user']['idstr'])
                        # 随机sleep1～5秒
                        time.sleep(random.randint(1,5))
        return at_users, at_user_ids

    def get_topics(self, selector):
        """获取参与的微博话题"""
        a_list = selector.xpath('.//a')
        topics = []
        for a in a_list:
            text = a.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                if text[1:-1] not in topics:
                    topics.append(text[1:-1])
        return topics

if __name__ == '__main__':
    import sys

    import fire

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
    )

    cookie = 'SINAGLOBAL=6761055116471.568.1680096400350; SCF=Au9Ep4Q_3LaiwFfetD52ihhPIbQuSk1xVe9e-yH36h4mjExqrBlruV_FdIl3g82_cFpMyaQig_SANqFyzOYgjVk.; SUB=_2A25JIIzADeRhGeNO4lIW-S_IwjmIHXVq6hSIrDV8PUJbkNANLUygkW1NTt9Rax90KjemdOUvrGryVJz0K1TF1CwP; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFZG1TMGEjxieh0wOZUKqdu5NHD95Qfeh.7S0.pSh.fWs4Dqcjci--NiK.Xi-2Ri--ciKL2i-2fi--ci-zfiKyFi--Ri-8siK.fi--Ni-2RiKyFi--fi-iWiKys; UOR=,,www.baidu.com; XSRF-TOKEN=Ze7KTr--XTT8gdjgisfS6ltt; _s_tentry=-; Apache=6296223148701.386.1684309833996; ULV=1684309834079:18:3:1:6296223148701.386.1684309833996:1683385721815; WBPSESS=sSZrHX-PcA5NmImzUNsEfF2F__f9jmCZmi0TzdVZgtrT6yDf_7CC1s4_hViuuYC7t9QKG5BaupEnQM1dyvJgHrpmEPscwaCyvkABtN62pCNdtmGdjyv7ShCdE1SoLNjt7kmEntFIEFbd6MSIUzp4Ag=='
    fire.Fire(WeiboSearchClient(cookie))
