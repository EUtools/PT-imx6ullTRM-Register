import pparser as pp
from jinja2 import FileSystemLoader, Environment
import pickle
import translator

def outRegRange(regstart, regend):
    rip = pp.RegInfoParser("pdf/imx6ullREF.pdf")
    regs = rip.extract_reg_info_range(regstart, regend)

    output = translator.zig(regs)
    print(output)

if __name__ == "__main__":
    outRegRange("CCM_CCR", "CCM_CMEOR")