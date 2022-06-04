import argparse
from ptt import PTT
import os
from pathlib import Path

ROOT = str(Path(__file__).parent) + '/res/'

def parse_args():
    """
    -k: keyword
    -f: forum
    -p: pasth
    -n: pages
    -a: author
    -l: headers
    -c: csv
    -x: xlsx
    -cp: path to  csv
    -xp: path to xlsx
    """
    description = 'hello'
    parser = argparse.ArgumentParser(description=description) 
                                                                     
    parser.add_argument('-k', help='your searching keyword', default=None)
    parser.add_argument('-f', help='The forum of ptt', type=str, default='Stock')
    parser.add_argument('-p', help='path to save your txt logger file', type=str, default='logger.txt')
    parser.add_argument('-n', help='number of page to parse', type=int, default=2)
    parser.add_argument('-a', help='search article from specify author', default=None)
    parser.add_argument('-l', help='the headers of requests module', type=dict, default={})
    parser.add_argument('-c', help='write output to csv', type=bool, default=False)
    parser.add_argument('-x', help='write output to xlsx', type=bool, default=True)
    parser.add_argument('-cp', help='path to save your csv file', default='ptt.csv')
    parser.add_argument('-xp', help='path to save your xlsx file', default='ptt.xlsx')
    
    args = parser.parse_args()                                        
    return args

if __name__ == '__main__':

    args = parse_args()

    params = {}
    if args.k or args.a is not None:
        params['q'] = args.k if args.a is None else args.a
    
    ptt = PTT(
        forum=args.f,
        num_pages=args.n,
        headers=args.l,
        params=params,
        txt_path=ROOT+args.p
        )
        
    ptt.fetch()
    if args.c:
        ptt.to_csv(ROOT+args.cp)
    if args.x: 
        ptt.to_xlsx(ROOT+args.xp)
