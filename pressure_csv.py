import csv
import re
from math import log
import random
import time

workpath = "C:/Users/Haseon/sejong-april/sejong-corpus/paperwork/"

print(time.ctime())
import pickle
with open("relfreq.pickle", "rb") as rp:
    relfreq = pickle.load(rp)
    logfreq = [log(i) for i in relfreq]
del pickle

def find_best_score(a):
    best_score = float("-inf")
    for n in range(2**(len(a)-1)):
        brepr = bin(n)[2:]
        size = len(a)-1
        blist = [bool(int(i)) for i in "0"*(size-len(brepr))+brepr]
        score = 0
        buff = a[0]
        for i, b in enumerate(blist, start=1):
            if b:
                buff+=a[i]
            else:
                try:
                    score += logfreq[buff-1]
                    buff = a[i]
                except:
                # drop it from the data if it exceeds the max syllable length
                    continue
        if best_score < score:
            best_score = score
    return best_score

#read init.csv
with open(workpath+"init.csv", "r", newline='') as init_csv:
    initL = list(csv.DictReader(init_csv))

fieldnames = list(initL[0].keys())

#load reftxt and creat syllens_list
stc_ix = 0
word_ix = 0
syllens_list = []
syllens = []
tokens = []
tokens_stc_ix = []
with open(workpath+"reftxt.txt", "r") as rf:
    for line in rf:
        tline = line.split('\t')
        if re.search("</s>", tline[1]):
            stc_ix += 1
            word_ix = 0
            syllens_list.append(syllens)
            syllens = []
            tokens.append(None)
        elif len(tline) >= 3:
            word = re.sub("<phon>[^<]+</phon>", "", tline[2])
            word = re.sub("<[^<]+>", "", tline[2])
            word = re.sub("\+[^\+/]+/J[^\+/]+", "", word)
            syllens.append(len(word))
            tokens.append({"word":word, "stc_ix":stc_ix, "word_ix":word_ix})
            word_ix += 1
        else:
            tokens.append(None)

print(time.ctime())
our_sample = []
for d in initL:
    if not int(d["particled"]) and int(d["tagged"]) and not int(d["last_word"]):
        our_sample.append(d["ID"])
our_sample += random.sample(initL, 1000)
while len(our_sample) < 2000:
    your_sample = random.sample(initL, 2000)
    for d in your_sample:
        if not int(d["last_word"]):
            our_sample.append(d["ID"])
        if len(our_sample) <= 2000:
            break

print(time.ctime())
print(len(syllens_list))
#tag surprisals from the table and save it as surp.csv
with open("pressure.csv", "w", newline='') as surp_csv:
    writer = csv.DictWriter(surp_csv, fieldnames=fieldnames)

    writer.writeheader()
    n = 0
    for d in our_sample:
        n += 1
        print(n, end='')
        ix = int(d["line_num"])
        print(":", end='')
        syllens = syllens_list[tokens[ix]["stc_ix"]]
        print(syllens, '')
        print(time.ctime())
        word_ix = tokens[ix]["word_ix"]
        syllens_ = syllens[:word_ix] + [syllens[word_ix]+1] + syllens[word_ix+1:]
        pressure = find_best_score(syllens) - find_best_score(syllens_)

        d.update({"pseudo_ap_pressure1": pressure})

        writer.writerow(d)
            
