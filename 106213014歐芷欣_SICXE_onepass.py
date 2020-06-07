from collections import defaultdict
OPTAB = defaultdict(dict) # opTable
data = []
pseudoCode = ['START', 'END', 'BASE','RESB','RESW','WORD','BYTE']
SYMTAB = {}
Mrecord = []
error = 0
errorMsg = []
base = -1
def opTable():
    # 讀入 opCode 檔案
    global OPTAB
    with open('opCode.txt', 'r') as file :
    # 一行一行讀入 
        linesOfData = file.readlines()
    # data[ <key> ] = <data>
    # 一個 key 會對應到一個 資料
    for i in linesOfData :
        # 用空白切割
        tmp = i.split()
        OPTAB[tmp[0]]['format'] = tmp[1]
        OPTAB[tmp[0]]['opCode'] = tmp[2]
def token(dataForLine):
    # 切割好的會有三種格式
    # TEST LDCH BUFFER, X -> label + mnemonic + operand
    #      LDA  DATA      -> mnemonic + operand
    #      RSUB           -> mnemonic
    label = ''
    mnemonic = ''
    operand = ''
    if len(dataForLine) == 3:
        label = dataForLine[0]
        mnemonic = dataForLine[1]
        operand = dataForLine[2]
    elif len(dataForLine) == 2:
        mnemonic = dataForLine[0]
        operand = dataForLine[1]
    elif dataForLine[0] == 'RSUB':
        mnemonic = dataForLine[0]
    return label, mnemonic, operand
def checkLines(line):
    # lines 為 讀入的資料們 (一行為一個單位)
    # 資料前處理 將資料做切割
    data = []
    # 忽略註解
    # 當有 '.' 出現 代表 '.'之後的內容為註解
    # 從資料最後項開始刪除 直到把 '.' 不存在為止
    while '.' in line:
        line = line[:-1]
    # 將 \n 從資料列中刪除
    line = line.strip()
    # 資料分割方式有 空白 或 TAB (\t)
    # 當有 TAB 時 
    if '\t' in line : 
        # There is a tab in line
        # 以 TAB 做切割
        data= line.split('\t')
    # 若無 TAB 則以空白做切割
    else:
        data= line.split(' ')
        # 如果用空白切割 會造成 ', X' 被切開
        # 因此要接回去
        if data[-1] == 'X' and ',' in data[-2]:
            # 將 最後兩項接起來後 將最後一項刪除
            data[-2] = data[-2]+' X'
            data = data[:-1]
    return data
def calculateLoc(line,LOCCTR, mnemonic, operand):
    # extend +4
    global error
    try :
        if '+' in mnemonic:
            LOCCTR += 4
        elif mnemonic == 'END': # 避免 PCTR 進入 exception
            return LOCCTR
        elif mnemonic == 'RESB':
            LOCCTR += int(operand)
        elif mnemonic == 'RESW':
            LOCCTR += 3 * int(operand)
        elif mnemonic == 'BASE':
            return LOCCTR
        elif mnemonic == 'WORD':
            LOCCTR += 3
        elif mnemonic == 'BYTE':
            if operand.startswith('C'):
                LOCCTR += len(operand.strip("C'"))
            elif operand.startswith('X'):
                # tmp = ''.join([x for x in operand if x.isdigit()])
                LOCCTR += 1
        elif '3' in OPTAB[mnemonic]['format']:
            LOCCTR += 3
        else:
            LOCCTR += int(OPTAB[mnemonic]['format'])
        return LOCCTR
    except KeyError:
        error += 1
        errorMsg.append(line +' ERROR : ' + ' mnemonic error' )
