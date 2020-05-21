import Rake as rk
import os
from importlib import import_module
ct=import_module ('crf-tagger')

def isPunc(t):
    punctions = "：「」？！。『』；，、《》（）…"
    return (t in punctions)

def cbeta_preSegText_tokenizer(rawtext):
    rawTokens = rawtext.split("/")
    tokenList=[]
    # Construct Stopword Lib
    # swLibList = [line.rstrip('\n') for line in open("data/stoplist/中文停用词表(1208个).txt",'r')]
    # Construct Phrase Deliminator Lib
    # conjLibList = [line.rstrip('\n') for line in open("data/stoplist/中文分隔词词库.txt",'r')]
    
    stopList =[]

    for rt in rawTokens:
        if rt=="": 
            continue #跳過空白
        
        if isPunc(rt)  or (rt in stopList):
            if len(tokenList)==0 or tokenList[-1] !="|": #不重複增加 "|"
                tokenList.append("|")
        else:
            tokenList.append(rt)

    print(1)
    return tokenList

def dila_wang_tokenizer(text):
    crf_model = os.path.join("lib","model.bin")
    crft = ct.CRFTagger(crf_model)
    rawTokens = crft.segment(text)

    tokenList=[]
    #  Construct Stopword Lib
    dilaSPWList = [line.strip() for line in open("data/stoplist/dila_stop_words.txt",'r')]
    # Chinese Empty Word
    emptyCharsList = [line.strip() for line in open("data/stoplist/chinese_empty_chars.txt",'r')]
    # emptyCharsList =[]
    
    stopList = dilaSPWList + emptyCharsList

    for rt in rawTokens:
        if rt=="": 
            continue #跳過空白
        
        if isPunc(rt)  or (rt in stopList):
            if len(tokenList)==0 or tokenList[-1] !="|": #不重複增加 "|"
                tokenList.append("|")
        else:
            tokenList.append(rt)

    return tokenList

with open('data/testCase/cbeta1.txt','r') as fp:
    text = fp.read().strip().replace("\n","")
    # tokenList = cbeta_preSegText_tokenizer(text)
    rake = rk.RakeAnalyze("stopfn.txt")
    # dila_wang_tokenizer(text)
    result = rake.run(text,dila_wang_tokenizer)
    for i, kw_info in enumerate(result):
        print("關鍵字{}: {}".format(i,kw_info))
        # print("   {",end="")
        # for kw in kw_info[0].split("/"):
        #     print ("({}:{:.4f})".format(kw,rake.words[kw].returnScore()),end="")
        # print("}")