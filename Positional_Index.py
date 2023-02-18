import nltk
nltk.download('punkt',quiet=True)
nltk.download("stopwords",quiet=True)
import string 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle

class Query:
    input_li = []

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

    def __init__(self,input_seq):
        input_li = self.tokenize_seq(input_seq)
        self.input_li = input_li
    
    def getQuery(self):
        return self.input_li

class Positional_Inverted_Index:
    inverted_ind = {} # {word:dict} #dict{id:list}
    document_count = 0
    name_arr = []

    def extract_text(self,s):
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
    
    def __init__(self):
        self.inverted_ind = {}
        self.document_count = 0
        self.name_arr = []

    def new_Data(self,path):
        f = open(path,"r")
        s = f.read()
        new_s = self.extract_text(s)
        new_s = new_s.lower()
        translate_table = dict((ord(char), " ") for char in string.punctuation)   
        new_s = new_s.translate(translate_table)
        f.close()
        li = word_tokenize(new_s)
        stop_words = set(stopwords.words("english"))
        filter_li = []
        for words in li:
            if(words not in stop_words):
                filter_li.append(words)
        self.addDoc(filter_li,self.document_count)
        self.name_arr.append(path)
        self.document_count+=1
    
    def addDoc(self,token_list,doc_id): #token list in order, id of parent document 
        for i in range(len(token_list)):
            key = token_list[i]
            if(key in self.inverted_ind.keys()):
                dict = self.inverted_ind[str(key)]
                if(int(doc_id) not in dict.keys()):
                    dict[int(doc_id)] = [i]
                else:
                    dict[int(doc_id)].append(i)
            else:
                dict = {}
                dict[int(doc_id)] = [i]
                self.inverted_ind[str(key)] = dict

    def getPositionalList(self,key):
        return self.inverted_ind[str(key)]
        
    def binary_search(self,arr, x):
        low = 0
        high = len(arr) - 1
        mid = 0
        while low <= high:
            mid = (high + low) // 2
            if arr[mid] < x:
                low = mid + 1
            elif arr[mid] > x:
                high = mid - 1
            else:
                return 1
        return 0
    
    def getFreq(self,key):
        return len(self.inverted_ind[key])
    
    def check_existence(self,word,document_id,position):
        if word in self.inverted_ind.keys():
            if document_id in self.inverted_ind[word].keys():
                return self.binary_search(self.inverted_ind[word][document_id],position)
            else:
                return -1
        return -2

    def processHelper(self,input_li):
        output = []
        override = 1
        if input_li[0] not in self.inverted_ind.keys():
            return output
        for cur_doc in self.inverted_ind[input_li[0]].keys():
            for cur_pos in self.inverted_ind[input_li[0]][cur_doc]:
                next_pos = cur_pos+1
                j = 1
                while(j< len(input_li)):
                    x = self.check_existence(input_li[j],cur_doc,next_pos)
                    j+=1
                    next_pos+=1
                    override = x
                    if(override <= 0):
                        break
                if(override <= -1):
                    break
                if(j == len(input_li)):
                    output.append(cur_doc)
            if(override <= -2):
                break
        return output
    
    def getOutput(self,input_seq,show_names = False):
        query = Query(input_seq)
        input_li= query.getQuery()
        input_li.append(input_li[-1])
        output = list(set(self.processHelper(input_li)))
        output.sort()
        if(show_names):
            out_list = []
            for i in output:
                out_list.append(self.name_arr[i])
            return out_list
        return output

def getNum(i):
    return (4-len(str(i)))*"0" + str(i)

try:
    invertedIndex = pickle.load(open("SaveData/positional_index_savefile.pickle", "rb"))
except:
    invertedIndex = Positional_Inverted_Index()
    for j in range(1,1401): # 1,1401
        f = invertedIndex.new_Data("Data/CSE508_Winter2023_Dataset/cranfield"+getNum(j))
    pickle.dump(invertedIndex, open("SaveData/positional_index_savefile.pickle", "wb"))

print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
n = int(input())
for i in range(n):
    inp_seq = input()
    print("Search Phrase:",inp_seq)
    output = invertedIndex.getOutput(inp_seq,show_names = True)
    print("Number of Documents Retrieved:",len(output))
    if(len(output)>0):
        print("The following documents contain your search phrase:")
        for j in range(len(output)):
            print("\t",str(j+1)+".",output[j])
    else:
        print("No matches found!")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
