############ This script counts the ratio of different verbal (root) structures, with significance testing; and calculate dependency length ########

#usr/bin/env python3

import stanza, json, logging, sys, os, io, random, statistics, argparse, csv
from os import path
from glob import glob
import numpy as np


def analyse(instance_data, total_sentences):

    stats = {}
    transitive_constructions = []
    all_constructions = []

    for line in instance_data:
        if line['Order'] in ['sov', 'svo', 'vso', 'vos', 'ovs', 'osv']:
            transitive_constructions.append(line['Order'])
        all_constructions.append(line['Order'])

    transitive_total = len(transitive_constructions)
    total = len(all_constructions)

    transitive_stats = {"sov": [], "svo": [], "vso": [], "vos": [], "ovs": [], "osv": []}
    all_stats = {"sov": [], "svo": [], "vso": [], "vos": [], "ovs": [], "osv": [], "sv": [], "vs": [], "vo": [], "ov": [], "v": []}

    ########### Significance testing for transitive constructions ##########
    for i in range(10000):
        sample = random.choices(transitive_constructions, k = transitive_total)

        for order in transitive_stats.keys():
            order_count = sample.count(order)
            transitive_stats[order].append(order_count * 100 / transitive_total)

    ########### Significance testing for all verbal constructions ##########
    for i in range(10000):
        sample = random.choices(all_constructions, k = total)

        for order in all_stats.keys():
            order_count = sample.count(order)
            all_stats[order].append(order_count * 100 / total)

    for order in transitive_stats.keys():
        transitive_stats[order].sort()
        stats['transitive_' + order] = [round(statistics.mean(transitive_stats[order]), 2), round(transitive_stats[order][250], 2), round(transitive_stats[order][9750], 2)]

    for order in all_stats.keys():
        all_stats[order].sort()
        stats[order] = [round(statistics.mean(all_stats[order]), 2), round(all_stats[order][250], 2), round(all_stats[order][9750], 2)]

    stats['Num_of_transitive'] = transitive_total
    stats['Num_of_contructions'] = total
    stats['Num_of_sent'] = total

    for key in stats:
        print(key, stats[key])

    return stats


def write_stats(language, corpus, stats, out_path):

    header = ['Language', 'File', 'Feature', 'Mean', 'CI250', 'CI9750', 'Construction', 'Num_of_transitive', 'Num_of_contructions', 'Num_of_sent']
    with io.open(path.join(out_path, "stats.csv"), 'a', newline = '', encoding = 'utf-8') as f:

        writer = csv.writer(f)
        #writer.writerow(header)

        if len(stats) > 0:

            for key in stats.keys():
                if key.split('_')[0] == 'transitive':
                    writer.writerow([language, corpus, key, stats[key][0], stats[key][1], stats[key][2], 'transitive', stats['Num_of_transitive'], stats['Num_of_contructions'], stats['Num_of_sent']])
                elif key == 'ave_dl':
                    writer.writerow([language, corpus, 'ave_dl', stats[key][0], stats[key][1], stats[key][2]])
                    writer.writerow([language, corpus, 'ave_dl_sl', stats[key][3], stats[key][4], stats[key][5]])
                elif key in ['ave_dl_sl', 'Num_of_transitive', 'Num_of_contructions', 'Num_of_sent']:
                    continue
                else:
                    writer.writerow([language, corpus, key, stats[key][0], stats[key][1], stats[key][2], 'all', '', '', ''])


####### Generating output ##########
def main(args):

    with open(args.instf, 'r') as instances_in:
        instances_reader = csv.DictReader(instances_in)
        stats = analyse(instances_reader, args.sentn)
        write_stats(args.lang, args.corp, stats, args.statp)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Analyze data from Stanza-formatted JSON and JSONL dependency parse files.')

    parser.add_argument('-i', '--instf', type = str, help = 'input path to instances file')
    parser.add_argument('-s', '--statp', type = str, help = 'output path for stats file')
    parser.add_argument('-l', '--lang', type = str, help = 'language name or code')
    parser.add_argument('-c', '--corp', type = str, help = 'corpus name or code')
    parser.add_argument('-n', '--sentn', type = str, help = 'original # of sentences')

    parser.add_argument('--log',    action='store_true', default=False, help='log events to file')

    args = parser.parse_args()

    if(args.log):
        logging.basicConfig(filename=(args.channel + '_dependencies.log'),level=logging.DEBUG)

    main(args)
