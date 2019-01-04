import random
import re

import textrazor
import json
import gensim
import logging
import numpy as np

from os.path import join

import KBPA_StockPrediction.settings.parameters as para

YOUR_API_KEY = "cef12937739c8cf599875c31e37ace2e1dddc24d91828a0e99504f17"
# text = "Barclays misled shareholders and the public about one of the biggest investments in the bank's history, a BBC Panorama investigation has found."

def concept_extract_save(filepath, text):
    client = textrazor.TextRazor(YOUR_API_KEY, extractors=["entities"])
    response = client.analyze(text)
    output_file = open(filepath, 'w+', -1, 'UTF-8')
    # concept_set = ([])
    concept_set = []
    for entity in response.entities():
        if 'entityId' in entity.json:
            concept_set.append(entity.json['entityId'])
        print(entity.json)
        output_file.write(str(entity.json) + '\n')
    output_file.close()

def concept_extract(text):
    client = textrazor.TextRazor(YOUR_API_KEY, extractors=["entities"])
    response = client.analyze(text)
    concept_set = ([])
    for entity in response.entities():
        if 'entityId' in entity.json:
            concept_set.append(entity.json['entityId'])
            print(entity.json)
    return concept_set

def text_extract(filepath, timefilepath):
    list_datetime = getDateTime(timefilepath)
    list_datetime_hour = getDateTime_hour(timefilepath)
    file = open(filepath)
    d_tweets = {}
    d_concepts = {}
    while 1:
        lines = file.readlines(100000)
        if not lines:
            break
        for line in lines:
            kv = str(line).split("-*-")
            # print(kv[0], kv[1])
            # time = strReplace(kv[1], 17, "0")
            # time = strReplace(time, 18, "0")
            time_hour = kv[1][0:10] + "-" + kv[1][11:13]
            time = kv[1][0:10]
            if time_hour in list_datetime_hour:
                # save all tweets in one day
                if time in d_tweets.keys():
                    # d_tweets[time] = list(set(d_tweets[time]).union(set(kv[2].replace("\n", ""))))
                    d_tweets[time] = d_tweets[time] + kv[2]
                else:
                    d_tweets[time] = kv[2].replace("\n", "")
                # d_tweets[time] = kv[2].replace("\n", "")

            # print(time, d_tweets[time])

            # if time in d_concepts:
            #     d_concepts[time] = list(set(d_concepts[time]).union(set(concept_extract(kv[2].replace("\n", "")))))
            # else:
            #     d_concepts[time] = concept_extract(kv[2].replace("\n", ""))
    # 返回的d_tweets是一个字典类型，存储的是time-tweets键值对
    # 返回的d_concepts是一个字典类型，存储的是time-concepts键值对
    # return d_tweets, d_concepts
    return d_tweets

def getSentences(filepath, timefilepath):
    d_tweets = text_extract(filepath, timefilepath)
    d_sentence = {}
    p = re.compile(r'\W+')
    for key in d_tweets.keys():
        # d_sentence[key] = ''.join(d_tweets[key]).split(" ")
        # d_sentence[key] = d_tweets[key].split(" ")
        d_sentence[key] = p.split(d_tweets[key])
    return d_sentence

def saveDict(filepath, dic):
    with open(filepath, 'a') as outfile:
        json.dump(dic, outfile, ensure_ascii=False)
        outfile.write('\n')
    outfile.close()

def loadJson2Dict(filepath):
    f = open(filepath, "r")
    for line in f:
        decodes = json.loads(line)
        # print(decodes)
    f.close()
    return decodes

# 修改字符串s，使得第n+1个字符s[n]改成x
def strReplace(s, n, x):
    tmp = list(s)
    tmp[n] = x
    s = ''.join(tmp)
    return s

# dir = join(para.SEMI_RESULT_DIRECTORY, "stockDate.xls")
def getTimestamps(filepath):
    list_timestamp = []
    with open(filepath) as file:
        lines = file.readlines()
        for line in lines:
            list_timestamp.append(line.strip("\n"))
    return list_timestamp

