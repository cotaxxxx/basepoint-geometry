# H-43-1(ii)-E — 独立端点補題の提出

日付：2026-10-09。独立した紙上証明。**H-43-1(ii) は OPEN、CHAT AUDIT 判定待ち。**
Code の未実行証明書を使用・複写・実行していない。
主報告 §3.1 と同文の証明に、必要な定義・原典 pin・前提評価を添えた独立提出物である。
46件の既存 exact 検査の対象にこの新しい解析補題が含まれるとは主張しない。

## 原典の固定と監査状態

| 項目 | 固定値 |
|---|---|
| 正式文書名 | D-OB P1 DESIGN NOTE — TRANSVERSE KERNEL, REGULARITY, CERTIFICATION QUANTITIES |
| Repository | `cotaxxxx/bg-oblate-spheroid` |
| Branch | 原典の Base 記載は `design/d-ob-p1`。今回の取得は下記 immutable commit で行った。現在の branch head の同一性は主張しない。 |
| Path | `analysis/D_OB_P1_DESIGN_NOTE.md` |
| Full commit | `69e104602e939817b6f4d71df3f6bd63cbc729e0` |
| Git blob | `f81e120e44a866d206117d4fab5fac627f26ccd1` |
| SHA-256 | `2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9` |
| 行数 | 164 |
| 節 | §1（密度・測度）、§3.2–3.4（微分と角関数）、§4（可積分性）、§5 Lemma V（83行目から） |
| 原典に記録された状態 | `CHAT_ANALYTIC_DERIVATION_PASS / EXTERNAL_AUDIT_PENDING / NOT_BINDING` |

この状態を外部監査済み・binding に変更して引用しない。Lemma V の境界値の**既存の定義**を用い、
本接続に必要な収束は以下で独立に証明する。原典は新たな境界値の定義で置換しない。
現行の証拠義務は predeclare v3.1 §4（commit `06f5bd2b69ce94a0dbe65dc6ff9a1c7025f0bf10`）
および 2026-10-09 の正式指示による。各 pin は `source_manifest.json` にも記録した。

## 定義と前提評価の独立確認

\[
2/5\le\lambda\le93/200,\quad L=\lambda^2,\quad m^2+\rho^2=1,
\quad112/113\le m\le1,\quad0\le\rho\le15/113.
\]
\[
\mu\in[m-\rho,1],\quad s=m-\mu\in[m-1,\rho],\quad0\le\phi\le\pi,
\quad -\rho\le\xi\le\rho.
\]
\[
a^2=1-\mu^2,\ b=a\cos\phi,\ y=a\sin\phi,\quad
w^2=\mu^2+L(1-\mu^2),\quad D^2=(b-\xi)^2+y^2+Ls^2,
\quad h=\lambda(1-m\mu-\xi b),\quad\mathcal F=h(\arccos\gamma)^2,
\quad\gamma=h/(wD).
\]
微分は \(\lambda,m,\mu,\phi\) を固定し、\(p_\xi=(\xi,0,\lambda m)\) の第一座標に関して行う。
\(D>0\) で
\[
n=(\lambda b,\lambda y,\mu)/w,\quad e=(b-\xi,y,-\lambda s)/D,
\quad\nu=n\cdot e_x,\quad\kappa=e\cdot e_x,
\quad\gamma=n\cdot e.
\]
両者は単位ベクトルであり、\(2h/\lambda=D^2+(1-L)s^2+\rho^2-\xi^2\ge0\) から \(0\le\gamma\le1\)。
射影の Cauchy–Schwarz により
\[
(\nu-\gamma\kappa)^2\le(1-\gamma^2)(1-\kappa^2)\le1,
\quad\gamma_\xi=(\gamma\kappa-\nu)/D.
\]
\(R=\arccos\gamma/\sqrt{1-\gamma^2}\) は原典 §3.2 の連続延長で解釈し、
\(1\le R\le\pi/2\)、\(-1\le R_\gamma\le0\) を用いる。
直接二回微分すると
\[
-\mathcal F_{\xi\xi}=\frac{2Rw}{D}\Phi+2hR_\gamma\gamma_\xi^2,
\quad\Phi=2(\nu-\gamma\kappa)^2-\gamma^2(1-\kappa^2).
\]
射影評価から \(-1\le\Phi\le2\)、従って
\[
|\mathcal F_{\xi\xi}|\le(2\pi+2)/D.
\]
これは主報告 (2.1)、(3.1)–(3.2) に当たる。対角の2点は
\((s,\phi,\xi)=(0,0,\rho),(0,\pi,-\rho)\)。積分ではその零測度集合を除く。

