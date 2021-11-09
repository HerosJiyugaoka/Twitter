import csv
import os
import sys
import requests
import numpy as np

import slackweb
import pandas as pd
from bs4 import BeautifulSoup

import tweepy

#タイトルをスクレイピングして抽出
def scraping_tit():
  url = 'url'
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  result = []
  for top_news in soup.find_all(class_=['該当ダグ']):
      result.append([
      top_news.text
      ])
  return result

#urlをスクレイピングして抽出
def scraping_url():
  url = 'url'
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  result = []
  for top_news in soup.find_all(class_=['該当タグ']):
      result.append([
      'https://e-gakkou.jp' + top_news.get('href')
      ])
  return result

#スクレイピングして抽出したタイトルとurlを対応させてリスト化
def array_con(result_tit, result_url):
    result = result_tit
    for i in range(9):
        result[i].extend(result_url[i])
    return result

#csvファイルを開いてリストを格納
def output_csv(result):
  with open('last_log.csv', 'w', newline='',encoding='utf_8') as file:
    headers = ['Title', 'URL']
    writer = csv.writer(file)
    writer.writerow(headers)
    for row in result:
      writer.writerow(row)

#csvファイルを開いてリストに格納
def read_csv():
  if not os.path.exists('last_log.csv'):
    raise Exception('ファイルがありません。')
  if os.path.getsize('last_log.csv') == 0:
    raise Exception('ファイルの中身が空です。')
  csv_list = pd.read_csv('last_log.csv', header=None).values.tolist()
  return csv_list

#last_log.csvから格納したリストとスクレイピングしたリストを比較し、異なる部分のみ格納
def list_diff(result, last_result):
    return_list = []
    for tmp in (result):
        if tmp not in last_result:
            return_list.append(tmp)
    return return_list

#slackに送信
def send_to_slack(diff_list):
  text = '<!channel>\n'
  for tmp in diff_list:
    text += tmp[0] + '\n' + tmp[1] + '\n'
  slack = slackweb.Slack(url='Slack WebHook Url')
  slack.notify(text=text)

#Twitter認証して更新をTweet
def hp_tweet(diff_list):
    API_KEY = "api_key"
    API_SECRET = "api_secret"
    ACCESS_TOKEN = "access_token_key"
    ACCESS_TOKEN_SECRET = "access_token_secret"

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    text = 'ブログ更新しました！\n'
    for tmp in diff_list:
        text += tmp[0] + '\n #ヒーローズ #自由ヶ丘 #個別指導 #学習塾 \n' + tmp[1]
    api.update_status(text)

#HPの更新がない場合定型文をTweet
def fixed_tweet():
    API_KEY = "api_key"
    API_SECRET = "api_secret"
    ACCESS_TOKEN = "access_token_key"
    ACCESS_TOKEN_SECRET = "access_token_secret"

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    text = 'ヒーローズ自由ヶ丘校ではお問い合わせをお待ちしております！\n 是非、お気軽にご相談くださいませ。\n #ヒーローズ #自由ヶ丘 #個別指導 #学習塾 \n'

    api.update_status(text)

result_tit = scraping_tit()

result_url = scraping_url()

result = array_con(result_tit,result_url)

csv_list = read_csv()

diff_list=list_diff(result, csv_list)

#更新があったらそれをTweet、slackにも。
if diff_list != []:
    send_to_slack(diff_list)
    hp_tweet(diff_list)

else:
    fixed_tweet()

output_csv(result)
