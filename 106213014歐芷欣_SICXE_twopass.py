from collections import defaultdict
from colorama import init

# global
data = []
startLine = 0
OPTAB = defaultdict(dict) # opTable
pseudoCode = ['START', 'END', 'BASE','RESB','RESW','WORD','BYTE']
SYMTAB = {}
Mrecord = []
forward = {}
def checkLines_Middle(line):
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
        if data[-2] == 'X' and ',' in data[-3]:
            # 將 最後兩項接起來後 將最後一項刪除
            data[-3] = data[-3]+' X'
            data[-2] = data[-1]
            data = data[:-1]
    return data
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
def opTable():
    # 讀入 opCode 檔案
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
    
def calculateLoc(LOCCTR, mnemonic, operand):
    # extend +4
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
        print(esc('1;31') + ' ERROR : '+ esc() + esc('1;33') + ' mnemonic error' + esc())
    
# CMD 顏色設置 
# code default 0
def esc(code = 0): 
    return f'\033[{code}m'

def forwardDef(label, LOCCTR, PCTR): # 這裡的 label 會丟入 還未定義 operand 
    global forward
    if label not in forward.keys():
        forward[label] = [[LOCCTR +1 , PCTR]]
    else:
        forward[label].append([LOCCTR +1 , PCTR])

def objectProgram(label, mnemonic, operand, PCTR, SYMTAB, LOCCTR):
    
    REGISTERS = {'PC':'8', 'SW':'9', 'A':'0', 'X':'1','L': '2','B':'3', 'S':'4', 'T':'5', 'F':'6'}
    object_prog = ''
    extend = False
    # Extension or not 
    if '+' in mnemonic:
        mnemonic = mnemonic.strip('+ ')
        extend = True
    if (mnemonic in pseudoCode) == False :
        program = int(OPTAB[mnemonic]['opCode'],16)
        if '#' in operand:
            program += 1
            object_prog = hex(program)[2:].upper().zfill(2)
            operand = operand.strip('#')
            if extend:
                object_prog += '1'
                object_prog += hex(int(operand)).upper()[2:].zfill(5)
            elif operand.isdigit():
                object_prog += '0'
                object_prog += hex(int(operand)).upper()[2:].zfill(3)
            else:
                # 是否有在 SYMTAB 裡
                if operand not in SYMTAB.keys():
                # 沒有: 把位置和要做的計算記下來
                    forwardDef(operand, LOCCTR, PCTR)
                # 有 :
                else:
                    # 先用 PC 計算
                    return object_prog
                        # 十進位範圍在 (-2048<=disp<=2047) 
                        # object_prog += 2
                        # object_prog += hex(SYMTAB[operand] - PCTR).zfill(3) 
                    # 不能再用 BASE
                        # object_prog += 4
                        # object_prog += hex(SYMTAB[operand] - base_loc).zfill(3)
        elif '@' in operand:
            program += 2
            object_prog = hex(program).upper()[2:].zfill(2)

        # Format 2 
        elif OPTAB[mnemonic]['format'] == '2':
            object_prog = hex(program).upper()[2:].zfill(2)
            # 當後面接 2 個 register 時
            if ',' in operand :
                for i in operand.split(','):
                    object_prog += REGISTERS[i]
            # 只有一個 register 後面要補 0
            else:
                object_prog += REGISTERS[operand]
                object_prog += '0'
        # Format 1
        elif OPTAB[mnemonic]['format'] == '1' :
            object_prog = hex(program).upper()[2:].zfill(2) 
        # SIC/XE
        else:
            program += 3
            object_prog = hex(program).upper()[2:].zfill(2)
            
            if operand in SYMTAB.keys():
                tmp = SYMTAB[operand] - PCTR
                if tmp <= 2047 and tmp >= (-2048):
                    object_prog += '2'
                    if tmp < 0:
                        tmp = 4096 + tmp
                        object_prog += hex(tmp).upper()[2:]
                    else:
                        
                        object_prog += hex(tmp).upper()[2:].zfill(3)
                else:
                    object_prog += '4'
        return object_prog
    # BYTE
    elif mnemonic == 'BYTE' and operand.startswith('X'):
        return operand.strip("X'")
    elif mnemonic == 'BYTE' and operand.startswith('C'):
        tmp = operand.strip("CX'")
        tmp_for_ord = ''
        # 將後面字串以 ord 找到對應的數字 (10進位)
        # 再轉為 16 進位 並將字串接起來 (要去掉 0x)
        for char in tmp :
            tmp_for_ord += str(hex(ord(char)).upper()[2:]) 
        return tmp_for_ord
    # WORD 
    elif mnemonic == 'WORD':
        return hex(int(operand)).upper()[2:].zfill(6)
    # BASE 跳過
    # RESB, RESW 換行
    else:
        return ''
