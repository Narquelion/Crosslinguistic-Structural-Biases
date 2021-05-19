import stanza, json, logging, sys, os, io, random, statistics, argparse, csv
from os import path
from glob import glob
import numpy as np


def head_final(sentence_list):

    closed_class = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'PUNCT']
    closed_rel = ['ROOT', 'AUX', 'CASE',  'CC', 'DET','EXPL', 'MARK', 'PUNCT']
    particles = ['は', 'に', 'で', 'には', 'では', 'が', 'を', 'へ', 'へと', 'と', 'の']

    head_final_c = 0
    head_final_c_no_func = 0

    dependency_c = 0
    dependency_c_no_func = 0

    head_final_list = []
    head_final_no_func_list = []

    for i in range(10000):

        sample = random.choices(sentence_list, k = len(sentence_list))

        for sentence in sample:

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

        head_final_list.append(head_final_c / dependency_c)
        head_final_no_func_list.append(head_final_c_no_func / dependency_c_no_func)

    head_final_list.sort()
    head_final_no_func_list.sort()

    return {'head_finality_updated': [round(statistics.mean(head_final_list), 2), round(head_final_list[250], 2), round(head_final_list[9750], 2)],
            'head_finality_no_func_updated': [round(statistics.mean(head_final_no_func_list), 2), round(head_final_no_func_list[250], 2), round(head_final_no_func_list[9750], 2)]}


