#!/usr/bin/env python

# 参考文献
# https://williamyaoh.com/posts/2023-04-22-drawing-trees-functionally.html

import sys


class BinaryTreeNode:

    # ノード間の最小距離をクラス変数として定義
    MINIMAL_X_DISTANCE = 1
    MINIMAL_Y_DISTANCE = 1

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

    X軸方向の位置（水平オフセットの計算）は、後順トラバーサルで行う。
    各ノードで現在のノードをルートとするツリーの輪郭を構築し、その輪郭を使ってサブツリー同士が重ならないように配置する。

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
    # 自分の位置は親ノードによって後で決められる
    if node.left == None and node.right == None:
        return

    # ここから先の処理は左か右に必ず子がいるので、子の位置を決めていく

    if node.left != None and node.right == None:

        # 左に子がいて、右にいない場合
        #    node
        #    /
        #   子

        # 左の子は、自分からみて -1
        node.left.relative_x = -1

        # 自分の左輪郭を構築する
        # 左の子が持っている左輪郭をコピーして、先頭に自分の相対位置 0 を追加する
        # ただし、左の子は相対位置を移動させたので、左輪郭もまとめて移動する
        node.left_contour = [0] + [x + node.left.relative_x for x in node.left.left_contour]

        # 自分の右輪郭を構築する
        # 右に子がいないので、左の子が持っている右輪郭をコピーして、先頭に自分の相対位置 0 を追加する
        # ただし、左の子は相対位置を移動させたので、左輪郭もまとめて移動する
        node.right_contour = [0] + [x + node.left.relative_x for x in node.left.right_contour]

    elif node.right != None and node.left == None:

        # 左に子がなく、右に子がある場合
        #    node
        #       \
        #        子

        # 右の子の自分からの相対位置は +1
        node.right.relative_x = +1

        # 自分の左輪郭を構築する
        # 左に子がいないので、右の子が持っている左輪郭を引き継いで使う
        node.left_contour = [0] + [x + node.right.relative_x for x in node.right.left_contour]

        # 自分の右輪郭を構築する
        # 左に子がいないので、右の子が持っている右輪郭を引き継いで使う
        node.right_contour = [0] + [x + node.right.relative_x for x in node.right.right_contour]

    else:

        # 左右に子がいる場合
        #    node
        #    /  \
        #   子   子

        # 左の子を頂点とするサブツリーと、右の子を頂点とするサブツリーで重なりがあるかもしれない
        # 左の子のサブツリーの右輪郭、右の子のサブツリーの左輪郭を、階層ごとに比較して、重なってたらずらす
        # ただし、必ずしも全ての階層を比較する必要はなく、サブツリーが存在する階層だけを調べればよい

        # 右の子が持つ左輪郭の長さと、左の子が持つ右輪郭の長さで、短い方を取る
        minimum_height = min(len(node.right.left_contour), len(node.left.right_contour))

        # 各階層で、右の子の左輪郭から、左の子の右輪郭を引いて、差を計算する
        # これが
        #   - マイナスの場合は、その階層で重なりが発生している
        #   - ゼロであれば左サブツリーの右端と、右サブツリーの左端がちょうど一致している
        #   - プラスであれば、左右のサブツリーが離れている
        # ということになる
        # 差の最小値を求める
        minimum_distance = sys.maxsize
        for i in range(minimum_height):
            diff = node.right.left_contour[i] - node.left.right_contour[i]
            if diff < minimum_distance:
                minimum_distance = diff

        # 最低限確保したい間隔
        minimal_distance = BinaryTreeNode.MINIMAL_X_DISTANCE

        # どのくらい移動すべきか、を求める
        shift_value = 0

        if minimum_distance + shift_value <= minimum_distance:
            # 左の子のサブツリーと、右の子のサブツリーで重複しているので、間隔を広げる必要がある
            shift_value = minimal_distance - minimum_distance

            # 左の子のサブツリーは左に、右の子のサブツリーは右に動かしたい
            # 左右均等に動かすので、動かす量は2の倍数にする
            if abs(shift_value) % 2 == 0:
                # 偶数なので+2にすることで、左サブツリーは左に1、右サブツリーは右に1、というように均等にずらせる
                shift_value = abs(shift_value) + 2
            else:
                # 奇数なので+1して、合計で2の倍数にする
                shift_value = abs(shift_value) + 1

            # 左の子は、自分からみて、マイナスの方向にずらす
            node.left.relative_x = -1 * shift_value // 2

            # 右の子は、自分からみて、プラスの方向にずらす
            node.right.relative_x = shift_value // 2

            # 自分の左輪郭を再構築する
            if len(node.right.left_contour) > len(node.left.left_contour):
                # 右サブツリーの左輪郭の方が長い場合、足りない分をそこから補う
                node.left_contour =  [0] + [x + node.left.relative_x for x in node.left.left_contour] + [ x + node.right.relative_x for x in node.right.left_contour[len(node.left.left_contour):]]
            else:
                # 左サブツリーの左輪郭の方が長いなら、足りない部分はない
                node.left_contour = [0] + [x + node.left.relative_x for x in node.left.left_contour]

            # 自分の右輪郭を再構築する
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

        # 子のY軸の位置を決める
        node.left.y = node.left.depth * BinaryTreeNode.MINIMAL_Y_DISTANCE

    if node.right != None:
        # 右の子の位置を決める
        node.right.x = node.right.relative_x + node.x

        # 子の深さは自分の深さ+1
        node.right.depth = node.right.y = node.depth + 1

        # 子のY軸の位置を決める
        node.right.y = node.right.depth * BinaryTreeNode.MINIMAL_Y_DISTANCE


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

        G.add_node(root.data, label=f"{root.data}")

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
    nx.draw(G, pos=position, node_size=300, with_labels=True, font_size=8, font_color='white')
    plt.savefig(filename)
    plt.cla()


