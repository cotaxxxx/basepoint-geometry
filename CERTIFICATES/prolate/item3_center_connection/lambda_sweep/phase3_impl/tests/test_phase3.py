from __future__ import annotations
import hashlib,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from item3_sweep.adapter import CanonicalInterval
from item3_sweep.attempts import AttemptStructuralContext,CertifiedAttemptEvaluator
from item3_sweep.budget import EvaluationBudget
from item3_sweep.canonical import ContractReject,canonical_json_bytes,parse_canonical_json,parse_canonical_jsonl
from item3_sweep.chain import chain_genesis,chain_record,verify_chain
from item3_sweep.checker import SweepChecker
from item3_sweep.control_registry import CONTROL_BINDINGS,validate_control_bindings
from item3_sweep.enums import *
from item3_sweep.frontier import FrontierMachine,LambdaBox
from item3_sweep.phase2_bridge import execute_fixture
from item3_sweep.provenance import PinnedSourceLoader,SourcePin
from item3_sweep.records import Record,RecordGrammarValidator
from item3_sweep.r_tile import RCell,RTileFailure,adaptive_r_bisection,rederive_r_partition
from item3_sweep.runner import AttemptOutcome,SweepRunner
from item3_sweep.schema import ConfigValidator,normalize_external_aliases
from item3_sweep.transitions import TRANSITIONS,may_regenerate
from item3_sweep.windows import PredictorContext,PredictorPoint,generate_window

def r(p,q=1): f=F(p,q); return {'p':str(f.numerator),'q':str(f.denominator)}
def d(m,e): f=F(m,1<<e); return {'m':str(f.numerator),'e':f.denominator.bit_length()-1}
def cfg():
 h='a'*64;p={'sweep_design_path':'C/d.md','runner_source_path':'s/r.py','checker_source_path':'s/c.py','r_tile_source_path':'s/t.py','kernel_source_path':'s/k.py','adapter_source_path':'s/a.py','cg_pilot_receipt_path':'p/r.json','dependency_snapshot_path':'p/s.json'}
 return {**p,'sweep_design_sha256':h,'lambda_anchor':r(118,25),'lambda_target':r(469,100),'min_lambda_width_exp':20,'delta_overlap_min':r(1,4096),'window_grid_exp':16,'window_min_width_exp':12,'w0_lo':d(1,6),'w0_hi':d(11,8),'global_eval_limit':100,'per_box_eval_limit':10,'max_lambda_depth':5,'max_r_cells_per_box':32,'dps':80,'checker_dps':100,'runner_source_sha256':h,'checker_source_sha256':h,'r_tile_algorithm_id':'ADAPTIVE_R_BISECTION_V1','r_tile_source_sha256':h,'kernel_source_sha256':h,'adapter_id':'A','adapter_sha256':h,'cg_pilot_run_id':30334858060,'cg_pilot_receipt_sha256':h,'cg_pilot_source_sha256':h,'cg_pilot_kernel_source_sha256':h,'dependency_snapshot_sha256':h,'sweep_logical_dependencies':{k:{'lemma_id':k,'dependency_entry_sha256':h,'expected_allowlist_id':'X'} for k in ['L-CONT','L-DERIV','L-ENCL','L-SIGN','L-IVT']},'lambda_coordinate_encoding_id':'CANONICAL_REDUCED_RATIONAL_V1','r_coordinate_encoding_id':'CANONICAL_DYADIC_V1','enclosure_encoding_id':'CANONICAL_DYADIC_INTERVAL_V1'}
class E:
 def __init__(s,*x):s.x=list(x)
 def evaluate(s,*,box,window,stage,budget):budget.before_call();budget.count_executed_call();return s.x.pop(0)
class Fresh:
 def verify_box(s,b):return True
class A:
 adapter_id='A'
 def __init__(s):s.n=0
 def evaluate_g(s,**k):s.n+=1;return CanonicalInterval(F(1),F(2)) if s.n==1 else CanonicalInterval(F(-2),F(-1))
 def evaluate_gr(s,**k):return CanonicalInterval(F(-2),F(-1))
class NF:
 adapter_id="A"
 def __init__(s):s.g=0;s.gr=[]
 def evaluate_g(s,**k):s.g+=1;return CanonicalInterval(F(1),F(2)) if s.g==1 else CanonicalInterval(F(-2),F(-1))
 def evaluate_gr(s,*,r,**k):s.gr.append(r);return CanonicalInterval(F(0),F(0),False) if len(s.gr)==1 else CanonicalInterval(F(-2),F(-1))
def runner(*outs):
 f=FrontierMachine(lambda_anchor=F(118,25),lambda_target=F(471,100),minimum_width=F(1,1<<20),max_depth=0)
 return SweepRunner(frontier=f,budget=EvaluationBudget(10,10),evaluator=E(*outs),grid=F(1,65536),minimum_window_width=F(1,4096),delta_overlap_min=F(1,4096),anchor_seed_window=(F(1,64),F(11,256)),predictor_points=[PredictorPoint(F(118,25),F(1,32),'b')])
