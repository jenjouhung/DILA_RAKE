'''
Implementation of Rapid Automatic Keyword Extraction (RAKE) algorithm for Chinese
Original algorithm described in: Rose, S., Engel, D., Cramer, N., & Cowley, W. (2010).
Automatic Keyword Extraction from Individual Documents. In M. W. Berry & J. Kogan
(Eds.), Text Mining: Theory and Applications: John Wiley & Sons. 
'''
__author__ = "Ruoyang Xu"
__revise__="Joey"

import jieba
import jieba.posseg as pseg
import operator
import json
from collections import Counter


# Data structure for holding data
class Word():
    def __init__(self, char, freq = 0, deg = 0):
        self.freq = freq
        self.deg = deg
        self.char = char

    def returnScore(self):
        return self.deg/self.freq

    def updateOccur(self, phraseLength):
        self.freq += 1
        self.deg += phraseLength

    def getChar(self):
        return self.char

    def updateFreq(self):
        self.freq += 1

    def getFreq(self):
        return self.freq

# Check if contains num
def notNumStr(instr):
    for item in instr:
        if '\u0041' <= item <= '\u005a' or ('\u0061' <= item <='\u007a') or item.isdigit():
            return False
    return True

class RakeAnalyze():
    def __init__(self, stopword_filename):
        self.stpfn =  stopword_filename
        self.words = {}
        # 一行一個停用詞
        # Construct Stopword Lib
        self.swLibList = [line.rstrip('\n') for line in open("data/stoplist/中文停用词表(1208个).txt",'r')]
        # Construct Phrase Deliminator Lib
        self.conjLibList = [line.rstrip('\n') for line in open("data/stoplist/中文分隔词词库.txt",'r')]

    # Read Target Case if Json
    def readSingleTestCases(self, testFile):
        with open(testFile) as json_data:
            try:
                testData = json.load(json_data)
            except:
                # This try block deals with incorrect json format that has ' instead of "
                data = json_data.read().replace("'",'"')
                try:
                    testData = json.loads(data)
                    # This try block deals with empty transcript file
                except:
                    return ""
        returnString = ""
        for item in testData:
            try:
                returnString += item['text']
            except:
                returnString += item['statement']
        return returnString

    def segText(self, rawText):

        # 斷詞
        rawtextList = pseg.cut(rawText)
        
        #段完詞，標點符號 的POS 會變成X

        # Construct List of Phrases and Preliminary textList
        wordList = []
        lastWord = ''
        poSPrty = ['m','x','uj','ul','mq','u','v','f']
        meaningfulCount = 0
        checklist = []
        print ("Dump Chartacters:")
        for eachWord, flag in rawtextList:
            print("{}:{}".format(eachWord, flag))
            checklist.append([eachWord,flag])
            # eachWord in conjLibList 介詞表
            # not notNumStr(eachWord) 中文數字詞
            #  eachWord in swLibList 停用詞表
            #  flag in poSPrty # 詞性表
            #  eachWord == '\n': #換行詞

            if eachWord in self.conjLibList or not notNumStr(eachWord) or eachWord in self.swLibList or flag in poSPrty or eachWord == '\n':
                # 若為以上分隔詞，則在list 中增加 '|'
                if lastWord != '|':
                    wordList.append("|")
                    lastWord = "|"
            elif eachWord not in self.swLibList and eachWord != '\n':
                wordList.append(eachWord)
                # meaningfulCount += 1
                # if eachWord not in listofSingleWord:
                #     listofSingleWord[eachWord] = Word(eachWord)
                lastWord = ''
        return wordList
        
    def rake(self, wordList):
        """
            chuckList = a list of text chucks. Each item in the chuckList is a word. 
            '|' indicates the boundry of phares
            ex :
                ['XXX', OOO","|","XX","OO","XX"]
        """

        # listofSingleWord = dict()

        for w in wordList:
            # if w not in listofSingleWord and w !="|":
                # listofSingleWord[w] = Word(w)
            if w not in self.words and w !="|":
                self.words[w] = Word(w)

        # meaningfulCount= len(listofSingleWord)
        meaningfulCount =  len(self.words)

        # Construct List of list that has phrases as wrds
        newList = []
        tempList = []
        for everyWord in wordList:
            if everyWord != '|':
                tempList.append(everyWord)
            else:
                newList.append(tempList)
                tempList = []

        tempStr = ''
        for everyWord in wordList:
            if everyWord != '|':
                tempStr += everyWord + '|'
            else:
                # if tempStr[:-1] not in listofSingleWord:
                    # listofSingleWord[tempStr[:-1]] = Word(tempStr[:-1])
                if tempStr[:-1] not in self.words:
                    self.words[tempStr[:-1]] = Word(tempStr[:-1])
                    tempStr = ''

        # Update the entire List
        for everyPhrase in newList:
            res = ''
            for everyWord in everyPhrase:
                # listofSingleWord[everyWord].updateOccur(len(everyPhrase))
                self.words[everyWord].updateOccur(len(everyPhrase))                
                res += everyWord + '|'
            phraseKey = res[:-1]
            # if phraseKey not in listofSingleWord:
                # listofSingleWord[phraseKey] = Word(phraseKey)
            if phraseKey not in self.words:
                self.words[phraseKey] = Word(phraseKey)
            else:
                # listofSingleWord[phraseKey].updateFreq()
                self.words[phraseKey].updateFreq()

        # Get score for entire Set
        outputList = dict()
        
        for everyPhrase in newList:
            #關鍵字應該不會大於5個Token
            if len(everyPhrase) > 10:
                continue
            score = 0
            phraseString = ''
            outStr = ''
            for everyWord in everyPhrase:
                # score += listofSingleWord[everyWord].returnScore()
                score += self.words[everyWord].returnScore()
                phraseString += everyWord + '|'
                # outStr += everyWord
            
            outStr = "/".join(everyPhrase)
            phraseKey = phraseString[:-1]
            # freq = listofSingleWord[phraseKey].getFreq()
            freq = self.words[phraseKey].getFreq()
            # if freq < 3:
                # continue
            # if freq / meaningfulCount < 0.01 and freq < 3 :
                # continue
            outputList[outStr] = score

        sorted_list = sorted(outputList.items(), key = operator.itemgetter(1), reverse = True)
        return sorted_list[:20]

    def run(self, rawText,segFunc=None):
        if segFunc:
           wordList = segFunc(rawText)
        else:
            wordList = self.segText(rawText)

        r= self.rake(wordList)
        return r

if __name__ == '__main__':
    rake = RakeAnalyze("stopfn.txt")
    with open('data/testCase/文本2.txt','r') as fp:
        text = fp.read()
        result = rake.run(text)
        print(result)
