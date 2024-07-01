#!/usr/bin/env python

# 参考文献
# https://williamyaoh.com/posts/2023-04-22-drawing-trees-functionally.html

import sys

from binary_search_tree import preorder, print_binary_tree

class BinaryTreeNode:

    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

        self.depth : int = 0

        self.left_contour = [0]
        self.right_contour = [0]

        self.relative_x: int = 0
        self.x: int = 0

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


def reingold_tilford_postorder(node):
    if node == None:
        return

    # 再帰呼び出しで深く降りていく
    reingold_tilford_postorder(node.left)
    reingold_tilford_postorder(node.right)

    #
    # postorderの場合はここに処理を書く
    #

    # 末端にたどり着いて、左右に子がいない場合は何もしない
    if node.left == None and node.right == None:
        return

    # ここから先の処理は、末端から順に上に遡っていくので、必ず子がいることになる

    # まず、各ノードからその子ノードまでの水平距離を計算します。
    # 次に、実際の距離を計算してツリーを「石化」します。
    # x座標は、各ノードのルートからのパスに基づいて計算されます。
    # 水平オフセットの計算は、後順トラバーサルによって行われます。
    # 各ノードで、
    # (1) 左と右のサブツリーの輪郭を再帰的に配置して構築し
    # (2) 左のサブツリーの右輪郭と右のサブツリーの左輪郭を同期して再帰的に計算することで、サブツリーをどのくらい離して配置するか (つまり、現在のノードでのオフセット) を計算し、
    # (3) 現在のノードをルートとするツリーの輪郭を構築します。

    if node.left != None and node.right == None:

        # 左に子がいて、右にいない場合
        #    node
        #    /
        #   子

        # 左の子は、自分からみて -1
        node.left.relative_x = -1

        # 左輪郭
        # 左の子が持っている左輪郭を引き継いで使う（左の子は相対位置をずらしたので、輪郭もずらす）
        node.left_contour = [0] + [x + node.left.relative_x for x in node.left.left_contour]

        # 右輪郭
        # 左の子が持っている右輪郭を引き継いで使う（左の子は相対位置をずらしたので、輪郭もずらす）
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
        # 右の子が持っている右輪郭を引き継いで使う（右の子は相対位置をずらしたので、輪郭もずらす）
        node.right_contour = [0] + [x + node.right.relative_x for x in node.right.right_contour]

    else:

        # 左右に子がいる場合
        #    node
        #    /  \
        #   子   子

        # 自分からの相対位置しか計算していないので、左のサブツリー、右のサブツリーで重なり合ってしまう
        # 左のサブツリーの右輪郭、右のサブツリーの左輪郭を、階層ごとに比較したいが、全階層を比較する必要はない
        # サブツリーが重なり合っている部分だけでよいので、短い方の長さを調べる
        # 右の子が持つ左輪郭の長さと、左の子が持つ右輪郭の長さで、短い方を取る
        minimum_height = min(len(node.right.left_contour), len(node.left.right_contour))

        # 各階層で、右の子の左輪郭から、左の子の右輪郭を引いて、その差を取る
        # これは、左右のサブツリーの間の距離を表している
        # この距離がマイナスの場合は、その階層で重なっている、ということ
        # ゼロであれば左サブツリーの右端と、右サブツリーの左端がちょうど一致している、ということ
        # プラスであれば、左右のサブツリーが離れている、ということ
        distances = []
        for i in range(minimum_height):
            distances.append(node.right.left_contour[i] - node.left.right_contour[i])

        # サブツリーが重ならないようにまるごと左右に動かす
        # どのくらい移動させればよいか、を求める
        # distancesの最小値はマイナスになっているはず
        # 右サブツリーをその絶対値だけ右にずらしたと仮定すると、左サブツリーの右輪郭と、右サブツリーの左輪郭が接した状態になる
        # なので、最小値の絶対値+α の距離を取ればよい
        # 右サブツリーだけを動かすのであれば、+αは1でよいが、
        # 左サブツリーは左に、右サブツリーは右にずらしたいので、+αの部分は2にしたい
        minimal_distance = 0
        if abs(min(distances)) % 2 == 0:
            # 偶数なので+2にする、左サブツリーは左に1、右サブツリーは右に1、というように均等にずらせる
            minimal_distance = abs(min(distances)) + 2
        else:
            # 奇数なので+1して、合計で2の倍数にする
            minimal_distance = abs(min(distances)) + 1

        # ずらす大きさが分かったので、直下の子の位置を決める

        # 左の子は、自分からみて、マイナスの方向にずらす
        node.left.relative_x = -1 * minimal_distance // 2

        # 右の子は、自分からみて、プラスの方向にずらす
        node.right.relative_x = minimal_distance // 2

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
        node.left.x = node.left.relative_x + node.x
        node.left.depth = node.depth + 1

    if node.right != None:
        node.right.x = node.right.relative_x + node.x
        node.right.depth = node.depth + 1

    # 再帰呼び出しで深く降りていく
    reingold_tilford_preorder(node.left)
    reingold_tilford_preorder(node.right)


def reingold_tilford(node):
    reingold_tilford_postorder(node)
    reingold_tilford_preorder(node)



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

        # reingold_tilford(root)

        return 0

    sys.exit(main())
