# MIT License
#
# Copyright (c) 2019 Phil Krylov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import xlrd
import pandas as pd
import csv
import re
import io
import unicodedata


TABLESEP = '\u0014'
XLRD_HTML_STYLE_MAP = (
    ('bold', 'b'),
    ('italic', 'i'),
    ('underlined', 'u'),
)

GLD_IPA_MAP_RAW = '''ɳʘ,ʘ̃
ɳǀ,ǀ̃
ɳǂ,ǂ̃
ɳǃ,ǃ̃
ɳǃǃ,‼̃
ɳǁ,ǁ̃
ʘ̰,ʘ̬
ɡʘ,ʘ̬
ǀ̰,ǀ̬
ɡǀ,ǀ̬
ǂ̰,ǂ̬
ɡǂ,ǂ̬
ǃ̰,ǃ̬
ɡǃ,ǃ̬
ǃǃ̰,‼̬
ɡǃǃ,‼̬
ǁ̰,ǁ̬
ɡǁ,ǁ̬
ǃǃ,‼
pᶠ,p͡ɸ
bᵛ,b͡β
p̪ᶠ,p̪͡f
b̪ᵛ,b̪͡v
tᶿ,t̪͡θ
dᶞ,d̪͡ð
tʳ,t͡ɹ̝̊
dʳ,d͡ɹ̝
kˣ,k͡x
gˠ,g͡ɣ
qᵡ,q͡χ
ɢʶ,ɢ͡ʁ
ʡʢ,ʡ͡ʢ
ʔh,ʔ͡h
c,t͡s
ʒ,d͡z
č,t̠͡ʃ
ǯ,d̠͡ʒ
c̢,ʈ͡ʂ
ᶚ,ɖ͡ʐ
ɕ,t͡ɕ
ʓ,d͡ʑ
ƛ,tɬ
ᴌ,dɮ
m,m
ɱ,ɱ
n,n
ɳ,ɳ
ɲ,ɲ
ŋ,ŋ
ɴ,ɴ
p,p
b,b
p̪,p̪
t,t
d,d
ʈ,ʈ
ɖ,ɖ
ȶ,c
ȡ,ɟ
k,k
g,g
q,q
ɢ,ɢ
ʡ,ʡ
ʔ,ʔ
ɂ,ʔ
Ɂ,ʔ
ˀ,ʔ
ɓ,ɓ
ɗ,ɗ
ʄ,ʄ
ɠ,ɠ
ʛ,ʛ
ɸ,ɸ
β,β
ꞵ,β
f,f
v,v
θ,θ
ð,ð
s,s
z,z
š,ʃ
ž,ʒ
ʂ,ʂ
ʐ,ʐ
ʆ,ɕ
,ɕ
ʑ,ʑ
x,x
ɣ,ɣ
γ,ɣ
χ,χ
ꭓ,χ
ʁ,ʁ
ħ,ħ
ʕ,ʕ
ˁ,ʕ
ʜ,ʜ
ʢ,ʢ
h,h
ɦ,ɦ
ʍ,ʍ
w,w
ɹ,ɹ
ɻ,ɻ
y,j
ɰ,ɰ
r,r
ʀ,ʀ
ⱱ,ⱱ
ɾ,ɾ
ɽ,ɽ
ɢ̆,ɢ̆
ɬ,ɬ
ʫ,ɮ
l,l
ɭ,ɭ
ʎ,ʎ
ɫ,ɫ
ʘ,ʘ
ǀ,ǀ
ǂ,ǂ
ǃ,ǃ
ǁ,ǁ
i,i
ü,y
ɨ,ɨ
ʉ,ʉ
ɯ,ɯ
u,u
ɪ,ɪ
ʏ,ʏ
ʊ,ʊ
e,e
ö,ø
ɘ,ɘ
ɵ,ɵ
ɤ,ɤ
o,o
ǝ,ə
ə,ə
ɛ,ɛ
œ,œ
ɜ,ɜ
ɞ,ɞ
ʌ,ʌ
ɔ,ɔ
ä,æ
ɐ,ɐ
a,a
ɑ,ɑ
ɒ,ɒ
◌̥,◌̥
◌̊,◌̊
◌̪,◌̪
◌̬,◌̬
ʰ,ʰ
ʱ,ʱ
◌̹,◌̹
◌͗,◌͗
◌˒,◌˒
◌̜,◌̜
◌͑,◌͑
◌˓,◌˓
◌̟,◌̟
◌˖,◌˖
◌̠,◌̠
◌˗,◌˗
◌̽,◌̽
◌̩,◌̩
◌̍,◌̍
◌̯,◌̯
◌̑,◌̑
◌˞,◌˞
◌ʳ,◌˞
◌̤,◌̤
◌̰,◌̰
◌̼,◌̼
ʷ,ʷ
ʸ,ʲ
◌ˠ,◌ˠ
◌ˤ,◌ˤ
◌̴,◌̴
◌̝,◌̝
◌˔,◌˔
◌̞,◌̞
◌˕,◌˕
◌̘,◌̘
◌̙,◌̙
◌̪,◌̪
◌͆,◌͆
◌̺,◌̺
◌̻,◌̻
◌̃,◌̃
ⁿ,ⁿ
ˡ,ˡ
◌̚,◌̚
ᵊ,ᵊ
ᶿ,ᶿ
ˣ,ˣ
ʼ,ʼ
◌͡◌,◌͡◌
◌͜◌,◌͜◌
ˈ,ˈ
ˌ,ˌ
ː,ː
ˑ,ˑ
◌̆,◌̆
|,|
‖,‖
.,.
‿,‿
◌̋,◌̋
˥,˥
◌́,◌́
˦,˦
◌̄,◌̄
˧,˧
◌̀,◌̀
˨,˨
◌̏,◌̏
˩,˩
ꜜ,ꜜ
ꜛ,ꜛ
◌̌,◌̌
˩˥,˩˥
◌̂,◌̂
˥˩,˥˩
◌᷄,◌᷄
˦˥,˦˥
◌᷅,◌᷅
˩˨,˩˨
◌᷈,◌᷈
˧˦˧,˧˦˧
↗,↗
↘,↘
'''

