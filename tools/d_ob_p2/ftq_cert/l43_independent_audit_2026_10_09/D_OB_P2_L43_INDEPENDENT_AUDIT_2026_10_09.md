# D-OB P2 / FT_q — L43 独立構造監査・解析的証明

日付：2026-10-09（Asia/Tokyo）。作成：この会話の Codex。

追補版：2026-10-09。初版 commit `0c1189f9af5eb221abfc518b110e11dda345b4b0` を保存し、
Judge の案A採用と chat 数学監査 PASS（条件付き）の伝達を受けて §3.1・§7・納品記録を追記した。
Code の26検査一致は照合所見であり countersign ではない。exact スクリプトと既存出力は変更していない。

**数学的結論：訂正後の near band で Q0–Q7 に必要な局所構造と積分上界を証明した。**
本稿の新しい解析的評価は

\[
U_{43}^{N3}\le
\frac{3887073979116207}{17284813033600000}
<\frac9{40}
<\frac{187614363159}{817216000000}.
\]

Judge は本連鎖を Contract 43 の証明構造として採用した（ユーザー伝達、2026-10-09）。
chat の数学監査は条件付き PASS。Predeclare v3 の設計 PASS と v3.1 の pin 更新監査 PASS は
今回の正式指示で確認した。§3.1 の新追補、Astra exact スクリプトの CHAT AUDIT、
22″ v1.2 の正式 pin、明示的 FREEZE 裁定は別工程である。Code 証明書は未実行・実行禁止のまま。
**Contract 43 の正式台帳は OPEN、D-P2 は NOT_CERTIFIED のまま。**

## 0. 原典・訂正・監査範囲

原典の取得先は `cotaxxxx/basepoint-geometry` と `cotaxxxx/bg-oblate-spheroid`。
全ファイルの repository / path / commit / Git blob / SHA-256 / 行数は同梱 `source_manifest.json` に記録した。
追補で照合した統治文書、Code 所見、成果物ハッシュ、残存義務も同 manifest の更新版に記録した。
初版 manifest は commit `0c1189f9af5eb221abfc518b110e11dda345b4b0` に保存されている。
Code ブランチの取得時点は `a11def1e4eab235e4340fa5950899b0d4e7e3dee`。
既存の PASS 判定を新補題の証明には用いず、以下で幾何と積分評価を独立に導出する。

- N3 原本：commit `2b53e1375163fef1fca56af1bd83905948673f72`、
  Git blob `3c22bfca6ee715f3135934f819e23775d533021d`、
  SHA-256 `63bfc769c3db49d8d728d099e5efefec3e509fd4796f7926133c4ec7628508c2`。
- 記号・端点を明記した N3 改訂：commit `79588e2e9373c06aa80589a5ab7ffe1611be99d7`、
  Git blob `6a40bede832c462917f16ae024437c6c93f93b98`、
  SHA-256 `a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c`。
- 既存契約 v1.1：commit `b1a10ea6f0ef127aaf4a40a93070cf270d03e073`、
  SHA-256 `db975daba9d712246ed5e27465437f34450b356f453729a5fb78ec8ceab468cb`。
  §21″ は near band を `|mu-m|<=rho including cap` とする。
- FT_q reduction：commit `20c5c59bd74f940fe0b1e05892bd2169e09d4fde`、
  SHA-256 `46443f0e981f360e57fb70d99754b0e480042d246e22d36732b00b96102a9cd1`。
  §3–4 の方位角積分恒等式を正規化の照合に使用した。
- P1 design note および pair-scale draft は canonical snapshot
  `69e104602e939817b6f4d71df3f6bd63cbc729e0` から取得した原典を使用。
  SHA-256 はそれぞれ
  `2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9`、
  `7132b4f4ab8384da524f9f2467a6ca163a1414968adb0edd44a5014ca819700a`。
  pair-scale draft の古い算術値「41」は使用しない。

**E-43-1（依頼者訂正、2026-10-09）：** 依頼書の `[rho,max(rho,1/10)]` は Contract 45 Piece 1 であり監査対象外。
正しい baseline band は `|mu-m|<=rho`、`|xi|<=rho`。
物理領域 `-1<=mu<=1` との共通部分は

