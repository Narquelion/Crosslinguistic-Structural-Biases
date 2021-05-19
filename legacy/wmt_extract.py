############ This script counts the ratio of different verbal (root) structures, with significance testing; and calculate dependency length ########

#usr/bin/env python3

import stanza, json, logging, sys, os, io, random, statistics, argparse, csv
from os import path
from glob import glob
import numpy as np


### check if verb has nsubj ###
### only nsubj to prevent language specificity ###
### therefore no nsubj:pass ###

def has_subj(verb_index, sentence):

    subj = {}

    for tok in sentence:
        if tok[6] == verb_index and tok[7].startswith('nsubj'):
            subj[tok[7]] = int(tok[0])

    return subj

### check if verb has obj ###

def has_obj(verb_index, sentence):

    obj = {}

    for tok in sentence:
        if tok[6] == verb_index and tok[7].startswith('obj'):
            obj[tok[7]] = int(tok[0])

    return obj

### check if verb has complement clause ###

def has_comp(verb_index, sentence):

    comp = {}

    for tok in sentence:
        if tok[6] == verb_index and (tok[7].startswith('ccomp') or tok[7].startswith('xcomp')):
            comp[tok[7]] = int(tok[0])

    return comp

### check if verb is in a V conj V relation ###

def has_conj(verb_index, sentence):

    conj = {}

    for tok in sentence:
        if tok[6] == verb_index and tok[7].startswith('conj'):
            conj[tok[7]] = int(tok[0])

    return conj

### check if verb has an auxiliary dependent ###

def has_aux(verb_index, sentence):
    aux = {}

    for tok in sentence:
        if tok[6] == verb_index and tok[7].startswith('aux'):
            aux[tok[7]] = int(tok[0])

    return aux


def determine_order(subj, obj, verb):

    # No expressed arguments
    if subj == None and obj == None:
        return 'v'

    # Subject only
    elif subj == None:
        if obj < verb:
            return 'ov'
        else:
            return 'vo'

    # Object only
    elif obj == None:
        if subj < verb:
            return 'sv'
        else:
            return 'vs'

    # Transitive; must check all possibilities?
    else:
        if subj < obj  and obj  < verb:
            return 'sov'
        if subj < verb and verb < obj:
            return 'svo'
        if verb < subj and subj < obj:
            return 'vso'
        if verb < obj  and obj  < subj:
            return 'vos'
        if obj  < verb and verb < subj:
            return 'ovs'
        if obj  < verb and subj < verb:
            return 'osv'

def order(verb_index, sentence):

    # Find arguments of verb
    subj_d = has_subj(verb_index, sentence)
    obj_d  = has_obj(verb_index, sentence)
    comp_d = has_comp(verb_index, sentence)
    conj_d = has_conj(verb_index, sentence)

    # Can include cases with AUX for languages like German and Dutch
    # aux_d = has_aux(verb_index, sentence)

    verb_index = int(verb_index)
    info = {'verb': verb_index}

    # Check for nominal subject
    if len(subj_d) == 1 and 'nsubj' in subj_d:

        # S, V and O, allowing cases with O and complemen
        if len(obj_d) == 1 and 'obj' in obj_d and len(conj_d) == 0:
            info['nsubj'] = subj_d['nsubj']
            info['obj'] = obj_d['obj']

        # S and V, allowing cases with O and complements
        elif len(obj_d) == 0 and len(comp_d) == 0 and len(conj_d) == 0:
            info['nsubj'] = subj_d['nsubj']
            info['obj'] = None

    # Check for object
    elif len(subj_d) == 0:

        # O and V, allowing cases with O and complements
        if len(obj_d) == 1 and 'obj' in obj_d and len(conj_d) == 0:
            info['nsubj'] = None
            info['obj'] = obj_d['obj']

        # V, no complements
        elif len(obj_d) == 0 and len(comp_d) == 0 and len(conj_d) == 0:
            info['nsubj'] = None
            info['obj'] = None

    try:
        info['order'] = determine_order(info['nsubj'], info['obj'], verb_index)
    except KeyError as e:
        logging.info("Sentence does not meet requirements; skipping")
        return None

    return info


########### Calculating average dependency length ###############

