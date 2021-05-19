############ This script counts the ratio of different verbal (root) structures, with significance testing; and calculate dependency length ########

#usr/bin/env python3

import sys, glob, os, io, random, statistics, argparse, csv
import numpy as np

### reading in sentences in CoNLL format ###

def conll_read_sentence(file_handle):

    sent = []

    for line in file_handle:
        line = line.strip('\n')

        if line.startswith('#') is False :
            toks = line.split("\t")

            if len(toks) == 1:
                return sent
            else:
                if toks[0].isdigit() == True:
                    sent.append(toks)

    return None


########## Calcularint degree of head-finality #######

def head_final(sentence_list):

    closed_class = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'PUNCT']
    closed_rel = ['ROOT', 'AUX', 'CASE',  'CC', 'DET','EXPL', 'MARK', 'PUNCT']
    particles = ['は', 'に', 'で', 'には', 'では', 'が', 'を', 'へ', 'へと', 'と', 'の']

    head_final_c = 0
    head_final_c_no_func = 0

    dependency_c = 0
    dependency_c_no_func = 0

    for sentence in sentence_list:

        for tok in sentence:
            if tok[7].upper() not in ['MARK'] and tok[3].upper() not in ['PUNCT'] and sentence[int(tok[6]) - 1][3].upper() not in ['PUNCT']:
                if tok[1] not in particles:
                    try:
                        if int(tok[6]) > int(tok[0]):
                            head_final_c += 1
                    except:
                        continue
                    dependency_c += 1
                if tok[7].upper() not in closed_rel and tok[3].upper() not in closed_class and sentence[int(tok[6]) - 1][3].upper() not in closed_class:
                    try:
                        if int(tok[6]) > int(tok[0]):
                            head_final_c_no_func += 1
                    except:
                        continue
                    dependency_c_no_func += 1

    return {'head_finality': head_final_c / dependency_c, 'head_finality_no_func': (head_final_c_no_func / dependency_c_no_func)}


###### Extracting instances ######


def extract_instance(file_handle, directory, file_type):

    all_sent = []
    head_final_list = []
    head_final_no_func_list = []

    with io.open(directory + '/' + file_handle, encoding = 'utf-8') as f:
        sent = conll_read_sentence(f)

        while sent is not None:
            all_sent.append(sent)
            sent = conll_read_sentence(f)

    for i in range(10000):
        sample = random.choices(all_sent, k = len(all_sent))

        head_final_sample = head_final(sample)
        head_final_list.append(head_final_sample['head_finality'])
        head_final_no_func_list.append(head_final_sample['head_finality_no_func'])


    head_final_list.sort()
    head_final_no_func_list.sort()

    print("{0} head_finality_updated: {1}, {2}, {3}".format(file_handle, round(statistics.mean(head_final_list), 2), round(head_final_list[250], 2), round(head_final_list[9750], 2)))
    print("{0} head_finality_no_func_updated: {1}, {2}, {3}".format(file_handle, round(statistics.mean(head_final_no_func_list), 2), round(head_final_no_func_list[250], 2), round(head_final_no_func_list[9750], 2)))


####### Generating output ##########

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type = str, help = 'path to UD data')
    args = parser.parse_args()

    path = args.input
    os.chdir(path)

    for directory in glob.glob('*'):
        directory_name = directory
        language = directory_name.split('-')[0][3 : ]

        train_f = ''
        test_f = ''

        for file in os.listdir(directory):
            if file.endswith('-ud-train.conllu'):
                train_f = file
                extract_instance(train_f, directory, 'train')
