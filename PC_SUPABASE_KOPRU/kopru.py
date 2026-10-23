"""SS OIL PC <-> Supabase event bridge, standard library only.
Does not edit or import the PC server or its SQLite file.
Requires a compatible /shared GET+POST endpoint and token.
"""
import json, os, sqlite3, time, uuid, urllib.request, urllib.parse, urllib.error, logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

BASE=os.environ.get('SSOIL_PC_URL','http://127.0.0.1:8767').rstrip('/')
TOKEN=os.environ.get('SSOIL_PC_TOKEN','')
SUPA=os.environ.get('SSOIL_SUPABASE_URL','').rstrip('/')
KEY=os.environ.get('SSOIL_SERVICE_ROLE_KEY','')
DB=Path(__file__).with_name('kopru_durum.sqlite3')
SECTIONS={'labels','orders','suppliers','supplierOf','minimum','discrepancies','orderUnits','barcodeErrors','photos'}
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

def req(url, method='GET', payload=None, headers=None):
    body=None if payload is None else json.dumps(payload,ensure_ascii=False).encode('utf-8')
    request=urllib.request.Request(url,data=body,method=method,headers=headers or {})
    with urllib.request.urlopen(request,timeout=8) as r:
        data=r.read()
        return json.loads(data) if data else None

def pc(path,method='GET',payload=None):
    return req(BASE+path,method,payload,{'X-SSOIL-Token':TOKEN,'Content-Type':'application/json'})

def cloud(path,method='GET',payload=None):
    return req(SUPA+'/rest/v1/'+path,method,payload,{
        'apikey':KEY,'Authorization':'Bearer '+KEY,'Content-Type':'application/json',
        'Prefer':'resolution=merge-duplicates,return=minimal'})

def getstate(db,key):
    row=db.execute('select v from state where k=?',(key,)).fetchone()
    return int(row[0]) if row else 0

def setstate(db,key,value):
    db.execute('insert into state(k,v) values(?,?) on conflict(k) do update set v=excluded.v',(key,str(value)))

# Each source is refreshed every cycle (nominally 3 seconds).
# Network calls run concurrently, and a slow snapshot does not delay others.
_snapshot_pool=ThreadPoolExecutor(max_workers=4)
_snapshot_pending={}

def _publish_snapshot(kind,path):
    value=pc(path)
    if not isinstance(value,dict):
        raise ValueError('Unexpected snapshot payload')
    if kind.startswith('kasa') and not all(k in value for k in ('cash','card')):
        raise ValueError('Kasa missing cash/card')
    cloud('ssoil_snapshots?on_conflict=kind','POST',[{'kind':kind,'data':value}])

def snapshots():
    bosnia_day=datetime.now(ZoneInfo('Europe/Sarajevo')).date().isoformat()
    tasks=[('kasa-date-'+bosnia_day,'/kasa?date='+bosnia_day),
           ('daily-sales','/daily-sales'),('sales','/sales'),
           ('products','/snapshot')]
    for kind,path in tasks:
        future=_snapshot_pending.get(kind)
        if future is not None and not future.done():
            continue
        if future is not None:
            try: future.result()
            except Exception as exc: logging.warning('Snapshot %s skipped: %s',kind,exc)
        _snapshot_pending[kind]=_snapshot_pool.submit(_publish_snapshot,kind,path)

def sync(db):
    # Pull remote commands first; each event has a stable ID for retry-safe PC writes.
    last=getstate(db,'cloud_id')
    path='ssoil_events?select=id,event_id,section,item_key,value&id=gt.'+str(last)+'&order=id.asc&limit=200'
    for event in cloud(path) or []:
        eid=event['event_id']; sec=event['section']
        if str(eid).startswith('pc-'):
            setstate(db,'cloud_id',event['id']); db.commit()
            last=event['id']
            continue
        if sec not in SECTIONS: raise RuntimeError('Unsupported section '+sec)
        result=pc('/shared','POST',{'section':sec,'key':event['item_key'],'value':event['value'],'event_id':eid})
        revision=result['revision']
        # PC change feed includes this event: don't send it back as a second cloud event.
        db.execute('insert or ignore into skip_revision(rev) values(?)',(revision,))
        setstate(db,'cloud_id',event['id']); db.commit()
        last=event['id']
    # Publish local PC changes. Do not advance cursor until cloud confirms write.
    cursor=getstate(db,'pc_rev')
    result=pc('/shared?since='+str(cursor))
    for item in result.get('changes',[]):
        rev=int(item['revision'])
        if item['section'] not in SECTIONS:
            raise RuntimeError('Unsupported section '+str(item['section']))
        if not db.execute('select 1 from skip_revision where rev=?',(rev,)).fetchone():
            cloud('ssoil_events?on_conflict=event_id','POST',[{
                'event_id':'pc-'+str(rev),'section':item['section'],
                'item_key':item['key'],'value':item.get('value')}])
        setstate(db,'pc_rev',rev)
        db.execute('delete from skip_revision where rev=?',(rev,))
        db.commit()
    # No cursor jumps: /shared returns max revision even if there are >2000 events.
    snapshots()


def main():
    if not all([TOKEN,SUPA,KEY]):
        raise SystemExit('Missing SSOIL_PC_TOKEN / SSOIL_SUPABASE_URL / SSOIL_SERVICE_ROLE_KEY')
    if not SUPA.startswith('https://'):
        raise SystemExit('Supabase URL must be HTTPS')
    with sqlite3.connect(DB) as db:
        db.execute('create table if not exists state(k text primary key,v text not null)')
        db.execute('create table if not exists skip_revision(rev integer primary key)')
        db.commit()
        while True:
            try: sync(db)
            except Exception as exc: logging.error('Sync failed (will retry): %s',exc)
            time.sleep(3)

if __name__=='__main__': main()
