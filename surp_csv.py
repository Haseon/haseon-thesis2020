import csv
import re
from math import log

workpath = "C:/Users/Haseon/sejong-april/sejong-corpus/paperwork/"

#read init.csv
with open(workpath+"init.csv", "r", newline='') as init_csv:
    initL = list(csv.DictReader(init_csv))

fieldnames = list(initL[0].keys())

#load reftxt
tokens = []
with open(workpath+"reftxt.txt", "r") as rf:
    for line in rf:
        tline = line.split('\t')
        if len(tline) >= 3:
            tokens.append(tline[2])
        else:
            tokens.append(None)

#calculate the ngram table
dicts = [[{},{},{}]]
unidic = {}
bidic = {}
tridic = {}
for d in initL:
    if not int(d["last_word"]):
        ix = int(d["line_num"])
        if not int(d["first_word"]):
            #previous word
            pw = re.search('[^\+]+$', tokens[ix-1]).group()
        #next word
        try:
            nw = re.search('^[^\+]+', tokens[ix+1]).group() 
        except:
            print(d["last_word"], tokens[ix-10:ix], " {{ ", tokens[ix], " }} ## ", tokens[ix+1], " ## ", tokens[ix+2:ix+12])
            raise Error
        #current word
        if int(d["particled"]):
            cw = re.search('((^|\+)[^\+]+\/[^J][^\+]+)+', tokens[ix]).group()
        else:
            cw = tokens[ix]
        if (not int(d["first_word"]) and not re.search('/S', pw)):
            if tridic.get((pw, cw)) == None:
                tridic.update({(pw, cw): {}})
            tridic.get((pw, cw)).update({nw: tridic.get((pw, cw)).get(nw, 0)+1})

        if bidic.get(cw) == None:
            bidic.update({cw: {}})
        bidic.get(cw).update({nw: bidic.get(cw).get(nw, 0)+1})

        unidic.update({nw: unidic.get(nw, 0)+1})

#tag surprisals from the table and save it as surp.csv
PUw = sum(unidic.values())-1
with open("surp.csv", "w", newline='') as surp_csv:
    writer = csv.DictWriter(surp_csv, fieldnames=fieldnames)

    writer.writeheader()
    for d in initL:
        ix = int(d["line_num"])
        cw = re.search('((^|\+)[^\+]+\/[^J][^\+]+)+', tokens[ix]).group()
        # surprisal = log(1/P(w|...))
        if not int(d["last_word"]):
            nw = re.search('^[^\+]+', tokens[ix+1]).group() 
            if not int(d["first_word"]):
                pw = re.search('[^\+]+$', tokens[ix-1]).group()

                if tridic.get((pw, cw))  != None \
                and tridic[(pw,cw)].get(nw) != None \
                and tridic[(pw,cw)][nw] != 1:

                    Ppwcwnw = tridic[(pw,cw)][nw]-1
                    Ppwcw = sum(tridic[(pw,cw)].values())-1
                    s = log(Ppwcw/Ppwcwnw)
                    d.update({'surprisal': s})

            elif bidic.get(cw) != None \
            and bidic[cw].get(nw) != None \
            and bidic[cw][nw] != 1:

                Pcwnw = bidic[cw][nw]-1
                Pcw = sum(bidic[cw].values())-1
                s = log(Pcw/Pcwnw)
                d.update({'surprisal': s})

            elif unidic.get(nw) != None \
            and unidic[nw] != 1:
                
                Pnw = unidic[nw]-1
                # Uw == sum(unidic.values())-1
                s = log(PUw/Pnw)
                d.update({'surprisal': s})

            else:
                pass

            writer.writerow(d)
                
