#coding=utf-8
import re

import streamlit as st
import requests

from PIL import Image

from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Radar, TreeMap
from pyecharts import options as opts
import streamlit_echarts
import numpy as np

import matplotlib.pyplot as plt
from wordcloud import WordCloud as WC
import seaborn as sns
import pandas as pd
import plotly.express as px


@st.dialog("词频统计可视化")
def vote():
    # st.write(f"")
    url = st.text_input("请输入文章url: ")
    if st.button("开始"):
        st.session_state.vote = {"url": url}
        st.rerun()

def st_pyecharts(chart):
    streamlit_echarts.st_pyecharts(chart)

def draw_chart(url):
    if url:
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        cleaned_text = re.sub(r'[^\u4e00-\u9fff]+', '', text)  # 保留中文字符，移除其他字符

        words = jieba.lcut(cleaned_text)
        word_counts = Counter(words)

        word_counts = {word: count for word, count in word_counts.items() if len(word) > 1}

        min_frequency = st.sidebar.slider('过滤词频低于:', 1, 10, 1)

        filtered_word_counts = Counter({word: count for word, count in word_counts.items() if count >= min_frequency})

        top_words = dict(filtered_word_counts.most_common(20))
        st.write("词频排名前20的词汇:")
        # st.write("词频排名前20的词汇:")
        # st.table(top_words)  # 使用表格格式展示

        # Add chart type selection in sidebar
        chart_type = st.sidebar.selectbox(
            "选择图表类型:",
            ["Word Cloud", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Chart", "Radar Chart", "Tree Map"]
        )

        # Depending on the selected chart type, generate the appropriate chart
        if chart_type == "Word Cloud":
            # 使用 Matplotlib 和 wordcloud 库绘制词云图
            # color_mask = np.array(Image.open("./crow.png"))
            wc = WC(width=800, height=400, background_color='white', font_path='C:\Windows\Fonts\simsun.ttc')  # 需要指定中文字体路径
            wc.generate_from_frequencies(filtered_word_counts)
            plt.figure(figsize=(10, 6))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.title("词频词云图")
            st.pyplot(plt)

        elif chart_type == "Bar Chart":
            # 使用 Seaborn 绘制条形图
            df = pd.DataFrame(list(top_words.items()), columns=['Word', 'Frequency'])
            # 设置全局字体为支持中文的字体，比如SimHei（黑体）
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
            # 或者如果你想要使用宋体，可以如下设置：
            # plt.rcParams['font.sans-serif'] = ['simsun']

            # 确保负号在matplotlib中能正确显示
            plt.rcParams['axes.unicode_minus'] = False
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Word', y='Frequency', data=df, palette='viridis')
            plt.xlabel('词语')
            plt.ylabel('频率')
            plt.title('词频条形图')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

        elif chart_type == "Pie Chart":
            # 使用 Plotly 绘制饼图
            fig = px.pie(names=top_words.keys(), values=top_words.values(), title='词频饼图')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)

        # pyEcharts
        elif chart_type == "Line Chart":
            line = (
                Line()
                .add_xaxis(list(top_words.keys()))
                .add_yaxis("词频", list(top_words.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
            )
            st_pyecharts(line)

        elif chart_type == "Scatter Chart":
            scatter = (
                Scatter()
                .add_xaxis(list(range(len(top_words))))
                .add_yaxis("词频", list(top_words.values()), symbol_size=20)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="词频散点图"),
                    xaxis_opts=opts.AxisOpts(name="词汇"),
                    yaxis_opts=opts.AxisOpts(name="频率")
                )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            )
            st_pyecharts(scatter)

        elif chart_type == "Radar Chart":
            max_freq = max(top_words.values())
            radar = (
                Radar()
                .add_schema(
                    schema=[
                        opts.RadarIndicatorItem(name=key, max_=max_freq) for key in top_words.keys()
                    ]
                )
                .add("词频", [[value for value in top_words.values()]])
                .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
            )
            st_pyecharts(radar)

        elif chart_type == "Tree Map":
            treemap = (
                TreeMap()
                .add("词频", [dict(value=value, name=key) for key, value in top_words.items()])
                .set_global_opts(title_opts=opts.TitleOpts(title="词频树状图"))
            )
            st_pyecharts(treemap)


if "vote" not in st.session_state:
    vote()
else:
    url = st.session_state.vote["url"]
    draw_chart(url)



