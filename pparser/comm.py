import fitz
from . import toc 
# import toc

class RegContentFinder:
    def __init__(self, filename):
        self.toc = toc.Toc(filename)
        self.doc = fitz.open(filename)

    def find_content(self,regname):
        '''
        找到指定regname 的 content-lines
        Note: 内容会超一点(ps 因为找不到结束标志, 所以以页为区分)
        '''
        pstart = self.toc.find_reg_pageno(regname) -1
        pend = self.toc.find_reg_next_pageno(regname) -1
        content = []
        haveFoundRegName = False
        while pstart<=pend:
            textlines = self.doc[pstart].get_text().split('\n')
            pstart+=1
            if haveFoundRegName:
                content = content + textlines
                continue
            else:
                for idx,line in enumerate( textlines):
                    if regname in line:
                        content = content + textlines[idx:]
                        haveFoundRegName = True
                        break
        return content

    def get_content_after(self,contentlines, mark):
        '''找到mark(字串)所在的行并返回其和后面的lines'''
        for i,v in enumerate(contentlines):
            if mark in v:
                return contentlines[i:]
        return None

if __name__ == "__main__":
    rcf = RegContentFinder("../pdf/imx6ullREF.pdf" )
    c = rcf.find_content("CCM_CCR")
    print(c)

    fc = rcf.get_content_after(c,"Address:")
    print(fc)