GLD_IPA_MAP = [(line[:line.find(',')].replace("◌", ""), line[line.find(',') + 1].replace("◌", ""))
               for line in io.StringIO(GLD_IPA_MAP_RAW)]
SORTED_GLD_TO_IPA = sorted(GLD_IPA_MAP, reverse=True)
RE_KEEP = re.compile(r"^[- ~*=()/,A-Z]")


def to_ipa(s: str) -> str:
    result = []
    while s:
        if RE_KEEP.match(s):
            gld = s[:1]
            ipa = gld
        else:
            gld, ipa = next(((gld, ipa) for gld, ipa in SORTED_GLD_TO_IPA if s.startswith(gld)),
                            (None, None))
        if gld:
            result.append(ipa)
            s = s[len(gld):]
        else:
            # Try to decompose the first character
            c = unicodedata.normalize('NFD', s[:1])
            if c == s[:1]:
                # print("{}: Unknown character U+{:04X} at '{}...'".format(context, ord(s[:1]), s[:20]))
                result.append(s[:1])
                s = s[1:]
            else:
                s = c + s[1:]
    return ''.join(result)


def get_unicode_from_cell(sheet, n_row, n_col) -> str:
    def apply_subscript(s: str, start: int, end: int) -> str:
        for ofs in range(start, (end if end >= 0 else len(s))):
            if s[ofs].isdigit():  # TODO: check if it breaks anything
                assert s[ofs].isdigit(), \
                    "Can only unicodize subscript digits in {} offset {} row {}, col {}".format(
                        s, ofs, n_row, n_col)
                s = ''.join((s[:ofs], chr(0x2080 + int(s[ofs])), s[ofs + 1:]))
        return s

    value = str(sheet.cell(n_row, n_col).value)
    runlist = sheet.rich_text_runlist_map.get((n_row, n_col))
    if runlist:
        subscript_start = -1
        for offset, font_index in runlist:
            if subscript_start >= 0:
                value = apply_subscript(value, subscript_start, offset)
                subscript_start = -1
            font = sheet.book.font_list[font_index]
            if font.escapement == 2:
                subscript_start = offset
            #elif font.escapement == 1:
            #    raise Exception("Can't process superscript in {} offset {} row {} col {}"
            #                    .format(value, offset, n_row, n_col))
        if subscript_start >= 0:
            value = apply_subscript(value, subscript_start, -1)
    return value


