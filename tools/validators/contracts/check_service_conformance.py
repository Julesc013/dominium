#!/usr/bin/env python3
"""Validate Dominium service/provider conformance contracts, registries, and fixtures."""
from __future__ import annotations
import argparse,json,re,subprocess,sys
from pathlib import Path
try:
    import tomllib
except ImportError:
    tomllib=None
SVC=Path('contracts/service/service.registry.json'); SK=Path('contracts/service/service_kind.registry.json')
SCON=Path('contracts/service/service.contract.toml'); SSCH=Path('contracts/service/service_descriptor.schema.json')
CREG=Path('contracts/conformance/conformance.registry.json'); CSTAT=Path('contracts/conformance/conformance_status.registry.json')
CCON=Path('contracts/conformance/conformance.contract.toml'); CSCH=Path('contracts/conformance/conformance_suite.schema.json')
PREG=Path('contracts/provider/provider.registry.json'); PK=Path('contracts/provider/provider_kind.registry.json')
CAP=Path('contracts/capability/capability.registry.json'); REF=Path('contracts/refusal/refusal_code.registry.json')
DIA=Path('contracts/diagnostic/diagnostic_code.registry.json'); CMD=Path('contracts/command/command_surface.contract.toml')
PUB=Path('contracts/public_surface/public_surface.contract.toml'); ART=Path('contracts/artifact/artifact_kind.registry.json')
SFIX=Path('tests/contract/service/fixtures'); CFIX=Path('tests/contract/conformance/fixtures')
J=[SSCH,SK,SVC,CSCH,CSTAT,CREG]; T={SCON:'dominium.service.contract.v1',CCON:'dominium.conformance.contract.v1'}
SRE=re.compile(r'^(domino|dominium)\.service(\.[a-z0-9][a-z0-9_.-]*)+$'); PRE=re.compile(r'^(domino|dominium)\.provider(\.[a-z0-9][a-z0-9_.-]*)+$'); CRE=re.compile(r'^dominium\.conformance\.(service|provider)(\.[a-z0-9][a-z0-9_.-]*)+$')
def j(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def _tv(v):
    v=v.strip()
    if v.startswith('\"') and v.endswith('\"'): return v[1:-1]
    if v in {'true','false'}: return v=='true'
    if v.startswith('[') and v.endswith(']'):
        inner=v[1:-1].strip()
        return [] if not inner else [_tv(x.strip()) for x in inner.split(',')]
    return v
def tl(p):
    text=p.read_text(encoding='utf-8-sig')
    if tomllib: return tomllib.loads(text)
    root={}; cur=root
    for raw in text.splitlines():
        line=raw.split('#',1)[0].strip()
        if not line: continue
        if line.startswith('[[') and line.endswith(']]'):
            key=line[2:-2].strip(); cur={}; root.setdefault(key,[]).append(cur); continue
        if line.startswith('[') and line.endswith(']'):
            cur=root
            for part in line[1:-1].split('.'):
                cur=cur.setdefault(part.strip(),{})
            continue
        if '=' in line:
            k,v=line.split('=',1); cur[k.strip()]=_tv(v)
    return root
def al(v): return v if isinstance(v,list) else ([] if v is None else [v])
def ss(v): return {x for x in al(v) if isinstance(x,str) and x}
def f(l,c,m,p=None):
    d={'level':l,'code':c,'message':m}
    if p: d['path']=p
    return d
def ids(data,key,idk='id'):
    return {str(x.get(idk)) for x in al(data.get(key)) if isinstance(x,dict) and x.get(idk)}
def vocab(root):
    d=j(root/SK); return {'k':ids(d,'kinds'),'st':ss(d.get('stability_values')),'det':ss(d.get('determinism_classes')),'auth':ss(d.get('authority_classes')),'exe':ss(d.get('execution_models')),'rep':ss(d.get('replay_impact_values'))}
def allids(root):
    return {'svc':ids(j(root/SVC),'services','service_id'),'conf':ids(j(root/CREG),'suites','conformance_id'),'prov':ids(j(root/PREG),'providers','provider_id'),'pk':ids(j(root/PK),'kinds'),'cap':ids(j(root/CAP),'capabilities','capability_id'),'ref':ids(j(root/REF),'codes','code'),'dia':ids(j(root/DIA),'codes','code'),'art':ids(j(root/ART),'kinds'),'cmd':ids(tl(root/CMD),'command'),'pub':ids(tl(root/PUB),'surface')}
def suites(root): return {str(x.get('conformance_id')):x for x in al(j(root/CREG).get('suites')) if isinstance(x,dict) and x.get('conformance_id')}
def stats(root): return {str(x.get('id')):bool(x.get('support_claim_allowed')) for x in al(j(root/CSTAT).get('statuses')) if isinstance(x,dict) and x.get('id')}
def exists(root,s):
    p=Path(s); return p.exists() if p.is_absolute() else (root/p).exists()
def pathy(s): return '/' in s or '\\' in s or ':' in s or s.lower().endswith(('.json','.toml','.py','.c','.cpp','.h','.hpp'))
def lookp(s): return '/' in s or '\\' in s or s.startswith(('contracts/','tests/'))
def contracts(root):
    out=[]
    for r in J:
        p=root/r
        if not p.exists(): out.append(f('error','missing_json_contract',f'missing JSON contract: {r}',str(r))); continue
        try:
            if not isinstance(j(p),dict): out.append(f('error','json_root_not_object',f'{r} must be a JSON object',str(r)))
        except Exception as e: out.append(f('error','invalid_json',f'{r} does not parse as JSON: {e}',str(r)))
    for r,cid in T.items():
        p=root/r
        if not p.exists(): out.append(f('error','missing_toml_contract',f'missing TOML contract: {r}',str(r))); continue
        try:
            if tl(p).get('contract',{}).get('id')!=cid: out.append(f('error','unexpected_contract_id',f'{r} has unexpected or missing contract id',str(r)))
        except Exception as e: out.append(f('error','invalid_toml',f'{r} does not parse as TOML: {e}',str(r)))
    return out
def val_service(x,path,root,I,V,S):
    out=[]; req=['service_id','service_kind','owner','version','stability','public_surface_ref','commands_exposed','result_schema_refs','refusal_code_refs','diagnostic_code_refs','capability_refs','provider_kinds_allowed','determinism_class','authority_class','artifact_inputs','artifact_outputs','replay_impact','execution_model','conformance_suite_refs','replacement_policy_ref','deprecation_policy_ref']
    for k in req:
        if k not in x or x.get(k) in (None,''): out.append(f('error','service_missing_required_field',f'service missing {k}',path))
    sid=str(x.get('service_id') or '')
    if sid and (not SRE.match(sid) or pathy(sid)): out.append(f('error','service_bad_id',f'invalid service_id: {sid}',path))
    for fld,b,c in [('service_kind','k','service_unknown_kind'),('stability','st','service_unknown_stability'),('determinism_class','det','service_unknown_determinism'),('authority_class','auth','service_unknown_authority'),('execution_model','exe','service_unknown_execution_model'),('replay_impact','rep','service_unknown_replay_impact')]:
        v=str(x.get(fld) or '')
        if v and v not in V[b]: out.append(f('error',c,f'unknown {fld}: {v}',path))
    surf=str(x.get('public_surface_ref') or '')
    if surf and I['pub'] and surf not in I['pub']: out.append(f('error','service_unknown_public_surface',f'unknown public_surface_ref: {surf}',path))
    for c in ss(al(x.get('commands_consumed'))+al(x.get('commands_exposed'))):
        if I['cmd'] and c not in I['cmd']: out.append(f('error','service_unknown_command',f'unknown command: {c}',path))
    for r in [str(i) for i in al(x.get('result_schema_refs')) if i]:
        if not exists(root,r): out.append(f('error','service_missing_result_schema',f'result schema ref does not exist: {r}',path))
    for code,b,c in [(z,'ref','service_unknown_refusal') for z in ss(x.get('refusal_code_refs'))]+[(z,'dia','service_unknown_diagnostic') for z in ss(x.get('diagnostic_code_refs'))]+[(z,'cap','service_unknown_capability') for z in ss(x.get('capability_refs'))]:
        if I[b] and code not in I[b]: out.append(f('error',c,f'unknown reference: {code}',path))
    for pk in ss(x.get('provider_kinds_allowed')):
        if I['pk'] and pk not in I['pk']: out.append(f('error','service_unknown_provider_kind',f'unknown provider kind: {pk}',path))
    for a in ss(al(x.get('artifact_inputs'))+al(x.get('artifact_outputs'))):
        if I['art'] and a not in I['art']: out.append(f('error','service_unknown_artifact_kind',f'unknown artifact kind: {a}',path))
    for k in ('replacement_policy_ref','deprecation_policy_ref'):
        r=str(x.get(k) or '')
        if r and lookp(r) and not exists(root,r): out.append(f('error','service_missing_policy_ref',f'{k} does not exist: {r}',path))
    passing=False
    for sr in [str(i) for i in al(x.get('conformance_suite_refs')) if i]:
        s=S.get(sr)
        if not s: out.append(f('error','service_unknown_conformance_suite',f'unknown conformance suite: {sr}',path)); continue
        if s.get('subject_kind')!='service' or s.get('subject_id')!=sid: out.append(f('error','service_conformance_subject_mismatch',f'conformance suite {sr} does not target {sid}',path))
        if s.get('status')=='passing' and s.get('support_claim') is True: passing=True
        elif s.get('status') in {'planned','fixture_only'}: out.append(f('warning','service_conformance_not_support',f'{sr} is {s.get("status")} and carries no support claim',path))
    if (x.get('stability')=='stable' or x.get('support_claim') is True) and not passing: out.append(f('error','service_missing_passing_conformance','stable/support service requires a passing conformance suite',path))
    return out
def val_suite(x,path,root,I,ST):
    out=[]; req=['conformance_id','subject_kind','subject_id','contract_refs','required_capabilities','required_fixtures','positive_cases','negative_cases','refusal_cases','determinism_cases','evidence_required','status']
    for k in req:
        if k not in x or x.get(k) in (None,''): out.append(f('error','conformance_missing_required_field',f'conformance suite missing {k}',path))
    cid=str(x.get('conformance_id') or ''); sk=str(x.get('subject_kind') or ''); sid=str(x.get('subject_id') or '')
    if cid and not CRE.match(cid): out.append(f('error','conformance_bad_id',f'conformance_id is invalid: {cid}',path))
    if sk not in {'service','provider'}: out.append(f('error','conformance_unknown_subject_kind',f'unknown subject_kind: {sk}',path))
    elif sk=='service' and I['svc'] and sid not in I['svc']: out.append(f('error','conformance_unknown_service_subject',f'unknown service subject: {sid}',path))
    elif sk=='provider' and I['prov'] and sid not in I['prov']: out.append(f('error','conformance_unknown_provider_subject',f'unknown provider subject: {sid}',path))
    for r in [str(i) for i in al(x.get('contract_refs')) if i]:
        if lookp(r) and not exists(root,r): out.append(f('error','conformance_missing_contract_ref',f'contract ref does not exist: {r}',path))
    for cap in ss(x.get('required_capabilities')):
        if I['cap'] and cap not in I['cap']: out.append(f('error','conformance_unknown_capability',f'unknown capability: {cap}',path))
    st=str(x.get('status') or '')
    if st not in ST: out.append(f('error','conformance_unknown_status',f'unknown conformance status: {st}',path))
    if x.get('support_claim') is True and not ST.get(st,False): out.append(f('error','conformance_support_claim_forbidden',f'{st} suites cannot carry support_claim=true',path))
    if st=='passing' and (not al(x.get('evidence_required')) or not al(x.get('positive_cases'))): out.append(f('error','passing_conformance_incomplete','passing suite requires evidence and positive cases',path))
    if st in {'planned','fixture_only'}: out.append(f('warning','conformance_not_support',f'{st} conformance does not imply runtime support',path))
    if st!='planned':
        for r in [str(i) for i in al(x.get('required_fixtures')) if i]:
            if lookp(r) and not exists(root,r): out.append(f('error','conformance_missing_fixture',f'required fixture does not exist: {r}',path))
    return out
def val_provider(x,path,I,S):
    out=[]; pid=str(x.get('provider_id') or '')
    if pid and (not PRE.match(pid) or pathy(pid)): out.append(f('error','provider_bad_id',f'provider_id is invalid: {pid}',path))
    for sid in ss(x.get('implemented_service_ids')):
        if I['svc'] and sid not in I['svc']: out.append(f('error','provider_unknown_service',f'unknown implemented service: {sid}',path))
    refs=[str(i) for i in al(x.get('conformance_suite_refs')) if i]
    if al(x.get('implemented_service_ids')) and not refs: out.append(f('error','provider_service_missing_conformance','provider implementing services requires conformance_suite_refs',path))
    passing=False
    for sr in refs:
        s=S.get(sr)
        if not s: out.append(f('error','provider_unknown_conformance_suite',f'unknown conformance suite: {sr}',path)); continue
        if s.get('subject_kind')!='provider' or s.get('subject_id')!=pid: out.append(f('error','provider_conformance_subject_mismatch',f'conformance suite {sr} does not target {pid}',path))
        if s.get('status')=='passing' and s.get('support_claim') is True: passing=True
        elif s.get('status') in {'planned','fixture_only'}: out.append(f('warning','provider_conformance_not_support',f'{sr} is {s.get("status")} and carries no support claim',path))
    for cap in ss(al(x.get('capabilities_provided'))+al(x.get('capabilities_required'))):
        if I['cap'] and cap not in I['cap']: out.append(f('error','provider_unknown_capability',f'unknown capability: {cap}',path))
    for code,b,c in [(z,'ref','provider_unknown_refusal') for z in ss(x.get('refusal_codes'))]+[(z,'dia','provider_unknown_diagnostic') for z in ss(x.get('diagnostic_codes'))]:
        if I[b] and code not in I[b]: out.append(f('error',c,f'unknown reference: {code}',path))
    if (x.get('support_claim') is True or str(x.get('stability') or '') in {'stable','available'}) and al(x.get('implemented_service_ids')) and not passing: out.append(f('error','provider_missing_passing_conformance','provider support claim requires passing conformance suite',path))
    return out
def fixture_file(root,p,I,S):
    rel=p.relative_to(root).as_posix(); x=j(p)
    if 'conformance_id' in x: return val_suite(x,rel,root,I,stats(root))
    if 'provider_id' in x: return val_provider(x,rel,I,S)
    if 'service_id' in x: return val_service(x,rel,root,I,vocab(root),S)
    return [f('error','unknown_fixture_shape','fixture is not a service, provider, or conformance suite',rel)]
def fixtures(root,I,S):
    out=[]; res=[]; paths=sorted((root/SFIX).glob('*.json'))+sorted((root/CFIX).glob('*.json')); valid=invalid=0
    if not paths: return [f('error','fixture_set_missing','service/conformance fixture set is missing')], {'status':'fail','fixture_count':0,'valid':0,'invalid':0,'fixtures':[]}
    for p in paths:
        rel=p.relative_to(root).as_posix(); bad=p.name.startswith('invalid_'); invalid+=1 if bad else 0; valid+=0 if bad else 1
        try: ff=fixture_file(root,p,I,S)
        except Exception as e: ff=[f('error','fixture_parse_or_validation_failed',f'fixture failed: {e}',rel)]
        errs=[x for x in ff if x['level']=='error']; ok=bool(errs) if bad else not errs
        if not ok: out.append(f('error','fixture_expectation_failed',f'fixture expectation failed for {rel}',rel))
        res.append({'path':rel,'fixture':rel,'expected':'invalid' if bad else 'valid','status':'pass' if ok else 'fail','errors':len(errs),'warnings':sum(1 for x in ff if x['level']=='warning'),'findings':ff})
    if not valid or not invalid: out.append(f('error','fixture_set_incomplete','service/conformance fixtures must include valid and invalid cases'))
    return out, {'status':'pass' if not out else 'fail','fixture_count':len(res),'valid':valid,'invalid':invalid,'fixtures':res}
def git_files(root):
    out=[]
    for a in (['git','ls-files'],['git','ls-files','--others','--exclude-standard']):
        try: out += [x.strip().replace('\\','/') for x in subprocess.run(a,cwd=str(root),check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.splitlines() if x.strip()]
        except Exception: pass
    return sorted(set(out))
def inv(root):
    counts={}; examples={}
    for p in git_files(root):
        l=p.lower(); cat=None
        for pre,c in [('contracts/service/','service_contract_surface'),('contracts/conformance/','conformance_contract_surface'),('contracts/provider/','provider_relationship_surface'),('contracts/capability/','capability_relationship_surface'),('tests/contract/service/','service_fixture'),('tests/contract/conformance/','conformance_fixture'),('runtime/','runtime_read_only_candidate'),('apps/workbench/','workbench_consumer_candidate')]:
            if l.startswith(pre): cat=c; break
        if cat is None and any(w in l for w in ('service','provider','conformance')): cat='deferred_service_provider_candidate'
        if cat: counts[cat]=counts.get(cat,0)+1; examples.setdefault(cat,[]); examples[cat]=examples[cat][:8]+([p] if len(examples[cat])<8 else [])
    return {'status':'warning','files_scanned':len(git_files(root)),'categories':counts,'examples':examples,'note':'Inventory is descriptive only; SERVICE-CONFORMANCE-LAW-01 does not implement runtime services or providers.'}
def validate_all(root,include_fixtures=False,include_inventory=False):
    fs=contracts(root); sc=cc=0; fx={'status':'not_run','fixture_count':0,'valid':0,'invalid':0,'fixtures':[]}
    if not any(x['level']=='error' for x in fs):
        try:
            I=allids(root); S=suites(root); V=vocab(root); ST=stats(root)
            sv=[x for x in al(j(root/SVC).get('services')) if isinstance(x,dict)]; co=[x for x in al(j(root/CREG).get('suites')) if isinstance(x,dict)]; sc=len(sv); cc=len(co)
            seen=set()
            for n,x in enumerate(sv):
                sid=str(x.get('service_id') or '')
                if sid in seen: fs.append(f('error','service_duplicate_id',f'duplicate service_id: {sid}',str(SVC)))
                seen.add(sid); fs += val_service(x,f'{SVC.as_posix()}#{n}',root,I,V,S)
            seen=set()
            for n,x in enumerate(co):
                cid=str(x.get('conformance_id') or '')
                if cid in seen: fs.append(f('error','conformance_duplicate_id',f'duplicate conformance_id: {cid}',str(CREG)))
                seen.add(cid); fs += val_suite(x,f'{CREG.as_posix()}#{n}',root,I,ST)
            for n,x in enumerate(al(j(root/PREG).get('providers'))):
                if isinstance(x,dict): fs += val_provider(x,f'{PREG.as_posix()}#{n}',I,S)
            if include_fixtures:
                ffs,fx=fixtures(root,I,S); fs += ffs
        except Exception as e: fs.append(f('error','validator_exception',f'service conformance validation failed: {e}'))
    errs=[x for x in fs if x['level']=='error']; warns=[x for x in fs if x['level']=='warning']
    return {'validator':'check_service_conformance','status':'pass' if not errs else 'fail','services_registered':sc,'conformance_suites_registered':cc,'summary':{'errors':len(errs),'warnings':len(warns)},'findings':fs,'fixtures':fx,'inventory':inv(root) if include_inventory else {'status':'not_run'},'runtime_implemented':False,'provider_runtime_loading_implemented':False}
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--repo-root',default='.'); ap.add_argument('--strict',action='store_true'); ap.add_argument('--json',action='store_true'); ap.add_argument('--fixtures',action='store_true'); ap.add_argument('--inventory',action='store_true'); ap.add_argument('--list-classes',action='store_true'); a=ap.parse_args(argv); root=Path(a.repo_root).resolve()
    if a.list_classes:
        for k in sorted(ids(j(root/SK),'kinds')): print(k)
        return 0
    r=validate_all(root,include_fixtures=a.fixtures or a.strict,include_inventory=a.inventory)
    if a.json: print(json.dumps(r,indent=2,sort_keys=True))
    else:
        print(f"service conformance: {r['status']}"); print(f"services: {r['services_registered']}"); print(f"conformance_suites: {r['conformance_suites_registered']}"); print(f"errors: {r['summary']['errors']}"); print(f"warnings: {r['summary']['warnings']}")
        if r['fixtures']['status']!='not_run': print(f"fixtures: {r['fixtures']['status']} count={r['fixtures']['fixture_count']} valid={r['fixtures']['valid']} invalid={r['fixtures']['invalid']}")
        if r['inventory']['status']!='not_run':
            print(f"inventory: {r['inventory']['status']} files_scanned={r['inventory']['files_scanned']}")
            [print(f"- {k}: {v}") for k,v in sorted(r['inventory']['categories'].items())]
        for item in r['findings']:
            p=f"{item.get('path')}: " if item.get('path') else ''; print(f"{item['level']}: {p}{item['code']}: {item['message']}")
    return 1 if a.strict and r['status']!='pass' else 0
if __name__=='__main__': sys.exit(main())
