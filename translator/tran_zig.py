from jinja2 import FileSystemLoader, Environment

def mhex(d):
    try:
        return '{:X}'.format(d)
    except:
        return d

def translate(data_regpact):
    # 加载模板文件夹
    loader = FileSystemLoader(searchpath='tpls') # tosolve
    # 环境对象
    enviroment = Environment(loader=loader, trim_blocks=True)
    # 指定模板文件
    tpl = enviroment.get_template('tpl_tran_zig.jinja2')
  
    # 渲染模板
    output = tpl.render(regs=data_regpact, mhex=mhex)

    return output