class Line:
    def __init__(self, line, label, mnemonic, operand,PCTR,LOCCTR):
        self.line = line
        self.label = label
        self.mnemonic = mnemonic
        self.operand = operand
        self.PCTR = PCTR
        self.LOCCTR = LOCCTR
        self.forward = False
        self.object_prog = ''
        self.clone = [line,label,mnemonic,operand,PCTR,LOCCTR]
    def getObj(self):
        return self.object_prog
    def objectProgram(self):
        self.object_prog = ''
        REGISTERS = {'PC':'8', 'SW':'9', 'A':'0', 'X':'1','L': '2','B':'3', 'S':'4', 'T':'5', 'F':'6'}
        extend = False
        if '+' in self.mnemonic:
            self.mnemonic = self.mnemonic.strip('+ ')
            extend = True 
        if (self.mnemonic in pseudoCode) == False :
            program = int(OPTAB[self.mnemonic]['opCode'],16)
            # Format 1
            if OPTAB[self.mnemonic]['format'] == '1' :
                # 單純只有 opCode 占 1byte (2位址)
                self.object_prog = hex(program).upper()[2:].zfill(2)
                self.forward = False 
            # Format 2 以 OPTAB 中的 formate 得知
            # 占 2 byte
            elif OPTAB[self.mnemonic]['format'] == '2':
                self.object_prog = hex(program).upper()[2:].zfill(2)
                # 當後面接 2 個 register 時
                if ',' in self.operand :
                    for i in self.operand.split(','):
                        self.object_prog += REGISTERS[i]
                # 只有一個 register 後面要補 0
                else:
                    self.object_prog += REGISTERS[self.operand]
                    self.object_prog += '0'
                self.forward = False
            # SIC/XE
            # 分成 
            # base relative + 4 / PC relative + 2 / direct + 0 /
            # index - base + C / index - PC + A 
            else:
                # SIC/XE opCode + 3
                if '@' in self.operand:
                    program += 2
                    
                    self.object_prog = hex(program)[2:].upper().zfill(2)
                    self.operand = self.operand.strip('@')
                elif '#' in self.operand:
                    program += 1
                    
                    self.object_prog = hex(program)[2:].upper().zfill(2)
                    self.operand = self.operand.strip('#')
                else:
                    program += 3
                    
                    self.object_prog = hex(program).upper()[2:].zfill(2)
                #-------------------------------------------#
                
                # direct addressing
                if self.operand.isdigit():
                    # Extend 
                    if extend:
                        self.object_prog += '1'
                        self.object_prog += hex(int(self.operand)).upper()[2:].zfill(5)
                        self.forward = False
                        return self.object_prog
                    else:
                        self.object_prog += '0'
                        self.object_prog += hex(int(self.operand)).upper()[2:].zfill(3)
                        self.forward = False
                    
                # indexed Addressing (PC/base)
                elif ',' in self.operand and 'X' in self.operand:
                    # 將 , 及 X 刪除 (不論中間有多少空白)
                    while ',' in self.operand:
                        self.operand = self.operand[:-1]
                    # 當 SYMTAB 存在時 可直接查詢
                    if self.operand in SYMTAB.keys():
                        # Extend 
                        if extend:
                            self.object_prog += '9' # xbpe = 1001 
                            self.object_prog += hex(SYMTAB[self.operand]).upper()[2:].zfill(5)
                            Mrecord.append(self.LOCCTR+1)
                            self.forward = False
                            return self.object_prog
                        tmp = SYMTAB[self.operand] - int(self.PCTR)
                        # 當計算完在合理範圍 則使用 PC
                        # Indexed Addressing - PC relative
                        if tmp <= 2047 and tmp >= (-2048):
                            self.object_prog += 'A' # xbpe = 1010
                            if tmp < 0:
                                # 計算 2 補數
                                tmp = 4096 + tmp
                                self.object_prog += hex(tmp).upper()[2:]
                            else:
                                self.object_prog += hex(tmp).upper()[2:].zfill(3)
                            self.forward = False
                        # 範圍超過時 使用 base relative
                        # Indexed Addressing - Base relative
                        else:
                            # 要確認 base 是否存在
                            if base >= 0:
                                self.object_prog += 'C' # xbpe = 1100
                                tmp = SYMTAB[self.operand] - int(base)
                                self.object_prog += hex(tmp).upper()[2:].zfill(3)
                                self.forward = False
                            # 若 base 也是還沒定義的 label 
                            # forward == True
                            else:
                                self.forward = True
                                # 初始化
                                self.mnemonic = self.clone[2]
                                self.operand = self.clone[3]
                    # Indexed Direct addressing 
                    elif self.operand.isdigit():
                        self.object_prog += '8' # xbpe = 1000
                        self.object_prog += hex(int(self.operand)).upper()[2:].zfill(3)
                        self.forward = False
                    else:
                        self.forward = True
                        # 初始化
                        self.mnemonic = self.clone[2]
                        self.operand = self.clone[3]
                # 不是 index 單純 base / PC
                elif self.operand in SYMTAB.keys():
                    # Extend 
                    if extend:
                        self.object_prog += '1' # xbpe = 1001 
                        self.object_prog += hex(SYMTAB[self.operand]).upper()[2:].zfill(5)
                        self.forward = False
                        Mrecord.append(self.LOCCTR+1)
                        return self.object_prog
                    tmp = SYMTAB[self.operand] - self.PCTR
                    # SIC/XE PC
                    if tmp <= 2047 and tmp >= (-2048):
                        self.object_prog += '2' #0010
                        if tmp < 0:
                            tmp = 4096 + tmp
                            self.object_prog += hex(tmp).upper()[2:]
                        else:
                            self.object_prog += hex(tmp).upper()[2:].zfill(3)
                        self.forward = False
                    # SIC/XE base - relative
                    else:
                        # 要確認 base 是否存在
                        if base >= 0:
                            self.object_prog += '4' # xbpe = 0100
                            tmp = SYMTAB[self.operand] - int(base)
                            self.object_prog += hex(tmp).upper()[2:].zfill(3)
                            self.forward = False
                        # 若 base 也是還沒定義的 label 
                        # forward == True
                        else:
                            self.forward = True
                            # 初始化
                            self.mnemonic = self.clone[2]
                            self.operand = self.clone[3]
                # operand 不存在
                # RSUB
                elif self.mnemonic == 'RSUB':
                    self.object_prog += '0000'
                    self.forward = False
                else:
                    self.forward = True
                    # 初始化
                    self.mnemonic = self.clone[2]
                    self.operand = self.clone[3]
        
        # BYTE
        elif self.mnemonic == 'BYTE' and self.operand.startswith('X'):
            self.forward = False
            self.object_prog = self.operand.strip("X'")
        elif self.mnemonic == 'BYTE' and self.operand.startswith('C'):
            tmp = self.operand.strip("CX'")
            tmp_for_ord = ''
            # 將後面字串以 ord 找到對應的數字 (10進位)
            # 再轉為 16 進位 並將字串接起來 (要去掉 0x)
            for char in tmp :
                tmp_for_ord += str(hex(ord(char)).upper()[2:]) 
            self.object_prog = tmp_for_ord
            self.forward = False
        # WORD 
        elif self.mnemonic == 'WORD':
            self.object_prog = hex(int(self.operand)).upper()[2:].zfill(6)
            self.forward = False
        # BASE 跳過
        # RESB, RESW 換行
        else:
            self.object_prog = ' '*6
            self.forward = False

        

