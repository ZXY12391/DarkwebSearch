# -*- coding: utf-8 -*-
# @Time    : 19-11-3 下午2:05
# @Author  : yiyun_yiyun
# @File    : search_engine_sc/CxExtractor_python.py
# @Software: PyCharm
# @Description:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import chardet
# import asyncio
import requests


class CxExtractor_python:
    """cx-extractor implemented in Python"""

    __text = []
    __indexDistribution = []

    def __init__(self, threshold=86, blocksWidth=3) -> None:
        self.__blocksWidth = blocksWidth
        self.__threshold = threshold

    def getText(self, content: str) -> str:
        if self.__text:
            self.__text = []
        lines = content.split('\n')
        for i in range(len(lines)):
            # lines[i] = lines[i].replace("\\n", "")
            if lines[i] == '\n':
                lines[i] = ''
        self.__indexDistribution.clear()
        for i in range(0, len(lines) - self.__blocksWidth):
            words_num = 0
            for j in range(i, i + self.__blocksWidth):
                lines[j] = lines[j].replace("\\s", "")
                words_num += len(lines[j])
            self.__indexDistribution.append(words_num)
        start = -1
        end = -1
        boolstart = False
        boolend = False
        for i in range(len(self.__indexDistribution) - 1):
            if self.__indexDistribution[i] > self.__threshold and (not boolstart):
                if (self.__indexDistribution[i + 1] != 0 or self.__indexDistribution[i + 2] != 0 or
                        self.__indexDistribution[i + 3] != 0):
                    boolstart = True
                    start = i
                    continue
            if boolstart:
                if self.__indexDistribution[i] == 0 or self.__indexDistribution[i + 1] == 0:
                    end = i
                    boolend = True
            tmp = []
            if boolend:
                for ii in range(start, end + 1):
                    if len(lines[ii]) < 5:
                        continue
                    tmp.append(lines[ii] + "\n")
                new_str = "".join(list(tmp))
                if "copyright" in new_str.lower() or "版权所有" in new_str:
                    continue
                self.__text.append(new_str)
                boolstart = boolend = False
        result = "".join(list(self.__text))
        return result

    def replaceCharEntity(self, htmlstr: str) -> str:
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()
            key = sz.group('name')
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def getHtml(self, url: str) -> str:
        proxies = {
            'http': 'http://127.0.0.1:8118',
            'https': 'http://127.0.0.1:8118'
        }
        response = requests.get(url, proxies=proxies)
        #response = requests.get(url,proxies='http://127.0.0.1:8118')
        encode_info = chardet.detect(response.content)
        response.encoding = encode_info['encoding'] if encode_info['confidence'] > 0.5 else 'utf-8'
        return response.text

    def getHtml1(self, url: str) -> str:
        proxy = 'http://127.0.0.1:8118'  # 设置代理
        proxies = {'http': proxy, 'https': proxy}  # 构建代理字典
        try:
            response = requests.get(url, proxies=proxies)
            response.raise_for_status()  # 检查请求是否成功
            encode_info = chardet.detect(response.content)
            response.encoding = encode_info['encoding'] if encode_info['confidence'] > 0.5 else 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            print(f"请求发生异常: {e}")
            return ''  # 或者您可以选择引发异常以便在需要时进行处理

    def readHtml(self, path: str, coding: str) -> str:
        page = open(path, encoding=coding)
        lines = page.readlines()
        s = ''
        for line in lines:
            s += line
        page.close()
        return s

    def filter_tags(self, htmlstr: str) -> str:
        # re_doctype = re.compile('<![DOCTYPE|doctype].*>')
        re_nav = re.compile('<nav.+</nav>')
        re_cdata = re.compile('//<!\[CDATA\[.*//\]\]>', re.DOTALL)
        re_script = re.compile(
            '<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.DOTALL | re.I)
        re_style = re.compile(
            '<\s*style[^>]*>.*?<\s*/\s*style\s*>', re.DOTALL | re.I)
        re_textarea = re.compile(
            '<\s*textarea[^>]*>.*?<\s*/\s*textarea\s*>', re.DOTALL | re.I)
        re_br = re.compile('<br\s*?/?>')
        re_h = re.compile('</?\w+.*?>', re.DOTALL)
        re_comment = re.compile('<!--.*?-->', re.DOTALL)
        re_space = re.compile(' +')
        s = re_cdata.sub('', htmlstr)
        # s = re_doctype.sub('',s)
        s = re_nav.sub('', s)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_textarea.sub('', s)
        s = re_br.sub('', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        s = re.sub('\\t', '', s)
        s = re_space.sub(' ', s)
        s = self.replaceCharEntity(s)
        return s

    def filter_tags1(self, htmlstr: str) -> str:
        # re_doctype = re.compile('<![DOCTYPE|doctype].*>')
        re_nav = re.compile('<nav.+</nav>')
        re_cdata = re.compile('//<!\[CDATA\[.*//\]\]>', re.DOTALL)
        re_script = re.compile(
            '<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.DOTALL | re.I)
        re_style = re.compile(
            '<\s*style[^>]*>.*?<\s*/\s*style\s*>', re.DOTALL | re.I)
        re_textarea = re.compile(
            '<\s*textarea[^>]*>.*?<\s*/\s*textarea\s*>', re.DOTALL | re.I)
        re_br = re.compile('<br\s*?/?>')
        re_h = re.compile('</?\w+.*?>', re.DOTALL)
        re_comment = re.compile('<!--.*?-->', re.DOTALL)
        re_space = re.compile(' +')
        s = re_cdata.sub('', htmlstr)
        # s = re_doctype.sub('',s)
        s = re_nav.sub('', s)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_textarea.sub('', s)
        s = re_br.sub('', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        s = re.sub('\\t', '', s)
        s = re_space.sub(' ', s)
        s = self.replaceCharEntity(s)
        # 在第二步中删除换行符
        s = s.replace('\n', ' ').replace('\r', ' ')
        return s
    
    
if __name__ == '__main__':
    url = 'https://news.china.com/domestic/945/20191011/37196990.html'
    # print(url)
    resp = requests.get(url)
    raw_content = resp.text
    cp = CxExtractor_python()
    content = cp.filter_tags(raw_content)
    content = cp.getText(content)
    print(content)