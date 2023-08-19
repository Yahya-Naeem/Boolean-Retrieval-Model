#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
ps = PorterStemmer()
def merge_corpus(corpus):
    i = 0 
    j = 0
    index = 0
    temp = corpus
    #this corpus will hold filtered data
    processed_corpus = []
    while i<len(corpus):
        #index to keep track of corpus length , an additional argument 
        index+=1
        #iteerable for inner loop
        j=i+1
        new_tuple = (index,corpus[i][1],{corpus[i][3]:[corpus[i][2]]})
        #comparing term[i] with term[j] that is changing with variable j until next term is diffferent 
        while j<len(corpus) and temp[i][1] == temp[j][1] :
            #as the terms will be equal , check document next 
            #new_tuple = (index,corpus[i][1],corpus[i][2],{})
            #same doc then we will simple extend the doc,positional index list
            if(temp[i][3] == temp[j][3]):
                #assigning preexisting doc with extended positional index list
                new_tuple[2][temp[i][3]].extend([temp[j][2]])
            #if docs are different
            else:
                #we'll make new key and provide the value of positional index 
                new_tuple[2][temp[j][3]] = ([temp[j][2]])
            #at the end increment the inner loop variable by 1
            j+=1
        i=j
        #as the inner loop as assesed the procedure for one term we will now append it to main corpus that'll used for query processing
        processed_corpus.append(new_tuple)
    return(processed_corpus)
#for applying stemming
def function_ps(p_corpus):
    i = 0 
    j = 0
    index = 0
    #storing stemmed words in 
    temp = [(p[0],ps.stem(p[1]),p[2]) for p in p_corpus]
    #this corpus will hold filtered data
    main_corpus = []
    while i<len(p_corpus):
        #index to keep track of corpus length , an additional argument 
        index+=1
        #iteerable for inner loop
        j=i+1
        new_tuple = (index,ps.stem(p_corpus[i][1]),p_corpus[i][2])
        #comparing term[i] with term[j] that is changing with variable j until next term is diffferent 
        while j<len(p_corpus) and ps.stem(temp[i][1]) == ps.stem(temp[j][1]) :
            #as the terms will be equal , check document next 
            #new_tuple = (index,corpus[i][1],corpus[i][2],{})
            #this loop will iterate through keys in next tuple and check if it exist in main tuple(common tupple) 
            for key in temp[j][2]:
                if key in temp[i][2]:
                    new_tuple[2][key].extend(temp[j][2][key]) #temp[j][2][key] = positional indexes
                else:
                    new_tuple[2][key] = temp[j][2][key]
            j+=1
        i=j
        #as the inner loop as assesed the procedure for one term we will now append it to main corpus that'll used for query processing
        main_corpus.append(new_tuple)
    return(main_corpus)
#data retrieved stemmed sorted 
def function_dataset():
    with open("Stopword-List.txt","r") as f:
        temp = f.read()
        sw = word_tokenize(temp)
    corpus = []
    index = 0
    doc = []
    for i in range(1,31):
        with open(f'{i}.txt', 'r') as f:
            content = f.read()
            words = word_tokenize(content)
            #removing stopwords and saving token in each document index in 2d list 
            doc.append([w.lower() for w in words if w.lower() not in sw])
            for j,t in enumerate(doc[i-1]):
                #saving tuples as (term , position in document , document _id) for every document 
                index +=1
                #corpus((indexofterm,term , position ,docid),())
                corpus.append((index,doc[i-1][j],j+1,i))
    corpus = ((p[0],ps.stem(p[1]),p[2],p[3]) for p in corpus)    
    corpus = sorted(corpus, key=lambda x: x[1])
    global processed_corpus
    processed_corpus = merge_corpus(corpus)

#_________________________QUEURY PROCESSING__________________________________________________ 
def fetch_plist(term):
    for i,t in enumerate(processed_corpus):
        if(term == t[1]):
            return t[2]       #returns dictionary doc :[ positional indexes ]
    # Term not found in the corpus, return an empty dictionary
    return {}

        #1- BOOLEAN QUERIES
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx_____NOT_____xxxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 
def eval_not(query):
    j=0
    new_list = []
    flag = False
    all_docs = [i for i in range(1,31)]
    for index,i in enumerate(query):
        if i == 'NOT':
            #complement
            query[index:index+2] = [list(set(all_docs)-set(query[index+1]))]
    return  query

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx_____AND_____xxxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 
def perform_and(list1,list2):
    #using sets functionality of intersection
    intersection = list(set(list1).intersection(set(list2)))
    return intersection
