#!/usr/bin/env python3
"""Original procedural ventilation + soft inharmonic metal. No samples/music."""
import argparse, json, subprocess, wave, hashlib
from pathlib import Path
import numpy as np
from timing import FPS, DURATION, CYCLE, EVENTS
ROOT=Path(__file__).resolve().parent
SR=48000

def db(x):return float(20*np.log10(max(float(x),1e-12)))
def wav(path,a):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((a*32767).round().astype('<i2').tobytes())
def synth(background_db,process_db):
    n=SR*DURATION;t=np.arange(n)/SR
    rng=np.random.default_rng(404)
    # FFT shaping defines a periodic random air stream; no crossfade or reset.
    f=np.fft.rfftfreq(n,1/SR)
    shape=(f/(f+95))**2 / (1+(f/720)**4)
    shape[0]=0
    def air():
        z=np.fft.rfft(rng.standard_normal(n))*shape
        a=np.fft.irfft(z,n);return a/np.sqrt(np.mean(a*a))
    common=air();left=.96*common+.04*air();right=.96*common+.04*air()
    bg=np.column_stack((left,right))
    bg+=.055*np.sin(2*np.pi*72*t)[:,None]+.025*np.sin(2*np.pi*144*t)[:,None]
    bg*=10**(background_db/20)/np.sqrt(np.mean(bg*bg))
    metal=np.zeros((n,2));events=[]
    # Each 12-second tail is folded into the 24-second loop, including tails
    # from previous iterations. Soft 100ms attack avoids percussive clicks.
    kt=np.arange(SR*12)/SR
    for name,fund,pan,tau in [('press',430,.18,1.05),('cut',610,0,1.25),('coat',790,-.18,1.45)]:
        attack=(1-np.exp(-kt/.055))**2
        fade=np.clip((12-kt)/.5,0,1);fade=fade*fade*(3-2*fade)
        k=np.zeros_like(kt)
        for ratio,amp,decay in [(1,1,1),(2.37,.20,.67),(3.91,.07,.43)]:
            k+=amp*np.sin(2*np.pi*fund*ratio*kt)*np.exp(-kt/(tau*decay))
        k*=attack*fade
        gains=np.sqrt(np.array([1-pan,1+pan])/2)
        for cycle in range(DURATION//CYCLE):
            start=EVENTS[name]+cycle*CYCLE
            idx=(np.arange(len(k))+round(start*SR))%n
            metal[idx]+=k[:,None]*gains
            events.append({'stage':name,'onset_seconds':start,'visual_shape_start_seconds':start,'offset_samples':0,'fundamental_hz':fund})
    metal*=10**(process_db/20)/np.max(np.abs(metal))
    mix=bg+metal
    if np.max(np.abs(mix))>=.95:raise ValueError('Requested gains too high; reduce levels (no hidden limiter).')
    return bg,metal,mix,events

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--background-db',type=float,default=-42,help='Air RMS dBFS')
    ap.add_argument('--process-db',type=float,default=-28,help='Combined metal bus peak dBFS')
    args=ap.parse_args();out=ROOT/'output';out.mkdir(exist_ok=True)
    bg,metal,mix,events=synth(args.background_db,args.process_db)
    for name,data in [('air-conditioning',bg),('process-metal',metal),('soundtrack',mix)]:wav(out/(name+'.wav'),data)
    source=out/'moon-cookie-factory.mp4';target=out/'moon-cookie-factory-sound.mp4'
    oldhash=hashlib.sha256(source.read_bytes()).hexdigest()
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-i',str(out/'soundtrack.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(SR),'-t',str(DURATION),'-movflags','+faststart',str(target)],check=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==oldhash
    def video_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
    assert video_hash(source)==video_hash(target)
    info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(target)]))
    v,a=info['streams'];assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1920,1080,'30/1','720')
    assert a['sample_rate']=='48000' and a['channels']==2
    assert abs(float(a['duration'])-DURATION)<1/SR
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(target),'-map','0:a:0','-t',str(DURATION),'-f','f32le','-acodec','pcm_f32le','-'])
    decoded=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    assert len(decoded)==SR*DURATION and np.max(np.abs(decoded))<1
    def metrics(data):
        diffs=np.abs(np.diff(data,axis=0));seam=float(np.max(np.abs(data[0]-data[-1])))
        # Compare seam with normal local waveform slopes at the join.
        local=np.concatenate((diffs[:4800].ravel(),diffs[-4800:].ravel()))
        bound=float(np.percentile(local,99.9))
        assert seam<=bound, (seam,bound)
        return {'peak_dbfs':db(np.max(np.abs(data))),'rms_dbfs':db(np.sqrt(np.mean(data*data))), 'dc_offset':data.mean(axis=0).tolist(),'boundary_sample_step':seam,'boundary_local_step_p99_9':bound,'clipped_samples':int(np.sum(np.abs(data)>=1))}
    report={'duration_seconds':DURATION,'sample_rate':SR,'channels':2,'original_silent_mp4_sha256':oldhash,'video_bitstream_unchanged':True,'settings':vars(args),'pcm':metrics(mix),'decoded_aac':metrics(decoded),'events':events,'listening_check':'Not performed: no audio-listening tool in this environment. Objective waveform, codec and timing checks only.','rights':'Original mathematical synthesis; no third-party recordings or music.'}
    # Check codec synchronization against the actual pre-encode waveform.
    start=SR;end=2*SR
    lags=np.arange(-64,65)
    errors=[np.mean((decoded[start:end]-mix[start+lag:end+lag])**2) for lag in lags]
    lag=int(lags[np.argmin(errors)])
    assert abs(lag)<=1, 'Unexpected codec alignment shift'
    report['aac_alignment_offset_samples']=lag
    report['aac_alignment_offset_milliseconds']=lag*1000/SR
    # Independent true-peak meter; keep machine output as supporting evidence.
    meter=subprocess.run(['ffmpeg','-hide_banner','-i',str(target),'-map','0:a','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
    (out/'audio-meter.txt').write_text(meter.stderr)
    (out/'audio-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2))
if __name__=='__main__':main()
