import sys
import string
import math

key = ""
query = ""
vectors = []
vec_len = 200;

totalwords = []


def wordsMatch(key, totalwords):
    wordlength = 0;
    matchlength = 0;
    for word in totalwords:
        wordlength += len(word)
        if key.find(word) >= 0:
            matchlength += len(word); 
    if wordlength > len(key) or float(matchlength) / len(key) > 0.6:
        return True;
    return False;


def vecToStr(vectors):
    if len(vectors) < 1:
        return;
    vector = vectors[0]
    for i in xrange(1, len(vectors)):
        for j in xrange(0, vec_len):
            vector[j] += vectors[i][j]
    outstr = ""
    sum = 0;
    for j in xrange(0, vec_len):
        sum += vector[j] * vector[j]
    sum = math.sqrt(sum);
    if sum < 1e-5:
        return ""

    for j in xrange(0, vec_len):
        outstr += "%0.7f "%(vector[j]/sum)
    return outstr[0:-1]

for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) < 4:
        continue;
    if fields[0] == "":
        continue;
    if key != fields[0]:
        if key != "":
            if wordsMatch(key, totalwords):
                outstr = vecToStr(vectors)
            #if outstr != "":
                print key + "\t" + outstr
        vectors = []
        key = fields[0]
        totalwords = []
    word = fields[1]
    totalwords.append(word);
    weight = string.atof(fields[2])
    #values = [weight * string.atof(x) for x in fields[3].split(" ")]
    norm = math.sqrt(sum([string.atof(x) ** 2 for x in fields[3].split(" ")]))
    values = [weight * string.atof(x) / norm for x in fields[3].split(" ")]
    vectors.append(values);

if wordsMatch(key, totalwords):
    outstr = vecToStr(vectors)
#if outstr != "":
    print key + "\t" + outstr
totalwords = []
vectors = []