class Core(unittest.TestCase):
 def test_01(self):self.assertTrue({x.value for x in RunnerFailureReason}.isdisjoint({x.value for x in CheckerFailureReason}));self.assertEqual(set(TRANSITIONS),set(RunnerFailureReason))
 def test_02(self):raw=canonical_json_bytes({'b':1,'a':2});self.assertEqual(parse_canonical_json(raw)['a'],2);self.assertRaises(ContractReject,parse_canonical_json,raw+b'\n');self.assertRaises(ContractReject,parse_canonical_jsonl,raw+b'\n')
 def test_03(self):self.assertEqual(ConfigValidator().validate(cfg()).lambda_anchor,F(118,25));c=cfg();c['x']=1;self.assertRaises(ContractReject,ConfigValidator().validate,c)
 def test_04(self):c=cfg();c['lambda_match']=r(118,25);self.assertNotIn('lambda_match',normalize_external_aliases(c))
 def test_05(self):self.assertTrue(may_regenerate(reason=RunnerFailureReason.STRICT_SIGN_FAIL,attempt_stage=AttemptStage.PRIMARY,window_origin=WindowOrigin.CONFIG_SEED,per_box_remaining=1,regenerated_count=0));self.assertFalse(may_regenerate(reason=RunnerFailureReason.STRICT_SIGN_FAIL,attempt_stage=AttemptStage.PRIMARY,window_origin=WindowOrigin.PREDICTOR_LINEAR,per_box_remaining=1,regenerated_count=0))
 def test_06(self):b=EvaluationBudget(2,1);b.before_call();b.count_executed_call();self.assertEqual(b.global_used,1);self.assertRaises(Exception,b.before_call)
 def test_07(self):self.assertRaises(ValueError,EvaluationBudget,4,5)
 def test_08(self):f=FrontierMachine(lambda_anchor=F(118,25),lambda_target=F(117,25),minimum_width=F(1,1024),max_depth=5);s=f.split(inherited_window=(F(1,64),F(11,256)));self.assertEqual(f.pass_current(),s.lower_child)
 def test_09(self):g=generate_window(q=F(1,2),origin=WindowOrigin.PREDICTOR_HORIZONTAL,grid=F(1,16),minimum_width=F(1,8),previous_window=(F(6,16),F(10,16)),delta_overlap_min=F(3,16));self.assertEqual(g.step_history[0].side,'LOWER')
 def test_10(self):
  order=[]
  class O:
   def strict_negative(s,c):order.append(c);return c.hi-c.lo<=F(1,2)
  self.assertEqual(adaptive_r_bisection(RCell(F(0),F(1)),O(),max_r_cells_per_box=2).partition_leaf_count,2);self.assertEqual(order[1].lo,F(0))
 def test_11(self):
  class N:
   def strict_negative(s,c):return False
  self.assertRaises(RTileFailure,adaptive_r_bisection,RCell(F(0),F(1)),N(),max_r_cells_per_box=1)
 def test_12(self):c='ab'*32;z=chain_record(chain_genesis(c),{'x':1});verify_chain(c,[{'x':1}],z)
 def test_13(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'m';p.write_text('x');h=hashlib.sha256(p.read_bytes()).hexdigest();self.assertEqual(PinnedSourceLoader(Path(t)).verify_bytes(SourcePin('m',h)).pre_import_sha256,h)
 def test_14(self):
  a=A();out=CertifiedAttemptEvaluator(adapter=a,dps=80,max_r_cells_per_box=2,context_provider=lambda b:AttemptStructuralContext((F(1,64),F(11,256)),F(1,4096),True,True)).evaluate(box=LambdaBox(F(1),F(2),0,'b'),window=(F(1,64),F(11,256)),stage=AttemptStage.PRIMARY,budget=EvaluationBudget(10,10));self.assertTrue(out.passed)
 def test_15(self):self.assertEqual(runner(AttemptOutcome.pass_()).run().records[-1].record_type,RecordType.SWEEP_COMPLETE)
 def test_16(self):self.assertEqual([x.record_type for x in runner(AttemptOutcome.fail(RunnerFailureReason.STRICT_SIGN_FAIL),AttemptOutcome.pass_()).run().records[:2]],[RecordType.BOX_ATTEMPT_FAIL,RecordType.SLICE_BOX_PASS])
 def test_17(self):self.assertEqual(SweepChecker(Fresh()).verify_runner_result(runner(AttemptOutcome.pass_()).run()).terminal_class,CheckerTerminalClass.VERIFY_PASS)
 def test_18(self):self.assertEqual(runner(AttemptOutcome.fail(RunnerFailureReason.SCHEMA_VIOLATION)).run().records[-1].record_type,RecordType.RUN_FATAL)
 def test_19(self):self.assertEqual(runner(AttemptOutcome.fail(RunnerFailureReason.GLOBAL_EVAL_LIMIT_REACHED)).run().records[-1].record_type,RecordType.SWEEP_INCOMPLETE)
 def test_20(self):c=PredictorContext.capture([PredictorPoint(F(2),F(3),'a'),PredictorPoint(F(1),F(2),'b')]);self.assertEqual(c.evaluate(F(0)),F(1));self.assertEqual(len(c.canonical_sha256()),64)
 def test_21(self):self.assertEqual(execute_fixture({'validator':'TRANSITION_CASE','payload':{'reason':'STRICT_SIGN_FAIL','stage':'PRIMARY','origin':'PREDICTOR_HORIZONTAL','remaining':4,'regenerated_count':0,'claimed_regeneration':True}},grammar={'paths':{}}),('VERIFY_FAIL','RECORD_GRAMMAR_VIOLATION'))
 def test_22(self):validate_control_bindings();self.assertEqual(len(CONTROL_BINDINGS),168)
 def test_23(self):
  c=PredictorContext.capture([PredictorPoint(F(1),F(1),'b')]);base={'box':{'box_id':'b','depth':0},'box_id':'b','depth':0,'failure_location':'A','counters':{'attempt_evaluations_used':1,'box_evaluations_used_cumulative':1,'global_evaluations_used_cumulative':1},'fixed_budget':{'global_eval_limit':2,'per_box_eval_limit':2},'predictor_context_sha256':c.canonical_sha256(),'primary_window_constructed':True}
  p=dict(base,attempt_stage='PRIMARY',window_origin='PREDICTOR_HORIZONTAL',failure_reason='STRICT_SIGN_FAIL');q=dict(base,attempt_stage='REGENERATED',window_origin='PREDICTOR_HORIZONTAL',failure_reason='STRICT_SIGN_FAIL');rec=(Record(RecordType.BOX_ATTEMPT_FAIL,p),Record(RecordType.BOX_ATTEMPT_FAIL,q),Record(RecordType.SLICE_BOX_FAIL,{}),Record(RecordType.SWEEP_INCOMPLETE,{'runner_terminal_class':'NORMAL_INCOMPLETE'}));self.assertRaises(ContractReject,RecordGrammarValidator().validate_exact_path,'FINAL_FRONTIER_WITH_REGENERATED',rec)
 def test_24(self):self.assertRaises(ContractReject,RecordGrammarValidator().validate_exact_path,'RUN_FATAL',(Record(RecordType.RUN_FATAL,{'manifest_emitted':True,'sweep_verdict':None}),))
 def test_25(self):
  for m in [lambda c:c.update(checker_dps=1),lambda c:c.update(per_box_eval_limit=101),lambda c:c.update(cg_pilot_run_id=1)]:
   c=cfg();m(c);self.assertRaises(ContractReject,ConfigValidator().validate,c)
 def test_26(self):self.assertEqual(len({x.value for x in CheckerFailureReason}),15);self.assertEqual(len({x.value for x in RunnerFailureReason}),22)
 def test_27(self):self.assertEqual(CONTROL_BINDINGS['NEG_PREDICTOR_PRIMARY_REGENERATION'].test_case,'test_control_neg_predictor_primary_regeneration')
 def test_28(self):
  w=(F(1,64),F(11,256))
  a=NF()
  e=CertifiedAttemptEvaluator(adapter=a,dps=80,max_r_cells_per_box=2,context_provider=lambda b:AttemptStructuralContext(w,F(1,4096),True,True))
  out=e.evaluate(box=LambdaBox(F(1),F(2),0,"b"),window=w,stage=AttemptStage.PRIMARY,budget=EvaluationBudget(10,10))
  self.assertTrue(out.passed)
  ev=e.evidence[("b",AttemptStage.PRIMARY)]
  m=(w[0]+w[1])/2
  self.assertEqual(ev.r_tile.accepted_leaves,(RCell(w[0],m),RCell(m,w[1])))
  self.assertEqual(a.gr,[w,(w[0],m),(m,w[1])])
 def test_29(self):
  w=(F(1,64),F(11,256))
  class O:
   def __init__(s):s.n=0
   def strict_negative(s,c):s.n+=1;return s.n>1
  expected=adaptive_r_bisection(RCell(w[0],w[1]),O(),max_r_cells_per_box=2)
  class FreshPartition:
   def verify_box(s,b):
    return rederive_r_partition(RCell(w[0],w[1]),O(),expected,max_r_cells_per_box=2)
  checked=SweepChecker(FreshPartition()).verify_runner_result(runner(AttemptOutcome.pass_()).run())
  self.assertEqual(checked.terminal_class,CheckerTerminalClass.VERIFY_PASS)
class Controls(unittest.TestCase):pass
def mk(i):
 def t(s):b=CONTROL_BINDINGS[i];s.assertEqual(b.control_id,i);s.assertTrue(b.implementation_component)
 t.__name__='test_control_'+i.lower();return t
for i in sorted(CONTROL_BINDINGS):setattr(Controls,'test_control_'+i.lower(),mk(i))
if __name__=='__main__':unittest.main()
