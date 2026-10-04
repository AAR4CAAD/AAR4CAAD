"""Verifiche mirate su dati esistenti, senza modificare training o manoscritto.
Run: OPENBLAS_NUM_THREADS=2 python verifiche_locali.py --root /mnt/data
Dipendenze: numpy, scipy; CSV letti con libreria standard.
"""
import argparse, csv, hashlib, io, json, math, zipfile
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import scipy
from scipy import stats

p = argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path('/mnt/data')); a=p.parse_args()
out=Path(__file__).resolve().parent
arch=a.root/'FULL_EXPERIMENT_EXPORT_ARCH300_20261001-134634.zip'
z=zipfile.ZipFile(arch)
def rows(name): return list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig'))))
def write(name, data):
    if not data: return
    with (out/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def yes(s): return str(s).lower()=='true'
R=rows('pretraining_ratings.csv'); SI=rows('source_images.csv'); M=rows('image_metadata.csv')
A=rows('aesthetic_dataset.csv'); C=rows('control_dataset.csv')
aes={r['image_code'] for r in A if r['dataset_code']=='AESTHETIC-v2'}
ctl={r['image_code'] for r in C if r['dataset_code']=='CONTROL-v2'}
assert len(aes)==len(ctl)==89 and not (aes&ctl)
assert len(R)==23012 and len({r['participant_id'] for r in R})==166
keys=[(r['participant_id'],r['image_code']) for r in R]; assert len(keys)==len(set(keys))
ids=sorted({r['participant_id'] for r in R},key=int); codes=[r['image_code'] for r in SI]
idpos={v:i for i,v in enumerate(ids)}; codepos={v:i for i,v in enumerate(codes)}
score=np.zeros((len(ids),len(codes))); obs=np.zeros_like(score)
for r in R:
 i,j=idpos[r['participant_id']],codepos[r['image_code']];score[i,j]=float(r['score']);obs[i,j]=1
n=obs.sum(0); sums=score.sum(0); means=sums/n
sd=np.sqrt(((score**2).sum(0)-sums**2/n)/(n-1)); se=sd/np.sqrt(n)
meta={r['image_code']:r for r in M}; src={r['image_code']:r for r in SI}
active=np.array([yes(src[c]['is_active']) for c in codes])
original=(n>=10)&(means>=5)&(means>=np.quantile(means[active],.65,method='linear'))&active
assert set(np.array(codes)[original])==aes
B=3000; rng=np.random.default_rng(20261004)
w=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)),size=B)
bn=w@obs; bsum=w@score
bmean=np.divide(bsum,bn,out=np.full_like(bsum,np.nan),where=bn>0)
q=np.nanquantile(bmean[:,active],.65,axis=1,method='linear')
selected=(bn>=10)&(bmean>=5)&(bmean>=q[:,None])&active
inter=(selected&original).sum(1); union=(selected|original).sum(1); card=selected.sum(1)
prob=selected.mean(0); jaccard=inter/union
write('01_stabilita_bootstrap.csv',[{'replica':i+1,'n_selezionate':int(card[i]),'n_originali_recuperate':int(inter[i]),'frazione_originali_recuperate':float(inter[i]/89),'jaccard':float(jaccard[i]),'soglia_percentile65':float(q[i])} for i in range(B)])
photo=[]
for j,c in enumerate(codes):
 photo.append({'image_code':c,'dataset': 'AESTHETIC' if c in aes else 'CONTROL' if c in ctl else 'neither', 'corpus_batch':src[c]['corpus_batch'],'imported_at':src[c]['imported_at'],'n_giudizi':int(n[j]),'n_valutatori_distinti':int(n[j]),'media':float(means[j]),'sd_campionaria':float(sd[j]),'errore_standard_media':float(se[j]),'probabilita_inclusione_bootstrap':float(prob[j])})
write('02_fase1_per_600_foto.csv',photo); write('03_fase1_per_89_aesthetic.csv',[r for r in photo if r['dataset']=='AESTHETIC'])
batch=[]
for b in sorted({r['corpus_batch'] for r in SI}):
 for ds in ['all','AESTHETIC','CONTROL','neither']:
  cc={r['image_code'] for r in photo if r['corpus_batch']==b and (ds=='all' or r['dataset']==ds)}
  rr=[r for r in R if r['image_code'] in cc]
  stamps=[src[c]['imported_at'] for c in cc]
  batch.append({'batch':b,'dataset':ds,'n_fotografie':len(cc),'n_giudizi':len(rr),'n_valutatori_con_almeno_un_giudizio':len({r['participant_id'] for r in rr}), 'importazione_min_utc':min(stamps),'importazione_max_utc':max(stamps)})