def ave_dl(json_data, sent_list):

    all_dl = []

    all_sent_dl = []

    for sent in sent_list:
        sl = len(sent)
        dl = []
        for tok in sent:
            try:
                dl.append(abs(int(tok[6]) - int(tok[0])))
            except:
                dl.append(abs(int(tok[-4]) - int(tok[0])))

        ### average dependency length ###

        ave_dl = sum(dl) / len(dl)

        ### average dependency length normalized by sentence length ###

        ave_sent_dl = ave_dl / sl

        all_dl.append(ave_dl)
        all_sent_dl.append(ave_sent_dl)

    ### significance testing ###

    all_dl_range = []
    all_sent_dl_range = []

    for i in range(10000):
        sample = random.choices(all_dl, k = len(all_dl)) # Sample with replacement
        ave = sum(sample) / len(sample)
        all_dl_range.append(ave)

    for i in range(10000):
        sample = random.choices(all_sent_dl, k = len(all_sent_dl))
        ave = sum(sample) / len(sample)
        all_sent_dl_range.append(ave)

    all_dl_range.sort()
    all_sent_dl_range.sort()

    return [round(statistics.mean(all_dl_range), 2), round(all_dl_range[250], 2), round(all_dl_range[9750], 2), round(statistics.mean(all_sent_dl_range), 2), round(all_sent_dl_range[250], 2), round(all_sent_dl_range[9750], 2)]


###### Extracting instances ######
def extract_instances(json_data, csv_out):

    # Convert sentences from Stanza format to CoNLLu format
    conll_sentences = stanza.utils.conll.CoNLL.convert_dict(json_data)
    n = 0

    # Iterate through sentences and determine their arguments and order
    for sent in conll_sentences:

        data = {'Subject': 'None',
                'Subject_lemma': 'None',
                'S_id': 'None',
                'Subject_feats': 'None',
                'Object': 'None',
                'Object_lemma': 'None',
                'O_id': 'None',
                'Object_feats': 'None',
                'Order': 'None'}

        for tok in sent:

            # Only consider sentences with a VERB as root
            if tok[3] == 'VERB' and tok[7] == 'root':

                order_info = order(tok[0], sent)
                if(order_info == None):
                    continue

                n += 1
                data.update({'Verb': tok[1], 'Verb_lemma': tok[2], 'V_id': tok[0]})

                nsubj = order_info['nsubj']
                obj = order_info['obj']

                if nsubj != None:
                    data.update({'Subject': sent[nsubj - 1][1], 'Subject_lemma': sent[nsubj - 1][2], 'S_id': nsubj, 'Subject_feats': sent[nsubj - 1][5]})
                if obj != None:
                    data.update({'Object': sent[obj - 1][1], 'Object_lemma': sent[obj - 1][2], 'O_id': obj, 'Object_feats': sent[obj - 1][5]})

                data.update({'Order': order_info['order']})
                csv_out.writerow(data)

    return n


def write_instances(fns, csv_path, name, type):

    header = ['Verb', 'Verb_lemma', 'V_id', 'Subject', 'Subject_lemma', 'S_id', 'Subject_feats', 'Object', 'Object_lemma', 'O_id', 'Object_feats', 'Order']
    n = 0

    with open(path.join(csv_path, name + '_instances.csv'), 'w') as csv_out:

        writer = csv.DictWriter(csv_out, fieldnames=header)
        writer.writeheader()

        for fn in fns:

            with open(fn, 'r') as corpus_in:

                if type == "json": # Each file is one Document
                    try:
                        json_data = json.load(corpus_in)
                        n += extract_instances(json_data, writer)
                    except json.decoder.JSONDecodeError:
                        logging.info("Could not decode JSON. Is it empty?")
                else: # Each line is one document
                    for line in corpus_in:
                        try:
                            n += extract_instances(json.loads(line), writer)
                        except json.decoder.JSONDecodeError:
                            logging.info("Could not decode JSON. Is it empty?")

    print("Found {0} instances".format(n))

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

    write_instances(fns, args.inst, args.name, type)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Analyze data from Stanza-formatted JSON and JSONL dependency parse files.')

    parser.add_argument('-c', '--corpus', type = str, help = 'path to data')
    parser.add_argument('-i', '--inst', type = str, help = 'path for instances output')
    parser.add_argument('-n', '--name', type = str, help = 'corpus name')
    parser.add_argument('--log',    action='store_true', default=False, help='log events to file')

    args = parser.parse_args()

    if(args.log):
        logging.basicConfig(filename=(args.channel + '_dependencies.log'),level=logging.DEBUG)

    main(args)
