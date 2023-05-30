import logging
import time
import random

from utils.utils import make_request, HEADERS

USER_INFO_API = 'https://weibo.com/ajax/profile/info'
USER_DETAIL_API = 'https://weibo.com/ajax/profile/detail'

# 获取用户个人基本信息
class UserProfileClient:
    def __init__(self, cookie: str='') -> None:
        headers = HEADERS.copy()
        headers['cookie'] = cookie
        self.headers = headers

    # 获取用户信息
    def get_info(self, user_id: str='', screen_name: str='') -> dict:
        params = {}
        if user_id != '':
            params['uid'] = user_id
        elif screen_name != '':
            params['screen_name'] = screen_name
        else:
            return None
        resp = make_request(url=USER_INFO_API, params=params, headers=self.headers)
        return resp.json()

    # 获取用户详细信息
    def get_detail_info(self, user_id: str) -> dict:
        params = {}
        if user_id != '':
            params['uid'] = user_id
        elif screen_name != '':
            params['screen_name'] = screen_name
        else:
            return None
        resp = make_request(url=USER_DETAIL_API, params=params, headers=self.headers)
        return resp.json()

    # 获取所有信息，包含info & detail
    def get_all_info(self, user_id: str):
        info = self.get_info(user_id)
        user_info = info['data']['user']
        # 随机sleep1～5秒
        time.sleep(random.randint(1,5))
        detail = self.get_detail_info(user_id)
        user_info.update(detail['data'])
        if not user_info.get('verified'):
            user_info['verified_reason'] = '未认证'
        return user_info

if __name__ == '__main__':
    import sys

    import fire

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
    )

    cookie = 'SINAGLOBAL=6761055116471.568.1680096400350; SCF=Au9Ep4Q_3LaiwFfetD52ihhPIbQuSk1xVe9e-yH36h4mjExqrBlruV_FdIl3g82_cFpMyaQig_SANqFyzOYgjVk.; SUB=_2A25JIIzADeRhGeNO4lIW-S_IwjmIHXVq6hSIrDV8PUJbkNANLUygkW1NTt9Rax90KjemdOUvrGryVJz0K1TF1CwP; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFZG1TMGEjxieh0wOZUKqdu5NHD95Qfeh.7S0.pSh.fWs4Dqcjci--NiK.Xi-2Ri--ciKL2i-2fi--ci-zfiKyFi--Ri-8siK.fi--Ni-2RiKyFi--fi-iWiKys; UOR=,,www.baidu.com; XSRF-TOKEN=Ze7KTr--XTT8gdjgisfS6ltt; _s_tentry=-; Apache=6296223148701.386.1684309833996; ULV=1684309834079:18:3:1:6296223148701.386.1684309833996:1683385721815; WBPSESS=sSZrHX-PcA5NmImzUNsEfF2F__f9jmCZmi0TzdVZgtrT6yDf_7CC1s4_hViuuYC7t9QKG5BaupEnQM1dyvJgHrpmEPscwaCyvkABtN62pCNdtmGdjyv7ShCdE1SoLNjt7kmEntFIEFbd6MSIUzp4Ag=='
    fire.Fire(UserProfileClient(cookie))
