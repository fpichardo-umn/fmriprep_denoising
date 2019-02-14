
import time
import os, glob
import pandas as pd
import numpy as np
from scipy import signal
from scipy.io import savemat
from nibabel import load
from nipype.utils import NUMPY_MMAP                 #may only work on certain systems??
from nilearn.input_data import NiftiLabelsMasker    #nilearn may require this version-->  pip install nilearn==0.5.0a0
from nilearn.input_data import NiftiMapsMasker
from nilearn.connectome import ConnectivityMeasure

#Data source, filenames, output directories
prepdir  = '/home/syliaw/shared/bids/fmriprep_output/fmriprep'   #directory where fmriprep was computed
atlas    = './atlases/Gordon2016+HarvOxSubCort.nii'              #atlas from which to extract ROI time-series
overwrite= False                                                 #should overwrite contents of "denoised/sub-????" directories?


cachedir = prepdir+'/denoised'
funcdat  = glob.glob(prepdir + '*/*/*/*/*bold_space-MNI152NLin2009cAsym_preproc.nii.gz')
if len(load(atlas, mmap=NUMPY_MMAP).shape)==4:
   atlasis4d = True
else:
   atlasis4d = False

from typing import NamedTuple
class MyStruct(NamedTuple):
    outid:       str
    usearoma:   bool
    nonaggr:    bool
    n_init2drop: int
    noise:      list
    addnoise:   list
    expansion:   int
    spkreg:      int
    fdthr:     float
    dvrthr:    float