\[
\mathcal B_\rho=\{m-\rho\le\mu\le1,\ 0\le\phi\le\pi,\ |\xi|\le\rho\},
\qquad s\in[m-1,\rho].                                      \tag{0.1}
\]

`s in [-rho,rho]` だけを使って `mu>1` に延長しない。cap は全て含まれる。
`1-m=rho^2/(1+m)<=rho` により `m+rho>=1` であり、この共通部分の表示は全パラメータで成立する。
Q0「N3 の ξ 平均表式がこの帯で可積分に成立するか」を最初の前提課題とした。
**E-43-2：** 上記 `63bfc769...` は SHA-256 であって Git blob ではない。

この監査記録には「Contract 43 領域を far Piece 1 区間と誤記、E-43-1 で訂正」を記録する。
中央台帳自体は変更していない。E-43 訂正通知は「本会話からは未送付・監査側で自己適用済み」。
本報告が chat・Code に共有され、双方が本文を照合したことは今回のユーザー伝達で確認した。
これを本会話から訂正通知を直接送信した事実に置き換えない。

初版では Contract 43 predeclare 本体は未確認だった。追補では次を取得・照合した：
`tools/d_ob_p2/predeclare/CONTRACT43_NEAR_BAND_PREDECLARE_DRAFT.md`、
commit `a6479efe3d173a5952087f9bd3df67da02856fb5`、
Git blob `f25c6330b90a91f1434ca203173631f988c670da`、
SHA-256 `8fc20d790325724e88c72533aa3b6dad6efb4cd2b5b169271370c9b0ce6f6403`（144行、NOT FROZEN）。
その §5 に保存された H-43-1(i)/(ii) の義務を照合対象とし、(C1)–(C5) を新証明の前提には使わない。
さらに正式指示に従い predeclare v3.1（commit `06f5bd2b69ce94a0dbe65dc6ff9a1c7025f0bf10`）
の §4–6 を原文照合した。Git blob は `9cb0becdfb8b84ab602cb8ba83fd0d386ff24a03`。
H-43-1(ii) の現在の義務は同 §4 と今回の正式指示による。22″ v1.2 の凍結ファイルは未提示。
far 上界と設計予算は今回の比較の入力であり、その全証明を本稿で再監査したとは主張しない。

## 1. 定義と結論一覧

\[
\frac25\le\lambda\le\frac{93}{200},\quad L=\lambda^2,
\quad m^2+\rho^2=1,\quad \frac{112}{113}\le m\le1,
\quad0\le\rho\le\frac{15}{113}.
\]
\[
s=m-\mu,\quad a^2=1-\mu^2,\quad b=a\cos\phi,\quad y=a\sin\phi,
\quad w^2=\mu^2+La^2,
\]
\[
D^2=(b-\xi)^2+y^2+Ls^2,\quad h=\lambda(1-m\mu-\xi b),
\quad T=y^2+Ls^2,
\]
\[
N=\lambda\{bs[m-(1-L)s]-\xi(b^2-\rho^2-ms)\},\quad
\mathcal M=\frac{[2N^2-h^2T]_+}{wD^5}.
\]
全ての分数恒等式は `D>0` で主張する。特異点上の値を積分に影響しない任意の値で定義してよい。
FT_q の `q=b^2`, `v=D_+D_-`, paired `F` は再定義しない。
P1 の unpaired density は `calF=h(arccos gamma)^2` と明記し、微分は ξ に関し λ,m,μ,φ を固定して行う。

| 問い | 判定 | 範囲 |
|---|---|---|
| Q0 | PROVED | ξ 平均と積分の可積分性、正規化、対角の零測度処理 |
| Q1 | PROVED | 全許容領域で `|N|<=wD^2<=D^2`、D>0 |
| Q2 | PROVED | 正部分の厳密な支持条件・Gram 恒等式 |
| Q3 | PROVED | 境界一致点と cap 内部の同時極限を区別 |
| Q4 | PROVED | ρ に依存しない可積分包絡と定量的積分上界 |
| Q5 | PROVED | N3 上界量は Θ(ρ^(3/2))。実寄与の先頭係数とは区別 |
| Q6 | PROVED / CONDITIONAL | 新上界は提示された設計予算未満。正式認証は v1.2 と入力証明の採用に従属 |
| Q7 | PROVED | 解析的に一つの積分片、exact 検算コードを提出 |

