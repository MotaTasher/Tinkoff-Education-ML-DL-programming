import ast
import argparse
from collections.abc import Iterable

parser = argparse.ArgumentParser(
    description="comparison of 2 files for plagiarism"
)
parser.add_argument(
    'inpput',
    type=str,
    help='file with path to couple of files for comparing'
)
parser.add_argument(
    'score',
    type=str,
    help='path for writing results'
)

args = parser.parse_args()

indir = open(args.inpput, 'r')
score = open(args.score, 'w')


class NodeContainer:
    def __init__(self, node: ast.AST) -> None:
        self.node = node

    def dfs(self, function) -> None:
        if len(self.node._fields) == 0:
            return
        function(self.node)
        for i in ast.iter_child_nodes(self.node):
            NodeContainer(i,).dfs(function)


def creator_list(new_list: list):
    def append_to_tuple(x: ast.AST) -> None:
        new_list.append([
            [x.__class__ for x in s[1]]
            if issubclass(s[1].__class__, Iterable) else s[1].__class__
            for s in ast.iter_fields(x)
        ])
    return append_to_tuple


def levenshtrain_distance(tuple1: tuple, tuple2: tuple) -> int:
    tuple1, tuple2 = sorted([tuple1, tuple2], key=len)

    dist = [
        [0 for i in range(len(tuple2) + 1)]
        for i in range(len(tuple1) + 1)
        ]
    for i in range(len(tuple2) + 1):
        dist[0][i] = i
    for num1, elm1 in enumerate(tuple1):
        num1 += 1
        dist[num1][0] = num1 + 1
        for num2, elm2 in enumerate(tuple2):
            num2 += 1
            if elm1 == elm2:
                dist[num1][num2] = dist[num1 - 1][num2 - 1]
            else:
                dist[num1][num2] = num1 + num2
            dist[num1][num2] = min(
                [
                    dist[num1][num2],
                    dist[num1][num2 - 1] + 1,
                    dist[num1 - 1][num2] + 1,
                    dist[num1 - 1][num2 - 1] + 1,
                ]
            )

    return dist[len(tuple1)][len(tuple2)]


while True:
    line = indir.readline()
    if line == '':
        break
    paths = line[0:-1].split(' ')
    if len(paths) == 2:
        path_first, path_second = paths
    else:
        print(len(paths))
        continue
    code_first = open(path_first, 'r').read()
    code_second = open(path_second, 'r').read()

    tree_first = ast.parse(code_first)
    tree_second = ast.parse(code_second)

    iter_first = ast.iter_child_nodes(tree_first)
    iter_second = ast.iter_child_nodes(tree_second)

    list_first = []
    list_second = []
    NodeContainer(tree_first).dfs(creator_list(list_first))
    NodeContainer(tree_second).dfs(creator_list(list_second))

    my_dist = levenshtrain_distance(list_first, list_second)
    print("Files need around", my_dist, "changes")
    print("Len of first: ", len(list_first))
    print("Len of second: ", len(list_second))

    score.write(
        str(1 - my_dist / max(len(list_first), len(list_second))) + '\n'
    )
