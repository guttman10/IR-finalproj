import math
import sys
from os import listdir
import os
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
ps = PorterStemmer()


def normalize_tw(tw):
    new_tw = {}
    sorted_tw = {}
    for word in tw:
        x = ""
        y = 0
        nsum = 0
        new_tw[word] = []
        sorted_tw[word] = []
        for info in tw[word]:
            if type(info) == float:
                nsum += info ** 2
        for info in tw[word]:
            if type(info) == float:
                if nsum != 0:
                    info /= nsum ** 0.5
            new_tw[word].append(info)
        for info in tw[word]:

            if type(info) == str:
                x = info
                flag = False
            else:
                y = info
                flag = True

            if flag:
                sorted_tw[word].append((x, y))

        sorted_tw[word].sort(key=lambda tup: tup[1], reverse=True)

    print(sorted_tw)
    return sorted_tw


def get_tw(pf):
    n = len(listdir("Files"))
    tw = {}
    idf = {}
    for word in pf:
        tw[word] = []
        df = 0
        for info in pf[word]:
            if type(info) == str:
                df += 1
        idf[word] = math.log(n/df)

        for info in pf[word]:
            if type(info) == str:
                tw[word].append(info)
            else:
                tf = info
                tw[word].append(math.log1p(tf)*idf[word])

    tw = normalize_tw(tw)
    return tw


def index_text_file():
    delimiter_chars = ",.;:!? '"
    word_occurrences = {}
    i = len(listdir("Files"))
    stop_words = set(stopwords.words('english'))
    for txt_filename in listdir("Source"):
        fptr = open("Source/"+txt_filename, "r")
        pfile = open("Files/"+str(i)+".txt", "w")
        for line in fptr:
            pfile.write(line)

        i += 1
        fptr.close()
        pfile.close()
        os.remove("Source/"+txt_filename)

    for txt_filename in listdir("Files"):
        fname = txt_filename
        txt_filename ="Files/" + txt_filename
        try:
            txt_fil = open(txt_filename, "r")

            line_num = 0
            for lin in txt_fil:
                line_num += 1
                # Split the line into words delimited by whitespace.
                words = lin.split()
                # Remove unwanted delimiter characters adjoining words.
                words2 = [word.strip(delimiter_chars) for word in words]
                words2 = [word.lower() for word in words2]
                # Find and save the occurrences of each word in the line.
                for word in words2:
                    if word not in stop_words:
                        word = ps.stem(word)
                        if word in word_occurrences:
                            if fname not in word_occurrences[word]:
                                word_occurrences[word].append(fname)
                            word_occurrences[word].append(line_num)
                        else:
                            word_occurrences[word] = [fname]
                            word_occurrences[word].append(line_num)

            print("Processed {} lines".format(line_num))

            if line_num < 1:
                print("No lines found in text file, no index file created.")
                txt_fil.close()
                sys.exit(0)

            # Display results.
            word_keys = word_occurrences.keys()

            txt_fil.close()

        except IOError as ioe:
            sys.stderr.write("Caught IOError: " + repr(ioe) + "\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write("Caught Exception: " + repr(e) + "\n")
            sys.exit(1)

            # Create the index file.

        idx_fil = open("Indexes/index.txt", "w")

        for word in word_keys:
            line_nums = word_occurrences[word]
            idx_fil.write(word + " ")
            for line_num in line_nums:
                idx_fil.write(str(line_num) + " ")

            idx_fil.write("\n")

        idx_fil.close()


def scan_new_files():
    i = len(listdir("Files"))
    x = len(listdir("Source"))
    if x != 0:
        for txt_filename in listdir("Source"):
            fptr = open("Source/"+txt_filename, "r")
            pfile = open("Files/"+str(i)+".txt", "w")
            for line in fptr:
                pfile.write(line)

            i += 1
            fptr.close()
            pfile.close()
            os.remove("Source/"+txt_filename)
        index_text_file()


def parseindex():
    pfile = {}
    fname = open("indexes/index.txt", "r")

    for line in fname:
        word = line.split(" ", 1)[0]
        pfile[word] = []
        tf = 0
        flag = True
        line = line.strip(word)

        for info in line.split():

            if str(info).endswith('.txt'):
                if flag:
                    flag = False
                else:
                    pfile[word].append(tf)
                    tf = 0

                pfile[word].append(info[0])

            else:
                tf += 1

        pfile[word].append(tf)
    return pfile

print(stopwords)

    # idx_fil = open("Indexes/index.txt", "w")
    # for word in pfile:
    #     line_nums = pfile[word]
    #     idx_fil.write(word + ": ")
    #     for line_num in line_nums:
    #         idx_fil.write(str(line_num) + " ")
    #
    #     idx_fil.write("\n")


# EOF
