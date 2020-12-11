import os
import re
import pickle

sejong_path = "C:/Users/Haseon/sejong-april/sejong-corpus/"
file_list = pickle.load(open(sejong_path+"annotation/file_list.p", "rb"))

reflist = []

for fname in file_list:
    with open(sejong_path+"corpus/"+fname, encoding='utf16') as f:
        s = f.read()
        l = s.split('\n')

    for ix, line in enumerate(l):
        if line == "<text>":
            startix = ix+1
        elif line == "</text>":
            endix = ix
            break
        else:
            pass

    fcontent = '\n'.join(l[startix:endix])
    reflist.append(fcontent)

reftxt = '\n'.join(reflist)

with open(sejong_path+"paperwork/reftxt.txt", "w") as f:
    f.write(reftxt)

