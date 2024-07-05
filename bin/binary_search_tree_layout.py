#!/usr/bin/env python

# 参考文献
# https://williamyaoh.com/posts/2023-04-22-drawing-trees-functionally.html

import sys


class BinaryTreeNode:

    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

        # 自分からみた左輪郭、右輪郭
        # 自分からの相対位置で各レベルのX軸方向の位置を表現する
        self.left_contour = [0]
        self.right_contour = [0]

        # 上位ノードからみた自分の相対位置
        self.relative_x: int = 0

        # 実際のX軸の位置
        self.x: int = 0

        # 実際のY軸の位置
        self.y: int = 0

        # 深さ = Y軸の位置
        self.depth : int = 0


    def insert(self, left, right):
        self.left = left
        self.right = right
        return self


def insert_binary_tree(root, data) -> BinaryTreeNode:
    """二分探索木に新たなノードを追加する
    """
    # rootがNoneの場合、新しいノードを作成して返す
    # これがツリーの頂点になる
    if root is None:
        root = BinaryTreeNode(data)
        return root

    if data == root.data:
        # 同じ値の場合は何もしない（追加できない）
        return root
    elif data < root.data:
        # 渡された値が小さければ左のサブツリーに追加し、
        root.left = insert_binary_tree(root.left, data)
    else:
        # そうでなければ右のサブツリーに追加
        root.right = insert_binary_tree(root.right, data)

    return root


def preorder(root: BinaryTreeNode):
    if root == None:
        return
    yield root
    yield from preorder(root.left)
    yield from preorder(root.right)


def postorder(root: BinaryTreeNode):
    if root == None:
        return
    yield from postorder(root.left)
    yield from postorder(root.right)
    yield root


def print_binary_tree(root: BinaryTreeNode, level=0):
    if root == None:
        return

    print_binary_tree(root.left, level + 1)
    print(' ' * 4 * level + '-> ' + str(root.data))
    print_binary_tree(root.right, level + 1)


def reingold_tilford_postorder(node):
    """_summary_

    水平オフセットの計算は、後順トラバーサルによって行われます。
    各ノードで、
    (1) 自分からみた左サブツリー、右サブツリーの輪郭を構築する
    (2) サブツリーをどのくらい離して配置するか (つまり、現在のノードでの相対位置) を計算し、
    (3) 現在のノードをルートとするツリーの輪郭を構築します。

    Args:
        node (_type_): _description_
    """

    if node == None:
        return

    # 再帰呼び出しで深く降りていく
    reingold_tilford_postorder(node.left)
    reingold_tilford_postorder(node.right)

    #
    # postorderの場合はここに処理を書く
    #

    # 末端にたどり着いて、左にも右にも子がいない場合は何もせずに、ひとつ上の階層に戻る
    if node.left == None and node.right == None:
        return

    # ここから先の処理は左か右に必ず子がいる
    if node.left != None and node.right == None:

        # 左に子がいて、右にいない場合
        #    node
        #    /
        #   子

        # 左の子は、自分からみて -1
        node.left.relative_x = -1

        # 左輪郭は、左の子が持っている左輪郭をコピーして、先頭に自分の相対位置 0 を追加する
        # ただし、左の子は相対位置を移動させたので、左輪郭もまとめて移動する
        node.left_contour = [0] + [x + node.left.relative_x for x in node.left.left_contour]

        # 右輪郭は、左の子が持っている右輪郭をコピーして、先頭に自分の相対位置 0 を追加する
        # ただし、左の子は相対位置を移動させたので、左輪郭もまとめて移動する
        node.right_contour = [0] + [x + node.left.relative_x for x in node.left.right_contour]

    elif node.right != None and node.left == None:

        # 左に子がなく、右に子がある場合
        #    node
        #       \
        #        子

        # 右の子の自分からの相対位置は +1
        node.right.relative_x = +1

        # 左輪郭
        # 左に子がいないので、右の子が持っている左輪郭を引き継いで使う（右の子は相対位置をずらしたので、輪郭もずらす）
        node.left_contour = [0] + [x + node.right.relative_x for x in node.right.left_contour]

        # 右輪郭
        # 左に子がいないので、右の子が持っている右輪郭を引き継いで使う（右の子は相対位置をずらしたので、輪郭もずらす）
        node.right_contour = [0] + [x + node.right.relative_x for x in node.right.right_contour]

    else:

        # 左右に子がいる場合
        #    node
        #    /  \
        #   子   子

        # 自分からの相対位置しか計算していないので、左のサブツリー、右のサブツリーで重なり合ってしまう
        # 左のサブツリーの右輪郭、右のサブツリーの左輪郭を、階層ごとに比較して、重なってたらずらす
        # ただし、必ずしも全ての階層を比較する必要はなく、
        # サブツリーが重なり合っているレベルだけを調べればよいので、それぞれの長さを調べる
        # 右の子が持つ左輪郭の長さと、左の子が持つ右輪郭の長さで、短い方を取る
        minimum_height = min(len(node.right.left_contour), len(node.left.right_contour))

        # 各階層で、右の子の左輪郭から、左の子の右輪郭を引いて、その差を取る
        # これは、左右のサブツリーの間の距離を表している
        # これがマイナスの場合は、その階層で重なっている、ということ
        # ゼロであれば左サブツリーの右端と、右サブツリーの左端がちょうど一致している、ということ
        # プラスであれば、左右のサブツリーが離れている、ということ
        distances = []
        for i in range(minimum_height):
            distances.append(node.right.left_contour[i] - node.left.right_contour[i])

        # 各階層での距離の最小値を求める
        minimum_distance = min(distances)

        # 最低限、どのくらい移動すればいいか、を求める
        minimal_movement = 0

        if minimum_distance <= 0:
            # 重なっているので、左右のサブツリーを離す必要がある
            # サブツリーが重ならないように、左サブツリーは左に、右サブツリーは右に動かす
            # 左右均等に動かすので、動かす量は2の倍数にする
            if abs(minimum_distance) % 2 == 0:
                # 偶数なので+2にすることで、左サブツリーは左に1、右サブツリーは右に1、というように均等にずらせる
                minimal_movement = abs(minimum_distance) + 2
            else:
                # 奇数なので+1して、合計で2の倍数にする
                minimal_movement = abs(minimum_distance) + 1

        # 左の子は、自分からみて、マイナスの方向にずらす
        node.left.relative_x = -1 * minimal_movement // 2

        # 右の子は、自分からみて、プラスの方向にずらす
        node.right.relative_x = minimal_movement // 2

        # 直下の子の移動量に応じて、輪郭を再計算する

        # 左輪郭をずらす
        if len(node.right.left_contour) > len(node.left.left_contour):
            # 右サブツリーの左輪郭の方が長い場合、足りない分をそこから補う
            node.left_contour =  [0] + [x + node.left.relative_x for x in node.left.left_contour] + [ x + node.right.relative_x for x in node.right.left_contour[len(node.left.left_contour):]]
        else:
            # 左サブツリーの左輪郭の方が長いなら、足りない部分はない
            node.left_contour = [0] + [x + node.left.relative_x for x in node.left.left_contour]

        # 右輪郭をずらす
        if len(node.left.right_contour) > len(node.right.right_contour):
            node.right_contour =  [0] + [x + node.right.relative_x for x in node.right.right_contour] + [x + node.left.relative_x for x in node.left.right_contour[len(node.right.right_contour):]]
        else:
            node.right_contour = [0] + [x + node.right.relative_x for x in node.right.right_contour]


