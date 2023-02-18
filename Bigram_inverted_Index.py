import nltk
nltk.download('punkt',quiet=True)
nltk.download("stopwords",quiet=True)
import string 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle

class Query:
    input_li = []
    # op_li = []

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
        
        filter_li_new = []
        for i in range(len(filter_li)-1):
            filter_li_new.append(filter_li[i]+" "+filter_li[i+1])
            
        return filter_li_new

    def __init__(self,input_seq):
        input_li = self.tokenize_seq(input_seq)
        self.input_li = input_li
    
    def getQuery(self):
        return self.input_li

class Bigram_Inverted_Index:
    inverted_ind = {}
    universal_set = set()
    document_count = 0
    name_arr = []

    def __init__(self):
        self.inverted_ind = {}
        self.universal_set = set()
        self.document_count = 0
        self.name_arr = []
            
    def addDoc(self,token_list,id):
        for i in range(len(token_list)):
            key = token_list[i]
            if(key in self.inverted_ind.keys()):
                self.inverted_ind[str(key)].append(int(id))
            else:
                li = [int(id)]
                self.inverted_ind[str(key)] = li
            self.universal_set.add(int(id))

    def showWord(self,key):
        return self.inverted_ind[str(key)]
    
    def getFreq(self,key):
        return len(self.inverted_ind[key])

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
        new_li = filter_li[::]
        filter_li = []
        for i in range(len(new_li)-1):
            filter_li.append(new_li[i]+" "+new_li[i+1])
        filter_li = list(set(filter_li))
        self.addDoc(filter_li,self.document_count)
        self.name_arr.append(path)
        self.document_count+=1
    
    def processQuery(self,input_seq):
        query = Query(input_seq)
        input_li = query.getQuery()
        op_helper = []
        for i in range(len(input_li)-1):
            op_helper.append('and')
        str_qry = self.getStringQuery(input_li,op_helper)
        for i in range(len(input_li)):
            if(input_li[i] in self.inverted_ind.keys()):
                input_li[i] = self.inverted_ind[input_li[i]]
            else:
                input_li[i] = []
        output = self.query_sched(input_li,op_helper)
        return output,str_qry
    
    def getStringQuery(self,input_li,op_li):
        ans = []
        i = 0
        j = 0
        while(i < len(op_li) and j < len(input_li)):
            ans.append(input_li[j])
            j+=1
            ans.append(op_li[i])
            i+=1

        if(j < len(input_li)):
            ans.append(input_li[j])
        final_ans = " ".join(ans)
        return final_ans

    def getOutput(self,input_seq, show_names = False):
        output,str_qry = self.processQuery(input_seq)
        print("Input Query:",str_qry)
        # print(str_qry)
        # print("Number of Documents:",len(output[0]))
        # print("Document IDs:",*output[0])
        # print("Number of comparisons for fetching result:",comp_ans)
        if(show_names):
            fin_out = []
            for i in output[0]:
                fin_out.append(self.name_arr[i])
            return fin_out
        return output[0]

    def query_sched(self,input_li,op_li): #input_li is list of lists, each list in input_li is the doc_list of a regex
        if(len(op_li) == 0):
            return input_li
        elif(op_li[0] == "and"):
            output = self.query_and(input_li[0],input_li[1])

        new_l = [output]+ input_li[2:]
        return self.query_sched(new_l,op_li[1:])

    def query_and(self,t1,t2):
        t1_li = t1
        t2_li = t2
        merge_li = []
        st = 0
        st2 = 0
        while(st<len(t1_li) and st2 < len(t2_li)):
            if(t1_li[st] == t2_li[st2]):
                merge_li.append(t1_li[st])
                st +=1
                st2 +=1
            elif(t1_li[st]<t2_li[st2]):
                st +=1
            else:
                st2+=1
        return merge_li

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

def getNum(i):
    return (4-len(str(i)))*"0" + str(i)

try:
    invertedIndex = pickle.load(open("SaveData/bigram_index_savefile.pickle", "rb"))
except (OSError, IOError) as e:
    invertedIndex = Bigram_Inverted_Index()
    for j in range(1,1401): # 1,1401
        f = invertedIndex.new_Data("Data/CSE508_Winter2023_Dataset/cranfield"+getNum(j))
    pickle.dump(invertedIndex, open("SaveData/bigram_index_savefile.pickle", "wb"))

print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# print(inverted_ind)
n = int(input())
for i in range(n):
    inp_seq = input()
    print("Search Phrase:",inp_seq)
    output = invertedIndex.getOutput(inp_seq, show_names = True)
    # output = invertedIndex.getOutput(inp_seq,show_names = True)
    print("Number of Documents Retrieved:",len(output))
    if(len(output)>0):
        print("The following documents contain your search phrase:")
        for j in range(len(output)):
            print("\t",str(j+1)+".",output[j])
    else:
        print("No matches found!")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
