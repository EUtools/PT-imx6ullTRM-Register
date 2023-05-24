import fitz
from . import toc 
from . import comm 
# import comm
# import toc
from collections import *

class RegReset:
    def __init__(self, filename):
        self.doc = fitz.open(filename)
        self.toc = toc.Toc(filename)
        self.contentFinder = comm.RegContentFinder(filename)
    
    def get_reg_reset_value(self,regname):
        '''获取regname对应的reg的默认值,返回值类型为 RegAddrInfo'''
        regcontent = self.contentFinder.find_content(regname)
        addrcontent = self.contentFinder.get_content_after(regcontent, 'Address:')
        bits = []
        isBitLiteral = lambda x: True if x == '0' or x == '1' else False
        for idx, i in enumerate(addrcontent):
            if len(bits) >= 32:
                break
            if 'Reset' == i:
                for j in range(32):
                    elem = addrcontent[idx+j+1]
                    if not isBitLiteral(elem):
                        break
                    bits.append(elem)

        resetValBitsLiteral = "".join(bits)
    
        if resetValBitsLiteral == "":
            return None

        return int(resetValBitsLiteral, 2)

    def _get_page_text_lines(self, pagetext):
        return pagetext.split("\n")


if __name__ == '__main__':
    rr = RegReset("../pdf/imx6ullREF.pdf")
    no = rr.get_reg_reset_value("CCM_CSR")

    print(hex(no))
    print(type(no))