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
        self.x: float = 0.0
        self.y: float = 0.0

        # ツリーの深さ
        self.depth: int = 0

        # このノード配下のサブツリー全体を左右に移動させるための変数
        # ツリーの探索回数を減らすために、この変数を使ってノードの位置を調整し、最後にまとめて位置を修正する
        self.mod: float = 0.0

    #
    # ツリーを操作するヘルパー関数
    #

    def is_leaf(self) -> bool:
        return len(self.children) == 0

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
    # 特殊メソッド
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


def calc_y_preorder(root: TreeNode, depth: int = 0):
    """preorderトラバーサルでノードの深さを求めてY座標を各ノードに設定します

    X座標を決める最後のpreorderトラバーサルで処理することもできるが、
    分かりやすさのために別関数にしている

    Args:
        root (TreeNode): _description_
        depth (int, optional): _description_. Defaults to 0.
    """
    if root == None:
        return

    #
    # preorder処理
    #

    # 深さをノードに設定
    root.depth = depth

    # Y座標は深さと同じものを設定
    # 見栄えを調整するときに変更すればよい
    root.y = depth

    for child in root.children:
        calc_y_preorder(child, depth + 1)


def calc_x_postorder(node: TreeNode):
    """postorderトラバーサルで探索してノードのサブツリーが重ならないようにX座標を設定します

    基本的な考え方はreingold-tilfordアルゴリズムに基づいています。
    ツリーの最下部から上に遡りながらX座標を設定していくので、
    子ノードの位置はすでに設定されている前提で処理します。
    兄弟ノードにおいては、一番左のノードを基準に一定間隔で並べていきます。
    自分よりも左にいる兄弟ノードとの重なりを解消する処理を行いますが、
    自分が右に動いたとき、自分の配下のサブツリーも同じ距離移動させる必要がありますが、
    その都度、サブツリーを探索するのは効率が悪いので、
    自分自身のmod変数に移動すべき量を記録しておいて、最後にまとめてサブツリーを移動させます。

    Args:
        node (TreeNode): _description_
    """
    if node == None:
        return

    for child in node.children:
        calc_x_postorder(child)

    #
    # postorder処理
    #

    #
    # 子がいない場合
    #
    if len(node.children) == 0:
        if node.is_left_most():
            # 自分が兄弟ノードの一番左ならX軸方向の位置は0に初期化
            node.x = 0
        else:
            # 左の兄弟のX座標+1に初期化
            node.x = node.get_previous_sibling().x + 1

        # サブツリーが存在しないので処理終了
        return

    #
    # 子が一つの場合
    #
    if len(node.children) == 1:

        if node.is_left_most():
            # 自分が兄弟ノードの一番左なら、自分が兄弟たちの基準位置になる
            # X軸方向の位置は子に合わせればよい
            # 子の位置は変わらないのでmodは設定しなくてよい
            node.x = node.children[0].x
        else:
            # 左隣のX座標に+1
            node.x = node.get_previous_sibling().x + 1

            # 子は一つなので自分と子のX座標を一致させたい
            # 自分が右に移動してしまったので、子も移動させるが、
            # 子の配下のサブツリー全体を移動させるのは大変なのでmodに移動すべき量を記録しておいて最後に移動する
            node.mod = node.x - node.children[0].x

    #
    # 子が複数ある場合
    #
    else:

        left_most_child = node.get_left_most_child()
        right_most_child = node.get_right_most_child()
        center_x = (left_most_child.x + right_most_child.x) / 2

        if node.is_left_most():
            # 自分自身が兄弟ノードの一番左なら、自分は兄弟における基準位置になる
            # 自分の位置は子の中央に初期化する
            node.x = center_x
        else:
            # 一番左でないなら、左隣のX座標に+1する
            node.x = node.get_previous_sibling().x + 1

            # 自分配下のサブツリーを動かす量をmodに記録しておく
            # 子の中央が自分になってほしいので、自分に対して子の中央がどれだけずれているかを記録する
            node.mod = node.x - center_x

    # この時点では、親子の位置関係は正しく設定されているものの、
    # サブツリー同士の重なりは解決できていない
    # 自分が一番左のサブツリーであれば、それが基準なのでそのままでよいが、
    # そうでなければ、必要なだけ右にずらす
    if len(node.children) > 0 and node.is_left_most() == False:
        fix_conflicts(node)


