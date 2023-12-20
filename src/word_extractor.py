# word_extractor.py
from lxml import html
import requests
from nltk.corpus import stopwords
import nltk
import string
import re
from collections import OrderedDict
import os
from urllib.parse import urljoin

nltk.download('stopwords')

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 拼接输出文件的路径
output_dir = os.path.join(current_dir, '..', 'data', 'output')

visited_links = set()


def extract_unique_words(url, prefix):
    try:
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 使用lxml解析HTML并获取纯文本
            tree = html.fromstring(response.content)

            # 去除<style>和<script>标签
            for elem in tree.xpath('//style | //script'):
                elem.getparent().remove(elem)

            text = tree.text_content()

            # 创建转换表，将标点符号替换成空格
            translator = text.maketrans(string.punctuation, ' ' * len(string.punctuation))
            # 应用转换表
            clean_text = text.translate(translator)

            # 使用正则表达式以大写字母切割单词
            splited_words = re.findall(r'[A-Z]?[a-z]+', clean_text)

            # 获取英文停用词列表
            stop_words = set(stopwords.words('english'))
            # 去除常用词汇
            filtered_words = [word for word in splited_words if word.lower() not in stop_words]

            # 去除重复的单词，并保留它们在列表中的顺序
            unique_words = list(OrderedDict.fromkeys(filtered_words))

            # 将 URL 中的特殊字符替换为下划线，避免影响文件名
            sanitized_url = url.replace('/', '_').replace(':', '_').replace('.', '_')

            # 拼接文件名
            filename = "{}_{}.txt".format('words_list', sanitized_url)
            # 拼接输出文件的路径
            output_file_path = os.path.join(output_dir, filename)
            print(output_file_path)

            # 写入文件
            with open(output_file_path, 'w', encoding='utf-8') as file:
                for word in unique_words:
                    file.write(word + '\n')

            # 提取页面中的链接并过滤
            links = [link.get('href') for link in tree.xpath('//a[@href]') if link.get('href').startswith(prefix)]

            # 递归处理链接
            for relative_link in links:
                if relative_link not in visited_links:
                    full_url = urljoin(url, relative_link)
                    print(full_url)
                    visited_links.add(relative_link)
                    extract_unique_words(full_url, relative_link)

        else:
            print("Failed to retrieve content. Status code:", response.status_code)

    except requests.RequestException as e:
        print("Error:", e)
