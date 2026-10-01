# -*- coding: utf-8 -*-
import os, subprocess as _sp, numpy as np, pyworld
FFMPEG = _sp.check_output([r'C:/Users/27264/.workbuddy/binaries/python/envs/default/Scripts/python.exe','-c','import imageio_ffmpeg,sys;sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())']).decode().strip()
SR=44100
def dec(p):
    r=_sp.run([FFMPEG,'-y','-loglevel','error','-i',p,'-ar',str(SR),'-ac','1','-f','f32le','pipe:1'],stdout=_sp.PIPE,check=True)
    return np.frombuffer(r.stdout,dtype='<f4').astype(np.float64)
KS=r'C:/Users/27264/WorkBuddy/2026-09-26-21-53-51/szgaokao-web/public/audio/ks'
for i in range(1,11):
    x=dec(os.path.join(KS,f'ks{i}f.mp3'))
    dur=len(x)/SR
    f0,tpos=pyworld.harvest(x,SR,f0_floor=80,f0_ceil=520); f0=pyworld.stonemask(x,f0,tpos,SR)
    v=f0>0; d=np.abs(np.diff(f0[v])); mj=d.max() if len(d) else 0
    # rms silence
    w=441; n=len(x)//w; y=x[:n*w].reshape(n,w); rms=np.sqrt((y**2).mean(1)+1e-12)
    pk=rms.max(); thr=pk*0.04; sil=(rms<thr).sum()*0.010
    print(f'ks{i}f: {dur:5.1f}s 浊音{100*v.mean():4.1f}% 静音{100*sil/dur:4.1f}% 最大跳变{mj:5.0f}Hz')