#for temporal filtering cosine functions, consider: https://nipype.readthedocs.io/en/latest/interfaces/generated/nipype.algorithms.confounds.html
baseregressors = ["Cosine*","NonSteadyStateOutlier*"]
pipelines = (
MyStruct(outid='00P',usearoma=False,n_init2drop=0,nonaggr=False,
         noise=[],expansion=0,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='01P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='02P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['WhiteMatter', 'CSF'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='03P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='06P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='24P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ'],expansion=2,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='09P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ', 'GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='36P',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ', 'GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='03P+SpkReg75thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2266,dvrthr=1.3992,addnoise=baseregressors),
#MyStruct(outid='03P+SpkReg80thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2501,dvrthr=1.4295,addnoise=baseregressors),
#MyStruct(outid='03P+SpkReg90thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.3263,dvrthr=1.5138,addnoise=baseregressors), 
#MyStruct(outid='09P+SpkReg75thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2266,dvrthr=1.3992,addnoise=baseregressors),
#MyStruct(outid='09P+SpkReg80thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2501,dvrthr=1.4295,addnoise=baseregressors),
#MyStruct(outid='09P+SpkReg90thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.3263,dvrthr=1.5138,addnoise=baseregressors),
#MyStruct(outid='36P+SpkReg75thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
#         spkreg=1,fdthr=0.2266,dvrthr=1.3992,addnoise=baseregressors),
#MyStruct(outid='36P+SpkReg80thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
#         spkreg=1,fdthr=0.2501,dvrthr=1.4295,addnoise=baseregressors),
#MyStruct(outid='36P+SpkReg90thPctile',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
#         spkreg=1,fdthr=0.3263,dvrthr=1.5138,addnoise=baseregressors), 
#MyStruct(outid='03P+SpkReg80thPctileFD',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2501,dvrthr=999999,addnoise=baseregressors),
#MyStruct(outid='03P+SpkReg80thPctileDVARS',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=999999,dvrthr=1.4295,addnoise=baseregressors),
#MyStruct(outid='09P+SpkReg80thPctileFD',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=0.2501,dvrthr=999999,addnoise=baseregressors),
#MyStruct(outid='09P+SpkReg80thPctileDVARS',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
#         spkreg=1,fdthr=999999,dvrthr=1.4295,addnoise=baseregressors),
MyStruct(outid='36P+SpkReg80thPctileFD',usearoma=False,n_init2drop=0,nonaggr=False,
         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
         spkreg=1,fdthr=0.2501,dvrthr=999999,addnoise=baseregressors),
#MyStruct(outid='36P+SpkReg80thPctileDVARS',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ','GlobalSignal', 'WhiteMatter', 'CSF'],expansion=2,
#         spkreg=1,fdthr=999999,dvrthr=1.4295,addnoise=baseregressors))
#MyStruct(outid='00P+aCompCor',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=[],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['aCompCor*']),
#MyStruct(outid='24P+aCompCor',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ'],expansion=2,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['aCompCor*']),
MyStruct(outid='24P+aCompCor+4GSR',usearoma=False,n_init2drop=0,nonaggr=False,
         noise=['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ', 'GlobalSignal'],expansion=2,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['aCompCor*']),
#MyStruct(outid='00P+AROMANonAgg',usearoma=True,n_init2drop=0,nonaggr=False,
#         noise=[],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='01P+AROMANonAgg',usearoma=True,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
MyStruct(outid='02P+AROMANonAgg',usearoma=True,n_init2drop=0,nonaggr=False,
         noise=['WhiteMatter', 'CSF'],expansion=0,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
MyStruct(outid='03P+AROMANonAgg',usearoma=True,n_init2drop=0,nonaggr=False,
         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors),
#MyStruct(outid='00P+AROMAAgg',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=[],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['AROMAAggrComp*','aroma_motion*']),
#MyStruct(outid='01P+AROMAAgg',usearoma=False,n_init2drop=0,nonaggr=False,
#         noise=['GlobalSignal'],expansion=0,
#         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['AROMAAggrComp*','aroma_motion*']),
MyStruct(outid='02P+AROMAAgg',usearoma=False,n_init2drop=0,nonaggr=False,
         noise=['WhiteMatter', 'CSF'],expansion=0,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['AROMAAggrComp*','aroma_motion*']),
MyStruct(outid='03P+AROMAAgg',usearoma=False,n_init2drop=0,nonaggr=False,
         noise=['GlobalSignal', 'WhiteMatter', 'CSF'],expansion=0,
         spkreg=0,fdthr=99,dvrthr=99,addnoise=baseregressors+['AROMAAggrComp*','aroma_motion*']) )

idlist      = np.chararray((len(funcdat),len(pipelines)),itemsize=len(os.path.basename(funcdat[0]).split('_')[0]),unicode=True)
atlaslist   = np.chararray((len(funcdat),len(pipelines)),itemsize=len(atlas),unicode=True)
fdthr       = np.zeros((len(funcdat),len(pipelines)))
dvthr       = np.zeros((len(funcdat),len(pipelines)))
ntr         = np.zeros((len(funcdat),len(pipelines)))
ntrabovethr = np.zeros((len(funcdat),len(pipelines)))
pctdflost   = np.zeros((len(funcdat),len(pipelines)))
mfd         = np.zeros((len(funcdat),len(pipelines)))
medfd       = np.zeros((len(funcdat),len(pipelines)))
maxfd       = np.zeros((len(funcdat),len(pipelines)))
mdv         = np.zeros((len(funcdat),len(pipelines)))
meddv       = np.zeros((len(funcdat),len(pipelines)))
maxdv       = np.zeros((len(funcdat),len(pipelines)))
if not os.path.isdir(cachedir):
    os.mkdir(cachedir)
for ii in range(0,len(funcdat)): 

   #get stuff for current case
   curfunc = funcdat[ii]
   curdir  = os.path.dirname(curfunc)
   curmask = glob.glob(curdir + '/*bold_space-MNI152NLin2009cAsym_brainmask.nii.gz')[0]
   curconf = glob.glob(curdir + '/*bold_confounds.tsv')[0]
   cursegm = glob.glob(curdir.split('/ses-')[0]+'/anat/*space-MNI152NLin2009cAsym_dtissue.nii.gz')[0]
   curcache= cachedir + '/' + os.path.basename(curfunc)[0:11]
   dim1,dim2,dim3,timepoints = load(curfunc, mmap=NUMPY_MMAP).shape
   t = time.time()
   print ('Current subject (' + str(ii) + '): ' + curfunc)

   # if the "atlas" is a set of weighted maps (e.g., ICA spatial maps), use the mapsMasker (with smoothing)
   if atlasis4d:
      masker = NiftiMapsMasker(    maps_img=atlas, detrend=True, standardize=True, mask_img=curmask, smoothing_fwhm=6)
   else:
      masker = NiftiLabelsMasker(labels_img=atlas, detrend=True, standardize=True, mask_img=curmask)

   # make subject output directory, if none exists
   if not os.path.isdir(curcache):
      os.mkdir(curcache)

   #select columns of confound tsv to reduce based upon
   confounds  = pd.read_csv(curconf,sep='\t')

   #loop "pipelines" to generate "denoised" data
   for jj in range(0,len(pipelines)):

     outfile = (curcache + '/' + os.path.basename(curfunc)[0:-7] + '_Proc-' + pipelines[jj].outid + '_ROI-' + os.path.basename(atlas)[0:-4] + '_TS.tsv')
     n_init2drop  = pipelines[jj].n_init2drop
     usearoma     = pipelines[jj].usearoma
     do_nonaggr   = pipelines[jj].nonaggr
     do_expansion = pipelines[jj].expansion
     do_spikereg  = pipelines[jj].spkreg
     addnoise     = pipelines[jj].addnoise
     fd_thresh    = pipelines[jj].fdthr
     dvar_thresh  = pipelines[jj].dvrthr
     
     # if usearoma==True, nullify any smoothing to be done beforehand
     # also, the functional file-derived signals should come from the existing AROMA.nii.gz, this section of code will
     # replace the contents of existing 'WhiteMatter', 'CSF', 'GlobalSignal' with new contents from the AROMA cleaned file
     nAROMAComps = 0
     if usearoma:
        from nipype.interfaces.fsl.utils import FilterRegressor
        nAROMAComps = nAROMAComps + len(np.loadtxt(glob.glob(curdir + '/*bold_AROMAnoiseICs.csv')[0],delimiter=',').astype('int'))
        if (not os.path.isfile(outfile) or overwrite) or (not os.path.isfile(curcache + '/tmpAROMA.nii.gz') and overwrite):
           FilterRegressor(design_file=glob.glob(curdir + '/*bold_MELODICmix.tsv')[0],
                           filter_columns=list(np.loadtxt(glob.glob(curdir + '/*bold_AROMAnoiseICs.csv')[0],delimiter=',').astype('int')),
                           in_file=curfunc,
                           mask=curmask,
                           out_file=curcache + '/tmpAROMA.nii.gz').run()
        if not os.path.isfile(curcache + '/AROMA_confounds.tsv'):
           if not os.path.isfile(curcache + '/aroma-wmmask.nii.gz') or not os.path.isfile(curcache + '/aroma-csfmask.nii.gz'):
              from nipype.interfaces.fsl.maths import Threshold
              from nipype.interfaces.fsl.utils import ImageMeants
              Threshold(in_file=cursegm, thresh=2.5, out_file=curcache + '/aroma-wmmask.nii.gz',  args=' -uthr 3.5 -kernel sphere 4 -ero -bin').run()
              Threshold(in_file=cursegm, thresh=0.5, out_file=curcache + '/aroma-csfmask.nii.gz', args=' -uthr 1.5 -kernel sphere 2 -ero -bin').run() 
           wmts = NiftiLabelsMasker(labels_img=curcache + '/aroma-wmmask.nii.gz', detrend=False, standardize=False).fit_transform(curcache + '/tmpAROMA.nii.gz')
           csfts= NiftiLabelsMasker(labels_img=curcache + '/aroma-csfmask.nii.gz',detrend=False, standardize=False).fit_transform(curcache + '/tmpAROMA.nii.gz') 
           gsts = NiftiLabelsMasker(labels_img=curmask                           ,detrend=False, standardize=False).fit_transform(curcache + '/tmpAROMA.nii.gz')
           AROMAconfounds = np.concatenate( (csfts, wmts, gsts), axis=1)
           np.savetxt(curcache + '/AROMA_confounds.tsv', AROMAconfounds, header='CSF\tWhiteMatter\tGlobalSignal',comments='',delimiter='\t')
        AROMAconfounds = pd.read_csv(curcache + '/AROMA_confounds.tsv',sep='\t')
        confounds[['CSF','WhiteMatter','GlobalSignal']] = AROMAconfounds[['CSF','WhiteMatter','GlobalSignal']]

     # "noise" and "addnoise" are both regressed from the data, however, (optional) derivative and expansion terms are applied
     # to the "noise" columns, whereas no derivatives/expansions are applied to "addnoise" (i.e., which will be 0-lag/non-expanded)
     noise = pipelines[jj].noise
     NoiseReg = np.ones(shape=(timepoints,1))
     if len(noise)>0:
        for kk in range(0,len(noise)):
            NoiseReg = np.concatenate(( NoiseReg, confounds.filter(regex=noise[kk])),axis=1)
     if do_expansion is 1:
        NoiseReg  = np.concatenate(( NoiseReg,np.concatenate(([np.zeros(NoiseReg.shape[1])],np.diff(NoiseReg,axis=0)),axis=0) ),axis=1)
     if do_expansion is 2:
        NoiseReg  = np.concatenate(( NoiseReg,np.concatenate(([np.zeros(NoiseReg.shape[1])],np.diff(NoiseReg,axis=0)),axis=0) ),axis=1)
        NoiseReg  = np.concatenate( (NoiseReg,np.square(NoiseReg)),axis=1)
     if len(addnoise)>0:
        for kk in range(0,len(addnoise)):
            NoiseReg = np.concatenate(( NoiseReg, confounds.filter(regex=addnoise[kk])),axis=1)
     col_mean       = np.nanmean(NoiseReg,axis=0)   #\
     inds           = np.where(np.isnan(NoiseReg))  # replace NaNs w/ column means
     NoiseReg[inds] = np.take(col_mean,inds[1])     #/

     #spike columns - taken from another script, a bit kloogey
     SpikeReg = np.ones([timepoints,1])
     if do_spikereg is 1:
        SpikeReg = (((confounds.stdDVARS > dvar_thresh) | (confounds.FramewiseDisplacement > fd_thresh))==False)*1
     if n_init2drop>0:
        SpikeReg[0:(n_init2drop)] = 0 
     censorcols   = np.where(SpikeReg==0)[0]
     SpikeCols    = np.zeros((NoiseReg.shape[0],len(censorcols)))
     SpikeCols[censorcols,range(0,len(censorcols))] = 1
     if len(np.where(SpikeReg==0)[0])>0:
        NoiseReg  = np.concatenate((NoiseReg,SpikeCols),axis=1)

     #de-mean noise[/spike] matrix, delete columns of constants
     NoiseReg = NoiseReg - np.mean(NoiseReg,axis=0)
     if any (np.mean(NoiseReg,axis=0)==0): 
        NoiseReg = np.delete(NoiseReg,np.where(np.mean(NoiseReg,axis=0)==0)[0][0],1)

     if not os.path.isfile(outfile) or overwrite:
        print ('Regressing ' + str(NoiseReg.shape[1]+nAROMAComps) + ' parameters from ROI time-series...')
        if usearoma: roits = masker.fit_transform(curcache + '/tmpAROMA.nii.gz',confounds=NoiseReg)
        else:        roits = masker.fit_transform(curfunc,                      confounds=NoiseReg) 
        np.savetxt(outfile, roits, delimiter='\t') 
        elapsed = time.time() - t
        print ('Elapsed time (s) for ' + pipelines[jj].outid + ': ' + str(np.round(elapsed,1)))

     #store info into dataframe w/ 
     idlist[ii,jj]      = os.path.basename(curfunc).split('_')[0]
     atlaslist[ii,jj]   = atlas
     ntr[ii,jj]         = float(timepoints)
     fdthr[ii,jj]       = float(pipelines[jj].fdthr)
     dvthr[ii,jj]       = float(pipelines[jj].dvrthr)
     ntrabovethr[ii,jj] = float(np.sum(SpikeReg==0)) - n_init2drop
     pctdflost[ii,jj]   = float(NoiseReg.shape[1]+nAROMAComps)/float(NoiseReg.shape[0])
     #pctdflost[ii,jj]   = float(NoiseReg.shape[1])/float(NoiseReg.shape[0])
     mfd[ii,jj]         = float(np.mean(confounds['FramewiseDisplacement'][1:-1])) 
     medfd[ii,jj]       = float(np.median(confounds['FramewiseDisplacement'][1:-1]))
     maxfd[ii,jj]       = float(np.max( confounds['FramewiseDisplacement'][1:-1]))
     mdv[ii,jj]         = float(np.mean(confounds['stdDVARS'][1:-1]))
     meddv[ii,jj]       = float(np.median(confounds['stdDVARS'][1:-1]))
     maxdv[ii,jj]       = float(np.max( confounds['stdDVARS'][1:-1]))

   if os.path.isfile(curcache + '/tmpAROMA.nii.gz'):      os.remove(curcache + '/tmpAROMA.nii.gz')
   if os.path.isfile(curcache + '/aroma-wmmask.nii.gz'):  os.remove(curcache + '/aroma-wmmask.nii.gz')
   if os.path.isfile(curcache + '/aroma-csfmask.nii.gz'): os.remove(curcache + '/aroma-csfmask.nii.gz')

for jj in range(0,len(pipelines)):
   df = pd.DataFrame({'participant_id':idlist[:,jj], 
                      'atlas':atlaslist[:,jj],
                      'TR':ntr[:,jj], 
                      'FDthr':fdthr[:,jj], 
                      'DVARthr':dvthr[:,jj], 
                      'TRabovethr':ntrabovethr[:,jj], 
                      'PctDFlost':pctdflost[:,jj], 
                      'meanFD':mfd[:,jj], 
                      'medFD':medfd[:,jj], 
                      'maxFD':maxfd[:,jj],
                      'meanDVARS':mdv[:,jj],
                      'medDVARS':meddv[:,jj],
                      'maxDVARS':maxdv[:,jj]})
   df.to_csv(path_or_buf= cachedir + '/' + pipelines[jj].outid + '.tsv',sep='\t',index=False)