def reingold_tilford_preorder(node):
    if node == None:
        return

    #
    # preorderの場合はここに処理を書く
    #

    # 前段の処理で上位ノードからの相対位置が求まっているので、それを反映させる

    if node.left != None:
        # 左の子の位置を決める
        node.left.x = node.left.relative_x + node.x

        # 子の深さは自分の深さ+1
        node.left.depth = node.left.y = node.depth + 1

    if node.right != None:
        # 右の子の位置を決める
        node.right.x = node.right.relative_x + node.x

        # 子の深さは自分の深さ+1
        node.right.depth = node.right.y = node.depth + 1

    # 再帰呼び出しで深く降りていく
    reingold_tilford_preorder(node.left)
    reingold_tilford_preorder(node.right)


def reingold_tilford(node):
    reingold_tilford_postorder(node)
    reingold_tilford_preorder(node)


def save_png(root, filename):
    import matplotlib.pyplot as plt
    import networkx as nx

    def add_tree(root, G):
        if root is None:
            return

        G.add_node(root.data)

        if root.left is not None:
            G.add_edge(root.data, root.left.data)
            add_tree(root.left, G)

        if root.right is not None:
            G.add_edge(root.data, root.right.data)
            add_tree(root.right, G)


    def get_postion_preorder(root, position={}):
        if root is None:
            return

        position[root.data] = (root.x, -root.y)
        get_postion_preorder(root.left, position)
        get_postion_preorder(root.right, position)

    position = {}
    get_postion_preorder(root, position)

    G = nx.Graph()
    add_tree(root, G)
    nx.draw(G, pos=position, node_size=100)
    plt.savefig(filename)
    plt.cla()


if __name__ == '__main__':

    def create_test_binary_tree():
        # アルゴリズム図鑑にかかれている例を使ってみる
        data_list = [15, 9, 23, 3, 12, 17, 28, 8]

        # 15を頂点にして、残りは上記のリストを使って二分探索木を作成する
        root = insert_binary_tree(None, data_list.pop(0))
        for data in data_list:
            insert_binary_tree(root, data)

        return root


    def main():
        root = create_test_binary_tree()
        print_binary_tree(root)

        reingold_tilford_postorder(root)

        print("\nreingold_tilford_postorder done\n")

        for node in preorder(root):
            print(node.data, node.relative_x, (node.x, node.depth), node.left_contour, node.right_contour)

        reingold_tilford_preorder(root)

        print("\nreingold_tilford_preorder done\n")

        for node in preorder(root):
            print(node.data, node.relative_x, (node.x, node.depth), node.left_contour, node.right_contour)

        save_png(root, "log/binary_search_tree_layout.png")

        # reingold_tilford(root)

        return 0

    sys.exit(main())
