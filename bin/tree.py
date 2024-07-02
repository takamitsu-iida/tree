#!/usr/bin/env python

# 参考文献
# https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/

import sys


class TreeNode:

    def __init__(self, node_name="", *children):

        # ノードを識別する名前
        self.node_name = node_name

        # 親ノードへのポインタ
        self.parent = None

        # コンストラクタで子ノードを渡されたら、それを子ノードとして設定する
        if children:
            self.children = children
            for child in self.children:
                child.parent = self
        else:
            self.children = []

        # ノードの位置情報
        self.x: int = 0
        self.y: int = 0

        # ツリーの深さ
        self.depth: int = 0

        # このノード配下のサブツリー全体を左右に移動させるための変数
        # ツリーの探索回数を減らすために、この変数を使ってノードの位置を調整し、最後にまとめて位置を修正する
        self.mod: int = 0

    #
    # ツリーを操作するヘルパー関数
    #

    def is_leaf(self) -> bool:
        return all(len(child) == 0 for child in self.children)

    def is_root(self) -> bool:
        return self.parent is None

    def is_left_most(self) -> bool:
        if self.is_root():
            return True
        return self.parent.children[0] == self

    def is_right_most(self) -> bool:
        if self.is_root():
            return True
        return self.parent.children[-1] == self

    def get_siblings(self) -> list:
        if self.is_root():
            return []
        return [child for child in self.parent.children if child != self]

    def get_previous_sibling(self) -> 'TreeNode':
        if self.is_root():
            return None
        if self.is_left_most():
            return None
        return self.parent.children[self.parent.children.index(self) - 1]

    def get_next_sibling(self) -> 'TreeNode':
        if self.is_root():
            return None
        if self.is_right_most():
            return None
        return self.parent.children[self.parent.children.index(self) + 1]

    def get_left_most_sibling(self) -> 'TreeNode':
        if self.is_root():
            return None
        if self.is_left_most():
            return self
        return self.parent.children[0]

    def get_right_most_sibling(self) -> 'TreeNode':
        if self.is_root():
            return None
        if self.is_right_most():
            return self
        return self.parent.children[-1]

    def get_left_most_child(self) -> 'TreeNode':
        if self.is_leaf():
            return None
        return self.children[0]

    def get_right_most_child(self) -> 'TreeNode':
        if self.is_leaf():
            return None
        return self.children[-1]

    #
    #
    #

    def __str__(self):
        return f"{self.node_name}"

    def __repr__(self):
        return f"{self.node_name}"

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, slice):
            return self.children[key]
        if isinstance(key, str):
            for child in self.children:
                if child.node == key:
                    return child

    def __iter__(self):
        return self.children.__iter__()

    def __len__(self):
        return len(self.children)


def preorder(root: TreeNode):
    if root == None:
        return

    yield root

    for child in root.children:
        yield from preorder(child)


def postorder(root: TreeNode):
    if root == None:
        return

    for child in root.children:
        yield from postorder(child)

    yield root


def initialize_tree_preorder(root: TreeNode, depth: int = 0):
    if root == None:
        return

    #
    # preorder処理
    #

    # 深さを計算して設定
    root.depth = depth
    root.y = depth

    for child in root.children:
        initialize_tree_preorder(child, depth + 1)


def calc_x_postorder(node: TreeNode):
    if node == None:
        return

    for child in node.children:
        calc_x_postorder(child)

    #
    # postorder処理
    #

    if node.is_leaf():
        # 子がいないとき
        if node.is_left_most():
            # これが兄弟ノードの一番左ならX軸方向の位置は0に初期化
            node.x = 0
        else:
            # 左の兄弟のX座標+1に初期化
            node.x = node.get_previous_sibling().x + 1

    elif len(node.children) == 1:
        # 子が一つしかない場合
        if node.is_left_most():
            # これが兄弟ノードの一番左なら、これが兄弟における基準位置になる
            # X軸方向の位置は子に合わせればよい
            node.x = node.children[0].x
        else:
            # 一番左ではないなら、左の隣のX座標に+1
            node.x = node.get_previous_sibling().x + 1

            # 自分配下のサブツリーを動かしたいので、modに差分を設定しておく
            node.mod = node.x - node.children[0].x

    else:
        # 子が複数ある場合
        left_child = node.get_left_most_child()
        right_child = node.get_right_most_child()
        center_x = (left_child.x + right_child.x) / 2

        if node.is_left_most():
            # これが兄弟ノードの一番左なら、これが兄弟における基準位置になる
            # X軸方向の位置は子の中央に初期化
            node.x = center_x
        else:
            # 一番左ではないなら、左隣のX座標に+1
            node.x = node.get_previous_sibling().x + 1

            # 自分配下のサブツリーを動かす量
            node.mod = node.x - center_x

    # 親子の位置関係は正しく設定されているものの、サブツリー同士の重なりは解決できていない
    # 一番左のサブツリーであれば、それが基準なのでそのままでよいが、そうでなければ、必要なだけ右にずらす
    if len(node.children) > 0 and node.is_left_most() == False:
        fix_conflicts(node)