def parse_tables(s: str) -> str:
    # Tables processing
    lines = s.split('\n')
    in_table = False
    out_lines = []
    for line in lines:
        this_out = ''
        if not in_table and line.startswith(TABLESEP):
            this_out += '<table><tbody>'
            in_table = True
        if in_table and not line.startswith(TABLESEP):
            this_out += '</tbody></table>'
            in_table = False
        if in_table:
            this_out += '<tr><td>' + line[1:].replace(TABLESEP, '</td><td>') + '</td></tr>'
        else:
            this_out += line
        if this_out.startswith(('<tr>', '</tbody>')):
            out_lines[-1] += this_out
        else:
            out_lines.append(this_out)
    value = '<br/>'.join(out_lines)
    if in_table:
        value += '</tbody></table>'
    return value


def get_html_from_cell(sheet: xlrd.sheet.Sheet, n_row: int, n_col: int) -> str:
    styles = dict(i=-1)

    def close_styles(s: str, start_pos: int, end_pos: int) -> str:
        start = ''
        end = ''
        for style, state in list(styles.items()):
            if state >= 0:
                start += '<{}>'.format(style)
                end += '</{}>'.format(style)
                styles[style] = -1
        return start + s[start_pos:end_pos] + end

    value = get_unicode_from_cell(sheet, n_row, n_col)
    runlist = sheet.rich_text_runlist_map.get((n_row, n_col))
    if runlist:
        out = ''
        run_start = 0
        for offset, font_index in runlist:
            out += close_styles(value, run_start, offset)
            run_start = offset
            font = sheet.book.font_list[font_index]
            for xlrd_style, html_style in XLRD_HTML_STYLE_MAP:
                styles[html_style] = offset if getattr(font, xlrd_style) else -1
            styles['sup'] = offset if font.escapement == 1 else -1
            styles['sub'] = offset if font.escapement == 2 else -1

        out += close_styles(value, run_start, len(value))
        value = out
    return parse_tables(value)


def read_formatted_excel(filename: str) -> pd.DataFrame:
    """
    Reads an xls file into Pandas DataFrame preserving bold/italic/underscore formatting
    and resolving tables into valid HTML
    :param filename:
    :return:
    """
    wb = xlrd.open_workbook(filename, formatting_info=True)
    sheet = wb.sheets()[0]
    colnames = []
    rows = []
    for i, row in enumerate(sheet.get_rows()):
        row_dict = {}
        for j, cell in enumerate(row):
            if i == 0:
                colnames.append(cell.value)
            else:
                if cell.ctype == 0:
                    row_dict[colnames[j]] = None
                elif cell.ctype == 1:
                    extractor = get_html_from_cell if ' notes' in colnames[j] and i > 1 else get_unicode_from_cell
                    row_dict[colnames[j]] = extractor(sheet, i, j)
                elif cell.ctype == 2:
                    row_dict[colnames[j]] = int(cell.value) if abs(cell.value - int(cell.value)) < 1e-6 else cell.value
        if i > 0:
            rows.append(row_dict)

    return pd.DataFrame(rows)
