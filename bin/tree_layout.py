#!/usr/bin/env python

# 参考文献
# https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/

import sys


class TreeNode:

    # ノード間の最小距離をクラス変数として定義
    MINIMAL_X_DISTANCE: float = 1.0
    MINIMAL_Y_DISTANCE: float = 1.0

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
        # modという名前は参考文献に倣っている
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


def preorder(node: TreeNode):
    if node == None:
        return

    yield node

    for child in node.children:
        yield from preorder(child)


def postorder(node: TreeNode):
    if node == None:
        return

    for child in node.children:
        yield from postorder(child)

    yield node


def calc_y_preorder(node: TreeNode, depth: int = 0):
    """preorderトラバーサルで探索し、ノードに自身の深さを設定する

    サブツリーが重ならないように調整する際に、ノードの深さの情報が必要になるので、
    最初にこれを実行して深さを設定する

    Args:
        node (TreeNode): _description_
        depth (int, optional): _description_. Defaults to 0.
    """
    if node == None:
        return

    #
    # preorder処理
    #

    # 深さをノードに設定
    node.depth = depth

    # Y座標は親のY座標に最小距離を加えたものに設定する
    if node.parent:
        node.y = node.parent.y + TreeNode.MINIMAL_Y_DISTANCE

    for child in node.children:
        calc_y_preorder(child, depth + 1)


