import sys
import CRFPP
import re

class CRFTagger:
    def __init__(self, model_path):
        self.tagger = CRFPP.Tagger("-m " + model_path)

    def segment(self, input_string):
        result = []
        self.tagger.clear()
        for w in input_string:
            w_type = 'zh'
            if re.match(r'^\d+$', w):
                w_type = 'num'
            elif re.match(r'^[a-zA-Z]+$', w):
                w_type = 'en'
            elif re.match(r'^[ \.\(\)\[\]\-　．。，、？！：；「」『』《》＜＞〈〉〔〕［］【】〖〗（）…—◎]+$', w):
                w_type = 'PUNC'
            self.tagger.add("{0} {1} {2}".format(w.strip(), w_type, "S"))
        self.tagger.parse()
        size = self.tagger.size()
        xsize = self.tagger.xsize()
        temp_str = ""
        for i in range(size):
            c = self.tagger.x(i, 0)
            tag = self.tagger.y2(i)
            if tag == 'B':
                if temp_str != "": 
                    result.append(temp_str)
                    temp_str = ""
                temp_str = c
            elif tag == 'I':
                temp_str += c
            elif tag == 'E':
                temp_str += c
                result.append(temp_str)
                temp_str = ""
            elif tag == 'S':
                result.append(c)
        return result


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python " + sys.argv[0] + " model test_str")
        sys.exit(-1)
    crf_model = sys.argv[1]
    test_str = sys.argv[2]
    model = CRFTagger(crf_model)
    res = model.segment(test_str)
    print(res)