## 2. 射影恒等式：N=O(D²) は全域で成立

\[
n=\frac{(\lambda b,\lambda y,\mu)}w,\qquad
e=\frac{(b-\xi,y,-\lambda s)}D.
\]
両者は単位ベクトルである。`e_x` を座標方向の単位ベクトルとして
\[
\nu=n\cdot e_x,\quad\kappa=e\cdot e_x,\quad\gamma=n\cdot e=\frac h{wD}.
\]
また
\[
\frac{2h}{\lambda}=D^2+(1-L)s^2+\rho^2-\xi^2\ge D^2,
\]
なので `0<=gamma<=1`。直接計算で
\[
\frac{N}{wD^2}=\nu-\gamma\kappa
=(n-\gamma e)\cdot(e_x-\kappa e).
\]
Cauchy–Schwarz により
\[
(\nu-\gamma\kappa)^2\le(1-\gamma^2)(1-\kappa^2)\le1,
\qquad \boxed{|N|\le wD^2\le D^2}.                         \tag{2.1}
\]
`D=0` では N=0 だが商そのものは未定義。方向に依存しない商の連続延長は主張しない。
ξ≈b でも発散しない。これは点ごとの核 `calM` が有界という主張ではない。

さらに `A_perp=mu+Ls` とすると Gram 行列の行列式から
\[
(1-\gamma^2)(1-\kappa^2)-(\nu-\gamma\kappa)^2
=\frac{A_\perp^2y^2}{w^2D^2}.                              \tag{2.2}
\]
従って
\[
\Phi=(2-3\gamma^2)(1-\kappa^2)-\frac{2A_\perp^2y^2}{w^2D^2},
\quad \mathcal M=\frac wD[\Phi]_+.                         \tag{2.3}
\]
正部分が非零なら `gamma^2<2/3` が必要。完全な必要十分条件は
`(2-3gamma^2)T > 2 A_perp^2 y^2/w^2`。
また `w^2-A_perp^2=L[rho^2+(1-L)s^2]` から
\[
2N^2-h^2T=
2LD^2\{[\rho^2+(1-L)s^2]y^2+w^2s^2\}-3h^2T.               \tag{2.4}
\]
これらは数値代入ではなく exact な多項式恒等式としても検算した。

## 3. Q0：N3 平均表式は near band で可積分に成立する

既存 N3 の微分恒等式は、D>0 なら s の符号によらず
\[
-\mathcal F_{\xi\xi}=
\frac{2Rw}{D}\Phi+2hR_\gamma\gamma_\xi^2,
\quad \gamma_\xi=\frac{\gamma\kappa-\nu}{D},
\]
であり、`1<=R<=pi/2`, `-1<=R_gamma<=0` を用いて
\[
[-\mathcal F_{\xi\xi}]_+\le\pi\mathcal M,
\qquad 0\le\mathcal M\le\frac2D.                          \tag{3.1}
\]
`|Phi|<=2`, `h<=wD<=D`, `|gamma_xi|<=1/D` でもあるので
\[
|\mathcal F_{\xi\xi}|\le\frac{2\pi+2}{D}.                 \tag{3.2}
\]

`rho>0` を固定する。帯を平面の半円板に射影すると
\[
u=(b,y),\quad |u|\le R_*=\sqrt{2m\rho},\ y\ge0,\quad
\mu=\sqrt{1-|u|^2}\ge\mu_0:=\frac{97}{113},\quad
\boxed{d\mu\,d\phi=\frac{db\,dy}{\mu}}.                   \tag{3.3}
\]
`D>=|u-(xi,0)|`。中心を `(xi,0)` に移すと半円板は半径 `R_e=R_*+rho` の半円板に含まれる。
したがって各 ξ について `int_B 1/D dmu dphi <= pi R_e/mu_0`。
これは ξ 平均後も有限であり、(3.2) により絶対可積分性と Fubini が成立する。
ξ 積分の途中で D=0 となる表面点は `(mu,phi)=(m,0),(m,pi)` のみ。
これらを除けば ξ に沿う基本定理を通常通り適用でき、除外集合は表面積測度零。

