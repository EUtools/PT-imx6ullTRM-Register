'''
此不是通用的. 是 pdfplumber 解析结果和imx6ull 文档特定的
'''


def is_page_contents(page_text_lines):
    if len(page_text_lines) == 0:
        return False

    if len(page_text_lines) >= 2 and 'Section number Title Page' in page_text_lines[1]:
        return True
    if 'Section number Title Page' in page_text_lines[0]:
        return True
    return False


def cleanup_page_lines(page_text_lines):
    pagelines = page_text_lines
    if pagelines[0] == 'Contents':
        pagelines = pagelines[1:]
    if pagelines[0] == 'Section number Title Page':
        pagelines = pagelines[1:]
    if 'NXP Semiconductors' in pagelines[-1]:
        pagelines = pagelines[:-1]
    if 'Reference Manual' in pagelines[-1]:
        pagelines = pagelines[:-1]

    return pagelines


def cleanup_contents_lines(contents_lines):
    '''移除chapter 和 chapter 说明, 修正被误识别为多行的一行。使之只是 "Section number Title Page" 的形式
    '''
    lines = contents_lines

    def isSectionNumberLine(x): return True if x[0].isnumeric() else False
    # remove chapter and chapter desc too
    tmplines = []
    idx = 0
    while idx < len(lines):
        if 'Chapter' in lines[idx]:
            idx += 1
            while not isSectionNumberLine(lines[idx]):
                idx += 1
            continue
        tmplines.append(lines[idx])
        idx += 1
    lines = tmplines

    # cleanup some multiply lines to one line
    finalLines = []
    for line in lines:
        if not line[0].isnumeric():
            finalLines[-1] = finalLines[-1] + ' ' + line
            continue
        finalLines.append(line)

    return finalLines


# test
if __name__ == "__main__":
    import pdfplumber

    with pdfplumber.open("pdf/imx6ullREF.pdf") as pdf:
        contentslines = []
        for i in range(200):
            page = pdf.pages[i]
            pagetext = page.extract_text()
            pagelines = pagetext.split("\n")
            if is_page_contents(pagelines):
                contentslines += cleanup_page_lines(pagelines)
            elif len(contentslines) != 0:
                break

        print("\n".join(cleanup_contents_lines(contentslines)))
