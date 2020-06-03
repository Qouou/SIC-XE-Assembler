# 106213014 
# 歐芷欣 
def opTable(mnemonic):
    # 讀入 opCode 檔案
    with open('opCode.txt', 'r') as file :
    # 一行一行讀入 
        linesOfData = file.readlines()
    # 以 dictionary 的方式建立 table
    data = {}
    # data[ <key> ] = <data>
    # 一個 key 會對應到一個 資料
    for i in linesOfData :
        # 用空白切割
        tmp = i.split()
        data[tmp[0]] = tmp[1]
    try:
        return data[mnemonic]
    except:
        return None
    
def main():
    # 輸入 輸出
    mnemonic = input("search(Input a mnemonic) : ")
    print("opCode : "+ opTable(mnemonic)) 

if __name__=='__main__':
    main()