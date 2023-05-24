'''
此是 pdfplumber 解析结果特定的
'''
from collections import *
from dataclasses import dataclass

@dataclass
class RegTableRowInfo:
    bits: str
    bith: int # helper for rendering
    bitl: int # helper for rendering
    name: str
    desc: list
    def get_bits_high(self):
        return int(self.bits.split("–")[0])
    def get_bits_low(self):
        return int(self.bits.split("-")[1])
@dataclass
class RegTableInfo:
    regName: str
    rows: list[RegTableRowInfo]


def parse_reg_table(clean_complete_reg_table):
    '''
    解析 reg_table. 产生易于操作的内部表示
    note: clean_complete_reg_table 需要是干净的完整的 reg-table (ps cleanup_reg_table 的输出)
    '''
    table = clean_complete_reg_table

    # extract reg-name
    regName = clean_complete_reg_table[0][0].split(' ')[0]
    # remove row 'Field Description' and row 'xxx field description'
    table = table[2:]

    rows = []
    for row in table:
        #note: format: e.g '31–28\nReserved' '11–7\nReserved' 'OSCNT' 'UART_CLK\nPODF' '15–14\n-' '17\nMMDC_CH0_\nMASK' '-'
        field = row[0]
        desc = row[1:]

        idesc = desc
        ibits = ""
        iname = ""
        # 枚举解析 field
        if field[0].isnumeric():
            ss = field.split('\n',1)
            fb =  ss[0]
            fn = ss[1].replace('\n','')

            if fn == '-':
                iname = "unamed"
            else:
                iname = fn

            ibits = fb
        else:
            ibits = "todo"
            if field == '-':
                iname = "unamed"
            else:
                iname = field.replace('\n','')

        # 统一 bits 形式为 high-low (e.g 6-6 7-0)
        if not '-' in ibits:
            ibits = ibits + '-'+ibits 
        
        rows.append(RegTableRowInfo(ibits,0,0, iname, idesc))

    # 处理 todo 的 bits 和 ...
    for i,v in enumerate(rows):
        if 'todo' in v.bits:
            bh = rows[i-1].get_bits_low()-1
            v.bits = str(bh) + '-0'

        # 支持 bith bitl 成员
        ss = v.bits.split("-")
        v.bith = int(ss[0])
        v.bitl = int(ss[1])

        # 处理 reserved 名重复
        if v.name == 'Reserved' or v.name == "unamed":
            v.name = v.name.lower() + '_'+ str(v.bith) + '_' + str(v.bitl)


    return RegTableInfo(regName, rows)


def cleanup_reg_table(complete_reg_table):
    '''鉴于原始扫描出来的reg-table的一些行有些问题(e.g 最后一行空行并不需要; 有些行被识别成为了多行), 所以需要做些处理
    Note: 输入的需要是完整的 reg-table 
    '''
    isEmptyElement = lambda x: True if x is None or x == '' or x == 'None' else False

    # 替换掉不规整的 '-'
    for i,items in enumerate(complete_reg_table):
        for j,item in enumerate(items):
            if item is not None:
                complete_reg_table[i][j] =  item.replace('–','-')
    regtable = complete_reg_table

    # try to remove the last useless row
    if len(regtable[-1]) > 1:
        if isEmptyElement(regtable[-1][0]) and isEmptyElement(regtable[-1][1]):
            regtable = regtable[:-1]
    


    # 合并一些分割的行
    finaltable = []
    for row in regtable:
        if isEmptyElement(row[0]):
            finaltable[-1] = finaltable[-1] + row[1:]
            continue
        finaltable.append(row)
    return finaltable


def merge_reg_sub_tables(reg_sub_tables):
    '''合并 reg 所有的sub-tables以得到完整的 reg-table
    Note: 需要确保 reg_sub_tables 是完整的且无多余且升序符合从头到尾
    '''
    if len(reg_sub_tables) == 0:
        return None

    if len(reg_sub_tables) == 1:
        return cleanup_reg_table(reg_sub_tables[0])

    head = reg_sub_tables[0]
    tail = reg_sub_tables[-1]
    mids = reg_sub_tables[1:-1]
    mid = []
    for table in mids:
        mid = mid+table[2:-1]
    regtable = head[:-1]+mid+tail[2:]

    # ensure return a clean reg-table
    return cleanup_reg_table(regtable)

def extract_reg_name(table):
    '''从 reg-table 获取reg的名字'''
    if not is_reg_table(table):
        return None
    regname = table[0][0].split(" ", 1)[0]
    return regname


