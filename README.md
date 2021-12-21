# SIC-XE-Assembler
SIC/XE Assembler in python

## Requirement
- Python 3

## Flow
![image](https://user-images.githubusercontent.com/46191514/146862769-69c84486-7ab7-4ea2-aef6-c1883a8640b0.png)

## Pseudo code
- `checkLines`: Preprocess 每行，處理註解及錯誤輸入
```python=
def checkLines(當前行號, 未處理過的各行資料):
    將 註解從資料中刪除
    將 資料切割
    計算 ,(逗號) 數量
    if ',' 數量 > 2:
        error : ndexed addressing error(有大於 2 個 ,)
    將 indexed addressing 被切割開的 operand ,  X 連接
    將 格式2byte 後面接兩個 registers 被切割開的 register , register 連接
    
    回傳處理完的資料
```
- `token`: 切割 label, mnemonic, operand 三個 tokens
```python=
def token(當前行號, 已切割的資料列表):
    定義 label, mnemonic, operand 起始為空值
    if 字串長度 > 3:
        error: token 超過三個欄位
    elif 字串長度 = 3:
        label = 列表第 1 筆資料
        mnemonic = 列表第 2 筆資料
        operand = 列表第 3 筆資料
        if mnemonic == RSUB:
            error: RSUB 不能有 operand
    elif 字串長度 = 2:
        mnemonic = 列表第 1 筆資料
        operand = 列表第 2 筆資料
        # RSUB has label
        if 列表第 2 筆資料 == RSUB:
            label = 列表第 1 筆資料
            mnemonic = 列表第 2 筆資料
            operand = 空字串
        elif operand 為 mnemonic and mnemonic 的格式不是 1 個 byte:
            error : mnemonic error(後面必須接 operand)
        elif 列表第 1 筆資料 == RSUB:
            error : RSUB error(RSUB 後不能接 operand)
    elif 列表長度為 1  and 資料為 RSUB:
        mnemonic = RSUB
    else:
        error : token error(token 大小等於 1，但不是 RSUB)
    # ---- error detection ---- #
    if label 不是空的 and label 的名字為 mnemonic:
        error : label error(label 與 mnemonic 齊名)
    if operand 不是空的 and operand 的名字為 mnemonic:
        error : operand error(operand 與 mnemonic 齊名)
    if label 不是空的 and operand 不是空的 and operand == label:
        error :operand error(operand 與 label 齊名)
    
    回傳 label, mnemonic, operand 三筆資料
```

- `calculateLoc`: 計算 Location counter 和 program counter
```python=
def calculateLoc(當前行號,Location counter, mnemonic, operand, 要計算的是Location counter 還是 program counter):
    if 格式為 extension:
        Location counter + 4
    elif mnemonic == END :
        回傳目前的 Location counter
    elif mnemonic == RESB :
        Location counter + operand 轉十進位
    elif mnemonic == RESW :
        Location counter + (operand 轉十進位 * 3)
    elif mnemonic == BASE :
        不用計算 Location counter
    elif mnemonic == WORD :
        Location counter + 3
    elif mnemonic == BYTE :
        if 接 C :
            Location counter + C 後面字串裡的長度  
        elif 接 X :
            Location counter + 1
    elif mnemonic 格式為 3 :
        Location counter + 3
    else:
        Location counter + 格式的 byte 數
        
    回傳 Location counter
    
```

- `record`: 將結果紀錄並寫入檔案
```python=
def record(要寫入的檔案,Trecord 的資料, 所有資料):
    # print Object code
    file.write(H record)
    print(Hrecord)
    for Trecord 的每行資料:
        if 長度為 0:
            跳過
        if 是補 forward reference 的 Trecord:
            file.write(Trecord)
            print(Trecord)
        else:
            計算每行長度
            file.write(Trecord & 每行長度)
            print(Trecord & 每行長度)
            if 長度是 0:
                跳過
    # M record
    file.write(M record)
    print(Mrecord)
    # E record
    file.write(E record)
    print(Erecord)
    
```
