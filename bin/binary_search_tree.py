#!/usr/bin/env python
"""
二分探索木 (Binary Search Tree)


各ノードが最大2つの子を持つツリー構造で、以下の特徴を持つ。

特徴１．
    同じ値はツリー内に存在しない（同じ値は後から追加挿入できない）

特徴２．
    左のサブツリーには、自身の値より小さい値を持つノードだけが存在する

特徴３．
    右のサブツリーには、より大きい値を持つノードだけが存在する

したがって、二分探索木の最小の値は左のサブツリーの末端に存在し、最大の値は右のサブツリーの末端に存在する
"""

import sys

class BinaryTreeNode:
    """二分探索木のノードクラス
    """

    def __init__(self, data: object):
        self.data = data
        self.left = None
        self.right = None

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


def delete_binary_tree(root: BinaryTreeNode, data: object) -> BinaryTreeNode:
    """二分探索木から指定された値のノードを削除する

    Args:
        root (_type_): _description_
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    if root is None:
        return root

    if data < root.data:
        # 削除すべきデータが現在のノードの値より小さい場合は左のサブツリーを探索し、
        root.left = delete_binary_tree(root.left, data)
    elif data > root.data:
        # 削除すべきデータが現在のノードの値より大きい場合は右のサブツリーを探索し、
        root.right = delete_binary_tree(root.right, data)
    else:
        # 削除すべきデータがルートノードの値であれば、このノード自身が削除対象
        if root.left is None:
            temp = root.right
            root = None
            return temp
        elif root.right is None:
            temp = root.left
            root = None
            return temp

        # 左サブツリーの最大値をここに昇格させる
        root.data = find_max_node(root.left).data
        root.left = delete_binary_tree(root.left, root.data)

        # もしくは、右サブツリーの最小値をここに昇格させる方法でもよい
        # root.data = find_min_node(root.right).data
        # root.right = delete_binary_tree(root.right, root.data)

    return root


def find_min_node(root: BinaryTreeNode):
    current = root
    while current.left is not None:
        current = current.left
    return current


def find_max_node(root: BinaryTreeNode):
    current = root
    while current.right is not None:
        current = current.right
    return current


def traverse_preorder(root: BinaryTreeNode, callback=None):
    if root == None:
        return

    #
    # ノードにたどり着いたときの処理をここに書く
    #
    if callback is not None and callable(callback):
        callback(root)

    #
    # 処理が終わったら左サブツリー、右サブツリーの順に探索して深いノードを探しに行く
    #
    traverse_preorder(root.left, callback=callback)
    traverse_preorder(root.right, callback=callback)


def traverse_inorder(root: BinaryTreeNode, callback=None):
    if root == None:
        return

    #
    # 左サブツリーを探索して深いノードを探しに行く
    #
    traverse_preorder(root.left, callback=callback)

    #
    # ノードににたどり着いたときの処理をここに書く
    #

    if callback is not None and callable(callback):
        callback(root)

    #
    # 右サブツリーを探索して深いノードを探しに行く
    #
    traverse_preorder(root.right, callback=callback)


def traverse_postorder(root: BinaryTreeNode, callback=None):
    if root == None:
        return

    #
    # postorder、すなわち末端から遡る方向に探索する
    #

    # 左サブツリー、右サブツリーと探索して、たどり着けるところ（すなわち末端）まで奥に進む
    traverse_postorder(root.left, callback=callback)
    traverse_postorder(root.right, callback=callback)

    #
    # ノードににたどり着いたときの処理をここに書く
    #

    if callback is not None and callable(callback):
        callback(root)


def preorder(root: BinaryTreeNode):
    if root == None:
        return
    yield root
    yield from preorder(root.left)
    yield from preorder(root.right)


def inorder(root: BinaryTreeNode):
    if root == None:
        return
    yield from inorder(root.left)
    yield root
    yield from inorder(root.right)


def postorder(root: BinaryTreeNode):
    if root == None:
        return
    yield from postorder(root.left)
    yield from postorder(root.right)
    yield root


def level_order(root: BinaryTreeNode):
    if root == None:
        return

    q = [root]

    while q:
        node = q.pop(0)

        yield node

        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)


def tree_height(root: BinaryTreeNode) -> int:
    return (max(tree_height(root.left), tree_height(root.right)) + 1) if root else 0


def print_binary_tree(root: BinaryTreeNode, level=0):
    """preorder探索でノードを表示する

    Args:
        root_node (Node): _description_
    """
    if root == None:
        return

    print_binary_tree(root.left, level + 1)
    print(' ' * 4 * level + '-> ' + str(root.data))
    print_binary_tree(root.right, level + 1)


def test_binary_tree():

    # アルゴリズム図鑑にかかれている例を使ってみる
    data_list = [15, 9, 23, 3, 12, 17, 28, 8]

    # 15を頂点にして、残りは上記のリストを使って二分探索木を作成する
    root = insert_binary_tree(None, data_list.pop(0))
    for data in data_list:
        insert_binary_tree(root, data)

    print("--- Binary Tree ---")
    print_binary_tree(root)
    print('')

    print("--- Tree Hight---")
    print(tree_height(root))
    print('')

    print("--- Preorder Traversal ---")
    traverse_preorder(root, lambda node: print(node.data))
    print('')

    print("--- Postorder Traversal ---")
    traverse_postorder(root, lambda node: print(node.data))
    print('')

    # 1を追加する
    print("--- insert 1 ---")
    insert_binary_tree(root, 1)
    print_binary_tree(root)
    print('')

    # 4を追加する
    print("--- insert 4 ---")
    insert_binary_tree(root, 4)
    print_binary_tree(root)
    print('')

    # 28を削除する
    # 28は末端に位置している
    print("--- delete 28 ---")
    delete_binary_tree(root, 28)
    print_binary_tree(root)
    print('')

    # 8を削除する
    # 8は中間で子を一つだけ持つ
    print("--- delete 8 ---")
    delete_binary_tree(root, 8)
    print_binary_tree(root)
    print('')

    # 9を削除する
    # 9は中間で子を二つ持つ
    print("--- delete 9 ---")
    delete_binary_tree(root, 9)
    print_binary_tree(root)
    print('')

    print("--- Preorder Traversal ---")
    print([node.data for node in preorder(root)])

    print("--- Inorder Traversal ---")
    print([node.data for node in inorder(root)])

    print("--- Postorder Traversal ---")
    print([node.data for node in postorder(root)])

    print("--- Level Order Traversal ---")
    print([node.data for node in level_order(root)])


if __name__ == '__main__':

    def main():
        test_binary_tree()
        return 0

    sys.exit(main())