\[
K_H=\frac{\mathcal F_\xi(\rho)-\mathcal F_\xi(-\rho)}{2\rho}
=\frac1{2\rho}\int_{-\rho}^{\rho}\mathcal F_{\xi\xi}\,d\xi
\quad\text{a.e.}                                         \tag{3.4}
\]
ξ の単独偶性は仮定しない。`(xi,phi)->(-xi,pi-phi)` の対称性から、方位角積分後に
`int calF_xi(-rho)=-int calF_xi(rho)`。
FT_q の方位角部分積分恒等式と合わせると、外側係数を含む既定の G に対して
\[
G(\mu)=\int_0^\pi K_H\,d\phi.                             \tag{3.5}
\]
よって P 単位で
\[
\int_{m-\rho}^1[-G(\mu)]_+\,d\mu
\le U_{43}^{N3}:=
\pi\int_{m-\rho}^1\int_0^\pi
\underbrace{\frac1{2\rho}\int_{-\rho}^{\rho}\mathcal M\,d\xi}_{\langle\mathcal M\rangle_\xi}
\,d\phi\,d\mu.                                           \tag{3.6}
\]
正部分は平均の外から内へ Jensen の片側不等式で移す。平均の係数を落とさない。
rho=0 は帯の測度が零。平均自体は `xi=rho z`, `dz/2` として解釈し、以下の一様評価で端点に接続する。

### 3.1 独立補題 H-43-1(ii)-E：端点トレース・Lemma V 境界値・広義積分

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

## 4. ρ に依存しない点ごとの可積分包絡

`a>0, 0<phi<pi` なら
\[
\boxed{\langle\mathcal M\rangle_\xi\le
\frac4a\left[1+\log\left(1+\frac1{\sin\phi}\right)\right]}. \tag{4.1}
\]
証明：`rho/a<=1/2` なら `D>=a/2`。(3.1) で十分。
`r_0=rho/a>=1/2` なら、一次元の偶・単調減少核を区間上で積分して
\[
\left\langle\frac1D\right\rangle_\xi
\le\frac1a\frac{\operatorname{arsinh}(r_0/\sin\phi)}{r_0}
\le\frac2a\operatorname{arsinh}\frac1{2\sin\phi}
\le\frac2a\log\left(1+\frac1{\sin\phi}\right).
\]
中央の単調性は `arsinh(x)>x/sqrt(1+x^2)` から従う。
この包絡は固定領域 `[97/113,1] x [0,pi]` で可積分。
`a^{-1}=(1-mu^2)^{-1/2}` と `-log(sin phi)` はそれぞれ端点で可積分である。
端点で包絡が無限大でも零測度なので問題ない。これはまだ小さい予算を保証する定数評価ではない。

## 5. 定量的補題：曲率と線分の深さを分ける

以後 `r=|u-(xi,0)|`, `t=b-xi` とする。rho や既存の q,v とは別の局所記号である。
\[
\mu_\xi=\sqrt{1-\xi^2},\quad \ell=\mu_\xi-m\ge0,\quad
\delta=\rho^2-\xi^2=(\mu_\xi+m)\ell,
\quad 2m\ell\le\delta\le2\ell.                            \tag{5.1}
\]
球面グラフ `g(u)=sqrt(1-|u|^2)` の傾きは、半円板全体で
\[
|\nabla g|\le\frac{R_*}{m-\rho}<\frac35=:k.
\]
実際 `z=rho/m<=15/112` について
`k^2(1-z)^2-2z>0`（Bernstein 表は §8）。線分も円板内にあるため
\[
|s+\ell|=|\mu_\xi-\mu|\le kr.                             \tag{5.2}
\]
この符号は `s+ell` である。

