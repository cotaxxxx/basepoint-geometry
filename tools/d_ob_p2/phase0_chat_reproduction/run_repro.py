import sys, hashlib; sys.path.insert(0, "/home/user/basepoint-geometry/tools/d_ob_p2")
import phase0_b44_sign as H
H.RESULTS_SHA = hashlib.sha256(open("b44_from_strips.tsv","rb").read()).hexdigest()   # only the input pin is replaced
sys.argv = ["x","--pinned","pinned.py","--results","b44_from_strips.tsv","--out","out","--workers","4"]
raise SystemExit(H.main())
