# Tree Layout

ツリーを綺麗にレイアウトするアルゴリズムとしてReingold-Tilfordがあります。

参考文献

https://llimllib.github.io/pymag-trees/

<br>

## 二分探索木(Binary Search Tree)

一般的なツリー構造の前に、二分探索木で考えます。

### 二分探索木とは

> 参考文献
>
> アルゴリズム図鑑 増補改訂版 石田保輝 宮崎修一著 翔泳社
>
> https://www.shoeisha.co.jp/book/detail/9784798172439

アルゴリズム辞典に詳しい説明があります。

二分探索木は各ノードが最大2つの子を持つツリー構造で、以下の特徴を持ちます。

特徴１．同じ値はツリー内に存在しない（同じ値は後から追加挿入できない）

特徴２．左のサブツリーには、自身の値より小さい値を持つノードだけが存在する

特徴３．右のサブツリーには、より大きい値を持つノードだけが存在する

このルールに従うと、二分探索木の最小の値は左のサブツリーの末端に存在し、最大の値は右のサブツリーの末端に存在します。

bin/binary_seach_tree.py

ノードの追加・削除のルールをアルゴリズム辞典の通りに実装したものです。

### preorder探索とpostorder探索

これを把握しておかないと先に進めません。

ツリーを探索するときに、頂点から順にたどるのがpreorder探索、末端から頂点に向かって辿るのがpostorder探索です。

それぞれの実装はこのようになります。

```python
def traverse_preorder(root: BinaryTreeNode):
    if root == None:
        return

    #
    # ノードにたどり着いたときの処理をここに書く
    #

    # 処理が終わったら左サブツリー、右サブツリーの順に探索して深いノードを探しに行く
    traverse_preorder(root.left)
    traverse_preorder(root.right)
```

```python
def traverse_postorder(root: BinaryTreeNode):
    if root == None:
        return

    # 左サブツリー、右サブツリーと探索して、たどり着けるところ（すなわち末端）まで奥に進む
    traverse_postorder(root.left)
    traverse_postorder(root.right)

    #
    # ノードににたどり着いたときの処理をここに書く
    #
```

処理を書く場所が違うだけで、ほぼ同じです。

## Reingold-Tilfordアルゴリズム

これら6個の原則を守るように描かれます。

Principle 1: The edges of the tree should not cross each other.

Principle 2: All nodes at the same depth should be drawn on the same horizontal line. This helps make clear the structure of the tree.

Principle 3: Trees should be drawn as narrowly as possible.

Principle 4: A parent should be centered over its children.

Principle 5: A subtree should be drawn the same no matter where in the tree it lies.

Principle 6: The child nodes of a parent node should be evenly spaced.

Principle 2を守るのは容易です。
ツリーを頂点からpreorder探索でたどっていき、深さに応じてY座標を決めるだけです。

問題はX座標の決め方です。

人間がツリーを書くときには頂点から書き始めた方が楽ですが、Reingold-Tilfordでは、postorder探索、すなわち下から上に向かって決めていきます。

postorder探索で末端にたどり着いたとき、そこでできることは何もありません。
上位ノード（つまり親）へのポインタを持っていないため、末端のノードが親や兄弟を参照することはできないからです。

一つ上の階層に上がるとノードは子を持つようになります。
子の持ち方は次の３パターンです。

左だけに子がいるパターン。左の子のX座標は、自分のX座標から相対的に-1します。

```text
  o
 /
o
```

右だけに子がいるパターン。右の子のX座標は、自分のX座標から相対的に+1にします。

```text
  o
   \
    o
```

左と右に子を持つパターン。この場合は複雑です。
単純に左の子は-1、右の子は+1、としてしまうと、下の方でツリーが重なってしまうかもしれないからです。

```text
  o
 / \
o   o
```

ここで登場するのが輪郭（contour）という概念です。

ツリーの各階層で一番左にいるノードを取り出したものが左輪郭（left contour）、
一番右にいるノードを取り出したものが右輪郭（right contour）です。

２つのツリーが重なっているかどうかを判定するには、この輪郭同士を比較します。

左の子の右輪郭（right contour）と、右の子の左輪郭（left contour）を比較して、
重なりが起こらないように子の位置を決める必要があります。

### 輪郭（contour）の作り方

ノードから親や兄弟を辿れるなら、その都度輪郭を取得することもできますが、
二分探索木の場合は親から子への参照しかできませんので、ノードの中に輪郭情報を保管しておく必要があります。

全てのノードは初期値として左輪郭、右輪郭共に`[0]`を持ちます。

```python
class BinaryTreeNode:

    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

        # 自分からみた左輪郭、右輪郭
        self.left_contour = [0]
        self.right_contour = [0]
```

postorder探索で階層を上がるたびに、子が持つ左輪郭・右輪郭に自分の位置を加えていきます。

もとに戻って、左右に子がいるパターンでのX座標の位置決めです。

```text
  o
 / \
o   o
```

右の子が持つ左輪郭と、左の子が持つ右輪郭を、各階層で引き算したとき、

- プラスの場合は離れている
- マイナスの場合は重なっている
- ゼロの場合は左のサブツリーの右端と、右のサブツリーの左端が重なっている

ということになります。

`min(右の子の左輪郭 - 左の子の右輪郭)` を計算して、
これが十分な大きさになるように左の子は左に、右の子は右に動かします。


## 例

`[15, 9, 23, 3, 12, 17, 28, 8]`

![例](/asset/binary_search_tree_0.png)


`[8, 3, 10, 1, 6, 14, 4, 7, 13]`
![例](/asset/binary_search_tree_1.png)


`[12, 6, 16, 2, 8, 14, 18, 4, 10, 9, 11]`
![例](/asset/binary_search_tree_2.png)


`[10, 5, 15, 3, 7, 13, 17, 2, 4, 6, 8, 12, 14, 16, 18]`
![例](/asset/binary_search_tree_3.png)

`[25, 20, 36, 10, 22, 30, 40, 5, 12, 28, 38, 48, 1, 8, 15, 18, 26, 32, 35, 39, 45, 49]`
![例](/asset/binary_search_tree_4.png)