Young の不等式で
\[
s^2\le\frac54 k^2r^2+5\ell^2=\frac9{20}r^2+5\ell^2.
\]
さらに `rho/m<=15/112` を用いて
\[
(1-L)s^2\le\frac{189}{500}r^2+\frac{21}5\ell^2
\le\frac{189}{500}r^2+\frac{\delta}{50}.                   \tag{5.3}
\]
最後は `(21/5)ell^2/delta <= (21/20)(rho/m)^2 < 1/50`。
ell=delta=0 のときも直接成立する。

また `(s+ell)^2<=k^2r^2` と `L k^2<1/12` から
\[
r^2+L\ell^2\le (1+4Lk^2)r^2+\frac43Ls^2
\le\frac43D^2,
\qquad\boxed{D^2\ge\frac34(r^2+L\ell^2)}.                \tag{5.4}
\]

核心は次の恒等式である：
\[
\frac N{D^2}=\lambda\left(\xi+\frac t2\zeta\right),\qquad
\zeta=1-\frac{(1-L)s^2+\delta}{D^2}.                       \tag{5.5}
\]
(5.3) により、`c_g=51/50` として
\[
-\frac{c_g\delta}{D^2}\le\zeta\le1.
\]
`v_g=c_g delta/D^2>=0` と置けば `|zeta|<=1+v_g`, `zeta^2<=1+v_g^2`。
平方を展開すると
\[
\frac{N^2}{D^4}\le L\left[
\xi^2+|\xi t|+\frac{t^2}4
+\frac{c_g\delta|\xi t|}{D^2}
+\frac{c_g^2\delta^2t^2}{4D^4}\right].                    \tag{5.6}
\]
従って一つの pointwise majorant が得られる：
\[
\boxed{\mathcal M\le\frac{2L}{w}\left[
\frac{\xi^2+|\xi t|+t^2/4}{D}
+\frac{c_g\delta|\xi t|}{D^3}
+\frac{c_g^2\delta^2t^2}{4D^5}\right]}.                   \tag{5.7}
\]
ここでは `-h^2T` を落としても予算内に収まる。重要なのは N の二項を無相関な定数で評価せず、
(5.5) の曲率項と深さ delta の構造を保持したことである。

## 6. 一つの積分片での閉形式上界

平面極座標を `(t,y)=(r cos(theta),r sin(theta))`, `0<=theta<=pi` とする。
実際の射影領域を `0<=r<=R_e` の半円板へ拡大する。この拡大は非負 majorant に対してのみ行う。
`R_e=R_*+rho` は幾何に由来し、可調整の分割境界は使わない。

**面積要素は (3.3) の `1/mu` を含む。**
`W(lambda)=sqrt(mu_0^2+lambda^2(1-mu_0^2))` と置く。
mu≥mu_0 より `mu*w>=mu_0 W(lambda)`。
`lambda/W(lambda)` と `lambda^2/W(lambda)` は lambda に関して増加するので
\[
\frac{\lambda^p}{\mu w}\le
\frac{\bar\lambda^p}{\mu_0W(\bar\lambda)}
<\frac{\bar\lambda^p}{\mu_0(89/100)},
\quad p=1,2,\quad\bar\lambda=\frac{93}{200}.              \tag{6.1}
\]
**`w>=89/100` を全 lambda で主張しているのではない。**
`W(bar_lambda)^2-(89/100)^2=211911/127690000>0`。

`D>=r` と半平面の角積分 `int 1=pi, int |cos theta|=2, int cos^2 theta=pi/2` より、
(5.7) の最初の三項の平面積分は
\[
\pi\xi^2R_e+|\xi|R_e^2+\frac{\pi R_e^3}{24}.
\]
ξ 平均すると
\[
\mathsf A(\rho,R_e)=\frac{\pi\rho^2R_e}{3}
+\frac{\rho R_e^2}{2}+\frac{\pi R_e^3}{24}.                \tag{6.2}
\]

交差項には (5.4) と `d_ell=lambda ell>0` を用いる：
\[
\int_0^{R_e}\frac{r^2\,dr}{(r^2+d_\ell^2)^{3/2}}
=\operatorname{arsinh}\frac{R_e}{d_\ell}
-\frac{R_e}{\sqrt{R_e^2+d_\ell^2}}
\le\log\left(1+\frac{2R_e}{d_\ell}\right).
\]
`ell>=delta/2`, `lambda>=2/5` より `d_ell>=delta/5`。
`delta log(1+10R_e/delta)` は delta に関して増加するので、
`<|xi|>=rho/2` と合わせて交差項の平均は
\[
c_g(4/3)^{3/2}\rho^3\log\left(1+\frac{10R_e}{\rho^2}\right). \tag{6.3}
\]
delta=0 では元の交差項は零。`delta log(1/delta)->0` で接続する。

