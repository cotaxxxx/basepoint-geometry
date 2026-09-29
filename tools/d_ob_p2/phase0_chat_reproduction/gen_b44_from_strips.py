from fractions import Fraction as Q
# B positions from the audited strip output (aggregator section 6): (i_t, i_lambda) -> B i_r range
B = {}
for il in (0,5,10,15): B[(13,il)] = [14,15]
B[(14,0)] = list(range(9,16)); B[(14,5)] = list(range(9,16)); B[(14,10)] = list(range(9,16)); B[(14,15)] = list(range(10,16))
B[(15,0)] = [13,14,15]; B[(15,5)] = [14,15]; B[(15,10)] = [14,15]; B[(15,15)] = [14,15]
rows=["r\tt\tlambda_\tR\tL_lower\tstop_reason"]; n=0
f=lambda q:f"{q.numerator}/{q.denominator}"
for it in (13,14,15):
  for il in (0,5,10,15):
    for ir in range(16):
      r=Q(7,8)+Q(2*ir+1,256); t=Q(7,8)+Q(2*it+1,256); l=Q(2,5)+Q(13,3200)*Q(2*il+1,2)
      b = ir in B[(it,il)]; n+=b
      rows.append(f"{f(r)}\t{f(t)}\t{f(l)}\t1/2\t{'0.5' if b else '-0.3'}\tmax_cell_count")
open("b44_from_strips.tsv","w").write("\n".join(rows)+"\n"); print("B count", n)
