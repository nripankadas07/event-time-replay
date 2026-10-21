import copy, unittest
from event_time_replay import analyze

def event(i,t,v=1,key='k'):return {'kind':'event','id':str(i),'timestamp':t,'key':key,'value':v}
def wm(t):return {'kind':'watermark','time':t}
def run(events,late=5,size=10,start=-100):return analyze({'size':size,'allowed_lateness':late,'initial_watermark':start,'events':events})

class ReplayTests(unittest.TestCase):
    def test_emit_correct_drop_and_evict(self):
        r=run([event(1,2,7),wm(10),event(2,3,4),wm(15),event(3,4)])
        self.assertEqual([x['sum'] for x in r['emissions']],[7,11]);self.assertEqual(r['purged'][0]['sum'],11)
        self.assertEqual([x['disposition'] for x in r['decisions']],['on_time','late','dropped']);self.assertEqual(r['remaining'],[])
    def test_negative_boundaries_keys_and_no_flush(self):
        r=run([event(1,-1),event(2,0),event(3,10,key='other')])
        self.assertEqual([x['start'] for x in r['remaining']],[-10,0,10]);self.assertEqual(r['emissions'],[])
    def test_zero_lateness_expiry_is_inclusive(self):
        r=run([event(1,0),wm(10),event(2,0)],late=0)
        self.assertEqual(len(r['emissions']),1);self.assertEqual(r['decisions'][-1]['disposition'],'dropped')
    def test_late_first_event_emits_update(self):
        r=run([wm(10),event(1,5)]);self.assertEqual(r['emissions'][0]['cause']['kind'],'late_update')
    def test_batch_oracle_and_input_preservation(self):
        events=[event(i,i-30,i%5-2,key=str(i%3)) for i in range(60)]
        data=copy.deepcopy(events);r=run(events);expected={}
        for e in events:
            key=(e['key'],e['timestamp']//10*10);expected.setdefault(key,[0,0]);expected[key][0]+=1;expected[key][1]+=e['value']
        self.assertEqual({(x['key'],x['start']):[x['count'],x['sum']] for x in r['remaining']},expected);self.assertEqual(events,data)
    def test_bad_watermark_duplicate_bool_and_unknown(self):
        for events in [[wm(2),wm(1)],[event(1,0),event(1,1)],[event(1,True)],[{'kind':'flush'}]]:
            with self.assertRaises(ValueError):run(events)

if __name__=='__main__':unittest.main()