def fix_conflicts(node: TreeNode):

    # サブツリー間にどれだけの最小距離を保つか
    min_distance = 1

    # このノードの左輪郭を求める
    # 各階層における最小のX座標を記録したいので{ depth: x } の形で保持する
    node_left_contour = {}
    get_left_contour(node, 0, node_left_contour)

    # 自分よりも左にいる兄弟ノードとの重なり合いを順番に調べていく
    # 自分よりも右側にいる兄弟は、あとで処理するので考慮しない
    shift_value = 0
    sibling = node.get_left_most_sibling()

    # 左端から、自分の左隣りまでの兄弟に関して、
    while sibling != None and sibling != node:

        # その兄弟の右輪郭を調べる
        sibling_right_contour = {}
        get_right_contour(sibling, 0, sibling_right_contour)

        # 全ての深さで重なりをチェックしてもいいが、片方が存在しない深さはチェックしても無駄になる
        # 深さの短い方を取って、その深さまでをチェックする
        # 辞書型で作成したcontourはキーが深さなので、キーの最大値を取れば深さの最大値がわかる
        min_depth = min(max(node_left_contour.keys()), max(sibling_right_contour.keys()))
        for depth in range(node.depth + 1, min_depth + 1):
            distance = node_left_contour[depth] - sibling_right_contour[depth]
            if distance + shift_value < min_distance:
                shift_value = min_distance - distance

        if shift_value > 0:
            # 自分の位置を右にずらす
            node.x += shift_value

            # サブツリーはあとでまとめて修正するのでmodにずらした量を加算しておく
            node.mod += shift_value

            # ずらし終わったので移動量をリセット
            shift_value = 0

            # 自分が右に移動したので、その間にいる兄弟達の位置を均等化する
            is_moved = center_nodes_between(sibling, node)

            if is_moved:
                # 間にいる兄弟が自分に寄ってきたことで重なりが発生するかもしれないので
                # 繰り返し確認して、自分よりも左側に重複がないことを担保する
                fix_conflicts(node)

        # 次の兄弟ノードとの間に重なりがあるかどうかを調べる
        sibling = sibling.get_next_sibling()



def center_nodes_between(left_sibling: TreeNode, right_sibling: TreeNode) -> bool:
    # 左と右の間にいる兄弟ノードを均等にずらす

    # 戻り値
    is_moved = False

    # 親ノードを取得
    parent = left_sibling.parent

    # 左右の兄弟ノードのインデックスを取得
    left_index = parent.children.index(left_sibling)
    right_index = parent.children.index(right_sibling)

    # その間に何個の兄弟ノードがあるか
    num_nodes_between = right_index - left_index - 1

    # その間に兄弟ノードが存在しない場合は何もしない
    if num_nodes_between <= 0:
        return is_moved

    is_moved = True

    # 存在する場合は、その間にいる兄弟ノードをずらす
    # 両端のX位置の差をノード数+1で割って間隔を求める
    distance = (right_sibling.x - left_sibling.x) / (num_nodes_between + 1)

    count = 1
    for i in range(left_index + 1, right_index):
        middle_sibling = parent.children[i]
        desired_x = left_sibling.x + distance * count
        offset = desired_x - middle_sibling.x
        middle_sibling.x += offset
        middle_sibling.mod += offset
        count += 1

    return is_moved


def calc_x_preorder(root: TreeNode, mod_sum: float = 0.0):
    """preorderトラバーサルで探索してノードのX座標を確定します
    """
    if root == None:
        return

    #
    # preorder処理
    #

    # 自分の位置をmod_sumd移動
    root.x += mod_sum

    # 自分のmodを加算して、子を動かす
    mod_sum += root.mod

    for child in root.children:
        calc_x_preorder(child, mod_sum)


def get_left_contour(node: TreeNode, mod_sum: float = 0.0, left_contour: dict = {}):
    if node == None:
        return

    if left_contour.get(node.depth) is None:
        left_contour[node.depth] = node.x + mod_sum
    else:
        left_contour[node.depth] = min(left_contour[node.depth], node.x + mod_sum)

    mod_sum += node.mod

    for child in node.children:
        get_left_contour(child, mod_sum, left_contour)


def get_right_contour(node: TreeNode, mod_sum: float = 0.0, right_contour: dict = {}):
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
    coutour = {}
    get_left_contour(node, 0, coutour)

    shift_amount = 0
    for level in coutour.keys():
        if coutour[level] + shift_amount < 0:
            shift_amount = -1 * coutour[level]

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


def save_png(root, filename):
    import matplotlib.pyplot as plt
    import networkx as nx

    def add_tree(root, G):
        if root is None:
            return
        G.add_node(root.node_name)
        for child in root.children:
            G.add_edge(root.node_name, child.node_name)
            add_tree(child, G)

    def get_postion_preorder(root, position={}):
        if root is None:
            return
        position[root.node_name] = (root.x, -root.y)
        for child in root.children:
            get_postion_preorder(child, position)

    position = {}
    get_postion_preorder(root, position)

    G = nx.Graph()
    add_tree(root, G)
    nx.draw(G, pos=position)
    plt.savefig(filename)
    plt.cla()

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

    def test_tree(tree, filename):
        calc_y_preorder(tree)
        calc_x_postorder(tree)
        shift_to_right(tree)
        calc_x_preorder(tree)
        dump_tree(tree)
        save_png(tree, filename)


    def main():
        trees = create_test_TreeNode()

        for i, tree in enumerate(trees):
            test_tree(tree, f"log/tree_{i}.png")

        return 0

    sys.exit(main())
