# 4-π研究：先行研究との接点

調査日：2026-07-25

## 1. 調査上の原則

本ファイルでは、次を区別する。

1. 文献中に明記されている既知結果
2. 既知結果から本研究で直接導出した恒等式
3. 文献上の優先権が未確定の統合的解釈

検索で同一表現が見つからないことだけをもって、新規性の証明とはしない。

## 2. Pólya–Szegő 型境界量

凸領域 \(\Omega\) に対する境界量

\[
B_\Omega
=
\int_{\partial\Omega}\frac{ds}{x\cdot n}
\]

は、Pólya–Szegő の等周不等式・ねじり剛性の文脈で用いられている。

Grant Keady, “Torsional rigidity for tangential polygons,” *IMA Journal of Applied Mathematics* 86 (2021), 1204–1211 は、Pólya–Szegő の記法としてこの量を記載し、接多角形について

\[
B_P=\frac{L}{r}
\]

を用いている。

- DOI: `10.1093/imamat/hxab022`
- 出版者ページ: `https://doi.org/10.1093/imamat/hxab022`
- arXiv: `https://arxiv.org/abs/2103.06129`

同論文は接多角形の古典公式

\[
|P|=\frac{rL}{2}
\]

も明記している。

## 3. 本研究での直接導出

極表示

\[
x(\theta)=\rho(\theta)e_r(\theta)
\]

から

\[
\frac{ds}{x\cdot n}
=
\left(1+|\partial_\theta\log\rho|^2\right)d\theta
\]

が直接得られる。したがって、

\[
B_\Omega-2\pi
=
\int_0^{2\pi}|\partial_\theta\log\rho|^2d\theta.
\]

接多角形について既知の二式

\[
B_P=\frac{L}{r},
\qquad
|P|=\frac{rL}{2}
\]

と組み合わせることで、

\[
|P|-\pi r^2
=
\frac{r^2}{2}
\int_0^{2\pi}|\partial_\theta\log\rho_P|^2d\theta
\]

を得る。

この導出は `THEOREM_NOTE_JA.md` に記録する。

## 4. 双対等周欠損との関係

R. J. Gardner and S. Vassallo, “Inequalities for dual isoperimetric deficits,” *Mathematika* 45 (1998), 269–285 は、星形体の動径関数を用いる双対等周欠損と、動径関数間の \(L^2\)・\(L^\infty\) 距離を研究している。

- DOI: `10.1112/S0025579300014200`
- 出版者ページ: `https://doi.org/10.1112/S0025579300014200`

同研究は、本研究と同じく動径関数を中心に置くが、主対象は動径関数そのものの距離および双対 Brunn–Minkowski 理論である。本研究の中心量

\[
\int|\partial_\theta\log\rho|^2
\]

は、微分型の角度エネルギーであり、少なくとも調査済みの同論文の要旨・主要記述とは異なる。

関連する安定性研究：

R. J. Gardner and S. Vassallo, “Stability of inequalities in the dual Brunn–Minkowski theory,” *Journal of Mathematical Analysis and Applications* 231 (1999), 568–587.

- DOI: `10.1006/jmaa.1998.6254`

## 5. 接多角形研究との関係

接多角形の面積・周長・内接円半径の関係、および正多角形・三角形等の具体計算は古典的である。したがって、

\[
|P|=\frac{rL}{2}
\]

や

\[
|P_n|=nr^2\tan\frac{\pi}{n}
\]

自体を新規結果とは扱わない。

4-π研究が問題にするのは、これらの面積公式を

\[
\partial_\theta\log\rho
\quad\text{および}\quad
\tan\alpha
\]

と結び、面積欠損を動径–法線角エネルギーとして解釈する統合構造である。

## 6. 現時点の文献判断

現在までに確認した範囲では、次の完全等式を「動径–法線角エネルギー」として中心定理に据えた文献は確認できていない。

\[
|P|-\pi r^2
=
\frac{r^2}{2}
\int_0^{2\pi}\tan^2\alpha\,d\theta.
\]

ただし、これは網羅的調査の完了を意味しない。特に以下の分野を追加調査する必要がある。

- Pólya–Szegő 境界汎関数の後続研究
- 接多角形・circumscribed polygon の積分幾何
- centro-affine perimeter および centro-affine 曲線エネルギー
- support function と radial function の変分公式
- dual Brunn–Minkowski 理論
- logarithmic Minkowski problem 周辺
- 星形領域の Dirichlet 型形状エネルギー

## 7. 新規性の暫定表現

論文草稿では、現段階では次のように表現する。

> The constituent identities are classical or elementary. The proposed contribution is their synthesis into an exact area-deficit identity governed by the radial–normal angle energy, together with its interpretation as the two-dimensional origin of geometric dual topology.

すなわち、個別公式の発見を主張するのではなく、完全等式としての統合、角度的解釈、一般化および三次元理論への接続を研究対象とする。
