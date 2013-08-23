#!/usr/bin/env python

import sys
from collections import namedtuple, defaultdict


Entry = namedtuple("Entry", ["s_ref", "e_ref", "s_qry", "e_qry", "len_ref", "len_qry", "contig_id"])
Scaffold = namedtuple("Scaffold", ["name", "contigs"])
Contig = namedtuple("Contig", ["name", "sign"])


def parse_quast_output(filename):
    entries = []
    for line in open(filename, "r"):
        line = line.strip()
        if line.startswith("[") or line.startswith("="):
            continue

        vals = line.split("|")
        coord_ref = map(int, vals[0].split())
        coord_qry = map(int, vals[1].split())
        lengths = map(int, vals[2].split())
        cname = vals[4].split("\t")[1]
        entries.append(Entry( *(coord_ref + coord_qry + lengths + [cname]) ))

    return entries


def parse_contigs_order(filename):
    scaffolds = []
    for line in open(filename, "r"):
        if line.startswith(">"):
            scaffolds.append(Scaffold(line.strip()[1:], []))
        else:
            if line.startswith("gaps"):
                pass
            else:
                name = line.strip("\n").replace("=", "_") #fix for quast
                without_sign = name[1:]
                sign = 1 if name[0] == "+" else -1
                scaffolds[-1].contigs.append(Contig(without_sign, sign))
    return scaffolds


def main():
    if len(sys.argv) < 3:
        print "Usage: test.py quast_out contigs_order"
        return

    entries = parse_quast_output(sys.argv[1])

    by_name = defaultdict(list)
    for entry in entries:
        by_name[entry.contig_id].append(entry)

    for name in by_name:
        by_name[name].sort(key=lambda e: e.len_qry, reverse=True)
        by_name[name] = filter(lambda e: e.len_qry > 0.8 * by_name[name][0].len_qry, by_name[name])
        #print map(lambda e: e.len_qry, by_name[name])

    filtered_entries = []
    for ent_lst in by_name.itervalues():
        filtered_entries.extend(ent_lst)
    filtered_entries.sort(key=lambda e: e.s_ref)

    entry_ord = defaultdict(list)
    for i, e in enumerate(filtered_entries):
        entry_ord[e.contig_id].append(i)
    #print entry_ord

    """
    true_signs = {}
    for e in by_name.itervalues():
        if abs(e[0].e_qry - e[0].s_qry) < 1000000:
            if e[0].e_qry > e[0].s_qry:
                true_signs[e[0].contig_id] = 1
            else:
                true_signs[e[0].contig_id] = -1
        else:
            if e[0].e_qry > e[0].s_qry:
                true_signs[e[0].contig_id] = -1
            else:
                true_signs[e[0].contig_id] = 1
    #print true_signs
    """

    scaffolds = parse_contigs_order(sys.argv[2])
    zero_step = False
    for s in scaffolds:
        #TODO: check signs
        print s.name
        for i, contig in enumerate(s.contigs):
            print contig.name, entry_ord[contig.name]

if __name__ == "__main__":
    main()
