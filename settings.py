# -*- coding: utf-8 -*-

# Cookie
# COOKIE = 'SUB=_2A25JIIhODeRhGeNO4lIW-S_IwjmIHXVq6igGrDV8PUJbkNAGLUj1kW1NTt9Ra39sVyO4QrW8Irdo8Dnm67M-gl5-; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFZG1TMGEjxieh0wOZUKqdu5NHD95Qfeh.7S0.pSh.fWs4Dqcj7i--Xi-z4iKnfi--NiKnRi-zpi--4iKLFiKnfi--fi-88iKL2i--fi-88iKL29Jfu; SINAGLOBAL=8122259686949.669.1680352590191; WBPSESS=sSZrHX-PcA5NmImzUNsEfF2F__f9jmCZmi0TzdVZgtrT6yDf_7CC1s4_hViuuYC7hURGiSTwaihc_OLrEiZ4yh3PYkhSdQELZtDsyZrKUIaR5Ghwfkx3pfqqAA8S_Lkll29MILgeFJKW7BmFS_Og_A==; _s_tentry=www.baidu.com; UOR=,,www.baidu.com; Apache=9426940487874.254.1682263779899; ULV=1682263779907:4:4:1:9426940487874.254.1682263779899:1681824598621; webim_unReadCount={"time":1682263790932,"dm_pub_total":3,"chat_group_client":0,"chat_group_notice":0,"allcountNum":7,"msgbox":0}; XSRF-TOKEN=m_mIpaQgmE0nILwdsHQnJS2Y'
COOKIE = 'SCF=Au9Ep4Q_3LaiwFfetD52ihhPIbQuSk1xVe9e-yH36h4mOT0fsMcmdphzFLnvHs-pUftjkrcSF737PiGWw3K_-oc.; SUB=_2A25JIIzBDeRhGeNO4lIW-S_IwjmIHXVq6hSJrDV6PUJbktAGLWblkW1NTt9RazVXQFEd29XvnghuArB-YGNOUZGZ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFZG1TMGEjxieh0wOZUKqdu5NHD95Qfeh.7S0.pSh.fWs4Dqcjci--NiK.Xi-2Ri--ciKL2i-2fi--ci-zfiKyFi--Ri-8siK.fi--Ni-2RiKyFi--fi-iWiKys; _T_WM=83172227019; WEIBOCN_FROM=1110006030; MLOGIN=1; XSRF-TOKEN=82b6a8; mweibo_short_token=a3266e0e5c; M_WEIBOCN_PARAMS=luicode=20000174&uicode=20000174'

# 要搜索的关键词列表，可写多个, 值可以是由关键词或话题组成的列表，也可以是包含关键词的txt文件路径，
# 如'keyword_list.txt'，txt文件中每个关键词占一行
KEYWORD_LIST = ['#普通人的一生应该是怎样的#']
# KEYWORD_LIST = 'keyword_list.txt'

# 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
WEIBO_TYPE = 1

# 筛选结果微博中必需包含的内容，0代表不筛选，获取全部微博，1代表搜索包含图片的微博，2代表包含视频的微博，3代表包含音乐的微博，4代表包含短链接的微博
CONTAIN_TYPE = 0

# 筛选微博的发布地区，精确到省或直辖市，值不应包含“省”或“市”等字，如想筛选北京市的微博请用“北京”而不是“北京市”，想要筛选安徽省的微博请用“安徽”而不是“安徽省”，可以写多个地区，
# 具体支持的地名见region.py文件，注意只支持省或直辖市的名字，省下面的市名及直辖市下面的区县名不支持，不筛选请用“全部”
REGION = ['全部']

# 搜索的起始日期，为yyyy-mm-dd形式，搜索结果包含该日期
START_DATE = ''

# 搜索的终止日期，为yyyy-mm-dd形式，搜索结果包含该日期
END_DATE = ''

