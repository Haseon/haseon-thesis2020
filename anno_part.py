import csv
from random import randint
from os.path import isfile
import datetime
import pickle

class anno_machine:
    def __init__(self, workpath=None, part_csv_path=None, init_csv_path=None, 
            reftxt_path=None, history_path=None, stride_path=None):
        # setting paths
        if workpath == None:
            from os.path import getcwd
            workpath = getcwd() + "/"
        if part_csv_path == None:
            part_csv_path = workpath+"part.csv"
        if init_csv_path == None:
            init_csv_path = workpath+"init.csv"
        if reftxt_path == None:
            reftxt_path = workpath+"reftxt.txt"
        if history_path == None:
            history_path = workpath+"history.p"
        if stride_path == None:
            stride_path = workpath+"stride.p"
        # read part.csv if there is one, otherwise read init.csv
        if isfile(part_csv_path):
            src_csv_path = part_csv_path
        elif isfile(init_csv_path):
            src_csv_path = init_csv_path
        else:
            raise FileNotFoundError(f"file '{init_csv_path}' does not exist.")
        self.save_path = part_csv_path
        self.history_path = history_path

        with open(src_csv_path, "r", newline='') as src_csv:
            self.srcL = list(csv.DictReader(src_csv))

        self.fieldnames = list(self.srcL[0].keys())

        #load reftxt
        self.analyzed_tokens = []
        self.unanalyzed_tokens = []
        with open(workpath+"reftxt.txt", "r") as rf:
            for line in rf:
                tline = line.split('\t')
                if len(tline) >= 3:
                    self.analyzed_tokens.append(tline[2][:-1])
                    self.unanalyzed_tokens.append(tline[1])
                else:
                    self.analyzed_tokens.append(tline[1][:-1])
                    self.unanalyzed_tokens.append('')
        #load history
        if isfile(history_path):
            with open(history_path, 'rb') as hf:
                self.history = pickle.load(hf)
        else:
            self.history = []
        self.historyix = self.historylen = len(self.history)
        #initialize some variables
        self.annotation = {} #{line_num: case}
        self.partlist = ["JKS" #nominative/subjective
                        ,"JKC" #complementative
                        ,"JKG" #gwanhyeonggyeok
                        ,"JKO" #accusative/objective
                        ,"JKB" #busagyeok
                        ,"JKV" #vocative
                        ,"JKQ" #quotative
                        ,"JX"  #bojosa
                        ,"JC"  #conjunctive
                        ,"NJ"  #cannot be particled
                        ]
        #{case: number_of_cases}
        self.tag_stats = {part: 0 for part in self.partlist}
        self.non_tag_stats = {part: 0 for part in self.partlist}
        self.number_of_unparticled = 0
        if src_csv_path == part_csv_path:
            for d in self.srcL:
                if d["tagged"] != '' and int(d["tagged"]):
                    self.annotation.update({int(d["line_num"]): d["case"]})
                    self.tag_stats[d["case"]] += 1
                elif int(d["particled"]):
                    self.non_tag_stats[d["case"]] += 1
                else:
                    self.number_of_unparticled += 1
        else:
            for d in self.srcL:
                if int(d["particled"]):
                    self.non_tag_stats[d["case"]] += 1
                else:
                    self.number_of_unparticled += 1
        self.workix = 0
        self.tokenlen = len(self.unanalyzed_tokens)
        self.srcLlen = len(self.srcL)
        if isfile(stride_path):
            with open(stride_path, "rb") as sf:
                self.stride_path = pickle.load(sf)
        else:
            self.stride = 10
   
    def interact(self):
        reselect = True
        should_show = True
        while True:
            if self.historyix < self.historylen:
                self.workix = self.history[self.historyix][1]
            elif reselect:
                self.select_line()
            else:
                pass
            if should_show:
                self.show_item()
            command = input("<Command>:")
            if command == '?':
                print("""? : 도움말
                p : 전으로 가기, n : 다음으로 가기
                h (숫자) : 역사 주소 직접 지정
                hlast : 역사 최신 주소로, hview: 역사 보기
                r : 다시 뽑기, s : 현재 대상 다시 보기
                stride (숫자) : 보기 폭  재설정
                save : 저장, quit : 끄기
                JKS : 주격 조사
                JKC : 보격 조사
                JKG : 관형격 조사
                JKO : 목적격 조사
                JKB : 부사격 조사
                JKV : 호격 조사
                JKQ : 인용격 조사
                JX : 보조사
                JC : 접속 조사
                NJ : 조사가 붙을 수 없음
                """)
                reselect = False
                should_show = False
            elif command == 'p':
                if self.historyix >= 0:
                    self.historyix -= 1
                reselect = False
                should_show = True
            elif command == 'n':
                if self.historyix < self.historylen:
                    self.historyix += 1
                reselect = False
                should_show = True
            elif command[0:2] == 'h ':
                try:
                    ix = int(command[2:])-1
                    if 0 <= ix <= self.historylen:
                        self.historyix = ix
                    else:
                        print("Error: Invalid history index.")
                except:
                    print(f"ValueError: {command[2:]} could not be cast into int.") 
                reselect = False
                should_show = True
            elif command == 'hlast':
                self.historyix = self.historylen
                reselect = True
                should_show = True
            elif command == 'hview':
                hix = self.historyix
                start = max(0, self.historyix-20)
                end = min(self.historylen, self.historyix+20)
                prev = '\n'.join(str(e) for e in self.history[start:hix])
                if hix < self.historylen:
                    curr = "\n ---> "+str(self.history[hix]) + "\n"
                    nxt = '\n'.join(str(e) for e in self.history[hix+1:end])
                else:
                    curr = "\n ---> "
                    nxt = ""
                #print('\n'.join(str(e) for e in self.history[start:end]))
                print(prev+curr+nxt)
                reselect = False
                should_show = False
            elif command == 'r':
                self.select_line()
                self.show_item()
                reselect = False
                should_show = False
            elif command == 's':
                self.show_item()
                reselect = False
                should_show = False
            elif command == 'save':
                self.save()
                reselect = False
                should_show = False
            elif command[:7] == 'stride ':
                try:
                    strd = int(command[7:])
                    if 1 <= strd <= 100:
                        self.stride = strd
                        print("Now the view span is ", strd)
                    else:
                        print("Stride should be between 1 and 100.")
                except:
                    print(f"ValueError: {strd} cannot be cast into int.")
                reselect = False
                should_show = True
            elif command == 'quit':
                break
            elif command in self.partlist:
                if self.historyix == self.historylen:
                    self.annotate(self.workix, command)
                    self.historylen += 1
                else:
                    self.annotate(self.workix, command, self.historyix)
                self.historyix += 1
                reselect = True
                should_show = True
            else:
                print("Error: Invalid command.")
                reselect = False
                should_show = True

    def select_line(self):
        #function that selects an (unparticled) item to annotate from reftxt
        # IO Int (line_num) 
        while True:
            i = randint(0, self.srcLlen-1)
            line_num = int(self.srcL[i]["line_num"])
            particled = bool(int(self.srcL[i]["particled"]))
            if particled:
                continue
            if line_num not in self.annotation.keys():
                break

        self.workix = line_num

    def annotate(self, line_num, case, hix_revised=None):
        #function that leads users to annotate an item 
        #users can tag omitted particles to the items or just pass
        # line_num -> case -> IO ()
        self.annotation.update({line_num: case})
        if hix_revised != None:
            self.tag_stats[self.history[hix_revised][3]] -= 1
        self.tag_stats[case] += 1
        item = self.unanalyzed_tokens[self.workix]
        total = sum(self.tag_stats.values())
        current_time = datetime.datetime.today().strftime('%c')
        # current_time can be turned back into a datetime object
        # by datetime.datetime.strptime(current_time, '%c')
        if hix_revised == None:
            self.history.append((total, line_num, item, case, current_time))
        else:
            self.history[hix_revised] = (hix_revised, line_num, item, case, current_time)
        

    def show_item(self):
        #function that shows an item and its context
        # IO ()
        i = self.workix
        s = self.stride
        print("\n\n")
        if self.historyix != self.historylen:
            print("[YOU ARE CURRENTLY REVIEWING THE PAST RECORDS]")
            print(self.history[self.historyix])
        total_tagged = sum(self.tag_stats.values())
        real_tagged = total_tagged - self.tag_stats["NJ"]
        print(f"total tagged: {total_tagged}, real tagged: {real_tagged}, total unparticled: {self.number_of_unparticled}, srcLlen: {self.srcLlen}")
        print(f"workix: {i}, historyix: {self.historyix}, historylen: {self.historylen}")
        print(', '.join("{}: {}/{}".format(j, self.tag_stats[j], self.non_tag_stats[j]) for j in self.partlist))
        lix = max(0, i-s)
        rix = min(self.tokenlen, i+s+1)
        print("{0} #<# {1} #># {2}".format(' '.join(self.unanalyzed_tokens[lix:i]), self.unanalyzed_tokens[i], ' '.join(self.unanalyzed_tokens[i+1:rix])))
        print("{0} #<# {1} #># {2}".format(' '.join(self.analyzed_tokens[lix:i]), self.analyzed_tokens[i], ' '.join(self.analyzed_tokens[i+1:rix])))

    def save(self):
        annotated_lines = self.annotation.keys()
        with open(self.save_path, "w", newline='') as part_csv:
            writer = csv.DictWriter(part_csv, fieldnames=self.fieldnames)

            writer.writeheader()
            for d in self.srcL:
                ix = int(d["line_num"])
                if ix in annotated_lines:
                    d.update({"case": self.annotation[ix]})
                    d.update({"tagged": 1})
                writer.writerow(d)

        with open(self.history_path, 'wb') as hf:
            pickle.dump(self.history, hf)
                
def main():
    wpath = "C:/Users/Haseon/sejong-april/sejong-corpus/paperwork/"
    anno = anno_machine(workpath=wpath)
    anno.interact()

if __name__ == '__main__':
    main()