if __name__ == '__main__':

    def create_binary_tree(data_list: list):
        root = insert_binary_tree(None, data_list.pop(0))
        for data in data_list:
            root = insert_binary_tree(root, data)
        return root

    def create_test_trees():

        trees = []

        # 参考文献のアルゴリズム図鑑にかかれている例
        data_list = [15, 9, 23, 3, 12, 17, 28, 8]
        trees.append(create_binary_tree(data_list))

        # Wikipediaの例
        data_list = [8, 3, 10, 1, 6, 14, 4, 7, 13]
        trees.append(create_binary_tree(data_list))

        data_list = [12, 6, 16, 2, 8, 14, 18, 4, 10, 9, 11]
        trees.append(create_binary_tree(data_list))

        data_list = [10, 5, 15, 3, 7, 13, 17, 2, 4, 6, 8, 12, 14, 16, 18]
        trees.append(create_binary_tree(data_list))

        data_list = [25, 20, 36, 10, 22, 30, 40, 5, 12, 28, 38, 48, 1, 8, 15, 18, 26, 32, 35, 39, 45, 49]
        trees.append(create_binary_tree(data_list))

        import random
        data_list = range(1, 50)
        data_list = random.sample(data_list, len(data_list))
        trees.append(create_binary_tree(data_list))

        return trees


    def test_tree(root, filename):

        print_binary_tree(root)

        reingold_tilford_postorder(root)
        print("\nreingold_tilford_postorder done\n")
        for node in preorder(root):
            print(node.data, node.relative_x, (node.x, node.depth), node.left_contour, node.right_contour)

        reingold_tilford_preorder(root)
        print("\nreingold_tilford_preorder done\n")
        for node in preorder(root):
            print(node.data, node.relative_x, (node.x, node.depth), node.left_contour, node.right_contour)

        save_png(root, filename)


    def main():
        trees = create_test_trees()
        for i, tree in enumerate(trees):
            test_tree(tree, f"log/binary_search_tree_{i}.png")
        return 0

    sys.exit(main())