# 进一步细分搜索的阈值，若结果页数大于等于该值，则认为结果没有完全展示，细分搜索条件重新搜索以获取更多微博。数值越大速度越快，也越有可能漏掉微博；数值越小速度越慢，获取的微博就越多。
# 建议数值大小设置在40到50之间。
FURTHER_THRESHOLD = 1

# 结果存储路径
OUTPUT_PATH = './output'
# output5行号,默认为1
ID_ROW_NUM = 1

# 选择要启用的功能, 开启True，关闭False
# 是否启用评论
ENABLE_COMMENT = True
# 是否启用转发
ENABLE_REPOST = True
# 是否启用点赞
ENABLE_ATTITUDE = True

# 选择要打印的字段
# OUTPUT1 输出的字段
# 博客需要打印的字段，可选：id、bid、user_id、screen_name、text、article_url、location、at_users、at_user_ids、topics、topics_num、comments_count、reposts_count、attitudes_count、created_at、source、pics、video_url、has_pic、has_video、retweet_id
BLOG_OUTPUT_FIELDS = ['id', 'user_id', 'text', 'at_users', 'at_user_ids', 'topics', 'topics_num', 'reposts_count', 'comments_count', 'attitudes_count', 'created_at', 'source', 'has_pic', 'has_video']

# OUTPUT2 输出的字段
# 评论需要打印的字段，可选：mid、comment_id、comment_user_id、comment_user_screen_name、comment_text、comment_created_at、comment_has_pic、has_secondary_comments、secondary_comments_num、secondary_comment_id、secondary_comment_user_id、secondary_comment_user_screen_name、、secondary_comment_text、secondary_comment_created_at、secondary_comment_has_pic
COMMENT_OUTPUT_FIELDS = ['mid', 'comment_id', 'comment_user_id', 'comment_user_screen_name', 'comment_text', 'comment_created_at', 'comment_has_pic', 'has_secondary_comments', 'secondary_comments_num', 'secondary_comment_id', 'secondary_comment_user_id', 'secondary_comment_user_screen_name', 'secondary_comment_text', 'secondary_comment_has_pic', 'secondary_comment_created_at']
# 转发需要打印的字段，可选：mid, transmit_id、transmit_user_id、transmit_user_screen_name、transmit_text、transmit_time、transmit_at_users、transmit_at_user_ids、transmit_at_user_num、is_secondary_transmit
REPOST_OUTPUT_FIELDS = ['mid', 'transmit_id', 'transmit_user_id', 'transmit_user_screen_name', 'transmit_text', 'transmit_time', 'is_secondary_transmit', 'transmit_at_users', 'transmit_at_user_ids', 'transmit_at_user_num']
# 点赞需要打印的字段，可选：mid、attitude_id、attitude_user_id、attitude_user_screen_name、attitude_create_at
ATTITUDE_OUTPUT_FIELDS = ['mid', 'attitude_id', 'attitude_user_id', 'attitude_user_screen_name', 'attitude_create_at']

# OUTPUT3 输出的字段 = OUTPUT1 + OUTPUT2[1:]

# OUTPUT4 输出的字段
COMMENT_OUTPUT4_FIELDS = ['text_label', 'comment_text_label', 'secondary_comment_text_label']
REPOST_OUTPUT4_FIELDS = ['text_label', 'transmit_text_label']
ATTITUDE_OUTPUT4_FIELDS = ['text_label']

# OUTPUT5 输出的字段
# 用户信息需要打印的字段，可选：id、idstr、screen_name、profile_image_url、profile_url、verified、verified_type、verified_reason、description、location、gender、followers_count、friends_count、statuses_count、birthday、created_at、ip_location、has_offensive、period
USERINFO_OUTPUT_FIELDS = ['id', 'screen_name', 'verified', 'verified_reason', 'location', 'gender', 'followers_count', 'friends_count', 'statuses_count', 'birthday', 'created_at', 'ip_location', 'has_offensive', 'action', 'period']
