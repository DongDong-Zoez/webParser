import argparse
from dcard import Dcard

def parse_args():
    """
    -f: forum
    -n: article
    -i: headers
    -p: params
    -w: keyword
    -l: logger 
    -c: content
    -t: titles
    -cp: path to  csv
    -xp: path to xlsx
    """
    description = 'It is a simple realization of Dcard parser'
    parser = argparse.ArgumentParser(description=description) 
                                                                     
    parser.add_argument('-f', help='forum', type=str, default='stock')
    parser.add_argument('-n', help='number of article', type=int, default=10)
    parser.add_argument('-i', help='the headers of requests', type=dict, default={})
    parser.add_argument('-p', help='the parameters of requests', type=dict, default={'popular' : 'false', 'limit' : 100})
    parser.add_argument('-w', help='query key word', type=str, default=None)
    parser.add_argument('-l', help='path to save your logger txt file', type=str, default='logger.txt')
    parser.add_argument('-c', help='parse individual content or not', type=bool, default=False)
    parser.add_argument('-t', help='parsing titles', type=list, default=['title', 'forumName','school', 'gender', 'commentCount', 'likeCount', 'totalCommentCount', 'topics', 'content'])
    parser.add_argument('-cp', help='path to save your csv file', default='./res/dcard.csv')
    parser.add_argument('-xp', help='path to save your xlsx file', default='./res/dcard.xlsx')

    args = parser.parse_args()                                        
    return args

if __name__ == '__main__':
    args = parse_args()

    dcard = Dcard(
        forum=args.f,
        num_article=args.n,
        headers=args.i,
        params=args.p,
        txt_path=args.l,
        kw=args.w,
        titles=args.t,
        parse_content=args.c,
        )

    dcard.fetch()
    if args.cp:
        dcard.to_csv(args.cp)
    if args.xp: 
        dcard.to_xlsx(args.xp)