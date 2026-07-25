# 4-π研究：中心定理と厳密導出

## 1. 設定

原点を内部に含む星形凸領域 \(\Omega\subset\mathbb R^2\) の境界を極座標で

\[
x(\theta)=\rho(\theta)e_r(\theta),
\qquad
0\le \theta<2\pi
\]

と書く。ここで

\[
e_r(\theta)=(\cos\theta,\sin\theta),
\qquad
e_\theta(\theta)=(-\sin\theta,\cos\theta)
\]

である。

\(\rho\) は滑らかな場合には通常の意味で微分し、多角形の場合には頂点方向を除く各区間で微分する。以下の積分等式はほとんど至る所で成立する微分を用いる。

## 2. 極表示による境界公式

境界の微分は

\[
x'(\theta)=\rho'(\theta)e_r(\theta)+\rho(\theta)e_\theta(\theta)
\]

であるから、弧長要素は

\[
ds=\sqrt{\rho^2+(\rho')^2}\,d\theta
\]

となる。

外向き単位法線は

\[
n(\theta)
=
\frac{\rho e_r-\rho'e_\theta}
{\sqrt{\rho^2+(\rho')^2}}
\]

であり、

\[
x\cdot n
=
\frac{\rho^2}{\sqrt{\rho^2+(\rho')^2}}
\]

を得る。したがって、

\[
\frac{ds}{x\cdot n}
=
\left(
1+\frac{(\rho')^2}{\rho^2}
\right)d\theta
=
\left(
1+\left|\partial_\theta\log\rho\right|^2
\right)d\theta.
\]

よって、Pólya–Szegő 型境界量

\[
B_\Omega
:=
\int_{\partial\Omega}\frac{ds}{x\cdot n}
\]

は

\[
\boxed{
B_\Omega
=
2\pi+
\int_0^{2\pi}
\left|\partial_\theta\log\rho(\theta)\right|^2d\theta
}
\]

と表される。

この式は、適切な正則性をもつ星形凸領域、および区分的に滑らかな星形凸領域に成立する。

## 3. 動径–法線角

動径方向 \(e_r\) と外向き法線 \(n\) の符号付き角を \(\alpha\) とする。上の法線表示から

\[
\cos\alpha
=
\frac{\rho}{\sqrt{\rho^2+(\rho')^2}},
\qquad
\sin\alpha
=
-\frac{\rho'}{\sqrt{\rho^2+(\rho')^2}}
\]

であるため、

\[
\boxed{
\tan\alpha
=-\frac{\rho'}{\rho}
=-\partial_\theta\log\rho
}
\]

となる。したがって、

\[
\boxed{
B_\Omega-2\pi
=
\int_0^{2\pi}\tan^2\alpha(\theta)\,d\theta
}
\]

である。

これは、Pólya–Szegő 型境界欠損が、動径方向と法線方向のずれの二乗エネルギーであることを示す。

## 4. 接多角形の面積欠損恒等式

\(P\) を原点を内心とし、内接円半径を \(r\) とする凸接多角形とする。各辺上では

\[
x\cdot n=r
\]

であるから、周長を \(L\) とすれば

\[
B_P
=
\int_{\partial P}\frac{ds}{r}
=
\frac{L}{r}.
\]

また、各辺と内心が作る三角形へ分割することにより、古典的な接多角形面積公式

\[
|P|=\frac{rL}{2}
\]

が成立する。ゆえに

\[
B_P
=
\frac{L}{r}
=
\frac{2|P|}{r^2}.
\]

一方、極表示による境界公式から

\[
B_P
=
2\pi+
\int_0^{2\pi}
\left|\partial_\theta\log\rho_P\right|^2d\theta.
\]

両者を比較すると、

\[
\frac{2|P|}{r^2}
=
2\pi+
\int_0^{2\pi}
\left|\partial_\theta\log\rho_P\right|^2d\theta.
\]

したがって次の定理を得る。

## 定理 4.1　接多角形の面積欠損–角エネルギー恒等式

原点を内心とし、内接円半径を \(r\) とする任意の凸接多角形 \(P\) に対し、

\[
\boxed{
|P|-\pi r^2
=
\frac{r^2}{2}
\int_0^{2\pi}
\left|\partial_\theta\log\rho_P(\theta)\right|^2d\theta
}
\]

が成立する。

同値に、動径–法線角 \(\alpha\) を用いて

\[
\boxed{
|P|-\pi r^2
=
\frac{r^2}{2}
\int_0^{2\pi}\tan^2\alpha(\theta)\,d\theta
}
\]

と書ける。

## 5. 正方形と 4-π

単位円に外接する正方形では

\[
r=1,
\qquad
|P|=4.
\]

したがって定理4.1から

\[
\boxed{
4-\pi
=
\frac12
\int_0^{2\pi}
\left|\partial_\theta\log\rho_\square\right|^2d\theta
=
\frac12
\int_0^{2\pi}\tan^2\alpha\,d\theta
}
\]

を得る。

直接計算では、一辺を担当する角域 \(-\pi/4\le\theta\le\pi/4\) において

\[
\rho_\square(\theta)=\sec\theta,
\qquad
\partial_\theta\log\rho_\square(\theta)=\tan\theta
\]

であるため、

\[
\frac12\cdot4
\int_{-\pi/4}^{\pi/4}\tan^2\theta\,d\theta
=
2\left[\tan\theta-\theta\right]_{-\pi/4}^{\pi/4}
=
4-\pi.
\]

## 6. 正 n 角形

内接円半径を \(r\) とする正 \(n\) 角形 \(P_n\) の面積は

\[
|P_n|=nr^2\tan\frac{\pi}{n}
\]

である。したがって、

\[
\boxed{
|P_n|-\pi r^2
=
r^2\left(
n\tan\frac{\pi}{n}-\pi
\right)
}
\]

であり、定理4.1によりこれは動径–法線角エネルギーに等しい。

単位内接円の場合、

\[
\boxed{
n\tan\frac{\pi}{n}-\pi
=
\frac12
\int_0^{2\pi}
\left|\partial_\theta\log\rho_{P_n}\right|^2d\theta
}
\]

となる。

また、\(n\to\infty\) で

\[
n\tan\frac{\pi}{n}-\pi
=
\frac{\pi^3}{3n^2}
+
\frac{2\pi^5}{15n^4}
+
\frac{17\pi^7}{315n^6}
+
O(n^{-8})
\]

である。

## 7. 現段階で確定した意味

\[
4-\pi
\]

は、次の三量が一致する最初の非自明例である。

1. 正方形と内接円の面積差
2. \(\log\rho\) の円周上 Dirichlet エネルギーの半分
3. 動径–法線角の \(\tan^2\) エネルギーの半分

したがって、4-π研究の中心問題は、数値 \(4-\pi\) の評価ではなく、これら三つの幾何量が同一になる構造を分類し、一般化することである。
