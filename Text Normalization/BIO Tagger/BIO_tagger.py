import pandas as pd
import numpy as np
import re
import itertools

class NumToVnStr:
    """Preprocess numbers into numerical words in Vietnamese"""
    def __init__(self, mot="mốt", muoi='mươi', nghin='nghìn', tu='tư', lam='lăm', linh='linh', ty='tỷ'):
        self.digit = ('không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười')
        self.muoi = muoi
        self.tram = 'trăm'
        self.nghin = nghin
        self.trieu = 'triệu'
        self.ty = ty
        self.mot = mot
        self.tu = tu
        self.lam = lam
        self.linh = linh

    def to_vn_str(self, s):
        return self._arbitrary(s.lstrip('0'))

    def _int(self, c):
        return ord(c) - ord('0') if c else 0

    def _LT1e2(self, s):
        if len(s) <= 1: return self.digit[self._int(s)]
        if s[0] == '1':
            ret = self.digit[10]
        else:
            ret = self.digit[self._int(s[0])]
            if self.muoi: 
                ret += ' ' + self.muoi
            elif s[1] == '0': 
                ret += ' mươi'
        if s[1] != '0':
            ret += ' '
            if   s[1] == '1' and s[0] != '1': ret += self.mot
            elif s[1] == '4' and s[0] != '1': ret += self.tu
            elif s[1] == '5': ret += self.lam
            else: ret += self.digit[self._int(s[1])]
        return ret

    def _LT1e3(self, s):
        if len(s) <= 2: 
            return self._LT1e2(s)
        if s == '000': 
            return ''
        ret = self.digit[self._int(s[0])] + ' ' + self.tram
        
        if s[1] != '0':
            ret += ' ' + self._LT1e2(s[1:])
        elif s[2] != '0':
            ret += ' ' + self.linh + ' ' + self.digit[self._int(s[2])]
        return ret

    def _LT1e9(self, s):
        if len(s) <= 3: 
            return self._LT1e3(s)
        if s == '000000' or s == '000000000': 
            return ''
        mid = len(s) % 3 if len(s) % 3 else 3
        left, right = self._LT1e3(s[:mid]), self._LT1e9(s[mid:])
        hang = self.nghin if len(s) <= 6 else self.trieu

        if not left:
            return self.digit[0] + ' ' + hang + ' ' + right
        if not right: 
            return left + ' ' + hang
        return left + ' ' + hang + ' ' + right

    def _arbitrary(self, s):
        if len(s) <= 9: 
            return self._LT1e9(s)
        mid = len(s) % 9 if len(s) % 9 else 9
        left, right = self._LT1e9(s[:mid]), self._arbitrary(s[mid:])
        hang = ' '.join([self.ty] * ((len(s) - mid) // 9))

        if not left:
            if right: 
                return self.digit[0] + ' ' + hang + ', ' + right
            else: 
                return right
        if not right: 
            return left + ' ' + hang
        return left + ' ' + hang + ', ' + right


def all_num_combinations(word, split=False):
    """Get all outputs of different argument combinations in NumToVnStr()"""
    params = {
        "mot":["mốt", "một"], 
        "linh":['lẻ', "linh"], 
        'tu':['bốn', 'tư'], 
        'nghin':['ngàn', 'nghìn'], 
        'muoi':[False, "mươi"], 
        'ty':'tỉ', 
        'lam':['nhăm','lăm']
    }

    keys = list(params)
    combinations = []
    for values in itertools.product(*map(params.get, keys)):
        num = NumToVnStr(**dict(zip(keys, values))).to_vn_str(word)
        combinations.append(num)
    
    if split == True:
        word_split = list(word)
        word_split = [NumToVnStr().to_vn_str(w) for w in word_split]
        combinations.append(" ".join(word_split))
        
    unique_combinations = list(dict.fromkeys(combinations))
    return unique_combinations


def num_preprocess(string):
    """Runs NumToVnStr and additional conversion for dates and floats"""
    re_1 = re.compile('.*[.,%].*')
    re_2 = re.compile('.*\/.*')
    
    if re_1.match(string):
        string = re.sub('(?<=\d)[.](?=\d)','', string)
        string = re.sub('(?<=\d)[,](?=\d)', ' phẩy ', string)
        string = re.sub('[%]', ' phần trăm ', string)
        # All possible combinations 
        all_combinations = [all_num_combinations(word) for word in string.split(" ") if word.isdecimal()]
        
        all_strings = []
        string_split = string.split(" phẩy ")
        # If there is "phẩy" in the string
        if len(string_split) > 1:
            # Convert the num before "phẩy" and after it
            string_list = [[front, tail] for front in all_combinations[0] for tail in all_combinations[1]]
            for s in string_list:
                all_strings.append(" phẩy ".join(s))
        else: 
            for comb in all_combinations[0]:
                string_split = [comb if word.isdecimal() else word for word in string.split(" ")]
            all_strings.append(" ".join(string_split))
        return all_strings
    elif re_2.match(string):
        if string.count('/') == 1:
            string = re.sub('[/]', ' tháng ', string)
            all_combinations = [all_num_combinations(word) for word in string.split(" ") if word.isdecimal()]
            all_strings = []
            # Convert the num before "tháng" and after it
            string_list = [[front, tail] for front in all_combinations[0] for tail in all_combinations[1]]
            for s in string_list:
                small_string_list = ["ngày "]
                small_string_list.append(" tháng ".join(s))
                all_strings.append("".join(small_string_list))
            return  all_strings
        elif string.count('/') == 2:
            string_split = list(string)
            string_split[string_split.index('/')] = ' tháng '
            string_split[string_split.index('/')] = ' năm '
            string = "".join(string_split)
            all_combinations = [all_num_combinations(word) for word in string.split(" ") if word.isdecimal()]
            all_strings = []
            string_list = [[front, mid, tail] for front in all_combinations[0] for mid in all_combinations[1] for tail in all_combinations[2]]
            for s in string_list:
                small_string_list = ["ngày "]
                small_string_list.append(" tháng ".join(s[0:2]))
                small_string_list.append(" năm "+ s[-1])
                all_strings.append("".join(small_string_list))
            return all_strings
    else: return all_num_combinations(string, split=True)


def both_letr_num(word):
    """Convert strings with both letters (capital) and numbers to Vietnamese words"""
    converter = {
        'A':'a', 'B':'bê', 'C':'xê', 'D':'đê', 'E':'e', 'F':'ép', 'G':'gờ', 'H':'hát', 'I':'i', 'J':'gi', 'K':'ca', 'L':'lờ',
        'M':'mờ', 'N':'nờ', 'O':'o', 'P':'pê', 'Q':'qui', 'R':'rờ', 'S':'ét', 'T':'tê', 'U':'u', 'V':'vê', 'W':'vê kép', 
        'X':'ích', 'Y':'i', 'Z':'dét'
    }
    word_split = list(word)
    new_word_list = []
    num_list = []
    for i, w in enumerate(word_split):
        try:
            if w.isalpha():
                new_word_list.append(converter[w])
            elif w.isdecimal():
                num_list.append(w)
                if word_split[i+1].isalpha():
                    new_word_list.append("".join(num_list))
                    num_list = []
        except IndexError:
            new_word_list.append("".join(num_list))
    
    # all_combinations = [all_num_combinations(w, split=True) for w in new_word_list if w.isdecimal()]

    # def convert(s, x):
    #     num_index = []
    #     reading = []
    #     for i in range(len(s)):
    #         if s[i].isdecimal():
    #             num_index.append(i)

    #     all_call(x, num_index, reading, s.copy(), 0)
    #     return reading

    # def all_call(x, numbers, read, moment, index):
    #     if index == len(numbers):
    #         read.append(moment)
    #         return 
    #     for words in x[index]:
    #         moment[numbers[index]] = words
    #         all_call(x, numbers, read, moment.copy(), index+1)
    
    # all_strings = []
    # for string in convert(new_word_list, all_combinations):
    #     all_strings.append(string)

    return new_word_list

def content_preprocess(content):
    """Preprocess the content of each article with Regex"""
    # Preprocess with regex
    content = re.sub('\xa0', ' ', content)
    content = re.sub('(\n)',' ', content)
    content = re.sub('[\(\)"\\\[\]\{}]', '', content)
    content = re.sub('(?<=\d)-(?=\d)', ' đến ', content)
    content = re.sub('(?<=\s)km(?=\W)', 'ki lô mét', content)
    content = re.sub('(?<=\s)km2(?=\W)', 'ki lô mét vuông', content)
    content = re.sub('(?<=\s)m(?=\W)', ' mét', content)
    content = re.sub('(?<=\s)m2(?=\W)', 'mét vuông', content)
    content = re.sub('(?<=\s)kg(?=\W)', 'ki lô gam', content)
    content = re.sub('(@gmail)', ' a còng gờ mêu ', content)
    content = re.sub('(?<=\D)[.]|[.](?=\D)', ' .', content)
    content = re.sub('(?<=\D)[,]|[,](?=\D)', ' ,', content)
    content = re.sub(';', ' ;', content)
    content = re.sub(':', ' :', content)
    content = re.sub('\?', ' ?', content)
    content = re.sub('!', ' !', content)
    # Abbreviations
    content = re.sub('(USD)', 'u ét đê', content)
    content = re.sub('(TP HCM)', 'Thành phố Hồ Chí Minh', content)
    content = re.sub('(THCS)', 'Trung học cơ sở', content)
    content = re.sub('(THPT)', 'Trung học phổ thông', content)
    content = re.sub('(CLB)', 'Câu lạc bộ', content)
    content = re.sub('(HTX)', 'Hợp tác xã', content)
    content = re.sub('(BTC)', 'Ban tổ chức', content)
    content = re.sub('(NXB)', 'Nhà xuất bản', content)
    content = re.sub('(TW)', "Trung ương", content)
    content = re.sub('(UBND)', 'Uỷ ban nhân dân', content)
    content = re.sub('(VNCH)', 'Việt Nam Cộng Hoà', content)
    content = re.sub('(LHQ)', 'Liên Hợp Quốc', content)
    content = re.sub('(cty)', 'công ty', content)
    content = re.sub('(TV)', 'ti vi', content)
    content = re.sub('(CD)', 'xi đi', content)
    content = re.sub('(DVD)', 'đi vi đi', content)
    content = re.sub('(HIV)', 'hát i vê', content)
    content = re.sub('(SIDA)', 'si đa', content)
    content = re.sub('(nCov)', 'cô vi', content)

    content_split = content.split(" ")
    new_content_split = []
    for i, word in enumerate(content_split):
        tired = False
        for w in list(word): 
            if w.isdecimal(): tired = True
        if tired == True:
            z1 = re.compile("[A-Z]+")
            if z1.match(word):
                z2 = re.findall("[A-Z]+", word)
                try:
                    both_letter_num = both_letr_num(z2[0])
                    for w in both_letter_num:
                        new_content_split.append(w)
                except IndexError:
                    pass
            else: new_content_split.append(word)
        else: new_content_split.append(word)

    new_content_split = [word for word in new_content_split if word != '']
    return new_content_split


def BIO_tagging(content_split):
    """BIO tagging with 3 tags for text normalization and 7 tags for punctuation restoration"""
    d = re.compile('\d')
    e = re.compile('.*\/.*')

    # Text normalization and Punctuation restoration for BIO tagging
    bio_tn_col = []
    bio_pr_col = []
    for i, word in enumerate(content_split):
        if word[0].isupper(): bio_tn_col.append("B-CAP")
        elif word.islower(): bio_tn_col.append("O")
        elif d.match(word):
            if e.match(word): bio_tn_col.append("B-DATE")
            else: bio_tn_col.append("B-NUMB")
        else: bio_tn_col.append("O")

        try:
            if content_split[i+1] == ".": bio_pr_col.append("PERIOD")
            elif content_split[i+1] == ";": bio_pr_col.append("SEMICOLON")
            elif content_split[i+1] == ":": bio_pr_col.append("COLON")
            elif content_split[i+1] == ",": bio_pr_col.append("COMMA")
            elif content_split[i+1] == "?": bio_pr_col.append("QUESTIONMARK")
            elif content_split[i+1] == "!": bio_pr_col.append("EXCLAIMATIONMARK")
            elif content_split[i+1] == "-": bio_pr_col.append("DASH")
            else: bio_pr_col.append("O")
        except IndexError:
            bio_pr_col.append("O")

    # df_bio has words in their raw forms + their temporary BIO tagging
    df_bio = pd.DataFrame(content_split, columns=["Raw words"])
    df_bio["BIO text norm"] = bio_tn_col
    df_bio["BIO punc rest"] = bio_pr_col
    # Drop punctuations
    df_bio = df_bio[df_bio["Raw words"] != "."]
    df_bio = df_bio[df_bio["Raw words"] != ";"]
    df_bio = df_bio[df_bio["Raw words"] != ":"]
    df_bio = df_bio[df_bio["Raw words"] != ","]
    df_bio = df_bio[df_bio["Raw words"] != "?"]
    df_bio = df_bio[df_bio["Raw words"] != "!"]
    df_bio = df_bio[df_bio["Raw words"] != "-"]
    df_bio.reset_index(inplace=True, drop=True)

    # New text normalization and punctuation restoration BIO tagging columns 
    bio_tn_col_2 = []
    bio_pr_col_2 = []
    # Words after being processed go into this list
    new_content_split = []
    for i, word in enumerate(df_bio["Raw words"]):
        if d.match(word):
            try:
                all_num_to_str = num_preprocess(word)
                for num_to_str in all_num_to_str:
                    new_content_split.append(num_to_str)

                    new_tn = [df_bio["BIO text norm"].values[i]]
                    new_pr = []
                    j = 0
                    while j < len(num_to_str.split(" "))-1:
                        new_tn.append("I-" + df_bio["BIO text norm"].values[i].split("-")[1])
                        new_pr.append("O")
                        j += 1
                    new_pr.append(df_bio["BIO punc rest"].values[i])
                    bio_tn_col_2.extend(new_tn)
                    bio_pr_col_2.extend(new_pr)
            except IndexError:
                continue
        else:
            new_content_split.append(word)
            bio_tn_col_2.append(df_bio["BIO text norm"].values[i])
            bio_pr_col_2.append(df_bio["BIO punc rest"].values[i])

    # Extend "ngày ba tháng tám" into "ngày", "ba", "tháng", "tám"
    for i, word in enumerate(new_content_split):
        word_split = word.split(" ")
        if len(word_split) > 1:
            new_content_split[i:i+1] = word_split
    
    # Decapitalize words
    new_content_split = [word.lower() for word in new_content_split]

    # df_bio_2 has processed words and their new BIO tagging
    df_bio_2 = pd.DataFrame(new_content_split, columns=["Processed words"])
    del df_bio
    # Change consecute B-CAP, B-CAP, ... to B-CAP, I-CAP, ...
    bio_tn_col_2 = " ".join(bio_tn_col_2)
    bio_tn_col_2 = re.sub("(?<=B-CAP )B-CAP", "I-CAP", bio_tn_col_2).split(" ")
    df_bio_2["BIO text norm"] = bio_tn_col_2
    df_bio_2["BIO punc rest"] = bio_pr_col_2
    return df_bio_2

if __name__ == "__main__":
    input_path = "/Users/macbook/Desktop/Everything Deep Learning/FPT.AI 2020/Text Normalization/raw_text/a/vnexpress_p2to402.csv"
    output_path = "/Users/macbook/Desktop/Everything Deep Learning/FPT.AI 2020/Text Normalization/BIO tags/test_BIO3.csv"
    df = pd.read_csv(input_path, index_col=0)
    content = df.Content[10054]
    content_split = content_preprocess(content)
    bio_df = BIO_tagging(content_split)
    bio_df.to_csv(output_path, index=False)
