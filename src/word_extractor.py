# word_extractor.py
from lxml import html
import requests
from nltk.corpus import stopwords
import nltk
import string
import re
from collections import OrderedDict
import os

nltk.download('stopwords')

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 拼接输出文件的路径
output_dir = os.path.join(current_dir, '..', 'data', 'output')
output_file_path = os.path.join(output_dir, 'words_list.txt')


def extract_unique_words(url):
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

            # 写入文件
            with open(output_file_path, 'w', encoding='utf-8') as file:
                for word in unique_words:
                    file.write(word + '\n')
        else:
            print("Failed to retrieve content. Status code:", response.status_code)

    except requests.RequestException as e:
        print("Error:", e)
