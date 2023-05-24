'''
通用的
'''

import fitz

class Toc:
    def __init__(self, filename):
        self.doc = fitz.open(filename)
        self.toc = self.doc.get_toc()
    
    def _find_reg_toc_row_index(self, regname):
        for idx, i in enumerate(self.toc):
            if regname in i[1]:
                return idx

    def find_reg_pageno(self,regname):
        idx = self._find_reg_toc_row_index(regname)
        if idx is None:
            return None
        return self.toc[idx][2]
    
    def get_regname_range(self, regnameBegin, regnameEnd):
        begin = self._find_reg_toc_row_index(regnameBegin)
        end = self._find_reg_toc_row_index(regnameEnd)
        if begin is None or end is None:
            return None
        
        regnames = []
        while begin <= end:
            name= self.toc[begin][1]
            regnames.append(name)
            begin += 1
        
        return regnames
    def find_reg_next_pageno(self, regname):
        idx = self._find_reg_toc_row_index(regname)
        return self.toc[idx+1][2]
        
    
if __name__ == '__main__':
    toc = Toc("pdf/imx6ullREF.pdf")
    # test1
    no = toc.find_reg_pageno("IOMUXC_GPR_GPR0")
    print(no)

    # test2
    names = toc.get_regname_range("IOMUXC_GPR_GPR0", "IOMUXC_GPR_GPR14")
    print(names)

