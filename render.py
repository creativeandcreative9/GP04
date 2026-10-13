#!/usr/bin/env python3
"""Deterministic, dedicated Moon Cookie Factory renderer. No external assets."""
import argparse, math, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat
ROOT=Path(__file__).resolve().parent
from timing import FPS, DURATION, CYCLE, PRESS_SHAPE, CUT_SHAPE, COAT_COLOR
S=2
BG='#172d38'; GOLD='#d8bd86'; CREAM='#f5e9c8'
def smooth(a,b,x):
    u=max(0,min(1,(x-a)/(b-a))); return u*u*(3-2*u)
def blend(a,b,u): return tuple(round(x+(y-x)*u) for x,y in zip(a,b))
def frame(t):
    # Exactly periodic; indexed conveyor settles while the three tools work.
    p=(t%CYCLE)/CYCLE; move=smooth(.60,1,p); press=smooth(.13,.26,p)*(1-smooth(.38,.52,p))
    im=Image.new('RGB',(1920,1080),BG); d=ImageDraw.Draw(im)
    def box(xy,c,r=0,outline=None,w=1):
        xy=tuple(round(v*S) for v in xy)
        if r:d.rounded_rectangle(xy,r*S,fill=c,outline=outline,width=w*S)
        else:d.rectangle(xy,fill=c,outline=outline,width=w*S)
    def ell(xy,c,outline=None,w=1):d.ellipse(tuple(round(v*S) for v in xy),fill=c,outline=outline,width=w*S)
    def line(xy,c,w=1):d.line(tuple(round(v*S) for v in xy),fill=c,width=w*S)
    def txt(x,y,s,size=12,c=GOLD):
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size*S)
        d.text((x*S,y*S),s,font=f,fill=c)
    # Quiet architectural backdrop, static stars and moon window.
    for y in range(540):
        c=blend((18,36,47),(36,64,70),y/540); line((0,y,960,y),c)
    for x in range(70,960,137):line((x,0,x,362),'#2a424a')
    box((54,49,270,218),'#102733',100,outline='#567273',w=2)
    ell((126,82,199,155),'#e1d4af');ell((148,71,212,138),'#102733')
    for x,y in [(84,94),(221,85),(97,164),(233,175),(171,189),(210,125)]:ell((x,y,x+2,y+2),'#829b9d')
    txt(321,66,'L U N A   /   B I S C U I T   W O R K S',17,CREAM)
    txt(323,99,'NIGHT SHIFT     •     SMALL BATCH / 001',10,'#91aaa8')
    line((322,130,892,130),'#496264')
    # Rear service pipe and three stations.
    line((296,194,736,194),'#577c7b',10);line((296,190,736,190),'#87a29a',2)
    for x,label,n in [(640,'PRESS','01'),(480,'MOON CUT','02'),(320,'CREAM','03')]:
        box((x-65,223,x-49,354),'#34575c',5)
        box((x+49,223,x+65,354),'#34575c',5)
        box((x-71,174,x+71,224),'#527c7a',12,outline='#8aa89e',w=1)
        box((x-63,181,x-35,207),'#29494e',5);txt(x-57,185,n,12)
        txt(x-25,188,label,10,CREAM)
        ell((x+54,187,x+59,192),'#e0c99a')
        for xx in [x-56,x+56]:ell((xx-2,216,xx+2,220),'#acc0ad')
    # Table, conveyor, and left-going repeating belt marks.
    box((27,377,933,440),'#102934',22)
    box((17,343,943,406),'#6a8580',28,outline='#adc0ab',w=2)
    box((29,350,931,390),'#2b454b',18)
    for k in range(-1,30):
        x=k*40-move*160
        if 39<x<921:line((x,353,x-13,386),'#456268',1)
    for x in [51,909]:ell((x-15,397,x+15,427),'#29474e','#89a39a',2);ell((x-4,408,x+4,416),GOLD)
    line((76,412,885,412),'#466267',3)
    for x in [122,810]:box((x,432,x+24,497),'#2e4b53',5);box((x-10,492,x+36,499),'#648078',4)
    txt(56,459,'←   S L O W   C O N V E Y O R',10,'#829e9a')
    txt(672,459,'HANDCRAFTED ON THE MOON',10,'#829e9a')
    # Cookie masks: real geometry changes, with crescent cutout transparency.
    flatten=smooth(*PRESS_SHAPE,p);cut=smooth(*CUT_SHAPE,p);coat=smooth(*COAT_COLOR,p)
    def cookie(x,flat,cutting,icing):
        cy=363;rx=17+9*flat;ry=18-3*flat
        mask=Image.new('L',im.size);md=ImageDraw.Draw(mask)
        md.ellipse(((x-rx)*S,(cy-ry-5)*S,(x+rx)*S,(cy+ry-5)*S),fill=255)
        if cutting>0:
            # Circular punch grows from the right edge while die is down.
            cr=22*cutting
            md.ellipse(((x+13-cr)*S,(cy-9-cr*.70)*S,(x+13+cr)*S,(cy-9+cr*.70)*S),fill=0)
        ell((x-30,376,x+29,384),'#1b353d')
        side=Image.new('RGB',im.size,blend((153,105,58),(196,177,137),icing))
        shifted=ImageChops.offset(mask,0,5*S); im.paste(side,(0,0),shifted)
        top=Image.new('RGB',im.size,blend((210,166,103),(245,233,200),icing));im.paste(top,(0,0),mask)
        # Tiny pores are clipped to cookie, never filling the crescent opening.
        detail=Image.new('RGB',im.size);detail.paste(top);dd=ImageDraw.Draw(detail)
        for dx,dy in [(-11,-5),(-16,3),(-3,7),(5,-11),(11,5),(-6,-11)]:
            dd.ellipse(((x+dx)*S,(cy+dy-5)*S,(x+dx+1.2)*S,(cy+dy-3.8)*S),fill=blend((175,132,77),(229,212,174),icing))
        im.paste(detail,(0,0),mask)
    for k in range(-1,8):
        base=k*160;x=base-160*move
        if not -45<x<1005:continue
        flat=1 if base<640 else flatten if base==640 else 0
        cutting=1 if base<480 else cut if base==480 else 0
        icing=1 if base<320 else coat if base==320 else 0
        cookie(x,flat,cutting,icing)
    # Tool rods and working heads in foreground; products remain visible below.
    for x in [640,480]:
        bottom=292+46*press
        box((x-6,224,x+6,bottom),'#acc0b2',3)
        box((x-25,bottom-6,x+25,bottom+5),'#c4c6ab',5,outline='#f1dfb7')
        if x==480:
            # Visible outline of the curved cutting die.
            d.arc(((x-23)*S,(bottom-1)*S,(x+23)*S,(bottom+20)*S),30,330,fill=GOLD,width=3*S)
        else:box((x-30,bottom+4,x+30,bottom+13),'#8ca399',3)
    box((307,224,333,259),'#b6c2a7',7);box((314,258,326,278),GOLD,3)
    flow=smooth(.17,.22,p)*(1-smooth(.46,.50,p))
    if flow>0:
        for dx in [-10,-5,0,5,10]:
            line((320+dx*.28,278,320+dx,351),blend((46,73,77),(236,221,179),flow),1)
        ell((297,348,343,352),blend((44,70,75),(243,231,196),flow))
    # Front safety trim, fixed station arrows, a warm pool of light.
    for x in [320,480,640]:
        line((x-8,326,x,331,x+8,326),'#9cbaa9',1)
    txt(53,28,'THE MOON COOKIE FACTORY',10,'#a7b9ac')
    txt(757,28,'CONTINUOUS / SILENT',9,'#829e9a')
    return im