def calc_x_postorder(node: TreeNode):
    """postorderトラバーサルで探索してノードのサブツリーが重ならないようにX座標を設定する

    基本的な考え方はreingold-tilfordアルゴリズムに基づいている。
    ツリーの最下部から上に遡りながらX座標を設定していくため、
    自分の子ノードの位置はすでに設定されている前提で処理を進めていく。
    自分のX座標の初期値は自分が兄弟のどこにいるかによって変わる。
    兄弟の一番左であれば自分が基準なのでX座標は0に設定する。
    そうでなければ、子ノードの中央に配置する。
    こうして自分のX座標を決めたあと、自分よりも左側にいる兄弟ノードのサブツリー同士で位置を確認し、重なっていれば自分を右に動かす。
    自分が動くとき、自分の配下のサブツリーも石化して同じ距離を移動させる必要があるが、
    その都度サブツリーを探索して位置を修正していくのは効率が悪いので、
    自分自身のmod変数に移動すべき量を記録しておいて、最後にまとめてサブツリーを移動させる。

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

    minimal_distance = TreeNode.MINIMAL_X_DISTANCE

    #
    # 子がいない場合
    #
    if len(node.children) == 0:
        if node.is_left_most():
            # 自分が兄弟ノードの一番左ならX軸方向の位置は0に初期化
            node.x = 0
        else:
            # 左の兄弟のX座標に最小間隔を加えて初期化
            node.x = node.get_previous_sibling().x + minimal_distance

        # サブツリーが存在しないので、ここで処理終了
        return

    #
    # 自分の子が一つの場合
    #
    if len(node.children) == 1:

        if node.is_left_most():
            # 自分が兄弟ノードの一番左なら、自分が兄弟たちの基準位置になる
            # 自分のX軸方向の位置は子に合わせればよい
            # 子の位置は変わらないのでmodは設定しなくてよい
            node.x = node.children[0].x
        else:
            # 左隣のX座標に最小間隔を加える
            node.x = node.get_previous_sibling().x + minimal_distance

            # 自分が右に移動してしまったので、子も移動させるが、
            # 子の配下のサブツリー全体を移動させるのは大変なのでmodに移動すべき量を記録しておいて最後に移動する
            node.mod = node.x - node.children[0].x

    #
    # 自分の子が複数の場合
    #
    else:

        # 子の中心位置を求める
        center_x: float = (node.get_left_most_child().x + node.get_right_most_child().x) / 2

        if node.is_left_most():
            # 自分自身が兄弟ノードの一番左なら、自分は兄弟における基準位置になる
            # 自分の位置を子の中央に初期化する
            # 子の位置は変わらないのでmodは設定しなくてよい
            node.x = center_x
        else:
            # 一番左でないなら、自分は左隣のX座標に最小間隔を加える
            node.x = node.get_previous_sibling().x + minimal_distance

            # 自分配下のサブツリーを動かす量をmodに記録しておく
            # 子の中央が自分のX座標になるように子の移動量を決める
            node.mod = node.x - center_x

    # この時点で、親子の位置関係および兄弟との位置関係は設定されたが、
    # サブツリー同士が重なっているか、は確認していない

    # 自分が一番左のサブツリーであれば、それが基準位置なので、重なりを確認する必要はない
    if node.is_left_most():
        return

    # 自分が一番左でなければ、必要なだけ自分を右にずらして重なりを解消する
    resolve_overlap(node)

    # 一番右の兄弟まで処理したら、最後に兄弟間の位置を均等化する
    # サブツリーは重ならない最小の距離を保っているものの、その間隔は均等ではない
    # 特に子を持たないノードはMINIMAL_X_DISTANCEで間隔が固定されているので、全体的に左に寄りがちになっている
    if node.is_right_most():
        # equalize_position()の戻り値がFalseになるまで繰り返し実行してもいいが、
        # さほど見栄えは良くならないので、ここでは１回だけ実行する
        equalize_position(node)


def get_left_contour(node: TreeNode, mod_sum: float = 0.0, left_contour: dict = {}):
    """preorderトラバーサルで探索し、ノードの左輪郭を取得する

    ノードにはdepthキーで深さが設定されているものとする。

    メモ:
        輪郭を形成するノードへのポインタを保持しておいた方がよいのかもしれないが、
        ここでは最も左にいるノードの位置を辞書型にして返却している

    Args:
        node (TreeNode): _description_
        mod_sum (float, optional): _description_. Defaults to 0.0.
        left_contour (dict, optional): _description_. Defaults to {}.
    """
    if node == None:
        return

    #
    # preorder探索の処理
    #

    if left_contour.get(node.depth) is None:
        left_contour[node.depth] = node.x + mod_sum
    else:
        left_contour[node.depth] = min(left_contour[node.depth], node.x + mod_sum)

    mod_sum += node.mod

    for child in node.children:
        get_left_contour(child, mod_sum, left_contour)


def get_right_contour(node: TreeNode, mod_sum: float = 0.0, right_contour: dict = {}):
    """preorderトラバーサルで探索し、ノードの右輪郭を取得する

    Args:
        node (TreeNode): _description_
        mod_sum (float, optional): _description_. Defaults to 0.0.
        right_contour (dict, optional): _description_. Defaults to {}.
    """
    if node == None:
        return

    #
    # preorder探索の処理
    #

    if right_contour.get(node.depth) is None:
        right_contour[node.depth] = node.x + mod_sum
    else:
        right_contour[node.depth] = max(right_contour[node.depth], node.x + mod_sum)

    mod_sum += node.mod

    for child in node.children:
        get_right_contour(child, mod_sum, right_contour)


def get_minimum_distance_between(left_node: TreeNode, right_node: TreeNode) -> float:
    """左ノードの右輪郭と、右ノードの左輪郭を比較して、最も狭い間隔を返す

    条件
        - left_nodeとright_nodeは同じ親を持つ兄弟とする
        - 各ノードにはdepth値が設定されているものとする

    ツリーの間隔が
        - マイナスなら、重なっている
        - ゼロなら左ノードの右端と、右ノードの左端が重なっている
        - プラスなら離れている
    ということを表している

    Args:
        left_node (TreeNode): left sibling
        right_node (TreeNode): right sibling

    Returns:
        float: distance between left and right sibling
    """

    # 左ノードの右輪郭を取得
    left_node_right_contour = {}
    get_right_contour(left_node, mod_sum=0, right_contour=left_node_right_contour)

    # 右ノードの左輪郭を取得
    right_node_left_contour = {}
    get_left_contour(right_node, mod_sum=0, left_contour=right_node_left_contour)

    # 輪郭の辞書のキーは階層を表しているので、その数字の最大値が輪郭の深さになる
    # 輪郭の深さの短い方を取得する
    min_depth = min(max(left_node_right_contour.keys()), max(right_node_left_contour.keys()))

    # 左右のツリー間が各階層でどのくらい離れているかを調べ、その最小値を求める
    min_distance: float = sys.float_info.max
    for depth in range(right_node.depth + 1, min_depth + 1):
        distance = right_node_left_contour[depth] - left_node_right_contour[depth]
        if distance < min_distance:
            min_distance = distance

    return float(min_distance)


def resolve_overlap(node: TreeNode):
    """自分よりも左にいる兄弟ノードと位置を比較し、サブツリーが重なるようであれば、自分自身を右に移動させる

    Args:
        node (TreeNode): _description_
    """
    # サブツリー間の最小間隔として確保したい量
    minimal_distance = TreeNode.MINIMAL_X_DISTANCE

    # 兄弟の左端から始めて、自分の左隣りまで、に関して、
    sibling = node.get_left_most_sibling()
    while sibling != None and sibling != node:
        # もしサブツリーが重なっていたら、自分が右に動くべき量
        shift_value = 0

        # 兄弟ノードとの距離を計測
        distance = get_minimum_distance_between(sibling, node)
        if distance + shift_value < minimal_distance:
            shift_value = minimal_distance - distance

        if shift_value > 0:
            # 自分の位置を右にずらす
            node.x += shift_value

            # 自分配下のサブツリーはあとでまとめて修正するのでmodにずらした量を加算しておく
            node.mod += shift_value

        # 次の兄弟ノードとの間に重なりがあるかどうかを調べる
        sibling = sibling.get_next_sibling()


def equalize_position(node: TreeNode) -> bool:
    """自分よりも左にいる兄弟ノードの位置をできるだけ均等化する

    兄弟ノードの位置は、重なりがない最小の間隔で並べたので、左に寄せられたバランスが悪い状態になっている。

    o---o---------------o
    left_most          node

    このように、できるだけ均等に配置し直す。

    o---------o---------o
    left_most          node

    Args:
        node (TreeNode): _description_

    Returns:
        _type_: _description_
    """

    # 元々の自分の位置を記録して、自分自身が右に動いたか、を確認できるようにする
    node_x = node.x

    # 自分は兄弟における何番目か
    node_index = node.parent.children.index(node)

    # 自分と左端ノードの間には、何個の兄弟ノードがあるか
    num_nodes_between = node_index - 1

    # 間に兄弟ノードがないなら、位置を調整する対象がないので何もしない
    if num_nodes_between <= 0:
        return False

    # 一番左の兄弟と、自分との間の距離を求める
    width = node.x - node.get_left_most_sibling().x

    # 間にいる兄弟の数を考慮して望ましい間隔を求める
    desired_interval = width / (num_nodes_between + 1)

    # 左端の一つ右のノードから始めて、自分に至るまで
    for i in range(1, node_index + 1):
        mid_node = node.parent.children[i]
        prev_node = node.parent.children[i-1]

        # 前のループで左隣のノードが間隔を広げて寄ってきているため、再びサブツリー同士の重複が発生しているかもしれない
        if i == 1:
            # 初回ループは関係なく
            pass
        elif len(mid_node.children) == 0:
            # また、子がいなければツリーの重複は起こり得ない
            pass
        else:
            # 左隣との距離を計測して重なっていれば右に移動する
            distance = get_minimum_distance_between(prev_node, mid_node)
            if distance < TreeNode.MINIMAL_X_DISTANCE:
                shift_value = TreeNode.MINIMAL_X_DISTANCE - distance
                mid_node.x += shift_value
                mid_node.mod += shift_value

        # 左隣りとの間隔が、望まれる間隔よりも狭ければ広げる
        if mid_node.x - prev_node.x < desired_interval:
            shift_value = desired_interval - mid_node.x + prev_node.x
            mid_node.x += shift_value
            mid_node.mod += shift_value

    # 元の位置から変わっていたらTrueを返し、変わらなければFalseを返す
    if node.x - node_x > 0:
        return True
    return False


def calc_x_preorder(node: TreeNode, mod_sum: float = 0.0):
    """preorderトラバーサルで探索してノードのX座標を確定します
    """
    if node == None:
        return

    #
    # preorder処理
    #

    # 自分の位置をmod_sumd移動
    node.x += mod_sum

    # 自分のmodを加算して、子を動かす
    mod_sum += node.mod

    # 自分のmodはこれでリセット
    node.mod = 0

    for child in node.children:
        calc_x_preorder(child, mod_sum)


def print_tree(node, indent=0):
    if node is None:
        return

    # 現在のノードを出力
    print(f"{indent * ' '}{node.node_name}")

    for child in node.children:
        print_tree(child, indent + 1)


def dump_tree(node, indent=0):
    if node is None:
        return

    # 現在のノードを出力
    print(f"{indent * ' '}{node.node_name} (x,y)=({node.x}, {node.y}) mod={node.mod}")

    for child in node.children:
        dump_tree(child, indent + 1)


def save_png(node, filename):
    import matplotlib.pyplot as plt
    import networkx as nx

    def add_tree(root, G):
        if root is None:
            return
        G.add_node(root.node_name, label=f"{root.node_name}")
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
    get_postion_preorder(node, position)

    G = nx.Graph()
    add_tree(node, G)
    # nx.draw(G, pos=position, node_size=100)
    nx.draw(G, pos=position, node_size=300, with_labels=True, font_size=8, font_color='white')
    plt.savefig(filename)
    plt.cla()


def calc_tree_position(tree : TreeNode):
    calc_y_preorder(tree)
    calc_x_postorder(tree)
    calc_x_preorder(tree)


if __name__ == '__main__':

    def create_test_TreeNode():

        trees = [
            # 0
            TreeNode("root",
                     TreeNode("L1"),
                     TreeNode("R1")),

            # 1
            TreeNode("root",
                     TreeNode("L1"),
                     TreeNode("M1"),
                     TreeNode("R1")),

            # 2
            TreeNode("root",
                     TreeNode("L1",
                              TreeNode("L1L2"),
                              TreeNode("L1R2")),
                     TreeNode("R1",
                              TreeNode("R1L2"),
                              TreeNode("R1R2"))),

            # 3
            TreeNode("root",
                     TreeNode("L1",
                              TreeNode("L1L2",
                                       TreeNode("L1L2L3",
                                                TreeNode("L1L2L3L4")))),
                     TreeNode("R1")),

            # 4
            TreeNode("root",
                     TreeNode("L1"),
                     TreeNode("R1",
                              TreeNode("R1R2",
                                       TreeNode("R1R2R3",
                                                TreeNode("R1R2R3R4"))))
                     ),

            # 5
            TreeNode("root",
                     TreeNode("L1",
                              TreeNode("L1L2",
                                       TreeNode("L1L2L3"), TreeNode("L1L2L3L4"))),
                     TreeNode("R1",
                              TreeNode("RL1"),
                              TreeNode("RR1",
                                       TreeNode("RR2"), TreeNode("RR3")))),

            # 6
            TreeNode("root",
                     TreeNode("L1",
                              TreeNode("L2",
                                       TreeNode("L3",
                                                TreeNode("L4",
                                                         TreeNode("L5"),
                                                         TreeNode("L6")),
                                                TreeNode("L7")),
                                       TreeNode("L8")),
                              TreeNode("L9")),
                     TreeNode("R1",
                              TreeNode("R2",
                                       TreeNode("R3"),
                                       TreeNode("R4")),
                              TreeNode("R5"))),

            # 7
            TreeNode("root",
                     TreeNode("E",
                              TreeNode("A"),
                              TreeNode("D",
                                       TreeNode("B"),
                                       TreeNode("C"))),
                     TreeNode("F"),
                     TreeNode("N",
                              TreeNode("G"),
                              TreeNode("M",
                                       TreeNode("H"),
                                       TreeNode("I"),
                                       TreeNode("J"),
                                       TreeNode("K"),
                                       TreeNode("L")))),

            # 8
            TreeNode("root",
                     TreeNode("L11",
                              TreeNode("L21"),
                              TreeNode("L22"),
                              TreeNode("L23"),
                              TreeNode("L24"),
                              TreeNode("L25",
                                       TreeNode("L31"),
                                       TreeNode("L32")),
                              TreeNode("L26",
                                       TreeNode("L33"),
                                       TreeNode("L34")),
                              TreeNode("L27",
                                       TreeNode("L35"))),
                     TreeNode("L12"),
                     TreeNode("L13"),
                     TreeNode("L14",
                               TreeNode("L28",
                                        TreeNode("L36"),
                                        TreeNode("L37"))),
                     TreeNode("L15",
                              TreeNode("L29",
                                       TreeNode("L38")),
                              TreeNode("L2A",
                                       TreeNode("L39"),
                                       TreeNode("L3A")),
                              TreeNode("L2B",
                                       TreeNode("L3B"))),
                     TreeNode("L16",
                              TreeNode("L2C",
                                       TreeNode("L3C"),
                                       TreeNode("L3D"),
                                       TreeNode("L3E"),
                                       TreeNode("L3F"))))

        ]
        return trees

    def test_tree(tree, filename):
        calc_tree_position(tree)
        dump_tree(tree)
        save_png(tree, filename)

    def main():
        trees = create_test_TreeNode()

        for i, tree in enumerate(trees):
            test_tree(tree, f"log/tree_{i}.png")

        return 0

    sys.exit(main())
