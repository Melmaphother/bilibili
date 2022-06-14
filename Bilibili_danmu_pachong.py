import requests
import re
import jieba
import wordcloud
import time
import sys
import os
import math
from bs4 import BeautifulSoup


class Bilibili:
    def __init__(self, videourl, page, img_path, quality):

        self.img_path = img_path
        self.baseurl = videourl.split('?')[0]

    # 爬取弹幕和评论
    def getAidAndCid(self):
        cidurl = self.baseurl + "?p=" + page
        cidRegx = '{"cid":([\d]+),"page":%s,' % (page)
        aidRegx = '"aid":([\d]+),'
        r = requests.get(cidurl)
        r.encoding = 'utf-8'
        self.cid = re.findall(cidRegx, r.text)[0]
        self.aid = re.findall(aidRegx, r.text)[int(page) - 1]


    def getBarrage(self):
        print('正在获取弹幕......')

        commentUrl = 'https://comment.bilibili.com/' + self.cid + '.xml'

        # 获取并提取弹幕 #
        r = requests.get(commentUrl)
        r.encoding = 'utf-8'
        content = r.text
        # 正则表达式匹配字幕文本
        comment_list = re.findall('>(.*?)</d><d ', content)
        comment_path = os.path.join(sys.path[0], 'comment.txt')
        file_path = open(comment_path, 'w', encoding='utf-8')
        for i in range(1, len(comment_list)):
            file_path.write(str(i) + '. ' + comment_list[i] + '\n')
        del comment_list[0]

        # jieba分词
        self.barrage = "".join(comment_list)

    def getComment(self, x, y):
        for i in range(x, y + 1):
            r = requests.get(
                'https://api.bilibili.com/x/v2/reply?pn={}&type=1&oid={}&sort=2'.format(i, self.aid)).json()
            replies = r['data']['replies']
            print('------评论列表------')
            for repliy in replies:
                print(repliy['content']['message'] + '\n')

        pass

    def genWordCloud(self):
        print('正在分词......')

        text = "".join(jieba.lcut(self.barrage))
        # 实例化词云，
        wc = wordcloud.WordCloud(
            # 选择字体路径，没有选择的话，中文无法正常显示
            font_path='C://Windows/Fonts/simfang.ttf',
            width=int(math.ceil(16 * int(quality) / 9)),
            height=int(quality)
        )
        # 文本中生成词云
        wc.generate(text)
        # 保存成图片
        wc.to_file(self.img_path + '.jpg')
        print('词云生成完毕，图片名称：{}.jpg'.format(self.img_path))


def checkUrl(url):
    try:
        r = requests.get(url)
    except:
        return 0
    r.encoding = 'utf-8'
    # 视频名称正则表达式
    regx = '"part":"(.*?)"'
    r.encoding = 'utf-8'
    result = re.findall(regx, r.text)
    count = 0
    if len(result) > 0:
        print('------视频列表------')
        for i in result:
            count += 1
            print("视频" + str(count) + " : " + i)
        return count
    return 0


if __name__ == '__main__':
    # 视频地址
    videourl = 'https://www.bilibili.com/video/' + input("请输入视频BV号，例如:BV13x41147nB\nBV号：")
    count = checkUrl(videourl)
    if count:
        print('------视频地址有效------')

        # 第n个视频
        if count == 1:
            page = '1'
        else:
            while(1):
                page = input('请输入视频的序号：')
                if int(page) in range(1,count):
                    break
                else:
                    print('输入错误！序号需介于1~%d之间'%count)
                    continue

        # 图片储存路径
        img_path = input('请输入你要生成的词云的图片名称：')

        # 清晰度选择
        print('可供选择的清晰度有 1080P,720p,480p,360p')
        while (1):
            quality = input('请选择您要下载视频的清晰度(输入数字即可)：')
            if quality.isdigit() == True:
                break
            else:
                print('输入错误！只需输入数字')
                continue

        # 计时
        start_time = time.time()

        # 实例化类
        b = Bilibili(videourl, page, img_path, quality)

        # 获取aid和cid
        b.getAidAndCid()

        # 获取弹幕
        b.getBarrage()

        # 获取评论 起始页和结束页
        # b.getComment(1, 4)

        # 生成词云
        b.genWordCloud()

        print('程序运行完毕，耗时:{:.2f}s'.format(time.time() - start_time))
    else:
        print('视频地址无效')
