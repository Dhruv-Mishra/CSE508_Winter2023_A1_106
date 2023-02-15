import nltk
nltk.download("stopwords")
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def getNum(i):
    return (4-len(str(i)))*"0" + str(i)
for i in range(3,4): # 1,1401
    # f = open("CSE508_Winter2023_Dataset\cranfield"+getNum(i),"r")
    f = open("CSE508_Winter2023_Dataset/cranfield"+getNum(i),"r")
    s = f.read()
    print(s)
    new_s = ""
    start = [0,0] #Start is inclusive 
    end = [0,0] #End is exclusive
    for i in range(len(s)):
        if(i + 7 <= len(s) and s[i:i+7] == "<TITLE>"):
            start[0] = i+7
        elif(i + 8 <= len(s) and s[i:i+8] == "</TITLE>"):
            end[0] = i
        elif(i + 6 <= len(s) and s[i:i+6] == "<TEXT>"):
            start[1] = i+6
        elif(i + 7 <= len(s) and s[i:i+7] == "</TEXT>"):
            end[1] = i
    new_s = s[start[0]:end[0]] + " " + s[start[1]:end[1]]
    new_s = "".join(new_s.split("\n"))
    # print(new_s)
    f.close()

    print(new_s)
    li = word_tokenize(new_s)
    print(li)
    stop_words = set(stopwords.words("english"))
    print(li)

    filter_li = []
    for words in li:
        if(word not in stop_words):
            filter_li.append(word)

    print(filter_li)