平面射影 \(u=(b,y)\) は半円板 \(|u|\le R_*:=\sqrt{2m\rho},y\ge0\) で、
\(\mu\ge\mu_0=97/113\)、\(D\ge|u-(\xi,0)|\)、
\[
d\sigma=d\mu\,d\phi=dA/w= db\,dy/\mu,
\qquad\int_BD^{-1}\,d\sigma\le\pi(R_*+\rho)/\mu_0.
\]
最後の式は中心移動後の半径 \(R_e=R_*+\rho\) の半円板へ非負核を拡大したもの。
以下の式番号は主報告の番号と共通である。(3.4) は
\(K_H=(\mathcal F_\xi(\rho)-\mathcal F_\xi(-\rho))/(2\rho)=\langle\mathcal F_{\xi\xi}\rangle_\xi\)、
(3.5) は \(G(\mu)=\int_0^\pi K_H\,d\phi\)、(3.6) は外側 \(\pi\) を持つ P 単位の N3 上界である。
本補題はこの ξ 平均と広義積分の接続を担う。FT_q から (3.5) への方位角恒等式そのものは主報告 §3 の原典照合対象である。

## 独立補題の全文

**義務の区別。** predeclare v3.1 §4 の H-43-1(i) は微分と面積分の交換、(ii) は帯境界での片側極限、
Lemma V 境界値との一致、および広義積分表示である。a.e. の FTC、Tonelli、pairing だけで
これら全体を履行したとはしない。本補題は、今回指定された ξ→±rho の端点も含めて明文化する。

**主張。** `rho>0`、lambda,m,rho を固定し、`p_xi=(xi,0,lambda m)` とする。
表面積分領域 B も ξ に関して固定する。B は (0.1) の半帯、または φ を `[0,2pi)` にした全帯。
`d sigma=dmu dphi=dA/w` と置く。

1. `calF_xi(.,xi)` は ξ→rho−、ξ→−rho＋で片側トレースを持つ。非対角では通常の境界公式に一致する。
2. `j=1,2` について、境界の一点を除いて定義した密度を用いれば
   \[
   \partial_\xi^j\mathcal F(\cdot,\xi)
   \longrightarrow \partial_\xi^j\mathcal F(\cdot,\pm\rho)
   \quad\text{in }L^1(B,d\sigma).                         \tag{3.E1}
   \]
3. これらの境界積分は、P1 design note §5 の Lemma V が定める境界値の B への制限と一致する。
   表面の一致点を小球で除いた広義積分は絶対収束し、その極限は同じ値である。
4. ξ の端点を切り詰めた FTC の極限として (3.4) が成立し、表面積分とも交換できる。
5. 固定 rho>0 での外端 `mu=m-rho` の両側極限、cap 端 `mu=1` の内側極限、および
   rho→0 で縮退する帯の積分寄与は、以下の意味で連続に接続する。

**証明 A：内点での微分交換。** `|xi|<rho` なら `xi^2+m^2<1` なので p_xi は楕円体の内点。
ξ の任意のコンパクト内区間上では表面全体で D に正の下界がある。
`alpha^2` と R は gamma=1 で解析的に延長できる（P1 §3.2）。
従って固定 B の積分は二回まで ξ 微分でき、
\[
\frac{d^j}{d\xi^j}\int_B\mathcal F\,d\sigma
=\int_B\partial_\xi^j\mathcal F\,d\sigma,\qquad j=1,2.    \tag{3.E2}
\]
ここで m や rho、帯の境界を ξ と同時に動かしていない。
これは内部積分の Tonelli とは別の、微分交換の証明である。

**証明 B：一階密度のトレース。** `alpha=arccos gamma` として
\[
\mathcal F_\xi=-\lambda b\alpha^2-2hR\gamma_\xi,
\quad |\mathcal F_\xi|\le C_{\rm tr}:=\frac{\pi^2}{4}+\pi
<\frac{275}{49}.                                        \tag{3.E3}
\]
(2.1) の射影評価による `|gamma_xi|<=1/D`、`h<=wD`、`w<=1` を用いた。
各 `x!=p_+` に対して ξ→rho− で通常の公式に点ごとに収束し、反対端も同様。
(3.E3) と支配収束で j=1 の (3.E1) が従う。
対角点でさえ、**ξ の一方向に限った**トレースは明示できる：
\[
w_*:=\sqrt{m^2+L\rho^2},\quad \gamma_*:=\frac{\lambda\rho}{w_*},
\quad
\mathcal F_\xi(p_+,\rho-)=-\lambda\rho(\arccos\gamma_*)^2,
\quad
\mathcal F_\xi(p_-,-\rho+)=+\lambda\rho(\arccos\gamma_*)^2. \tag{3.E4}
\]
例えば x=p_+ では `D=rho-xi`, `h=lambda rho(rho-xi)` なので gamma は一定であり、直接微分で得られる。
**対角における密度の共同連続性は主張しない。** Lemma V も x=p を除外して積分を定義する。
従って「Lemma V と一致」とは境界積分の一致であり、対角の密度に経路非依存の値を割り当てることではない。

