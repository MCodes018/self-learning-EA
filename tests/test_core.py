from ea.autonomy import choose_autonomy_mode
from ea.connectors.demo import DemoSource
from ea.context import ContextStore
from ea.policy import HeuristicPolicy

def test_shadow_never_acts(): assert choose_autonomy_mode(.99,.01,True)=='propose'
def test_low_confidence_asks(): assert choose_autonomy_mode(.5,.1,False)=='ask'
def test_policy():
    c=ContextStore('user_001'); i=DemoSource().fetch(1)[0]; d=HeuristicPolicy().decide(i,c.company(),c.user(),True)
    assert d.priority=='high' and d.autonomy_mode=='propose'
