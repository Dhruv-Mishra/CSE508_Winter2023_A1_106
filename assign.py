import nltk
nltk.download('punkt',quiet=True)
nltk.download("stopwords",quiet=True)
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
        op_li = []
        first_op_li = []
        if(op_seq != ""):
            first_op_li = op_seq.split(",")
            for i in range(len(first_op_li)):
                temp_l = first_op_li[i].split()
                for j in temp_l:
                    op_li.append(j)
        for i in range(len(op_li)):
            op_li[i] = (op_li[i].strip()).lower()
        self.input_li = input_li
        self.op_li = op_li
    
    def getQuery(self):
        return self.input_li,self.op_li

class Inverted_index:
    inverted_ind = {}
    universal_set = set()
    comparisons = 0

    def __init__(self):
        self.inverted_ind = {}
        self.universal_set = set()
        self.comparisons = 0
    
    def addDoc(self,key,id):
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

    def simplify_not(self,op_seq):
        if(op_seq == []):
            return op_seq
        simplified_seq = []
        not_count = 1
        for i in range(len(op_seq)-1):
            if(op_seq[i+1] == op_seq[i] and op_seq[i] == "not"):
                not_count+=1
            else:
                if(op_seq[i] == "not"):
                    if(not_count%2 == 1):
                        simplified_seq.append(op_seq[i])
                    not_count = 1
                else:
                    simplified_seq.append(op_seq[i])
        simplified_seq.append(op_seq[len(op_seq)-1])
        return simplified_seq
    
    def processQuery(self,input_seq,op_seq):
        self.comparisons = 0
        query = Query(input_seq,op_seq)
        input_li,op_li = query.getQuery()
        op_li = self.simplify_not(op_li)
        str_qry = self.getStringQuery(input_li,op_li)
        for i in range(len(input_li)):
            if(input_li[i] in self.inverted_ind.keys()):
                input_li[i] = self.inverted_ind[input_li[i]]
            else:
                input_li[i] = []
        output = self.query_sched(input_li,op_li)
        comp_ans = self.comparisons
        self.comparisons = 0
        return output,comp_ans,str_qry
    
    def getStringQuery(self,input_li,op_li):
        ans = []
        i = 0
        j = 0
        while(i < len(op_li) and j < len(input_li)):
            if(op_li[i] == "not"):
                ans.append(op_li[i])
                i+=1
            else:
                ans.append(input_li[j])
                j+=1
                ans.append(op_li[i])
                i+=1
        if(j < len(input_li)):
            ans.append(input_li[j])
        final_ans = " ".join(ans)
        return final_ans

    def getOutput(self,input_seq,op_seq):
        output,comp_ans,str_qry = self.processQuery(input_seq,op_seq)
        print("Input Query:",str_qry)
        print("Number of Documents:",len(output[0]))
        print("Document IDs:",*output[0])
        print("Number of comparisons for fetching result:",comp_ans)

    
    def query_sched(self,input_li,op_li): #input_li is list of lists, each list in input_li is the doc_list of a regex
        if(len(op_li) == 0):
            return input_li
        elif(op_li[0] == "not"):
            output = self.query_not(input_li[0])
            return self.query_sched([output]+input_li[1:],op_li[1:])
        elif(op_li[0] == "and"):
            if(len(op_li) > 1 and op_li[1] == "not"):
                op_li[0] = "not"
                op_li[1] = "and"
                temp = input_li[0]
                input_li[0] = input_li[1]
                input_li[1] = temp
                return self.query_sched(input_li,op_li)
            else:
                output = self.query_and(input_li[0],input_li[1])
        elif(op_li[0]  == "or"):
            if(len(op_li) > 1 and op_li[1] == "not"):
                op_li[0] = "not"
                op_li[1] = "or"
                temp = input_li[0]
                input_li[0] = input_li[1]
                input_li[1] = temp
                return self.query_sched(input_li,op_li)
            else:
                output = self.query_or(input_li[0],input_li[1])
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
            self.comparisons+=1
        return merge_li

    def query_or(self,a,b):
        a_list = a
        b_list = b
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
            self.comparisons+=1
        while(a[ait] < len(a_list)):
            output.append(a[ait])
            ait+=1
        while(b[bit] < len(b_list)):
            output.append(b[bit])
            bit+=1
        return output 
    
    def query_not(self,a):
        a_set = set(a)
        output = list(self.universal_set-a_set)
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

for j in range(1,10): # 1,1401
    f = open("CSE508_Winter2023_Dataset/cranfield"+getNum(j),"r")
    s = f.read()
    #print("Original File:",s)
    new_s = extract_text(s)
    #print("Baisc Text Extraction:",new_s)
    new_s = new_s.lower()
    #print("Converting to Lowercase:",new_s)
    translate_table = dict((ord(char), " ") for char in string.punctuation)   
    new_s = new_s.translate(translate_table)
    #print("After Removal of Punctuation:",new_s)
    f.close()
    li = word_tokenize(new_s)
    #print("Tokenizing the string:",end = " ")
    #print(li)
    stop_words = set(stopwords.words("english"))
    filter_li = []
    for words in li:
        if(words not in stop_words):
            filter_li.append(words)
    #print("Filtering Stopwords:",filter_li)
    filter_li = list(set(filter_li))
    for token in filter_li:
        inverted_index.addDoc(token,getNum(j))

n = int(input())
for i in range(n):
    inp_seq = input()
    op_seq = input()
    output = inverted_index.getOutput(inp_seq,op_seq)
with open('file.pkl', 'wb') as file:
    pickle.dump(inverted_index,file)