**証明 C：二階密度の一様可積分性。** `C_{\rm der}=2pi+2<58/7` とし (3.2) を用いる。
任意の可測集合 A⊂B の平面射影を A' とすると、`|A'|=int_A mu d sigma<=sigma(A)`。
平面の任意の可測集合 V に対して layer-cake により
\[
\int_V\frac{du}{|u-(\xi,0)|}
\le\int_0^\infty\min(|V|,\pi r^2)r^{-2}\,dr
=2\sqrt{\pi|V|}.
\]
よって
\[
\int_A|\mathcal F_{\xi\xi}|\,d\sigma
\le\frac{2C_{\rm der}\sqrt\pi}{\mu_0}\sqrt{\sigma(A)}
\le\frac{26216}{679}\sqrt{\sigma(A)},\qquad \mu_0=97/113. \tag{3.E5}
\]
定数は全パラメータ・ξ に一様。通常の境界公式への a.e. 収束と (3.E5) から j=2 の (3.E1) が従う。
これは Vitali の定理、または一致点付近の小円板を (3.E5) で一様に捨て、
その補集合で一様収束を用いる直接の切除論法で証明できる。

**証明 D：Lemma V との一致と広義積分。** P1 §5 の定義は
\[
E_\beta(p)=\frac1{4\pi\lambda}
\int_{\partial K\setminus\{p\}}\partial_p^\beta\mathcal F(x,p)\,\frac{dA}w.
\]
ξ 微分は同じ固定方向 e_x の p 微分であり、密度も測度も同一である。
全帯 B の外側は `mu<m-rho` なので、固定 rho>0 では全ての ξ に対して `D>=lambda rho`。
従って B 内では (3.E1)、B 外では通常の支配収束を使い、全表面の境界値も上記 E_beta と一致する。
原典の統治上の地位を変更せず、この接続に必要な収束をここで独立に証明した。

境界 p=p_± で一致点の半径 epsilon 小球を除くと、二階密度の除外部分の絶対積分は
`<=2pi C_{\rm der} epsilon/mu_0`（平面の半径 epsilon 円板へ拡大）。一階密度は (3.E3) で制御される。
従って球切除による広義積分は絶対収束し、(3.E1) の値と一致する。
ξ 方向も (3.2) の表面積分が一様に有限なので
\[
\int_B[\mathcal F_\xi(\rho-)-\mathcal F_\xi(-\rho+)]\,d\sigma
=\lim_{\epsilon\downarrow0}\int_{-\rho+\epsilon}^{\rho-\epsilon}
\int_B\mathcal F_{\xi\xi}\,d\sigma\,d\xi
=\int_B\int_{-\rho}^{\rho}\mathcal F_{\xi\xi}\,d\xi\,d\sigma. \tag{3.E6}
\]
したがって端点で欠損項・集中質量を加えずに (3.4)–(3.6) を使用できる。

**証明 E：帯境界。** 固定 rho>0 では `mu=m-rho` において `D>=lambda rho>0`。
その近傍でも正の下界があるため G の near 側・far 側の片側極限は同じ境界値に一致する。
cap 端 `mu=1` でも `D>=lambda(1-m)>0` なので内側極限が存在する。
これらの正の下界を rho→0 に一様なものとは主張しない。
内部の緯度 `mu=m` では (3.E3) により `|K_H|<=C_{\rm tr}/rho`（固定 rho）であり、
方位角の二点を除く収束と支配収束により G の両側極限を接続できる。
rho→0 では、ここでは B を (0.1) の半帯として、(3.2)–(3.3) から
\[
\int_{m-\rho}^1|G(\mu)|\,d\mu
\le\int_B|K_H|\,d\sigma
\le\frac{C_{\rm der}\pi R_e}{\mu_0}\longrightarrow0.              \tag{3.E7}
\]
これは縮退する **near 帯の寄与** のみを零に接続するもので、全体の H の軸端値を零とはしない。
以上で補題を証明した。∎

**契約判定との関係。** 旧 §3 の a.e. FTC だけから H-43-1 全体の履行を宣言するのは不十分だった。
追補では (3.E2) が固定母数における微分交換、(3.E1)・(3.E6)・(3.E7) が端点・帯境界・広義積分を担う。
H-43-1(i) の数学的論証は既に CHAT AUDIT で確認済みと正式指示に記載されている。
本補題は (ii) の新たな独立提出であり、その CHAT AUDIT は未了。H-43-1(ii) は OPEN のまま。
本稿が判定権限を代行するものではない。