def main():
    lineInfo = []
    breakNote = -1
    opTable()
    global base
    base_operand = ''
    with open('(test)SICXE.asm','r') as f:
        lines = f.readlines()
        i = 1 # 計算第幾行
        valid = 0
        for line in lines:
            if breakNote > 0:
                break
            # 將資料做前處理 (包括分割，處理註解等)
            dataForLine = checkLines(line)
            # print(dataForLine)
            # 將已被過濾掉的跳過
            if dataForLine[0] == '':
                i += 1
                continue
            # 將 token 的三個欄位 label mnemonic operand 區別
            label, mnemonic, operand = token(dataForLine)
            # 用以紀錄目前讀到的資料 方便 location 抓前一筆資料
            data.append([i,mnemonic,operand])
            # 抓取 base
            if mnemonic == 'BASE':
                base_operand = operand
            
            if mnemonic == 'START':
                LOCCTR = int(operand)
                startLine = i
                PCTR = 0
            elif mnemonic == 'END': # 中止
                breakNote = i
            # 計算 location 
            # 那一行的 location 為上一行的 mnemonic 和 operand 算出
            if i > startLine and data[-2][1] != 'START':
                LOCCTR = calculateLoc(i,LOCCTR, data[-2][1], data[-2][2])
                PCTR = calculateLoc(i,LOCCTR, mnemonic, operand) # program counter
            elif mnemonic != 'START' and mnemonic != 'END': # START 的下一個
                PCTR = calculateLoc(i,LOCCTR, mnemonic, operand)

            lineInfo.append(Line(i,label,mnemonic,operand, PCTR, LOCCTR))
            lineInfo[valid].objectProgram()
            
            # SYMTAB
            if label != '':
                # 如果已經存在 SYMTAB 則為 redefine
                if label in SYMTAB.keys():
                    # 37 白字體 41 紅底 31 紅字體
                    print(esc('1;31') + 'Line ' + str(i) +' ERROR : '+ esc() + esc('1;33') + ' redefined symbol' + esc())
                else :
                    SYMTAB[label] = LOCCTR
                    for x in range(len(lineInfo)):
                        if lineInfo[x].forward == True and (label in lineInfo[x].operand):
                            lineInfo[x].objectProgram()
            if base_operand in SYMTAB.keys():
                base = SYMTAB[base_operand]
                for x in range(len(lineInfo)):
                    if lineInfo[x].forward == True:
                        lineInfo[x].objectProgram()
            valid += 1
            i+=1
        f.close()
        # print Object code
        length = len(lineInfo)
        # H record
        print('\nH '+ lineInfo[0].label+' '+(6-len(lineInfo[0].mnemonic))*' '+hex(int(lineInfo[0].operand)).upper()[2:].zfill(6) + ' ' + hex(int(lineInfo[length-1].LOCCTR) - SYMTAB[lineInfo[length-1].operand]).upper()[2:].zfill(6))
        # T record 去掉第一筆
        countLength = 0
        Trecord = [[]]
        TrecordStart = []
        index = 0
        for num in lineInfo[1:-1]:
            if num.mnemonic == 'BASE':
                continue
            if countLength == 0:
                TrecordStart.append(num.LOCCTR)
            countLength += len(num.object_prog)/2
            if countLength < 30:
                Trecord[index].append(num.object_prog)
            else:
                index += 1
                Trecord.append([])
                TrecordStart.append(num.LOCCTR)
                Trecord[index].append(num.object_prog)
                countLength = len(num.object_prog)/2

        for i in range(len(Trecord)):
            print('T '+ hex(TrecordStart[i]).upper()[2:].zfill(6), end=' ')
            total = 0
            for j in Trecord[i]:
                if ' ' not in j:
                    total += int(len(j)/2)
            print(hex(total).upper()[2:].zfill(2)+' '+' '.join(Trecord[i]))
        
        # M record
        for i in Mrecord:
            print('M '+ hex(i)[2:].zfill(6)+' 05')
        
        # E record
        print('E '+ hex(SYMTAB[lineInfo[-1].operand])[2:].zfill(6))
    
        # for i in range(len(lineInfo)):
        #     print(str(lineInfo[i].line) + ' : ' ,end='')
        #     # print(lineInfo[i].clone)
        #     print(lineInfo[i].getObj())
main()