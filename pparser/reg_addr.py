import fitz
from . import comm 
from . import toc
# import toc
from collections import *
from dataclasses import dataclass

@dataclass
class RegAddrInfo:
    abs: int
    base: int
    offset: int
    rawText: str

class RegAddress:
    def __init__(self, filename):
        self.doc = fitz.open(filename)
        self.toc = toc.Toc(filename)
        self.contentFinder = comm.RegContentFinder(filename)
    
    def _get_address_line(self, regname):
        regcontent = self.contentFinder.find_content(regname)

        addrline = None
        for i in regcontent:
            if 'Address:' in i:
                addrline = i
                break

        return addrline
    
    def get_reg_addr_info(self,regname):
        '''获取regname对应的reg的地址信息,返回值类型为 RegAddrInfo'''
        addrline = self._get_address_line(regname)
        
        return self._parse_addr_line(addrline)
    
    def _parse_addr_line(self, addrline):
        if addrline is None:
            return None
        # todo
        ret = {"abs":None, "base":None, "offset":None, "rawText":addrline}
        addrline = addrline.replace("Address: ",'')
        # detect format 
        if 'Base address' in addrline: 
            # e.g "Address: Base address + 98h offset"
            line = addrline
            line = line.replace("Base address + ",'')
            line = line.replace(" offset",'')
            line = line.replace("h",'')
            offset = int(line,16)
            ret["offset"] = offset
        elif 'where' in addrline: 
            # e.g "Address: 20C_8000h base + 20h offset + (4d × i), where i=0d to 3d"
            # refer to manual for keyword "SCT" to understand d
            line = addrline
            line = line.split("offset",1)[0].strip()
            line = line.replace(" base + ",' ').replace("_",'').replace("h",'')
            ss = line.split(" ")
            ret['base'] = int(ss[0],16)
            ret['offset'] = int(ss[1],16)
        elif 'base' in addrline: 
            # e.g "Address: 200_4000h base + 34h offset = 200_4034h"
            line = addrline
            line = line.replace(' base + ','').replace(' offset = ','')
            line = line.replace('_', '')
            line = line.replace('h',' ')
            ss = line.split(" ")
            ret['base'] = int(ss[0],16)
            ret['offset'] = int(ss[1],16)
            ret['abs'] = int(ss[2],16)
        else:
            raise Exception("unknown addr format: "+ addrline)
        

        retstruct = RegAddrInfo(ret['abs'], ret['base'], ret['offset'], ret['rawText'])

        return retstruct

    def _get_page_text_lines(self, pagetext):
        return pagetext.split("\n")


if __name__ == '__main__':
    toc = RegAddress("pdf/imx6ullREF.pdf")
    # no = toc.get_reg_addr_info("UARTx_UBRC")
    # no = toc.get_reg_addr_info("CCM_CCR")
    # no = toc.get_reg_addr_info("CCM_ANALOG_PLL_ARMn")

    # no = toc.get_reg_addr_info("CCM_CCGR0")
    no = toc.get_reg_addr_info("CCM_CISR")

    print(no)
    print(type(no))