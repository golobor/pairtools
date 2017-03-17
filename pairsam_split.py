#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import pipes
import sys


def main():
    parser = argparse.ArgumentParser(
        'Splits a .pairsam file into pairs and sam entries')
    parser.add_argument(
        'infile', nargs='?', 
        type=argparse.FileType('r'), 
        default=sys.stdin)
    parser.add_argument(
        "--out-pairs", 
        type=str, 
        required=True)
    parser.add_argument(
        "--out-sam", 
        type=str, 
        required=True)
    parser.add_argument(
        "--comment-char", 
        type=str, 
        default="#", 
        help="The first character of comment lines")
    args = vars(parser.parse_args())

    # Output streams
    if args['out_pairs'] is None:
        pairs_file = sys.stdout
    else:
        pairs_file = open_bgzip(args['out_pairs'], mode='w')
    sam_file = open_sam_or_bam(args['out_sam'], 'w')

    # Input pairsam
    instream = args['infile']
    comment_char = args['comment_char']

    # Split
    for line in instream.readlines():
        if line.startswith(comment_char):
            if line.startswith(comment_char+'@'):
                sam_file.write(line[len(comment_char):])
            else:
                pairs_file.write(line)
            continue

        cols = line[:-1].split('\v')
        pairs_file.write('\t'.join(cols[:8]))
        pairs_file.write('\n')
        
        for col in cols[8:]:
            sam_file.write(col)
            sam_file.write('\n')

    if hasattr(pairs_file, 'close'):
        pairs_file.close()

    if hasattr(sam_file, 'close'):
        sam_file.close()


def open_sam_or_bam(path, mode):
    if mode not in ['r','w']:
        raise Exception("mode can be either 'r' or 'w'")
    if path.endswith('.bam'):
        if mode =='w': 
            t = pipes.Template()
            t.append('samtools view -bS', '--')
            f = t.open(path, 'w')
        elif mode =='r': 
            t = pipes.Template()
            t.append('samtools view -h', '--')
            f = t.open(path, 'r')
        else:
            raise Exception("Unknown mode : {}".format(mode))
        return f
    else:
        return open(path, mode)


def open_bgzip(path, mode):
    if mode not in ['r','w']:
        raise Exception("mode can be either 'r' or 'w'")
    if path.endswith('.gz'):
        if mode =='w': 
            t = pipes.Template()
            t.append('bgzip -c', '--')
            f = t.open(path, 'w')
        elif mode =='r': 
            t = pipes.Template()
            t.append('zcat', '--')
            f = t.open(path, 'r')
        else:
            raise Exception("Unknown mode : {}".format(mode))
        return f
    else:
        return open(path, mode)


if __name__ == '__main__':
    main()