def calObject(PCTR, mnemonic, operand, nowProgram, base):
    if mnemonic in pseudoCode:
        return ' '
    if '#' in operand or '@' in operand:
            operand = operand.strip('#@')
    if '+' in mnemonic: # format 4
        tmp = SYMTAB[operand] 
        nowProgram += '1'
        nowProgram += hex(tmp).upper()[2:].zfill(5)
    elif ',' in operand and 'X' in operand:
        while ',' in operand:
            operand = operand[:-1]
        tmp = SYMTAB[operand] - int(PCTR)
        if tmp <= 2047 and tmp >= (-2048):
            nowProgram += 'A'
            if tmp < 0:
                tmp = 4096 + tmp
                nowProgram += hex(tmp).upper()[2:]
            else:
                nowProgram += hex(tmp).upper()[2:].zfill(3)
        else:
            nowProgram += 'C'
            tmp = SYMTAB[operand] - int(base)
            nowProgram += hex(tmp).upper()[2:].zfill(3)
    elif mnemonic == 'RSUB':
        nowProgram += '0000'
    else: # format 3
        tmp = SYMTAB[operand] - int(PCTR)       
        if tmp <= 2047 and tmp >= (-2048):
            nowProgram += '2'
            if tmp < 0:
                tmp = 4096 + tmp
                nowProgram += hex(tmp).upper()[2:]
            else:
                nowProgram += hex(tmp).upper()[2:].zfill(3)
        else:
            nowProgram += '4'
            tmp = SYMTAB[operand] - int(base)
            nowProgram += hex(tmp).upper()[2:].zfill(3)
    return nowProgram

def writeForMiddle(file, line,location, label, mnemonic, operand,objectProgram, PCTR):
    if label == '':
        label = 'NULL'
    if operand == '':
        operand = 'NULL'
    if objectProgram == '':
        objectProgram = 'NULL'
    
    file.write(str(line)+' '+ str(location) +' '+ str(PCTR) +' '+ label +' '+ mnemonic +' '+ operand +' '+objectProgram+'\n')