def render(path,seconds=DURATION):
    path.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(round(seconds*FPS)):
            proc.stdin.write(frame(i/FPS).tobytes())
            if i%180==0:print(f'{i}/{round(seconds*FPS)} frames',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('FFmpeg failed')
def verify(path):
    a=frame(0);b=frame(24);last=frame(24-1/FPS)
    assert ImageChops.difference(a,b).getbbox() is None
    stats=ImageStat.Stat(ImageChops.difference(a,last))
    info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(path)]))
    v=info['streams'][0]
    assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1920,1080,'30/1','720')
    assert len(info['streams'])==1 and abs(float(info['format']['duration'])-24)<.01
    report={'duration_seconds':24,'width':1920,'height':1080,'fps':30,'frames':720,'audio_streams':0,'periodic_frame_0_equals_24':True,'seam_mean_absolute_rgb_difference':stats.mean,'codec':v['codec_name'],'pixel_format':v['pix_fmt']}
    (path.parent/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    # Filmstrip extracted from the actual compressed MP4, before/during/after work.
    for n,t in enumerate([.5,1.8,3.2,3.6,4.8,5.9666667]):
        fp=path.parent/f'frame-{n+1}.png'
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(path),'-frames:v','1',str(fp)],check=True)
    sheet=Image.new('RGB',(1440,610),'#172d38');sd=ImageDraw.Draw(sheet)
    for n,t in enumerate([.5,1.8,3.2,3.6,4.8,5.9666667]):
        sheet.paste(Image.open(path.parent/f'frame-{n+1}.png').resize((480,270)),((n%3)*480,(n//3)*305))
        sd.text(((n%3)*480+12,(n//3)*305+281),f't = {t:.2f} s',fill='white')
    sheet.save(path.parent/'contact-sheet.jpg',quality=93)
    # Check the encoded seam against all other adjacent frames. This also decodes
    # the entire file, catching truncated or otherwise unreadable output.
    import numpy as np
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    count=0; first=None; previous=None; deltas=[]
    while True:
        buf=proc.stdout.read(480*270*3)
        if not buf:break
        assert len(buf)==480*270*3
        current=np.frombuffer(buf,dtype=np.uint8).astype(np.int16)
        if first is None:first=current
        if previous is not None:deltas.append(float(np.abs(current-previous).mean()))
        previous=current;count+=1
    assert proc.wait()==0 and count==720
    seam=float(np.abs(first-previous).mean())
    report['decoded_frame_count']=count
    # Measure decoded before/after products while tools are retracted.
    before=np.asarray(Image.open(path.parent/'frame-1.png'))
    after=np.asarray(Image.open(path.parent/'frame-3.png'))
    measured={}
    for name,x in [('press',640),('cut',480),('coat',320)]:
        def product(a):
            crop=a[680:755,(x-32)*2:(x+32)*2].astype(np.int16)
            return (crop[:,:,0]>140)&(crop[:,:,0]-crop[:,:,2]>25)
        bmask=product(before);amask=product(after)
        by,bx=np.where(bmask);ay,ax=np.where(amask)
        measured[name]={'before_pixels':int(bmask.sum()),'after_pixels':int(amask.sum()),'before_width':int(bx.max()-bx.min()+1),'after_width':int(ax.max()-ax.min()+1)}
    assert measured['press']['after_width']>measured['press']['before_width']*1.3
    assert measured['cut']['after_pixels']<measured['cut']['before_pixels']*.8
    bc=before[690:745,590:642,0].mean();ac=after[690:745,590:642,0].mean()
    assert ac>bc+5, 'Cream coating must visibly brighten cookie'
    report['decoded_process_measurements']=measured
    report['cream_crop_red_increase']=float(ac-bc)
    report['encoded_seam_mean_absolute_difference_480x270']=seam
    report['encoded_adjacent_max_mean_absolute_difference_480x270']=max(deltas)
    assert seam<=max(deltas), 'Loop seam exceeds the largest ordinary frame step'
    (path.parent/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--still',type=float);ap.add_argument('--verify',action='store_true');args=ap.parse_args()
    out=ROOT/'output';out.mkdir(exist_ok=True)
    if args.still is not None:frame(args.still).save(out/'preview.png')
    elif args.verify:verify(out/'moon-cookie-factory.mp4')
    else:render(out/'moon-cookie-factory.mp4');verify(out/'moon-cookie-factory.mp4')
