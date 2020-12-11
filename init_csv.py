import csv
import re
from math import log

rpath = "C:/Users/Haseon/sejong-april/sejong-corpus/paperwork/reftxt.txt"
wpath = "C:/Users/haseon/sejong-april/sejong-corpus/paperwork/init.csv"

import pickle
with open("relfreq.pickle", "rb") as rp:
    relfreq = pickle.load(rp)
    logfreq = [log(i) for i in relfreq]
    lenfreq = len(logfreq)
    diffreq = [a-b for a, b in zip(logfreq[:-1], logfreq[1:])]
del pickle

with open(rpath, "r") as rf:
    reflist = rf.readlines()

with open(wpath, "w") as wf:
    fields = ['ID', 'line_num', 'noun_num', 'particled', 'case', 'tagged', 'syl_length', 'first_word', 'second_word', 'last_word', 'surprisal1', 'surprisal2', 'pw_pressure1', 'pw_pressure2', 'pseudo_ap_pressure1', 'pseudo_ap_pressure2']

    writer = csv.DictWriter(wf, fieldnames=fields)
    writer.writeheader()

    noun_num = 0
    rows = []
    nth_word = -1
    the_last_noun_is_the_last_word = 0

    for i, line in enumerate(reflist):
        tline = line.split('\t')
        if len(tline) == 3:
            nth_word += 1
            if re.search('(/N[^+]+|/XSN|/ETN)$', tline[2]):
                particled = 0
                case = ''
                the_last_noun_is_the_last_word = 1
            elif re.search('(/N[^+]+|/XSN|ENT)\+[^+]*/J[^+]+$', tline[2]):
                particled = 1
                case = tline[2].split('/')[-1][:-1]
                jlen = 0
                jlist = re.findall('[^\+/]+/J[^+/]+', tline[2])
                jlist = [re.search('^[^/]+', j).group() for j in jlist]
                for j in jlist:
                    if j in 'ㄴㄹㅔㅣ':
                        jlen += 0
                    else:
                        jlen += len(j)
                the_last_noun_is_the_last_word = 1
            else:
                the_last_noun_is_the_last_word = 0
                continue

        else:
            if len(rows) >= 1:
                if the_last_noun_is_the_last_word:
                    rows[-1].update({"last_word": 1})
                for row in rows:
                    writer.writerow(row)
                rows = []
            nth_word = -1
            the_last_noun_is_the_last_word = 0
            continue

        ref_id = tline[0]
        word = re.sub("<phon>[^<]+</phon>", "", tline[1])
        word = re.sub("<[^<]+>", "", word)
        syl_length = len(word) - jlen
        if particled and syl_length > lenfreq:
            pw_pressure = ''
        elif particled:
            pw_pressure = str(logfreq[syl_length]-logfreq[syl_length+jlen])
        elif syl_length+1 > lenfreq:
            pw_pressure = ''
        else:
            pw_pressure = str(diffreq[syl_length-1])

        first_word = int(nth_word == 0)
        second_word = int(nth_word == 1)
        tagged = particled

        rows.append({"ID": ref_id, "line_num": i, "noun_num": noun_num, "particled": particled, "case": case, "tagged": tagged, "syl_length": syl_length, "first_word": first_word, "second_word": second_word, "last_word": 0, 'pw_pressure1': pw_pressure})
        noun_num += 1
        