def main():
    init(autoreset = True) # 開啟 CMD 輸出顏色
    breakNote = -1
    opTable()
    
    START_LOCCTR, END_LOCCTR = 0,0
    global LOCCTR
    global SYMTAB

    f_for_write = open('106213014_middle.txt','w+') # 每次清空再寫入
    with open('(test)SICXE.asm','r') as f:
        lines = f.readlines()
        i = 1 # 計算第幾行
        # print("{:^4}  {:^6}  {:^8}  {:^8}  {:^8}  {:^8}".format('line', 'Loc', 'label', 'mnemonic', 'operand', 'object code'))
        for line in lines:
            if breakNote > 0:
                break
            # print(str(i) +':'+line,end = '')
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
            if mnemonic == 'START':
                LOCCTR = int(operand)
                startLine = i
                PCTR = 0
            elif mnemonic == 'END': # 中止
                breakNote = i

            # 計算 location 
            # 那一行的 location 為上一行的 mnemonic 和 operand 算出
            if i > startLine and data[-2][1] != 'START':
                LOCCTR = calculateLoc(LOCCTR, data[-2][1], data[-2][2])
                PCTR = calculateLoc(LOCCTR, mnemonic, operand) # program counter
            elif mnemonic != 'START' and mnemonic != 'END': # START 的下一個
                PCTR = calculateLoc(LOCCTR, mnemonic, operand)
            
            if mnemonic == 'START':
                START_LOCCTR = LOCCTR
            elif mnemonic == 'END':
                END_LOCCTR = LOCCTR
            # SYMTAB
            if label != '':
                # 如果已經存在 SYMTAB 則為 redefine
                if label in SYMTAB.keys():
                    # 37 白字體 41 紅底 31 紅字體
                    print(esc('1;31') + 'Line ' + str(i) +' ERROR : '+ esc() + esc('1;33') + ' redefined symbol' + esc())
                else :
                    SYMTAB[label] = LOCCTR
            # 紀錄 base location
            if mnemonic == 'BASE':
                base_loc = operand
            # object program
            if mnemonic != 'START' and mnemonic != 'END': 
                object_prog = objectProgram(label, mnemonic, operand, PCTR, SYMTAB,LOCCTR)
            else:
                object_prog = ''
            
            # print("{:4d}  {:^6}  {:^8}  {:^8}  {:^8}  {:^8}".format(i, LOCCTR, label, mnemonic, operand, object_prog))
            writeForMiddle(f_for_write, i, LOCCTR, label, mnemonic, operand,object_prog, PCTR)
            i = i + 1
        f_for_write.write(hex(END_LOCCTR-START_LOCCTR)[2:].zfill(6)+"\n")
        f_for_write.write(str(SYMTAB[base_loc]))
        f.close()
    
    objectLine = ''
    with open('106213014_middle.txt','r') as f_for_write:
        lines = f_for_write.readlines()
        base = lines[-1].strip()
        length = lines[-2].strip()
        count = 0
        for line in lines[:-2]:
            line = line.replace('  ',' ') # 避免有多空一格的情況
            dataForLine = checkLines_Middle(line)
            mnemonic = dataForLine[4].replace('+','')
            if count > 30 or count == 0 and mnemonic != 'START':
                objectLine += '\nT '
                objectLine += hex(int(dataForLine[1])).upper()[2:].zfill(6) + ' '
                count = 0
            if mnemonic == 'START':
                objectLine += 'H ' + dataForLine[3] + (6-len(dataForLine[3]))*' '
                objectLine += ' '+ dataForLine[5].zfill(6) +' '+length

            elif mnemonic == 'END':
                end =  '\nE ' + str(SYMTAB[dataForLine[5]]).zfill(6)
            elif mnemonic == 'RESB' or mnemonic == 'RESW':
                objectLine += ' '*6 + ' '
                count += 6
            elif mnemonic == 'BASE':
                continue
            elif mnemonic == 'BYTE' or OPTAB[mnemonic]['format'] == '2':
                objectLine += dataForLine[6]+' '
                count += 2
            elif len(dataForLine[6]) == 6  and dataForLine[6] != 'NULL':
                if count + 3 > 30 :
                    objectLine += '\nT '
                    objectLine += hex(int(dataForLine[1])).upper()[2:].zfill(6) + ' '
                    count = 0 
                objectLine += dataForLine[6]+' '
                count += 3
            elif len(dataForLine[6]) == 8 and dataForLine[6] != 'NULL':
                if count + 4 > 30 :
                    objectLine += '\nT '
                    objectLine += hex(int(dataForLine[1])).upper()[2:].zfill(6) + ' '
                    count = 0 
                objectLine += dataForLine[6]+' '
                
                count += 4
            else:
                objectProg = calObject(dataForLine[2],dataForLine[4], dataForLine[5], dataForLine[6], base)
                if count + len(objectProg)/2 > 30 :
                    objectLine += '\nT '
                    objectLine += hex(int(dataForLine[1])).upper()[2:].zfill(6) + ' '
                    count = 0
                objectLine += objectProg + ' '
                if len(objectProg)/2 == 4:
                    Mrecord.append(hex(int(dataForLine[1])+1).upper()[2:].zfill(6))
                count += len(objectProg) /2
            
        # data[0] line, data[1] LOCCTR, data[2] PCCTR, 
        # data[3] label, data[4] mnemonic, data[5] operand 
        # data[6] object program
        for i in Mrecord:
            objectLine += '\nM ' + i + ' '+ '05'
        objectLine += end
    f_for_write.close()
    
    print('objectProgram : \n')
    objectProgramLine = objectLine.split('\n')
    for line in objectProgramLine:
        perLine = line.split()
        perLength = 0
        if perLine[0] == 'T':
            for element in perLine[2:]:
                perLength += int(len(element) / 2)
            perLength_16 = hex(perLength).upper()[2:].zfill(2)
            perLine.insert(2,perLength_16)
        
        print (' '.join(perLine))

if __name__ == '__main__':
    main()