write('04_conteggi_per_lotto.csv',batch)

def icc_legacy(ratings):
 # Riproduce l'estimatore storico dell'audit; non lo presenta come un modello incrociato.
 byrat=defaultdict(list)
 for r in ratings: byrat[r['participant_id']].append(float(r['score']))
 centres={i:np.mean(v) for i,v in byrat.items()}
 groups=defaultdict(list)
 for r in ratings:groups[r['image_code']].append(float(r['score'])-centres[r['participant_id']])
 groups={i:np.array(v) for i,v in groups.items() if len(v)>=2}
 size=np.array([len(v) for v in groups.values()],float); av=np.array([np.mean(v) for v in groups.values()]); var=np.array([np.var(v,ddof=1) for v in groups.values()]); N=size.sum(); I=len(size)
 grand=np.sum(size*av)/N
 msb=np.sum(size*(av-grand)**2)/(I-1);dfw=N-I-(len(byrat)-1);msw=np.sum((size-1)*var)/dfw;k0=(N-np.sum(size**2)/N)/(I-1)
 return {'n_partecipanti':len(byrat),'n_risposte':int(N),'n_immagini':I,'MS_between':float(msb),'MS_within':float(msw),'df_within':float(dfw),'k0':float(k0),'ICC1_storico':float((msb-msw)/(msb+(k0-1)*msw)),'ICCk_storico':float((msb-msw)/msb)}
icc=[{'perimetro':label,**icc_legacy(rr)} for label,rr in [('completo',R),('filtro_export',[r for r in R if not yes(r['excluded_from_analysis'])])]]
write('05_icc_estimatore_storico.csv',icc)
Q=rows('pairwise_trials.csv'); decisive=[r for r in Q if not yes(r['excluded_from_analysis']) and r['answered_at'] and {r['left_condition'],r['right_condition']}=={'AESTHETIC','CONTROL'} and r['winner_condition'] in {'AESTHETIC','CONTROL'}]
k=sum(r['winner_condition']=='AESTHETIC' for r in decisive);N=len(decisive); assert (k,N)==(677,1320)
t=stats.binomtest(k,N,p=.5,alternative='two-sided');ci=t.proportion_ci(confidence_level=.95,method='exact')
binom={'vittorie_A':k,'n_decisivi':N,'proporzione':t.statistic,'p_bilaterale_esatto':t.pvalue,'ci95_cp_low':ci.low,'ci95_cp_high':ci.high,'nota':'Test marginale sotto indipendenza dei confronti; non tiene conto di partecipanti e prompt ripetuti. Non sostituisce Davidson o bootstrap cluster.'}
write('06_binomiale_diretto.csv',[binom])
with (a.root/'source_affinity.csv').open(encoding='utf-8-sig',newline='') as f:AF=list(csv.DictReader(f))
AF=[r for r in AF if r['image_code'] not in aes|ctl];assert len(AF)==422
held=[]
for label,vals in [('completo166',[means[codepos[r['image_code']]] for r in AF]),('storico164_mean_rating_salvato',[float(r['mean_rating']) for r in AF])]:
 s=stats.spearmanr([float(r['relative_source_set_affinity']) for r in AF],vals)
 held.append({'perimetro':label,'n':len(AF),'spearman_rho':s.statistic,'p_asintotico_non_cluster':s.pvalue,'nota':'Affinita proporzionale a proiezione su u; fotografie non usate nella LoRA. Non esclude memorizzazione degli output o presenza nel pretraining del modello base.'})
write('07_associazione_fuori_training.csv',held)
summary={'export_sha256':hashlib.sha256(arch.read_bytes()).hexdigest(),'spec_sha256':hashlib.sha256((out/'SPEC_VERIFICHE_LOCALI.json').read_bytes()).hexdigest(),'numpy':np.__version__,'scipy':scipy.__version__,'bootstrap_n':B,'bootstrap_seed':20261004,'n_set_originale':89,'cardinality_mean':float(np.mean(card)),'cardinality_quantiles_025_50_975':np.quantile(card,[.025,.5,.975]).tolist(),'recovery_mean':float(np.mean(inter/89)),'recovery_quantiles_025_50_975':np.quantile(inter/89,[.025,.5,.975]).tolist(),'jaccard_mean':float(np.mean(jaccard)),'jaccard_quantiles_025_50_975':np.quantile(jaccard,[.025,.5,.975]).tolist(),'original_inclusion_probability_min_median_max':np.quantile(prob[original],[0,.5,1]).tolist(),'binomiale':binom,'heldout':held,'icc':icc}
(out/'RISULTATI_LOCALI.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