def fix_conflicts(node: TreeNode):

    min_distance = 1

    # 各階層において、その階層における最小のX座標を記録する（このノードの左輪郭を調べる）
    node_contour = {}
    get_left_contour(node, 0, node_contour)

    # 自分よりも左にいる兄弟ノードを、左から順番に調べていく
    shift_value = 0
    sibling = node.get_left_most_sibling()
    while sibling != None and sibling != node:
        # その右輪郭を調べる
        sibling_contour = {}
        get_right_contour(sibling, 0, sibling_contour)

        # 全ての深さで重なりをチェックする必要はない
        # 深さの短い方を取って、それだけをチェックすればよい
        min_depth = min(max(node_contour.keys()), max(sibling_contour.keys()))

        for depth in range(node.depth + 1, min_depth + 1):
            distance = node_contour[depth] - sibling_contour[depth]
            if distance + shift_value < min_distance:
                shift_value = min_distance - distance

        if shift_value > 0:
            # 自分の位置を右にずらす
            node.x += shift_value

            # サブツリーはあとでまとめて修正するのでmodにずらした量を加算しておく
            node.mod += shift_value

            # 自分を右にずらしたので、その間にいる兄弟達も均等にずらす
            center_nodes_between(sibling, node)

            # ずらし終わったので移動量をリセット
            shift_value = 0

            # 間にいる兄弟をずらしたことで重なりが発生するかもしれないので、再度確認する
            fix_conflicts(node)

        # 次の兄弟ノードとの間に重なりがあるかどうかを調べる
        sibling = sibling.get_next_sibling()



def center_nodes_between(left_sibling: TreeNode, right_sibling: TreeNode):
    parent = left_sibling.parent
    left_index = parent.children.index(left_sibling)
    right_index = parent.children.index(right_sibling)

    # その間に何個の兄弟ノードがあるか
    num_nodes_between = right_index - left_index - 1

    # その間に兄弟ノードが存在しない場合は何もしない
    if num_nodes_between <= 0:
        return

    # 存在する場合は、その間にいる兄弟ノードをずらす
    # 両端のX位置の差をノード数で割って間隔を求める
    distance = (right_sibling.x - left_sibling.x) / (num_nodes_between + 1)

    count = 1
    for i in range(left_index + 1, right_index):
        middle_node = parent.children[i]
        desired_x = left_sibling.x + distance * count
        offset = desired_x - middle_node.x
        middle_node.x += offset
        middle_node.mod += offset
        count += 1


def finalize_tree_position(root: TreeNode, mod_sum: int = 0):
    if root == None:
        return

    root.x += mod_sum
    mod_sum += root.mod

    for child in root.children:
        finalize_tree_position(child, mod_sum)


    if len(root.children) == 0:
        root.width = root.x
        root.height = root.y
    else:
        root.width = root.children[0].width
        root.height = root.children[0].height

        for child in root.children[1:]:
            root.width = max(root.width, child.width)
            root.height = max(root.height, child.height)

        root.width = root.width + 1
        root.height = root.height + 1


def get_left_contour(node: TreeNode, mod_sum: int = 0, left_contour: dict = {}):
    if node == None:
        return

    if left_contour.get(node.depth) is None:
        left_contour[node.depth] = node.x + mod_sum
    else:
        left_contour[node.depth] = min(left_contour[node.depth], node.x + mod_sum)

    mod_sum += node.mod

    for child in node.children:
        get_left_contour(child, mod_sum, left_contour)


def get_right_contour(node: TreeNode, mod_sum: int = 0, right_contour: dict = {}):
    if node == None:
        return

    if right_contour.get(node.depth) is None:
        right_contour[node.depth] = node.x + mod_sum
    else:
        right_contour[node.depth] = max(right_contour[node.depth], node.x + mod_sum)

    mod_sum += node.mod

    for child in reversed(node.children):
        get_right_contour(child, mod_sum, right_contour)


