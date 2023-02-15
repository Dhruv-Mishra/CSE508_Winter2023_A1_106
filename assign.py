import nltk
nltk.download('punkt')
nltk.download("stopwords")
import string 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle

class Query:
    input_li = []
    op_li = []

    def tokenize_seq(self,new_s):
        new_s = new_s.lower()
        translate_table = dict((ord(char), " ") for char in string.punctuation)   
        new_s = new_s.translate(translate_table)
        li = word_tokenize(new_s)
        stop_words = set(stopwords.words("english"))
        filter_li = []
        for words in li:
            if(words not in stop_words):
                filter_li.append(words)
        return filter_li

    def __init__(self,input_seq,op_seq):
        input_li = self.tokenize_seq(input_seq)
        op_li = op_seq.split(",")
        for i in range(len(op_li)):
            op_li[i] = op_li[i].strip()
        self.input_li = input_li
        self.op_li = op_li
    
    def getQuery(self):
        return self.input_li,self.op_li
        

class Inverted_index:
    inverted_index = {}

    def __init__(self):
        self.inverted_ind = {}
    
    def addDoc(self,key,id):
        if(key in self.inverted_ind.keys()):
            self.inverted_ind[str(key)].append(int(id))
        else:
            li = [int(id)]
            self.inverted_ind[str(key)] = li

    def showWord(self,key):
        return self.inverted_ind[str(key)]
    
    def getFreq(self,key):
        return len(self.inverted_ind[key])
    
    def processQuery(self,input_seq,op_seq):
        query = Query(input_seq,op_seq)
        input_li,op_li = query.getQuery()


    def query_and(t1,t2):
        t1_li = self.showWord(t1)
        t2_li = self.showWord(t2)
        merge_li = []
        st = 0
        sr2 = 0
        while(st<len(t1_li) and st2 < len(t2_li)):
            if(t1_li[st] == t2_li[st2]):
                merge_li.append(t1_li[st])
                st +=1
                st2 +=1
            elif(t1_li[st]<t2_li[st2])
                st +=1
            else:
                st2+=1
        return merge_li
    

     def query_or(self,a,b):
        a_list = self.showWord(a)
        b_list = self.showWord(b)
        ait = 0
        bit = 0
        output = []
        while(ait < len(a_list) and bit < len(b_list)):
            if(a[ait] < b[bit]):
                output.append(a[ait])
                ait+=1
            elif(a[ait] == b[bit]):
                output.append(a[ait])
                ait+=1
                bit+=1
            else:
                output.append(b[bit])
                bit+=1
        while(a[ait] < len(a_list)):
            output.append(a[ait])
            ait+=1
        while(b[bit] < len(b_list)):
            output.append(b[bit])
            bit+=1
        return output 






def extract_text(s):
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
    new_s = " ".join(new_s.split("\n"))
    new_s = " ".join(new_s.split("-"))

    return new_s

def getNum(i):
    return (4-len(str(i)))*"0" + str(i)

inverted_index = Inverted_index()
for j in range(3,4): # 1,1401
    f = open("CSE508_Winter2023_Dataset/cranfield"+getNum(j),"r")
    s = f.read()
    #print("Original File:",s)
    new_s = extract_text(s)
    print("Baisc Text Extraction:",new_s)
    new_s = new_s.lower()
    print("Converting to Lowercase:",new_s)
    translate_table = dict((ord(char), " ") for char in string.punctuation)   
    new_s = new_s.translate(translate_table)
    print("After Removal of Punctuation:",new_s)
    f.close()
    li = word_tokenize(new_s)
    print("Tokenizing the string:",end = " ")
    print(li)
    stop_words = set(stopwords.words("english"))
    filter_li = []
    for words in li:
        if(words not in stop_words):
            filter_li.append(words)
    print("Filtering Stopwords:",filter_li)
    filter_li = list(set(filter_li))
    for token in filter_li:
        inverted_index.addDoc(token,getNum(j))

print(inverted_index.inverted_ind)
with open('file.pkl', 'wb') as file:
    pickle.dump(inverted_index,file)

