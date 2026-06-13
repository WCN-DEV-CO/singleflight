import threading, time
from singleflight import Group

def test_single_caller_runs():
    g=Group(); calls=[]
    def fn(): calls.append(1); return 42
    val,shared=g.do("k", fn)
    assert val==42 and shared is False and len(calls)==1

def test_concurrent_callers_share_one_execution():
    g=Group()
    runs=[]
    barrier=threading.Barrier(20)
    results=[]
    def fn():
        runs.append(1); time.sleep(0.05); return "shared-result"
    def worker():
        barrier.wait()                  # all start together
        results.append(g.do("same-key", fn))
    threads=[threading.Thread(target=worker) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(runs)==1                 # fn executed exactly ONCE
    assert all(v=="shared-result" for v,_ in results)
    assert sum(1 for _,shared in results if shared)==19   # 19 shared, 1 leader

def test_error_propagates_to_all():
    g=Group()
    barrier=threading.Barrier(5)
    errors=[]
    def fn(): time.sleep(0.02); raise ValueError("boom")
    def worker():
        barrier.wait()
        try: g.do("k", fn)
        except ValueError as e: errors.append(str(e))
    ths=[threading.Thread(target=worker) for _ in range(5)]
    for t in ths: t.start()
    for t in ths: t.join()
    assert len(errors)==5 and all(e=="boom" for e in errors)

def test_different_keys_run_independently():
    g=Group(); runs=[]
    def fn(): runs.append(1); return 1
    g.do("a", fn); g.do("b", fn)
    assert len(runs)==2

def test_sequential_calls_not_deduped():
    g=Group(); runs=[]
    def fn(): runs.append(1); return 1
    g.do("k", fn); g.do("k", fn)        # not concurrent -> both run
    assert len(runs)==2

def test_forget_allows_reexecution():
    g=Group()
    g.forget("missing")                 # no error on missing key