最後の深さ項は
\[
\int_0^\infty\frac{r^3\,dr}{(r^2+d_\ell^2)^{5/2}}
=\frac{2}{3d_\ell}.
\]
角積分と `delta^2/ell <= 2delta`, `<delta>=2rho^2/3` を用いると
\[
\frac{\pi c_g^2(4/3)^{5/2}\rho^2}{9\lambda}.              \tag{6.4}
\]
ell=0 では元の項が零なので、除算で端点を除外してから連続極限を取ればよい。

(3.6) の外側の pi を含め、**有効なパラメータ依存上界**は
\[
U_{43}^{N3}\le
\frac{2\pi\lambda^2}{\mu_0W(\lambda)}
\left\{\mathsf A(\rho,R_e)
+c_g(4/3)^{3/2}\rho^3\log\left(1+\frac{10R_e}{\rho^2}\right)
+\frac{\pi c_g^2(4/3)^{5/2}\rho^2}{9\lambda}\right\}.      \tag{6.5}
\]

## 7. 全域の有理定数と予算比較

以下を全て exact に確認した：
\[
\rho\le r_0:=\frac{15}{113},\quad R_e\le\sqrt{2\rho}+\rho<\frac{13}{20},
\quad (4/3)^{3/2}<\frac{77}{50},\quad (4/3)^{5/2}<\frac{103}{50}.
\]
`pi<22/7` は正の積分
`int_0^1 x^4(1-x)^4/(1+x^2) dx = 22/7-pi` で証明できる。
ここでは (6.2)、外側係数、(6.4) の全ての pi に上界を適用する。

小さい rho で対数だけを 6 と抑えることはしない。
固定 `H_0=13/20` に対して
`rho^3 log(1+10H_0/rho^2)` が増加することを使用する。
\[
1+\frac{10H_0}{r_0^2}=\frac{166447}{450}
<\sum_{j=0}^{10}\frac{6^j}{j!}=\frac{67591}{175}<e^6.
\]
よって積全体を `6 r_0^3` で抑えられる。

(6.1) を使って (6.5) の lambda^2 と lambda をそれぞれ評価した結果：

| 成分 | 厳密な有理上界 |
|---|---|
| 曲率三項 | `20682286967199/152962947200000` |
| 交差項 | `4323211299/110234777000` |
| 深さ平方項 | `3014712459/59751151250` |
| 和 | `3887073979116207/17284813033600000` |

丸め余裕も exact：
\[
\frac9{40}-\frac{3887073979116207}{17284813033600000}
=\frac{2008953443793}{17284813033600000}>0.
\]
従って `U_43^N3 < 9/40`。提示された設計予算との差は
\[
B_{\rm near}-\frac9{40}
=\frac{3740763159}{817216000000}>0.                         \tag{7.1}
\]
入力として提示された far 上界と設計上の正質量を採用すれば
\[
\frac{635530452759}{817216000000}
-\frac{5481}{10000}-\frac9{40}
=\frac{3740763159}{817216000000}>0.
\]
これは **設計値との条件付き接続**。未凍結 v1.2 を凍結済みと呼ばず、c_FT を設定しない。
書面上の現行予算 `104/625` を、この新しい設計予算に黙って置換しない。
既存の上界が旧予算を超えることは、真の寄与が旧予算を超える証明でもない。

**最終余裕の薄さ。** 固定した丸め定数での余裕は
`Delta=3740763159/817216000000`（表示用近似 0.00458）であり、
`Delta/S''_lb=415640351/70614494751`、すなわち S″_lb の **0.58% より大きく 0.60% より小さい**。
南側の下界減少を epsilon_S、far と near の上界増加を epsilon_F, epsilon_N とすると、
この定数組で正の有理 gap を維持するには `epsilon_S+epsilon_F+epsilon_N<Delta` が必要である。
いずれかの入力を修正するときは和を exact に再計算する。c_FT を設定する段階でも、
この Delta とその P 単位から H 単位への換算を明記する。

