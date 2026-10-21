import argparse, json, pathlib, sys

def need(ok, message):
    if not ok: raise ValueError(message)

def integer(x, label, minimum=None):
    need(type(x) is int and abs(x) <= 10**15, label + " must be a bounded integer")
    need(minimum is None or x >= minimum, label + " below minimum")
    return x

def ident(x):
    need(isinstance(x,str) and 0 < len(x) <= 128, "expected nonempty identifier <=128 characters")
    return x

def fields(x, required, optional=()):
    need(type(x) is dict and set(required)<=set(x)<=set(required)|set(optional), "invalid object fields")

def pairs(items):
    out={}
    for k,v in items:
        need(k not in out, "duplicate JSON key")
        out[k]=v
    return out

def load(path):
    with pathlib.Path(path).open('rb') as handle: raw=handle.read(1048577)
    need(len(raw)<=1048576,"input exceeds 1 MiB")
    def bad(x): raise ValueError("nonfinite JSON number")
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=bad)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='UTF-8 JSON input; read only')
    args=parser.parse_args()
    try:
        result=analyze(load(args.input))
        print(json.dumps(result,ensure_ascii=True,indent=2,allow_nan=False))
        return 1 if result.get('findings') else 0
    except (ValueError,OSError,RecursionError,OverflowError) as exc:
        print(str(exc),file=sys.stderr);return 2

def analyze(data):
    fields(data, ['size','allowed_lateness','initial_watermark','events'])
    size=integer(data['size'],'size',1)
    lateness=integer(data['allowed_lateness'],'allowed_lateness',0)
    watermark=integer(data['initial_watermark'],'initial_watermark')
    need(type(data['events']) is list and len(data['events'])<=5000,'events must be a list <=5000')
    windows={}; seen=set(); decisions=[]; emissions=[]; purged=[]
    def snapshot(key, state, cause):
        return {'key':key[0],'start':key[1],'end':key[1]+size,'count':state['count'],'sum':state['sum'],'cause':cause}
    for index,event in enumerate(data['events']):
        need(type(event) is dict,'event must be an object')
        if event.get('kind')=='watermark':
            fields(event,['kind','time'])
            value=integer(event['time'],'watermark')
            need(value>=watermark,'watermarks must be monotonic')
            watermark=value
            for key in sorted(windows):
                state=windows[key];end=key[1]+size
                if end<=watermark and not state['emitted']:
                    emissions.append(snapshot(key,state,{'kind':'on_time','index':index}));state['emitted']=True
                if watermark>=end+lateness:
                    purged.append(snapshot(key,state,{'kind':'purge','index':index}));del windows[key]
        elif event.get('kind')=='event':
            fields(event,['kind','id','timestamp','key','value'])
            eid=ident(event['id']);need(eid not in seen,'duplicate event id');seen.add(eid)
            stamp=integer(event['timestamp'],'timestamp');key=(ident(event['key']),stamp//size*size)
            value=integer(event['value'],'value');end=key[1]+size
            disposition='dropped' if watermark>=end+lateness else ('late' if stamp<watermark else 'on_time')
            decisions.append({'id':eid,'index':index,'watermark':watermark,'window':[key[1],end],'disposition':disposition})
            if disposition=='dropped':continue
            state=windows.setdefault(key,{'count':0,'sum':0,'emitted':False})
            state['count']+=1;state['sum']+=value
            if end<=watermark:
                emissions.append(snapshot(key,state,{'kind':'late_update','index':index}));state['emitted']=True
        else:raise ValueError('unsupported event kind')
    return {'watermark':watermark,'decisions':decisions,'emissions':emissions,'purged':purged,
            'remaining':[snapshot(k,windows[k],{'kind':'remaining'}) for k in sorted(windows)],
            'policy':'integer tumbling windows; expiry is watermark >= end + allowed_lateness; no implicit flush'}

if __name__=='__main__':sys.exit(main())