def ave_dl(sent_list):

    closed_class = ['ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'PUNCT']
    closed_rel = ['ROOT', 'AUX', 'CASE',  'CC', 'DET','EXPL', 'MARK', 'PUNCT']
    particles = ['は', 'に', 'で', 'には', 'では', 'が', 'を', 'へ', 'へと', 'と', 'の']

    all_dl = []
    all_dl_no_func = []
    all_sent_dl = []
    all_sent_dl_no_func = []

    for sent in sent_list:

        sl = 0
        sl_no_func = 0

        dl = []
        dl_no_func = []

        for tok in sent:
            if tok[7].upper() not in ['MARK'] and tok[3].upper() not in ['PUNCT'] and sent[int(tok[6]) - 1][3].upper() not in ['PUNCT']:
                if tok[1] not in particles:
                    try:
                        dl.append(abs(int(tok[6]) - int(tok[0])))
                    except:
                        try:
                            dl.append(abs(int(tok[-4]) - int(tok[0])))
                        except:
                            continue
                    sl += 1

                if tok[7].upper() not in closed_class and tok[3].upper() not in closed_rel and sent[int(tok[6]) - 1][3].upper() not in closed_class:
                    try:
                        dl_no_func.append(abs(int(tok[6]) - int(tok[0])))
                    except:
                        dl_no_func.append(abs(int(tok[-4]) - int(tok[0])))
                    sl_no_func += 1

        try: # Note: length may be zero when punct is excluded.

            ### average dependency length ###
            ave_dl = sum(dl) / len(dl)
            all_dl.append(ave_dl)

            ### average dependency length normalized by sentence length ###
            ave_sent_dl = ave_dl / sl
            all_sent_dl.append(ave_sent_dl)

        except:
            continue

        ### exclude fuction words/relations ###

        try:
            ave_dl_no_func = sum(dl_no_func) / len(dl_no_func)
            ave_sent_dl_no_func = ave_dl_no_func / sl_no_func
            all_dl_no_func.append(ave_dl_no_func)
            all_sent_dl_no_func.append(ave_sent_dl_no_func)
        except:
            continue


    ### significance testing ###

    all_dl_range = []
    all_dl_range_no_func = []

    all_sent_dl_range = []
    all_sent_dl_range_no_func = []

    for i in range(10000):

        sample_all_dl = random.choices(all_dl, k = len(all_dl))
        sample_all_dl_no_func = random.choices(all_dl_no_func, k = len(all_dl_no_func))

        sample_all_sent_dl = random.choices(all_sent_dl, k = len(all_sent_dl))
        sample_all_sent_dl_no_func = random.choices(all_sent_dl_no_func, k = len(all_sent_dl_no_func))

        ave_all_dl = sum(sample_all_dl) / len(sample_all_dl)
        ave_all_dl_no_func = sum(sample_all_dl_no_func) / len(sample_all_dl_no_func)

        ave_all_sent_dl = sum(sample_all_sent_dl) / len(sample_all_sent_dl)
        ave_all_sent_dl_no_func = sum(sample_all_sent_dl_no_func) / len(sample_all_sent_dl_no_func)

        all_dl_range.append(ave_all_dl)
        all_dl_range_no_func.append(ave_all_dl_no_func)

        all_sent_dl_range.append(ave_all_sent_dl)
        all_sent_dl_range_no_func.append(ave_all_sent_dl_no_func)

    all_dl_range.sort()
    all_dl_range_no_func.sort()
    all_sent_dl_range.sort()
    all_sent_dl_range_no_func.sort()

    return {'ave_dl': [round(statistics.mean(all_dl_range), 2), round(all_dl_range[250], 2), round(all_dl_range[9750], 2)],
            'ave_dl_no_func': [round(statistics.mean(all_dl_range_no_func), 2), round(all_dl_range_no_func[250], 2), round(all_dl_range_no_func[9750], 2)],
            'ave_dl_sl': [round(statistics.mean(all_sent_dl_range), 2), round(all_sent_dl_range[250], 2), round(all_sent_dl_range[9750], 2)],
            'ave_dl_sl_no_func': [round(statistics.mean(all_sent_dl_range_no_func), 2), round(all_sent_dl_range_no_func[250], 2), round(all_sent_dl_range_no_func[9750], 2)]}


def read_sentences(json_data):

    # Convert sentences from Stanza format to CoNLLu format
    conll_sentences = stanza.utils.conll.CoNLL.convert_dict(json_data)
    return [sent for sent in conll_sentences]


def get_avg_dl(fns, statsf, language, corpus, type):

    all_sentences = []

    for fn in fns:

        with open(fn, 'r') as corpus_in:

            if type == "json": # Each file is one Document
                try:
                    json_data = json.load(corpus_in)
                    all_sentences += read_sentences(json_data)
                except json.decoder.JSONDecodeError:
                    logging.info("Could not decode JSON. Is it empty?")
            else: # Each line is one document
                for line in corpus_in:
                    try:
                        all_sentences += read_sentences(json.loads(line))
                    except json.decoder.JSONDecodeError:
                        logging.info("Could not decode JSON. Is it empty?")

    #dl_results = ave_dl(all_sentences)
    finality_results = head_final(all_sentences)

    with open(statsf, 'a') as stats_out:

        #for key in dl_results:
        #    data = dl_results[key]
        #    if len(data) > 1:
        #        stats_out.write("{0},{1},{2},{3},{4},{5},all,,,\n".format(language, corpus, key, data[0], data[1], data[2]))
        #    else:
        #        stats_out.write("{0},{1},{2},{3},,,all,,,\n".format(language, corpus, key, data[0]))

        for key in finality_results:
            data = finality_results[key]
            stats_out.write("{0},{1},{2},{3},{4},{5},all,,,\n".format(language, corpus, key, data[0], data[1], data[2]))


####### Generating output ##########

def main(args):

    type = "json"
    fns = sorted(glob(path.join(args.corpus, "*.json")))

    if(len(fns) == 0):

        fns = sorted(glob(path.join(args.corpus, "*.jsonl")))

        if(len(fns) == 0):
            logging.error("No JSON(L) files found. Did you specify the correct path?")
            return 1
        else:
            type = "jsonl"

    get_avg_dl(fns, args.statsf, args.lang, args.name, type)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Analyze data from Stanza-formatted JSON and JSONL dependency parse files.')

    parser.add_argument('-c', '--corpus', type = str, help = 'path to data')
    parser.add_argument('-l', '--lang', type = str, help = 'language')
    parser.add_argument('-n', '--name', type = str, help = 'corpus name')
    parser.add_argument('-o', '--statsf', type = str, help = 'stats output file')
    parser.add_argument('--log',    action='store_true', default=False, help='log events to file')

    args = parser.parse_args()

    if(args.log):
        logging.basicConfig(filename=(args.channel + '_dependencies.log'),level=logging.DEBUG)

    main(args)