## 8. Exact 証明書と再現性

新規検算コード：`l43_graph_majorant_exact.py`。
SHA-256：`6187c2b0c22d3e1b75ede72da3f470185eb6d93722b25265974ce2e01488cf18`。
実行環境：daybreak-works、Python 3.11.16、SymPy 1.14.0。
`python -I` による実行結果：**46 checks PASS、exit 0、stderr 空**。
出力原文と構造化結果を同梱する。浮動小数点による判定・数値求積・格子探索はない。
この46検査は初版の代数・積分定数に対する既存の実行記録である。
今回スクリプトを変更・再実行しておらず、新設 §3.1 は紙の解析証明として別途監査に提出する。

固定区間での Bernstein 係数は以下の通り。内部二分割も不要。

| 多項式・区間 | 全係数 | 最小 |
|---|---|---|
| `(9/25)(1-z)^2-2z`, `z in [0,15/112]` | `9/25, 249/1400, 681/313600` | `681/313600` |
| `1/12-(9/25)L`, `L in [4/25,8649/40000]` | `193/7500, 16477/3000000` | `16477/3000000` |
| `1/50-(21/20)z^2`, `z in [0,15/112]` | `1/50, 1/50, 209/179200` | `209/179200` |

コードは本文の解析を formal proof assistant で検証したものではない。
Lipschitz 評価、Cauchy–Schwarz、積分変数変換、Fubini、単調性の論理は本文を人が監査する。
コードは恒等式、平方完成、係数、原始関数、端点極限、有理算術を独立に支える。

## 9. 局所構造・反例・最終オーダー

### 9.1 外端 s=rho は固定 rho>0 で退化しない

この外端では `a^2=2m rho`。Contract 46 の幾何学的下界から
`D>=51 sqrt(rho)/100>0`。
従って「s->rho だけで距離下界が退化する」という表現は不正確。
退化は rho->0 との同時極限、または帯内部の一致点にある。
near band へ far の `D>=a-rho` を一律に移植することはしない。

### 9.2 固定 rho>0 の境界一致点

`xi=rho`, `mu=m`, `phi=0`（および反射点）で D=0。
境界 xi=rho に沿えば `h=lambda[D^2+(1-L)s^2]/2=O(D^2)` なので
`gamma=O(D)`、`N/D^2 -> lambda rho`。
この方向では `calM ~ 2L rho^2/(w D)`。表面の二次元局所積分として可積分である。
内点 ξ から近づく方向では商の極限が変わり得るが、(2.1) は全方向を被覆する。

### 9.3 一様な小ささと核の有界性は偽：exact な同時極限

`n>=8`, `tau_n=(n-1)/n` とし、既定の式で m_n,rho_n を定める。
さらに
\[
\lambda=\frac25,\quad\xi=0,\quad\phi=0,\quad
a=b=\frac{\rho_n^2}{5},\quad
\mu=\sqrt{1-\rho_n^4/25},\quad s=m_n-\mu.
\]
全て許容範囲内で、`a<rho_n` なので cap、`s in [m_n-1,0]`。
rho->0 において
\[
\frac{s}{\rho^2}\to-\frac12,\quad
\frac{D^2}{\rho^4}\to\frac{L}{2},\quad
\frac{N}{D^2}\to-\frac12,\quad
\rho^2\mathcal M\to\frac{\sqrt2}{4\lambda}=\frac{5\sqrt2}{8}>0.
\]
従って `N=o(D^2)` の全域一様主張と `calM` の一様定数上界は **DISPROVED**。
一方、求められた `N=O(D^2)` は成立し、この例はそれを否定しない。
この cap 内部の薄い層を無視して通常の一変数 Taylor 展開だけを使ってはいけない。

### 9.4 ρ→0 の総量

