# Tree Layout

ツリーを綺麗にレイアウトするアルゴリズムにReingold-Tilfordがあります。

Reingold-TilfordをPythonおよびJavaScriptで実装したものです。

<br>

> [!NOTE]
>
>  参考文献
>
> https://llimllib.github.io/pymag-trees/


<br><br>

# ライブデモ

JavaScript実装ではcytoscape.jsを使って可視化しています。

こちらの[Live Demo](https://takamitsu-iida.github.io/tree/index.html)を参照。

<br><br>

# 実装メモ

意外に参考になる文献や実装は少ないです。

<br>

## 二分探索木(Binary Search Tree)のレイアウト実装

一般的なツリー構造の前に、二分探索木で考えます。

二分探索木におけるレイアウト決定のPython実装

[bin/binary_search_tree_layout.py](bin/binary_search_tree_layout.py)

<br>

### 二分探索木とは

> [!NOTE]
>
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

[bin/binary_seach_tree.py](/bin/binary_search_tree.py) はノードの追加・削除のルールをアルゴリズム辞典の通りに実装したものです。

<br>

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

<br>

## Reingold-Tilfordアルゴリズム

Reingold-Tilfordアルゴリズムでは、以下の6個の原則を守るように描かれます。

<dl>
<dt>Principle 1</dt> <dd>The edges of the tree should not cross each other.（エッジは交差しない）</dd>

<dt>Principle 2</dt> <dd>All nodes at the same depth should be drawn on the same horizontal line.（同じ階層のノードは同じ高さに）</dd>

<dt>Principle 3</dt> <dd>Trees should be drawn as narrowly as possible.（ツリーはできるだけ狭く）</dd>

<dt>Principle 4</dt> <dd>A parent should be centered over its children.（親は子の中央に）</dd>

<dt>Principle 5</dt> <dd>A subtree should be drawn the same no matter where in the tree it lies.（サブツリーはどこにあっても同じ形状を保つように）</dd>

<dt>Principle 6</dt> <dd>The child nodes of a parent node should be evenly spaced.（兄弟ノードの間隔はできるだけ一定に）</dd>
</dl>

Principle 2を守るのは容易です。
ツリーを頂点から（すなわちpreorder探索で）たどっていき、深さに応じてY座標を決めるだけです。

問題はX座標の決め方です。

人間がツリーを書くときには頂点から書き始めた方が楽ですが、Reingold-Tilfordでは末端から頂点に向かって（すなわちpostorder探索で）決めていきます。

postorder探索で末端にたどり着いたとき、そこでできることは何もありません。

二分探索木では上位ノード（つまり親）へのポインタを持っていないため、末端のノードが親や兄弟を参照することはできないからです。

一つ上の階層に戻るとノードは子を持ちます。子の持ち方は次の３パターンです。

左だけに子がいるパターン。左の子のX座標を、自分のX座標から相対的に-1します。
自分のX座標はさらに上位のノードが決めてくれるので、初期値のままにしておきます。

```text
  o
 /
o
```

右だけに子がいるパターン。右の子のX座標を、自分のX座標から相対的に+1します。
自分のX座標は初期値のままにしておきます。

```text
  o
   \
    o
```

左と右に子を持つパターン。この場合、左右の子の位置を決めるのは複雑です。
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
左の子の右輪郭と、右の子の左輪郭を比較して、重なりが起こらないように子の位置を決める必要があります。

### 輪郭（contour）の作り方

ノードから親や兄弟を辿れるなら、必要に応じて知りたい輪郭を取得すればよいのですが、
二分探索木の場合は親から子への参照しかできませんので、そういうわけにはいきません。
ノードの中に自分の左輪郭、右輪郭の情報を保管しておく必要があります。
そこで、全てのノードに初期値として左輪郭、右輪郭共にリスト `[0]` を持たせます。

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

postorder探索で階層を上がるたびに、子が持つ左輪郭リスト・右輪郭リストに自分の位置を加えていきます。

もとに戻って、左右に子がいるパターンでのX座標の決め方です。

```text
  o
 / \
o   o
```

右の子が持つ左輪郭の座標リストから、左の子が持つ右輪郭の座標リストを各階層で引き算したとき、

- プラスの場合は離れている

- マイナスの場合は重なっている

- ゼロの場合は左のサブツリーの右端と、右のサブツリーの左端が重なっている

ということになります。

`min(右の子の左輪郭 - 左の子の右輪郭)` を計算して、
これが十分な大きさになるように左の子は左に、右の子は右に動かします。

<br>

### 相対位置から絶対位置への変換処理

ボトムアップで下から上に探索するときに、親は子の位置を自分からの相対位置で指定しています。
これを絶対位置に反映させるには、今度は頂点から順に末端に向けて適用していく必要があります。
つまりpreorder探索で実行します。

```python
def reingold_tilford_preorder(node):
    if node == None:
        return

    if node.left != None:
        # 左の子の位置を決める
        node.left.x = node.left.relative_x + node.x

    if node.right != None:
        # 右の子の位置を決める
        node.right.x = node.right.relative_x + node.x

    # 再帰呼び出しで深く降りていく
    reingold_tilford_preorder(node.left)
    reingold_tilford_preorder(node.right)
```

<br>

## 二分探索木での位置決めの例

[bin/binary_search_tree_layout.py](/bin/binary_search_tree_layout.py) は二分探索木をReingold-Tilfordアルゴリズムで位置決めするスクリプトです。

<br>

> [!NOTE]
>
> Pythonスクリプトでは networkx および matplotlib を使って画像を出力しています。

<br>

二分探索木に `[15, 9, 23, 3, 12, 17, 28, 8]` の入力を与えたとき、
下記のような描画結果が得られます。

![例](/asset/binary_search_tree_0.png)

<br>

二分探索木に `[8, 3, 10, 1, 6, 14, 4, 7, 13]` の入力を与えたとき、
下記のような描画結果が得られます。

![例](/asset/binary_search_tree_1.png)

<br>

二分探索木に `[12, 6, 16, 2, 8, 14, 18, 4, 10, 9, 11]` の入力を与えたとき、
下記のような描画結果が得られます。

![例](/asset/binary_search_tree_2.png)

<br>

二分探索木に `[10, 5, 15, 3, 7, 13, 17, 2, 4, 6, 8, 12, 14, 16, 18]` の入力を与えたとき、
下記のような描画結果が得られます。

![例](/asset/binary_search_tree_3.png)

<br>

二分探索木に `[25, 20, 36, 10, 22, 30, 40, 5, 12, 28, 38, 48, 1, 8, 15, 18, 26, 32, 35, 39, 45, 49]` の入力を与えたとき、
下記のような描画結果が得られます。

![例](/asset/binary_search_tree_4.png)


<br><br><br>

## 一般的なツリー構造での位置決めの例

基本的な考え方は二分探索木の場合と同じです。

自分よりも左にいる兄弟の右輪郭と、自分自身の左輪郭を比較して、重なっていれば自分を右に動かす、という戦略で位置を決めていきます。

実装はPythonスクリプト [bin/tree_layout.py](bin/binary_search_tree_layout.py) を参照。

以下、実行結果の例です。

<br><br>

例．シンプルなツリー構造の場合

![例](/asset/tree_1.png)

<br>

例．バランスのとれたツリー構造の場合

![例](/asset/tree_2.png)

<br>

例．左に偏ったツリー構造の場合

![例](/asset/tree_3.png)

<br>

例．右に偏ったツリー構造の場合

![例](/asset/tree_4.png)

<br>

例．バランスのとれた深いツリー構造の場合

![例](/asset/tree_5.png)

<br>

例．左に偏った階層が深いツリー構造の場合

![例](/asset/tree_6.png)

<br>

例．右下に大きなサブツリーがある場合

![例](/asset/tree_7.png)

<br>

例．混雑したツリーの場合

![例](/asset/tree_8.png)

<br>
