#!/usr/bin/env python3
"""Read-only evidence checks and new, explicitly exploratory caption/tie analyses.

Usage:
  python analisi_riscontro.py --export FULL_EXPERIMENT_EXPORT_ARCH300_20261001-134634.zip \
      --inputs /path/to/report_csvs --out /path/to/results --bootstrap 3000

Original data, training and manuscript are never overwritten. No raw participant data
are exported. Required inputs: export zip, triplet_transfer.csv, source_affinity.csv,
results.csv, and caption_lexicon_v1.json (next to this script).
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, sys, unicodedata, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import scipy
from scipy import stats, optimize, special


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def csv_out(out: Path, name: str, rows: list[dict], fields=None):
    if not rows and fields is None:
        raise ValueError(f'Empty output without explicit fields: {name}')
    fields = list(rows[0]) if fields is None else fields
    with (out/name).open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='raise')
        w.writeheader();w.writerows(rows)


def corr(x, y):
    x,y=np.array(x,float),np.array(y,float)
    if len(x)<3 or np.ptp(x)==0 or np.ptp(y)==0:
        return None
    return float(stats.pearsonr(x,y).statistic)


def norm_text(s: str) -> str:
    return unicodedata.normalize('NFKC',s).lower().translate(str.maketrans('–—−','---'))


def lexical_hits(text, patterns):
    text=norm_text(text);found={}
    for pattern in patterns:
        for m in re.finditer(pattern,text):
            # Negation is propagated over coordination, stopped at punctuation / but.
            # Do not split on ordinary spaces.
            clause=re.split(r'[,.;:!?]|\bbut\b|\bhowever\b',text[:m.start()])[-1]
            clause=re.sub(r'\bnot only\b','',clause)
            negative=bool(re.search(r'\b(?:no|not|without|lack|lacking|absence|absent|never)\b',clause))
            key=(m.start(),m.end())
            found[key]=dict(term=m.group(0),negative=negative,start=m.start(),end=m.end(),context=text[max(0,m.start()-50):min(len(text),m.end()+60)])
    return list(found.values())


def mean_test(values):
    x=np.array(values,float);n=len(x)
    if n<2:raise ValueError('Too few units')
    mean=float(x.mean());sd=float(x.std(ddof=1));se=sd/np.sqrt(n)
    q=float(stats.t.ppf(.975,n-1));p=float(stats.ttest_1samp(x,0).pvalue)
    return dict(n=n,mean=mean,sd_between_units=sd,se=se,ci_low=mean-q*se,ci_high=mean+q*se,p=p,d_z=mean/sd)


# Pairs have fixed orientation; theta_BASE=0.
PAIRS=[('AESTHETIC','CONTROL'),('AESTHETIC','BASE'),('BASE','CONTROL')]
V={'AESTHETIC':np.array([1.,0.]),'CONTROL':np.array([0.,1.]),'BASE':np.array([0.,0.])}
DESIGNS=[]
for i,j in PAIRS:
    DESIGNS.append(np.array([np.r_[V[i],0.],np.r_[V[j],0.],np.r_[.5*(V[i]+V[j]),1.]]))
DESIGNS=np.array(DESIGNS)


def fit_davidson(counts, init=None):
    """p_i:p_j:p_tie = exp(theta_i):exp(theta_j):nu*exp((theta_i+theta_j)/2)."""
    counts=np.array(counts,float)
    def fun(par):
        logits=np.einsum('pck,k->pc',DESIGNS,par)
        logp=logits-special.logsumexp(logits,axis=1)[:,None]
        prob=np.exp(logp)
        loss=-float((counts*logp).sum())
        grad=np.einsum('pc,pck->k',counts.sum(axis=1)[:,None]*prob-counts,DESIGNS)
        return loss,grad
    start=np.zeros(3) if init is None else np.array(init)
    result=optimize.minimize(fun,start,jac=True,method='BFGS',options={'gtol':1e-7,'maxiter':200})
    if (not result.success) and np.max(np.abs(fun(result.x)[1]))>1e-4:
        raise RuntimeError(f'Davidson fit failed: {result.message}')
    return result.x


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--export',type=Path,required=True);ap.add_argument('--inputs',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--bootstrap',type=int,default=3000)
    args=ap.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
    inp=args.inputs
    for p in [args.export,inp/'triplet_transfer.csv',inp/'source_affinity.csv',inp/'results.csv']:
        if not p.is_file():raise FileNotFoundError(p)
    z=zipfile.ZipFile(args.export)
    def zrows(n):return list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig'))))
    def keep(r):return r['excluded_from_analysis'].lower()=='false'
    A=[r for r in zrows('aesthetic_dataset.csv') if r['dataset_code']=='AESTHETIC-v2']
    C=[r for r in zrows('control_dataset.csv') if r['dataset_code']=='CONTROL-v2']
    assert len(A)==len(C)==89
    aids={r['image_code'] for r in A};cids={r['image_code'] for r in C};assert not aids&cids
    meta={r['image_code']:r for r in zrows('image_metadata.csv')}
    def cstratum(r):
        if r['reason']=='matched: random fill':return 'random_fill'
        if r['reason'].startswith('matched (relaxed to BuildingType)'):return 'type_only'
        if r['reason'].startswith('matched: BuildingType=') and 'Style=' in r['reason']:return 'type_and_style'
        raise ValueError('Unknown matching reason '+r['reason'])
    strata=Counter(cstratum(r) for r in C)
    assert strata=={'type_and_style':20,'type_only':41,'random_fill':28}
    manifest=[]
    for group,rows in [('AESTHETIC',A),('CONTROL',C)]:
        for r in rows:
            m=meta[r['image_code']]
            manifest.append(dict(condition=group,image_code=r['image_code'],control_construction=cstratum(r) if group=='CONTROL' else '',sort_order=r['sort_order'],reason=r['reason'],period=m['period'],continent=m['continent'],country=m['country'],building_type=m['building_type'],style=m['architectural_style'],caption=r['caption_snapshot']))
    csv_out(out,'01_training_manifest.csv',manifest)
    csv_out(out,'02_control_construction.csv',[dict(stratum=k,n=v,share=v/89) for k,v in strata.items()])
    comp=[]
    for var in ['period','continent','country','building_type','style']:
        cats=sorted({r[var] for r in manifest})
        for cat in cats:
            na=sum(r[var]==cat for r in manifest if r['condition']=='AESTHETIC')
            nc=sum(r[var]==cat for r in manifest if r['condition']=='CONTROL')
            comp.append(dict(variable=var,category=cat,A_n=na,C_n=nc,A_share=na/89,C_share=nc/89,difference_A_minus_C=(na-nc)/89,
                C_type_style=sum(r[var]==cat and r['control_construction']=='type_and_style' for r in manifest),
                C_type_only=sum(r[var]==cat and r['control_construction']=='type_only' for r in manifest),
                C_random_fill=sum(r[var]==cat and r['control_construction']=='random_fill' for r in manifest)))
    csv_out(out,'03_composition_by_stratum.csv',comp)
    # Original paired A identities are not in the manifest. Candidate counts do not establish pairing.
    candidates=[]
    for r in C:
        s=cstratum(r);m=meta[r['image_code']]
        aa=[] if s=='random_fill' else [a['image_code'] for a in A if meta[a['image_code']]['building_type'].casefold()==m['building_type'].casefold() and (s=='type_only' or meta[a['image_code']]['architectural_style'].casefold()==m['architectural_style'].casefold())]
        candidates.append(dict(C_image_code=r['image_code'],stratum=s,A_candidate_count=len(aa) if s!='random_fill' else '',A_candidates=';'.join(aa),original_pair_id_available=False))
    csv_out(out,'04_pairing_identifiability.csv',candidates)
    # Caption lexicon is versioned; all literal evidence contexts are retained.
    dict_path=Path(__file__).resolve().with_name('caption_lexicon_v1.json')
    dictionary=json.loads(dict_path.read_text(encoding='utf-8'))
    features=dictionary['features'];assert len(features)==31
    affine={r['image_code']:r for r in read_csv(inp/'source_affinity.csv')}
    hitrows=[];binary=np.full((178,31),np.nan);negbinary=np.full((178,31),np.nan)
    for i,r in enumerate(manifest):
        for j,f in enumerate(features):
            if f['status']=='not_operationalised':continue
            hh=lexical_hits(r['caption'],f['patterns']);pos=[h for h in hh if not h['negative']];neg=[h for h in hh if h['negative']]
            binary[i,j]=bool(pos);negbinary[i,j]=bool(neg)
            for h in hh:hitrows.append(dict(condition=r['condition'],image_code=r['image_code'],feature=f['feature'],**h))
    csv_out(out,'05_caption_hits.csv',hitrows)
    caption_counts=[];aff_assoc=[]
    aff=np.array([float(affine[r['image_code']]['relative_source_set_affinity']) for r in manifest])
    affcenter=np.r_[aff[:89]-aff[:89].mean(),aff[89:]-aff[89:].mean()]
    for j,f in enumerate(features):
        valid=f['status']!='not_operationalised';x=binary[:,j]
        row=dict(feature=f['feature'],group=f['group'],status=f['status'],A_n=int(np.nansum(x[:89])) if valid else '',C_n=int(np.nansum(x[89:])) if valid else '',A_negative=int(np.nansum(negbinary[:89,j])) if valid else '',C_negative=int(np.nansum(negbinary[89:,j])) if valid else '',A_share=float(np.mean(x[:89])) if valid else '',C_share=float(np.mean(x[89:])) if valid else '',difference_A_minus_C=float(np.mean(x[:89])-np.mean(x[89:])) if valid else '',note=f['note'])
        caption_counts.append(row)
        within=np.r_[x[:89]-np.mean(x[:89]),x[89:]-np.mean(x[89:])] if valid else None
        aff_assoc.append(dict(feature=f['feature'],n=178,status=f['status'],pearson_pooled=corr(x,aff) if valid else '',pearson_within_source_set=corr(within,affcenter) if valid else '',estimand='caption presence vs saved per-photo relative source-set affinity (leave-one-out for training members); NOT correlation of 31 caption and visual contrast profiles'))
    csv_out(out,'06_caption_feature_counts.csv',caption_counts)
    csv_out(out,'06b_caption_presence_matrix.csv',[dict(image_code=r['image_code'],condition=r['condition'],**{f['feature']:('' if np.isnan(binary[i,j]) else int(binary[i,j])) for j,f in enumerate(features)}) for i,r in enumerate(manifest)])
    csv_out(out,'07_caption_affinity_diagnostic.csv',aff_assoc)
    exact=[]
    for term in ['curved','organic','iconic','contemporary','beautiful','elegant','monumental','concrete','glass','glazed','timber','white','cars','people','interior','sunlight']:
        pat=r'\b'+term+r'\b'
        exact.append(dict(term=term,A_n=sum(bool(re.search(pat,norm_text(r['caption_snapshot']))) for r in A),C_n=sum(bool(re.search(pat,norm_text(r['caption_snapshot']))) for r in C)))
    csv_out(out,'08_exact_word_counts.csv',exact)
    # Transfer scales: no new embeddings; operate on original exported scalar quantities.
    tr=read_csv(inp/'triplet_transfer.csv');rows159=[r for r in tr if r['all_three_shown_to_participants'].lower()=='true'];assert len(tr)==192 and len(rows159)==159
    S=np.array([float(r['representation_transfer_score']) for r in rows159]);P=np.array([float(r['shift_projection_aesthetic'])-float(r['shift_projection_control']) for r in rows159]);D=float(np.median(S/P));ratio=np.array([float(r['transfer_ratio']) for r in rows159])
    assert np.max(np.abs(S-D*P))<1e-12
    assert np.max(np.abs(P/D-ratio))<1e-12
    ratings=np.array([float(r['rating_difference_aesthetic_minus_control']) for r in rows159]);choices=np.array([float(r['share_aesthetic_chosen']) for r in rows159])
    transfer=[]
    for name,x in [('affinity_difference_S',S),('unit_direction_projection_P',P),('transfer_ratio_P_over_D',ratio)]:
        transfer.append(dict(measure=name,n=len(x),mean=float(x.mean()),median=float(np.median(x)),minimum=float(x.min()),maximum=float(x.max()),sample_sd=float(x.std(ddof=1)),positive=int((x>0).sum()),spearman_rating=float(stats.spearmanr(x,ratings).statistic),spearman_choices=float(stats.spearmanr(x,choices).statistic)))
    csv_out(out,'09_transfer_scale_check.csv',transfer)
    defs=dict(source_distance_D=D,max_absolute_error_S_equals_D_P=float(np.max(np.abs(S-D*P))),max_absolute_error_ratio_equals_P_over_D=float(np.max(np.abs(ratio-P/D))))
    rr=[r for r in read_csv(inp/'results.csv') if r['embedding']=='cls']
    dsr=next(float(r['estimate']) for r in rr if r['analysis']=='standardised distance AESTHETIC–CONTROL (distance / pooled dispersion)')
    defs['source_pooled_multivariate_dispersion']=D/dsr
    defs['projection_over_source_dispersion']=float(P.mean()/(D/dsr))
    defs['projection_over_source_dispersion_note']='NOT output SD, NOT Cohen d; pooled dispersion is the scalar denominator of the reported source centroid distance.'
    (out/'transfer_definitions.json').write_text(json.dumps(defs,indent=2),encoding='utf-8')
    scalarrows=[]
    for r in tr:
        scalarrows.append(dict(prompt=r['prompt_code'],generation_seed=r['seed'],included_in_primary=r['all_three_shown_to_participants'],affinity_difference_S=r['representation_transfer_score'],unit_direction_projection_P=float(r['shift_projection_aesthetic'])-float(r['shift_projection_control']),ratio=r['transfer_ratio']))
    csv_out(out,'10_transfer_triplets.csv',scalarrows)
    # Participant counts and historical vs exported-filter perimeters.
    pre=zrows('pretraining_ratings.csv');pre_f=[r for r in pre if keep(r)];post=zrows('posttraining_ratings.csv');post_f=[r for r in post if keep(r)]
    participants={r['participant_id']:r for r in zrows('participants.csv')}
    n_by=Counter(r['participant_id'] for r in pre_f)
    byA=Counter(r['participant_id'] for r in pre_f if r['image_code'] in aids);byC=Counter(r['participant_id'] for r in pre_f if r['image_code'] in cids)
    pids=set(r['participant_id'] for r in post_f);preids={r['participant_id'] for r in pre}
    linked=pids&preids
    cohorts=Counter('linked' if pid in linked else participants[pid]['prior_participation_self_report'] for pid in pids)
    sample=[dict(scope='phase1_complete',participants=len(preids),ratings=len(pre)),dict(scope='phase1_export_filter',participants=len(n_by),ratings=len(pre_f)),dict(scope='phase1_export_at_least_10',participants=sum(n>=10 for n in n_by.values()),ratings=''),dict(scope='phase1_export_at_least_3_each_frozen_set',participants=sum(byA[p]>=3 and byC[p]>=3 for p in n_by),ratings=''),dict(scope='phase2_included',participants=len(pids),ratings=len(post_f))]
    for k,v in cohorts.items():sample.append(dict(scope='phase2_cohort_'+k,participants=v,ratings=''))
    csv_out(out,'11_sample_counts.csv',sample)
    # Recompute primary mean contrasts as specified in report; retain sensitivity labels.
    def per_person_diff(rr,i,j):
        temp=defaultdict(lambda:defaultdict(list))
        for r in rr:temp[r['participant_id']][r['condition_code']].append(float(r['score']))
        return {p:np.mean(d[i])-np.mean(d[j]) for p,d in temp.items() if i in d and j in d}
    hc=[]
    for i,j in [('AESTHETIC','CONTROL'),('BASE','CONTROL'),('AESTHETIC','BASE')]:
        vals=per_person_diff(post_f,i,j)
        hc.append(dict(analysis='primary',contrast=i+'-'+j,unit='participant',**mean_test(list(vals.values()))))
    for label,rrx in [('without_global_exclusions',post),('exclude_responses_under_500ms',[r for r in post_f if not r['response_time_ms'] or float(r['response_time_ms'])>=500])]:
        vals=per_person_diff(rrx,'AESTHETIC','CONTROL');hc.append(dict(analysis=label,contrast='AESTHETIC-CONTROL',unit='participant',**mean_test(list(vals.values()))))
    # Explicit extra eligibility check. This is not asserted to recover unavailable original code.
    cnt_ac=defaultdict(Counter)
    for r in post:cnt_ac[r['participant_id']][r['condition_code']]+=1
    eligible3={p for p,v in cnt_ac.items() if v['AESTHETIC']>=3 and v['CONTROL']>=3}
    vals=per_person_diff([r for r in post if r['participant_id'] in eligible3],'AESTHETIC','CONTROL')
    hc.append(dict(analysis='new_sensitivity_no_exclusions_min3_each',contrast='AESTHETIC-CONTROL',unit='participant',**mean_test(list(vals.values()))))
    csv_out(out,'12_human_contrasts_recomputed.csv',hc)
    # New sensitivity including ties: descriptive half-tie score + Davidson common tie parameter.
    pw=[r for r in zrows('pairwise_trials.csv') if keep(r) and r['answered_at']]
    counts=np.zeros((3,3),dtype=int);byid=defaultdict(lambda:np.zeros((3,3),dtype=int));byprompt=defaultdict(lambda:np.zeros((3,3),dtype=int))
    for r in pw:
        pair_idx=next(i for i,p in enumerate(PAIRS) if set(p)=={r['left_condition'],r['right_condition']})
        i,j=PAIRS[pair_idx];w=r['winner_condition'];widx=0 if w==i else 1 if w==j else 2 if w=='TIE' else -1
        if widx<0:raise ValueError('Unknown winner')
        counts[pair_idx,widx]+=1;byid[r['participant_id']][pair_idx,widx]+=1;byprompt[r['prompt_code']][pair_idx,widx]+=1
    assert counts.sum()==4736 and counts[:,2].sum()==726
    pair_counts=[]
    for k,(i,j) in enumerate(PAIRS):
        ni,nj,nt=map(int,counts[k]);pair_counts.append(dict(first=i,second=j,first_wins=ni,second_wins=nj,ties=nt,total=ni+nj+nt,decisive_share=ni/(ni+nj),half_tie_share=(ni+.5*nt)/(ni+nj+nt),tie_share=nt/(ni+nj+nt)))
    csv_out(out,'13_pairwise_counts_including_ties.csv',pair_counts)
    theta=fit_davidson(counts);tie_results=[]
    for clustering,groupcounts,seedoffset in [('participant',byid,17),('prompt',byprompt,29)]:
        mats=np.array(list(groupcounts.values()));ng=len(mats);rng=np.random.default_rng([20261003,seedoffset]);boots=[];halfboots=[]
        for b in range(args.bootstrap):
            weights=rng.multinomial(ng,np.ones(ng)/ng);cc=np.einsum('g,gpc->pc',weights,mats)
            fit=fit_davidson(cc,theta);boots.append([float((V[i]-V[j])@fit[:2]) for i,j in PAIRS]);halfboots.append([(cc[k,0]+.5*cc[k,2])/cc[k].sum() for k in range(3)])
        boots=np.array(boots);halfboots=np.array(halfboots)
        for k,(i,j) in enumerate(PAIRS):
            q=np.quantile(boots[:,k],[.025,.975]);hq=np.quantile(halfboots[:,k],[.025,.975]);est=float((V[i]-V[j])@theta[:2])
            tie_results.append(dict(analysis='new_exploratory_Davidson',contrast=i+'-'+j,resampling_unit=clustering,n_clusters=ng,bootstrap_replicates=args.bootstrap,odds_ratio=float(np.exp(est)),ci_low=float(np.exp(q[0])),ci_high=float(np.exp(q[1])),nu=float(np.exp(theta[2])),half_tie_share=pair_counts[k]['half_tie_share'],half_tie_ci_low=float(hq[0]),half_tie_ci_high=float(hq[1])))
    csv_out(out,'14_pairwise_new_sensitivity.csv',tie_results)
    # Immutable generation prompt/seed definitions recovered, no named user accounts.
    gg=zrows('generated_images.csv');pp=zrows('prompt_sets.csv');finalpp=[r for r in pp if r['prompt_set_id']=='15'];assert len(finalpp)==48
    for r in gg:
        config=json.loads(r['generation_parameters_json']);orig=next(p for p in finalpp if p['prompt_code']==r['prompt_code'])
        assert config['prompt']==orig['text'] and config['negative_prompt']==orig['negative_prompt']
    csv_out(out,'15_final_prompts.csv',[{k:r[k] for k in ['prompt_code','text','negative_prompt','category','frozen_at']} for r in finalpp])
    timeline=[]
    def addtime(label,t,note=''):timeline.append(dict(event=label,time_utc=t,note=note))
    addtime('first_phase1_rating',min(r['created_at'] for r in pre));addtime('last_phase1_rating',max(r['created_at'] for r in pre))
    for label,t in [('frozen_AESTHETIC_v2',A[0]['frozen_at']),('frozen_CONTROL_v2',C[0]['frozen_at']),('final_prompt_set_frozen',finalpp[0]['frozen_at'])]:addtime(label,t)
    for r in zrows('training_runs.csv'):
        if r['code'] in ['RUN-AESTHETIC-4','RUN-CONTROL-4']:
            addtime(r['code']+'_start',r['started_at']);addtime(r['code']+'_end',r['completed_at'])
    addtime('first_final_generation',min(r['created_at'] for r in gg));addtime('last_final_generation',max(r['created_at'] for r in gg))
    reviews=[r['reviewed_at'] for r in gg if r['reviewed_at']];addtime('first_screening_record',min(reviews));addtime('last_screening_record',max(reviews))
    addtime('first_phase2_rating',min(r['created_at'] for r in post));addtime('last_phase2_rating',max(r['created_at'] for r in post))
    csv_out(out,'16_timeline.csv',sorted(timeline,key=lambda x:x['time_utc']))
    phases_overlap=any(r['created_at']>=min(p['created_at'] for p in post) for r in pre)
    assert not phases_overlap
    # Inventory and limitations: no full embedding/descriptor matrices fabricated from plots.
    # Source inventory only; does not prove historical sampling procedure or relevance claims.
    sources=zrows('source_images.csv')
    csv_out(out,'18_source_inventory.csv',[dict(image_code=r['image_code'],corpus_batch=r['corpus_batch'],imported_at=r['imported_at'],sha256=r['sha256'],**{k:meta[r['image_code']][k] for k in ['building_name','architect','year_completed','country','continent','period','building_type','architectural_style','award_or_relevance','wikimedia_page_url','photographer','license','license_url']}) for r in sources])
    photo_scores=defaultdict(list)
    for r in pre:photo_scores[r['image_code']].append(float(r['score']))
    admitted={k for k,v in photo_scores.items() if len(v)>=10 and np.mean(v)>=5}
    assert admitted==aids
    inventory=[dict(path=n,size=z.getinfo(n).file_size,kind='zip_member') for n in z.namelist()]
    csv_out(out,'17_export_inventory.csv',inventory)
    metadata=dict(export_sha256=sha(args.export),triplets_sha256=sha(inp/'triplet_transfer.csv'),affinity_sha256=sha(inp/'source_affinity.csv'),results_sha256=sha(inp/'results.csv'),dictionary_sha256=sha(dict_path),numpy_version=np.__version__,scipy_version=scipy.__version__,bootstrap=args.bootstrap,seed=20261003,phase1_continued_during_phase2=phases_overlap,training_run_codes_evaluated=sorted({r['training_run'] for r in post_f if r['training_run']}),post_groups=dict(sorted(cohorts.items())),source_batches=dict(sorted(Counter(r['corpus_batch'] for r in sources).items())),source_images=len(sources),threshold_n10_mean5_matches_frozen_aesthetic=(admitted==aids),dictionary_features=len(features),caption_features_operationalised=sum(f['status']!='not_operationalised' for f in features),distinct_final_prompts=len(finalpp),caption_affinity_is_partial_diagnostic=True,full_embedding_and_descriptor_matrices_available=False,manuscript_modified=False)
    (out/'verification_summary.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(metadata,indent=2,ensure_ascii=False))
    print('CONTROL',dict(strata));print('CAPTIONS',json.dumps(caption_counts,ensure_ascii=False))
    print('TRANSFER',transfer);print('HUMAN',hc);print('TIES',tie_results)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}',file=sys.stderr);raise