def shift_to_right(node: TreeNode):
    # ノードのX座標がマイナスだと、画面の左にはみ出てしまうので右にずらす
    node_coutour = {}
    get_left_contour(node, 0, node_coutour)

    shift_amount = 0
    for level in node_coutour.keys():
        if node_coutour[level] + shift_amount < 0:
            shift_amount = -1 * node_coutour[level]

    if shift_amount > 0:
        node.x += shift_amount
        node.mod += shift_amount




def print_tree(root, indent=0):
    if root is None:
        return

    # 現在のノードを出力
    print(f"{indent * ' '}{root.node_name}")

    for child in root.children:
        print_tree(child, indent + 1)


def dump_tree(root, indent=0):
    if root is None:
        return

    # 現在のノードを出力
    print(f"{indent * ' '}{root.node_name} (x,y)=({root.x}, {root.y}) mod={root.mod}")

    for child in root.children:
        dump_tree(child, indent + 1)


if __name__ == '__main__':

    def create_test_TreeNode():

        trees = [
            # 0 simple test
            TreeNode("root",
                     TreeNode("l"),
                     TreeNode("r")),

            # 1 deep left
            TreeNode("root",
                     TreeNode("l1",
                              TreeNode("l2",
                                       TreeNode("l3",
                                                TreeNode("l4")))),
                     TreeNode("r1")),

            # 2 deep right
            TreeNode("root",
                     TreeNode("l1"),
                     TreeNode("r1",
                              TreeNode("r2",
                                       TreeNode("r3",
                                                TreeNode("r4"))))
                     ),

            # 3 tight right
            TreeNode("root",
                     TreeNode("l1",
                              TreeNode("l2",
                                       TreeNode("l3"), TreeNode("l4"))),
                     TreeNode("r1",
                              TreeNode("rl1"),
                              TreeNode("rr1",
                                       TreeNode("rr2"), TreeNode("rr3")))),

            # 4 unbalanced
            TreeNode("root",
                     TreeNode("l1",
                              TreeNode("l2",
                                       TreeNode("l3",
                                                TreeNode("l4",
                                                         TreeNode("l5"),
                                                         TreeNode("l6")),
                                                TreeNode("l7")),
                                       TreeNode("l8")),
                              TreeNode("l9")),
                     TreeNode("r1",
                              TreeNode("r2",
                                       TreeNode("r3"),
                                       TreeNode("r4")),
                              TreeNode("r5"))),

            # 5 Wetherell-Shannon Tree
            TreeNode("root",
                     TreeNode("l1",
                              TreeNode("ll1"),
                              TreeNode("lr1",
                                       TreeNode("lrl"),
                                       TreeNode("lrr"))),
                     TreeNode("r1",
                              TreeNode("rr2",
                                       TreeNode("rr3",
                                                TreeNode("rrl",
                                                         TreeNode("rrll",
                                                                  TreeNode(
                                                                      "rrlll"),
                                                                  TreeNode("rrllr")),
                                                         TreeNode("rrlr")))))),

            # 6 Buchheim Failure
            TreeNode("root",
                     TreeNode("l",
                              TreeNode("ll"),
                              TreeNode("lr")),
                     TreeNode("r",
                              TreeNode("rl"),
                              TreeNode("rr"))),

            # 7 simple n-ary
            TreeNode("root",
                     TreeNode("l"),
                     TreeNode("m"),
                     TreeNode("r")),

            # 8 buchheim n-ary tree
            # this works perfectly.
            TreeNode("root",
                     TreeNode("bigleft",
                              TreeNode("l1"),
                              TreeNode("l2"),
                              TreeNode("l3"),
                              TreeNode("l4"),
                              TreeNode("l5"),
                              TreeNode("l6"),
                              TreeNode("l7", TreeNode("ll1"))),
                     TreeNode("m1"),
                     TreeNode("m2"),
                     TreeNode("m3", TreeNode("m31")),
                     TreeNode("m4"),
                     TreeNode("bigright",
                              TreeNode("brr",
                                       TreeNode("br1"),
                                       TreeNode("br2"),
                                       TreeNode("br3"),
                                       TreeNode("br4"),
                                       TreeNode("br5"),
                                       TreeNode("br6"),
                                       TreeNode("br7")))),
        ]
        return trees

    def main():
        trees = create_test_TreeNode()

        for tree in trees:
            initialize_tree_preorder(tree)
            calc_x_postorder(tree)
            shift_to_right(tree)
            finalize_tree_position(tree)
            dump_tree(tree)
            print()

        return 0

    sys.exit(main())
