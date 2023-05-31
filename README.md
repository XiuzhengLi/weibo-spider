# weibo-search
> 微博抓取需求

## 代码运行
* 运行环境：`Python3.7+`
* 代码下载
```
git clone git@github.com:XiuzhengLi/weibo-spider.git
```
* 安装依赖
```
pip install -r requirements.txt
```
* 运行，通过settings.py修改运行参数
```
python3 -m weibo_spider run
```
> 后台运行
```
nohup python3 -m weibo_spider run > logs/run.log 2>&1 &
```
* 从user_id文件得到user_info，触发反爬后继续抓取
> 输入：stdin, sort -u 排序去重
```
cat output/output5/user_id.csv | sort -u | python3 -m get_user_info_by_stdin
```
* 从抓取失败的行开始
> 找到抓取失败的行数
```
tail -1 output/output5/user_info.csv | awk -F ',' '{print $1}' | xargs -n1 -I {} grep -n {} output/output5/user_id.csv
```
> 从失败的行数开始继续抓取，例如第100行
```
awk 'NR>100' | sort -u | python3 -m get_user_info_by_stdin
```

## 输出目录结构
> 通过settings.py修改输出路径/增删输出的字段或顺序
```
output
├── output1
│   └── blogs.csv     微博详情
├── output2
│   ├── attitudes.csv 点赞信息
│   ├── comments.csv  评论信息
│   └── reposts.csv   转发信息
├── output3
│   ├── attitudes.csv 微博详情 + 点赞信息
│   ├── comments.csv  微博详情 + 评论信息
│   └── reposts.csv   微博详情 + 转发信息
├── output4
│   ├── attitudes.csv 微博详情 + 点赞信息 + 冒犯性言论识别
│   ├── comments.csv  微博详情 + 评论信息 + 冒犯性言论识别
│   └── reposts.csv   微博详情 + 转发信息 + 冒犯性言论识别
└── output5
    ├── user_id.csv   发布微博、评论和转发中出现的user_id
    └── user_info.csv 用户详情 + 冒犯性言论识别
```
## 参数说明
> 详见settings.py

## 代码组成
### weibo-search
> 微博搜索结果抓取

> 参数：keyword(搜索关键词，必填)、page_num(页码，选填默认为1)、
> start_date(开始时间，选填)、end_date(结束时间，选填)、region(地区代码，选填)、
> weibo_type(微博类型，选填默认为1)、contain_type(包含内容的类型，选填默认为0)
* 运行示例1: 抓取从 **2023-05-01** 到 **2023-05-07** 搜索 **迪丽热巴** 得到的第 **1** 页微博搜索结果
```
python3 -m weibo_blogs.weibo_search search 迪丽热巴 1 2023-05-01 2023-05-07
```
* 运行示例2: 抓取话题 **#迪丽热巴#** 的第 **2** 页搜索结果
```
python3 -m weibo_blogs.weibo_search search "#迪丽热巴#" 2
```
### weibo-signal
> 交互信号抓取(评论、转发、点赞)
* 评论抓取
```
python3 -m weibo_signal.weibo_signal get_comments 4903507318016735

python3 -m weibo_signal.weibo_signal get_secondary_comments 4906409953598218

python3 -m weibo_signal.weibo_signal get_all_secondary_comments 4906409953598218

python3 -m weibo_signal.weibo_signal get_all_comments_and_secondary_comments 4903507318016735

```
* 转发抓取
```
python3 -m weibo_signal.weibo_signal get_reposts 4903507318016735

python3 -m weibo_signal.weibo_signal get_all_reposts 4903507318016735
```
* 点赞抓取
```
python3 -m weibo_signal.weibo_signal get_attitudes 4904227594046445

python3 -m weibo_signal.weibo_signal get_all_attitudes 4904227594046445
```
### user_info
> 用户个人信息抓取
* 运行示例
```
python3 -m user_info.user_info get_info 6269329742
python3 -m user_info.user_info get_detail_info 6269329742
python3 -m user_info.user_info get_all_info 6269329742
```
### sentiments_predictor
> 情绪预测
* 运行示例
```
python3 -m sentiments_predictor.sentiments_predictor predict "黑人很多都好吃懒做，偷奸耍滑！"
python3 -m sentiments_predictor.sentiments_predictor predict "男女平等，黑人也很优秀。"
python3 -m sentiments_predictor.sentiments_predictor predict ""
"""
```