def is_reg_table(table):
    '''判断是不是 reg-table'''

    if len(table) < 2:
        return False
    if len(table[1]) < 2:
        return False
    if table[1][0] == 'Field' and table[1][1] == 'Description':
        return True
    return False


def infer_reg_table_completeness(table):
    '''
    判断 reg_table 的完整性
    返回值 0-完整状态 1-头部 2-尾部 3-中部
    如非reg-table返回None
    '''

    if not is_reg_table(table):
        return None

    havePrev = "continued" in table[0][0]
    haveNext = "Table continues on the next page" in table[-1][0]

    p = 1 if havePrev else 0
    n = 1 if haveNext else 0

    return (p << 1) | n


def is_complete_reg_table(table):
    return infer_reg_table_completeness(table) == 0


def is_head_reg_table(table):
    return infer_reg_table_completeness(table) == 1


def is_tail_reg_table(table):
    return infer_reg_table_completeness(table) == 2


def is_middle_reg_table(table):
    return infer_reg_table_completeness(table) == 3


def find_reg_table_idx(tables):
    '''
    在tables中找到(第一个)reg-table并返回其在tables中的索引
    如无则返回None
    '''

    for table,idx in enumerate( tables):
        if is_reg_table(table):
            return idx
    return None


def find_reg_table(tables):
    '''
    在 tables 中找到第一个reg-table并返回
    如无则返回None
    '''

    idx = find_reg_table_idx(tables)
    if idx != None:
        return tables[idx]
    return None


def find_reg_tables(tables):
    '''
    在 tables 中找到第一个reg-table并返回
    如无则返回None
    '''

    regTables = []
    for table in tables:
        if is_reg_table(table):
            regTables.append(table)
    if len(regTables) == 0:
        return None
    return regTables


class Producer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.currentRegSubTables = []

    def input_table(self, table):
        """输入一个 table. 并触发生成, 如果可以得到一个完整的 reg-table 则返回它, 否则返回None
        Note: 需要保证输入的第一个reg-table是头部
        """
        if not is_reg_table(table):
            return None
        self.currentRegSubTables.append(table)
        ft = self.try_get_final_table()
        if ft is not None:
            self.reset()
        return ft
    
    def try_get_final_table(self):
        """尝试从已输入的tables中拼出一个完整的reg-table
            若ok则返回 最终的 reg-table, 否则 None
        """
        tables = self.currentRegSubTables
        tablesMap = defaultdict(list)  # {regname}[table]
        careRegName = ''
        for table in tables:
            regname = extract_reg_name(table)
            tablesMap[regname].append(table)

            if careRegName == '':
                careRegName = regname

        # here only deal the first
        if not len(tablesMap) > 0:
            return None
        regSubTables = tablesMap[careRegName]
        if len(regSubTables) == 1 and is_complete_reg_table(regSubTables[0]):
            return merge_reg_sub_tables(regSubTables)

        if is_head_reg_table(regSubTables[0]) and is_tail_reg_table(regSubTables[-1]):
            return merge_reg_sub_tables(regSubTables)
        
        return None


def new_reg_table_producer():
    return Producer()

def extract_reg_table_info_by_reg_name(plumberPdf, regName, regStartPage):
    '''
    找到 regName 的 table 信息
    plumberPdf 是 'pdfplumber.open(xx)' 的结果
    regStartPage 是 reg 信息定义的起始页
    '''
    pdf = plumberPdf
    regStartPage -= 1
    producer = new_reg_table_producer()
    ft = None
    for i in range(50):
        page = pdf.pages[regStartPage+i]
        tables = find_reg_tables(page.extract_tables())
        if tables is None:continue

        for table in tables:
            if extract_reg_name(table) != regName: continue
            ret = producer.input_table(table)
            if ret is not None:
                ft = ret
                break

        if ft is not None:
            break
    if ft is None:
        raise Exception("it shouldn't happen. check here")

    return parse_reg_table(ft)


if __name__ == "__main__":
    import pdfplumber

    with pdfplumber.open("pdf/imx6ullREF.pdf") as pdf:
        res = extract_reg_table_info_by_reg_name(pdf, "CCM_CCR", 660)
        print(res)
        # producer = new_reg_table_producer()

        # pageStart = 659
        # fts = []
        # for i in range(50):
        #     page = pdf.pages[pageStart+i]
        #     tables = find_reg_tables(page.extract_tables())
        #     if tables is None:continue
        #     for table in tables:
        #         ret = producer.input_table(table)
        #         if ret is not None:
        #             fts.append(ret)

        #     if len(fts) >= 10:
        #         break

        # print(fts)