from collections import *
from dataclasses import dataclass
from . import reg_table as rt
from . import reg_addr as ra
from . import reg_reset as rr
from . import toc
import pdfplumber

@dataclass
class RegInfo:
    regName: str
    regAddressInfo: ra.RegAddrInfo
    regResetValue: int
    tableInfo: rt.RegTableInfo

class RegInfoParser():
    def __init__(self, refFilname):
        self.filename = refFilname
        self.plumberpdf = pdfplumber.open(self.filename) # this is very slow
        self.helperToc = toc.Toc(self.filename)
        # self.helperTable = rt.new_reg_table_producer()
        self.helperAddr = ra.RegAddress(self.filename)
        self.helperReset = rr.RegReset(self.filename)

    def extract_reg_info(self, regname):
        '''
        解析得到指定 regname 的信息
        '''
        pageno = self.helperToc.find_reg_pageno(regname)
        if pageno is None:
            raise Exception("cannot find reg: "+ regname)
        
        itable = rt.extract_reg_table_info_by_reg_name(self.plumberpdf, regname, pageno)
        ireset = self.helperReset.get_reg_reset_value(regname)
        iaddr = self.helperAddr.get_reg_addr_info(regname)
        ret = RegInfo(itable.regName, iaddr, ireset, itable)

        return ret
    
    def extract_reg_info_range(self, regnameBegin, regnameEnd):
        '''
        解析得到指定寄存器范围的[regnameBegin:regnameEnd] 的信息
        '''
        names = self.helperToc.get_regname_range(regnameBegin, regnameEnd)
        if names is None:
            return None
        ret = []
        for name in names:
            reginfo = self.extract_reg_info(name)
            ret.append(reginfo)
        return ret
    
if __name__ == "__main__":
    rip = RegInfoParser("pdf/imx6ullREF.pdf")

    # test1
    # res = rip.extract_reg_info("IOMUXC_GPR_GPR4")
    # print(res)

    # test2
    ress = rip.extract_reg_info_range("IOMUXC_GPR_GPR0", "IOMUXC_GPR_GPR14")
    print(ress)
        
        