def getDateTime_hour(filepath):
    list_datetime_hour = []
    list_timestamp = getTimestamps(filepath)
    for timestamp in list_timestamp:
        list_datetime_hour.append(timestamp[0:10] + "-" + timestamp[11:13])
    return list_datetime_hour

def getDateTime(filepath):
    list_datetime = []
    list_timestamp = getTimestamps(filepath)
    for timestamp in list_timestamp:
        list_datetime.append(timestamp[0:10])
    return list_datetime

def word2vec(sentences_filepath):
    sentences = []
    d_sentences = loadJson2Dict(sentences_filepath)
    for key in d_sentences.keys():
        sentences.append(d_sentences[key])
    model = gensim.models.Word2Vec(sentences, min_count=1, size=para.SIZE_WORDVEC)
    return model

def wordVec_extract(sentences_filepath):
    d_wordVec = {}
    model = word2vec(sentences_filepath)
    d_sentences = loadJson2Dict(sentences_filepath)
    for key in d_sentences.keys():
        wordVec = []
        for word in d_sentences[key]:
            wordVec.append(model[word].tolist())
        d_wordVec[key] = wordVec
    return d_wordVec

def form_wordVec(sentences_filepath):
    d_wordVec_form = wordVec_extract(sentences_filepath)
    for datetime in getDateTime(join(para.SEMI_RESULT_DIRECTORY, "stockDate.xls")):
        if datetime not in d_wordVec_form.keys():
            d_wordVec_form[datetime] = []
            print(datetime)
    list_add = [0] * para.SIZE_WORDVEC
    for key in d_wordVec_form.keys():
        if len(d_wordVec_form[key]) <= para.NUM_WORDS:
            for i in range(len(d_wordVec_form[key]), para.NUM_WORDS):
                d_wordVec_form[key].append(list_add)
        else:
            d_wordVec_form[key] = random.sample(d_wordVec_form[key], para.NUM_WORDS)
    return d_wordVec_form