def eval_and(query):
    length_index=[]
    #making a list of list in which sublist contains index of fetchlist and length of fetchlist 
    for index,i in enumerate(query):
        if i != 'AND' and i != 'OR':
            length_index.append([index,len(i)])
    #sorting it to implement and operation on smallest list first
    length_index = sorted(length_index,key = lambda x:x[1]) #sort with respect to length of fetchlists
    while 'AND' in query:
        for i in enumerate(length_index):
            #if len(length_index)>1 and len(query)>1:
            index , len_i = i #extracting value from tuple
            if index-1>=1 and query[index-1] == 'AND':
                #sending in function
                temp_list = perform_and(query[index-2],query[index])
                #clearing from index list
                if [index-2,len(query[index-2])] in length_index:
                    length_index.remove([index-2,len(query[index-2])])
                if [index,len(query[index])] in length_index:
                    length_index.remove([index,len(query[index])])
                #clearing from main query
                query[index-2:index+1] = [temp_list]
            #check for out of bounds
            elif index+2<=(len(query)-1) and query[index+1] == 'AND':
                temp_list = perform_and(query[index+2],query[index])
                #clearing from index list
                if [index-2,len(query[index-2])] in length_index:
                    length_index.remove([index-2,len(query[index-2])])
                if [index,len(query[index])] in length_index:
                    length_index.remove([index,len(query[index])])
                #clearing from main query
                query[index:index+3] = [temp_list]
    return query
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXxxxxx____OR__xxxxxxxXXXXXXXXXXXXXXXXXXXXXx
def perform_or(list1,list2):
    l = [list(set(list1) | set(list2))]
    return l
def eval_or(query):
    while 'OR' in query:
        for index,term in enumerate(query):
            if term == 'OR':
                temp = perform_or(query[index-1],query[index+1])
                query[index-1:index+2] = temp
    return query
#-----------------------------------------Boolean query----------------------------------------
def bq():
    oper = ['AND','OR','NOT']
    term_list = [] #list of only terms from query
    term_pl = {}   #dictionary with terms and posting list
    plist = []     #posting list to be outputed
    o_q = []
    print("Write ,AND OR NOT operation in capital letters")
    query = input("Enter Query with each space between each term :-> ")
    o_q = query
    query = word_tokenize(query)
    #fetch posting list for each term 
    for i in query:
        if i not in oper:
            #appending a stemmed 
            i = i.lower()
            i = ps.stem(i)
            term_list.append(i)
            
    for i in term_list:
        L = fetch_plist(i)
        term_pl[i] = list(L.keys())
    #replacing terms with fetch lists
    for j,term in enumerate(query):
        if term in term_pl:
            query[j] = term_pl[term]
            
    #query has only one term
    if(len(query)==1):
        plist = term_pl[term_list[0]]
        
    #2 terms means Not operator used with one term 
    elif(len(query)==2 and query[0]=="NOT"):
        for i in range(1,31):
            if i not in term_pl[term_list[0]]:
                plist.append(i)
     # more then one term apply complexity check
    else:
        query = eval_not(query)
        #apply and
        query = eval_and(query)
        #apply or
        plist = eval_or(query)        
    print(o_q," exist in following Documents : ")
    if len(plist) == 0:
        print("No results Found ")
    else:
        for i in plist:
            print("Document ",i)
    #if user want to query again
    print("\n")
    menu()
#__________________________________________proximity query_____________________________  
def skiplist(p1,p2,d):
    i=0
    j=0
    while i<len(p1) and j<len(p2):
        #check if distance condition true return 
        if(abs(p1[i]-p2[j])<=d):
            return True
        elif(p1[i]>p2[j]):
            j = j+1
        elif(p1[i]<p2[j]):
            i = i+1
    return False
def pq():
    plist = []
    t = [] #temp list for operations
    query = input("Enter query , only for two terms as term1 term2 / distance : ")
    query = word_tokenize(query)
    query = [i.lower() for i in query]
    t_1 = [ps.stem(i) for i in query]
    distance = int(query[3])
    for i in range(2):
        temporary = fetch_plist(t_1[i])
        t.append(temporary)
    #common docs and then apply skip list
    common_k = t[0].keys() & t[1].keys()
    for j in common_k:
        p1 = sorted(t[0][j]) #positional index of first term t[termid][key] it will give positional index 
        p2 = sorted(t[1][j])  #positional index for second term
        #check if difference exist is in range , use proximity query 
        if(skiplist(p1,p2,distance)):
            plist.append(j) #get doc id in outputlist
    print("posting list for ",query," -> ",plist)
    print("\n")
    menu()

#user menu
def menu():
    print("1 - Proximity Queries \n2 - Boolean Queries\n3 - Exit")
    flag = True
    while flag:
        t = int(input("Enter Option : "))
        print("\n")
        if(t==1):
            pq()
            flag=False 
        elif(t==2):
            bq()
            flag=False
        elif(t==3):
            flag = False
        else:
            print("Wrong Choice Re-enter")
            flag=True
        #####_____MAIN____
#preprocessing Files 
function_dataset()
print("Dataset evaluated")
menu()