`R_e=sqrt(2m rho)+rho=O(sqrt(rho))` を (6.5) に戻すと
\[
U_{43}^{N3}=O(\rho^{3/2})+O(\rho^2)+O(\rho^3|\log\rho|)
=O(\rho^{3/2})                                             \tag{9.1}
\]
であり、定数は lambda の全範囲で一様である。

さらに N3 上界量自体の先頭係数も求められる。`s=rho u`, `xi=rho z`、
`u in [eta,1]`, `z in [-1,1]` とすると、eta>0 を固定したコンパクト領域で一様に
\[
\frac{\mathcal M}{\sqrt\rho}\longrightarrow
\frac{L\sqrt u}{2\sqrt2}[3\cos^2\phi-1]_+.
\]
残り `s in [m-1,eta rho]` は、§6 の同じ評価で半径を
`sqrt(rho^2+2m eta rho-eta^2 rho^2)` に変えれば、
`limsup rho^(-3/2) U_inner <= C eta^(3/2)`。
深さ項と交差項はこの尺度で零になる。
したがって eta->0 の順に極限を取り、
\[
\boxed{\frac{U_{43}^{N3}}{\rho^{3/2}}\longrightarrow
\frac{\pi L}{3\sqrt2}\left[\arccos\frac1{\sqrt3}+\sqrt2\right]>0}. \tag{9.2}
\]
`int_0^pi [3cos^2(phi)-1]_+ dphi = arccos(1/sqrt3)+sqrt2` を使用した。
この極限も lambda の閉区間で一様。
これは **N3 majorant の Θ(ρ^(3/2))** であり、実際の signed G やその負部分に同じ先頭係数を与える主張ではない。

## 10. Governance と引渡し

数学的な積分上界は **一つの near-band 積分片** で導いた。
分割境界は corrected baseline band とその幾何学的射影だけ。
点ごとの majorant は (5.7)、Bernstein 係数は §8、閉形式積分は §6、
pi 上界使用箇所と全域定数は §7、端点は §3・§6・§9 に明記した。
方式(B)の実行、格子に基づく定数選択、細分割 Riemann 上和は行っていない。
§9 の eta 分割は漸近定理の証明用で、予算証明の追加積分片ではない。

**Judge 決定の記録（ユーザー伝達、2026-10-09）：** 案A、本稿の単一片連鎖を採用。
Code の (C1)–(C5) 系統は SHELVED とし履歴を保持する。二経路並走を新たに開始しない。
Code は本文から独立証明書を実装し、Astra 側スクリプト受領後も複写しない。
Code 証明書の実行は四つの FREEZE 条件と CHAT AUDIT の明示裁定の後に限る。
設計 PASS のみでは実行許可にならない。Code の既存26検査一致は照合所見であり countersign ではない。
Code↔監査側の分解・方針・note・報告共有は正式指示で許可済み。証明書コードは相互複写しない。

**次の最小単位：** chat が新設 §3.1 を H-43-1(ii) の義務と照合して判定する。
旧 §3 の a.e. FTC と、新しい端点・帯境界の補題を区別して審査する。

FREEZE 条件1（v3 設計 PASS）は充足済み。残存条件は成果物5点の pin と exact スクリプト CHAT AUDIT、
§3.1 の独立補題確認、22″ v1.2 の完全 pin であり、FREEZE は CHAT AUDIT の明示裁定のみ。
本納品は pin を提供するが、受領だけで条件2の CHAT AUDIT や FREEZE を充足したとはしない。
これらが終わるまで c_FT は UNSET、Boundary Pair Lemma は OPEN、D-P2 は NOT_CERTIFIED。

## 11. 自己訂正と証拠の区分

監査途中の進捗コメントで、平面座標への変換に伴う `1/mu` を落とした暫定上界
`201/1000` を述べた。これは撤回した。最終証明では (3.3)、(6.1)、コードの `den=mu_lo*W_hi_parameter`
でこの因子を保持し、lambda と w の相関も保持して `9/40` を証明した。
撤回した暫定値は証明定数でも正式台帳の値でもない。

報告・コード・exact 出力・原典 manifest・訂正文を独立監査ブランチに固定する。
最終 commit と各ファイル SHA-256 は納品時の pin 表で報告する。
報告本文自体の SHA をその本文に埋め込む自己参照は行わない。