if __name__ == '__main__':
    # text = "S&P 500 Fut 2353.75 (-0.1%), VIX 11.79 (-4.8%), Nikkei +0.2%, Shanghai +1.2%, Brent $54.49 (+0.6%), Gold $1257.25, €/$ 1.0673 #pruss5015utro"
    # p = re.compile(r'\W+')
    # list_word = p.split(text)
    # print(list_word)
    # s = ','.join(list_word)
    # print(s)
    # s = s.replace(",", " ") + "."
    # print(s)
    # print(concept_extract(s))
    text = "Barclays misled shareholders and the public about one of the biggest investments in the bank's history, a BBC Panorama investigation has found."
    text = "When stocks go down, people get nervous and buy downside protection. That tends to spike implied volatility of options on S&P 500"
    text = "The S&P 500 is stuck in a range just below the all-time record high set in early March."
    text = "Shares of Acuity Brands slip 1.1% to lead S&P 500's early laggards"
    text = "S&P 500 Weekly Update: Investor Worries Are Everywhere. There Is A Time When Investors Need To Be Worried, This Isn't One Of Them."
    print(concept_extract(text))
    tweets_filepath = join(para.DATA_INPUT_DIRECTORY, "tweets.log")
    concepts_filepath = join(para.SEMI_RESULT_DIRECTORY, "concepts.json")
    sentences_filepath = join(para.SEMI_RESULT_DIRECTORY, "sentences.json")
    timestamp_filepath = join(para.SEMI_RESULT_DIRECTORY, "stockDate.xls")
    tweetsClear_filepath = join(para.SEMI_RESULT_DIRECTORY, "tweets.json")
    wordVec_filepath = join(para.SEMI_RESULT_DIRECTORY, "wordVec.json")
    wordVecForm_filepath = join(para.SEMI_RESULT_DIRECTORY, "wordVec_Form.json")

    # list_lost = ["04-11", "04-13", "04-25", "04-27", "05-01", "05-02", "05-10", "05-11", "07-14", "07-18", "07-20", "07-27", "08-17",  "08-25", "08-31"]
    # file = open(tweets_filepath)
    # file2 = open(join(para.DATA_INPUT_DIRECTORY, "tweets_2.log"), "w")
    # while 1:
    #     lines = file.readlines(100000)
    #     if not lines:
    #         break
    #     for line in lines:
    #         ha = 1
    #         for day in list_lost:
    #             if str(line).split("-*-")[1][0:13] == "2017-" + day + " 00":
    #                 ha = 0
    #                 kv = str(line).replace("-*-2017-" + day + " 00", "-*-2017-" + day + " 09")
    #                 file2.write(kv)
    #                 continue
    #             for i in range(1, 8):
    #                 if str(line).split("-*-")[1][0:13] == "2017-" + day + " 0" + str(i):
    #                     ha = 0
    #                     kv = str(line).replace("-*-2017-" + day + " 0" + str(i),  "-*-2017-" + day + " " + str(i+9))
    #                     file2.write(kv)
    #         if ha == 1:
    #             file2.write(str(line))
    # file2.close()
    # file.close()

    #
    # """generate dict: time-tweet"""
    # d_tweets = text_extract(tweets_filepath, timestamp_filepath)
    # # # print(d_tweets)
    # # print(d_tweets.keys().__len__())
    # # for datetime in getDateTime(join(para.SEMI_RESULT_DIRECTORY, "stockDate.xls")):
    # #     if datetime not in d_tweets.keys():
    # #         print(datetime)
    # """save dict to json: time-tweet"""
    # saveDict(tweetsClear_filepath, d_tweets)
    # """test"""
    # # text = d_tweets['2017-04-28 11:16:00']
    # # text = d_tweets['2017-04-28-11']
    # """load dict from json: time-tweet"""
    # # d_cleartweets = loadJson2Dict(tweetsClear_filepath)
    # # print(d_cleartweets)
    #
    # # d_concepts = {}
    #
    # """generate dict: time-sentences
    #     make the words of a tweet into a sentence list,
    #     each sentence is split by a blank and saved in a list
    # """
    # d_sentence = getSentences(tweets_filepath, timestamp_filepath)
    # # print(d_sentence)
    # saveDict(sentences_filepath, d_sentence)
    #
    # """generate dict: time-wordEmbedding"""
    # d_wordVec = wordVec_extract(sentences_filepath)
    # # print(d_wordVec)
    # # print(d_wordVec.keys().__len__())
    # # 709, 说明存在tweets缺失，有的时段的tweet没有爬到，需要重新爬到补上
    # # 缺失的天数是：4.11, 4.13, 4.25, 4.27, 5.1, 5.2, 5.10, 5.11, 7.14, 7.18, 7.20, 7.27, 8.17, 8.21, 8.23, 8.25, 8.31
    # # 经过tweet补全之后，最后的d_wordVec.keys().__len__() = 845，说明每小时都有对应的tweet，great！
    #
    # # saveDict(wordVec_filepath, d_wordVec)
    #
    # """d_wordVec中的所有sentence list，一天内，word数目最大的是21192，最小的是706
    #     (一个小时内，word数目最大的是9564，最小的是16)
    #     (1分钟内，word数目最大的是47，最小的是1)
    #     这里限定每个sentence的word数量为para.NUM_WORDS = 706, 便于后面进行卷积操作
    #     不够706的用0填充，超过706的就随机选择706个wordVec
    # """
    # list_len = []
    # for key in d_wordVec.keys():
    #     list_len.append(len(d_wordVec[key]))
    # print(max(list_len), min(list_len))
    #
    # """generate dict: time-wordEmbedding (formalized)"""
    # d_wordVec_form = form_wordVec(sentences_filepath)
    # # saveDict(wordVecForm_filepath, d_wordVec_form)
    # # print(d_wordVec_form)
    #
