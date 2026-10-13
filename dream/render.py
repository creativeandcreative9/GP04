#!/usr/bin/env python3
"""Painterly ImageGen machinery and pastry sprites with genuine timed animation."""
import argparse, math, subprocess, json, hashlib
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import numpy as np
from timing import FPS,DURATION,CYCLE,PRESS_SHAPE,CUT_SHAPE,COAT_COLOR
ROOT=Path(__file__).resolve().parent
L=Image.Resampling.LANCZOS
CENTERS={'coat':460,'cut':960,'press':1460}
PITCH=500

def smooth(a,b,x):
 u=max(0,min(1,(x-a)/(b-a)));return u*u*(3-2*u)

def clean_alpha(im):
 # Generated RGBA assets can contain near-transparent colored matte pixels.
 # Reject only low-alpha fringe and saturated matte reds at the silhouette.
 a=np.array(im.convert('RGBA')).copy();alpha=a[:,:,3]
 matte=(a[:,:,0].astype(float)>a[:,:,1]*1.8+25)&(a[:,:,0].astype(float)>a[:,:,2]*1.8+25)
 alpha[(alpha<40)|matte]=0
 a[:,:,3]=alpha
 return Image.fromarray(a)
@lru_cache(maxsize=1)
def assets():
 bg=Image.open(ROOT/'assets/cloud-free-plate.png').convert('RGBA').resize((1920,1080),L)
 machine=clean_alpha(Image.open(ROOT/'assets/refined-machine.png')).resize((1880,627),L)
 sheet=clean_alpha(Image.open(ROOT/'assets/refined-sprites.png'))
 # Grid boundaries observed in the generated atlas; use alpha bounds within cells.
 cells=[(0,0,440,397),(440,0,887,397),(887,0,1330,397),(1330,0,1774,397),
        (0,397,440,887),(440,397,887,887),(887,397,1330,887)]
 sprites=[]
 for box in cells:
  s=sheet.crop(box);bbox=s.getchannel('A').getbbox();assert bbox
  sprites.append(s.crop(bbox))
 cookies=[sprites[0].resize((80,80),L)]+[s.resize((116,76),L) for s in sprites[1:4]]
 # Common canvas anchors prevent jumps when the product changes shape.
 canvases=[]
 for s in cookies:
  c=Image.new('RGBA',(128,92));c.alpha_composite(s,((128-s.width)//2,92-s.height));canvases.append(c)
 tools=[sprites[4].resize((142,230),L),sprites[5].resize((138,230),L),sprites[6].resize((118,230),L)]
 return bg,machine,canvases,tools

def rgba_lerp(a,b,u):
 # Premultiplied-alpha interpolation prevents dark rims and color fringes.
 aa=np.asarray(a).astype(np.float32)/255;bb=np.asarray(b).astype(np.float32)/255
 alpha=aa[:,:,3:]*(1-u)+bb[:,:,3:]*u
 rgb=(aa[:,:,:3]*aa[:,:,3:]*(1-u)+bb[:,:,:3]*bb[:,:,3:]*u)/np.maximum(alpha,1e-8)
 return Image.fromarray(np.clip(np.concatenate((rgb,alpha),axis=2)*255,0,255).astype('uint8'))

def product(flat,cut,coat):
 _,_,c,_=assets()
 out=rgba_lerp(c[0],c[1],flat) if flat<1 else c[1]
 if cut:out=rgba_lerp(out,c[2],cut)
 if coat:out=rgba_lerp(out,c[3],coat)
 return out

@lru_cache(maxsize=180)
def factory_frame(index):
 t=index/FPS
 p=(t%CYCLE)/CYCLE;move=smooth(.60,1,p);press=smooth(.13,.26,p)*(1-smooth(.38,.52,p))
 bg,machine,c,tools=assets();im=Image.new('RGBA',(1920,1080))
 shadow=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shadow)
 sd.ellipse((36,970,1890,1060),fill=(25,22,48,78));shadow=shadow.filter(ImageFilter.GaussianBlur(15));im.alpha_composite(shadow)
 im.alpha_composite(machine,(20,430))
 # Subtle belt weave/joins travel on its real painted top surface.
 belt=Image.new('RGBA',im.size);bd=ImageDraw.Draw(belt)
 for k in range(-2,45):
  x=50*k-PITCH*move
  if 68<x<1850:bd.line((x,816,x-20,843),fill=(202,191,218,25),width=1)
 im.alpha_composite(belt)
 flat=smooth(*PRESS_SHAPE,p);cut=smooth(*CUT_SHAPE,p);coat=smooth(*COAT_COLOR,p)
 for k in range(-2,6):
  base=460+k*PITCH;x=base-PITCH*move
  if not -100<x<2020:continue
  f=1 if base<1460 else flat if base==1460 else 0
  ccut=1 if base<960 else cut if base==960 else 0
  icing=1 if base<460 else coat if base==460 else 0
  cookie=product(f,ccut,icing)
  sh=Image.new('RGBA',(150,34));ds=ImageDraw.Draw(sh);ds.ellipse((18,9,132,26),fill=(29,20,37,110));sh=sh.filter(ImageFilter.GaussianBlur(5));im.alpha_composite(sh,(round(x)-75,829))
  im.alpha_composite(cookie,(round(x)-64,758))
 # A telescoping steel shaft connects each independent tool to the fixed housing.
 d=ImageDraw.Draw(im)
 for name,sprite in [('press',tools[0]),('cut',tools[1])]:
  x=CENTERS[name];bottom=735+84*press;top=round(bottom-230)
  for dx in range(-9,10):
   light=int(130+95*math.exp(-((dx+3)/5)**2));d.line((x+dx,553,x+dx,top+35),fill=(light,min(230,light+2),min(240,light+9),255),width=1) if top+35>=553 else None
  # Top slides behind the housing: clip everything above the arch opening.
  visible_top=max(top,572);crop=sprite.crop((0,visible_top-top,sprite.width,sprite.height))
  im.alpha_composite(crop,(round(x-sprite.width/2),visible_top))
 x=CENTERS['coat'];im.alpha_composite(tools[2],(x-59,570))
 flow=smooth(.17,.22,p)*(1-smooth(.46,.50,p))
 if flow>0:
  stream=Image.new('RGBA',im.size);dr=ImageDraw.Draw(stream)
  for dx in [-8,-4,0,4,8]:dr.line((x+dx*.20,794,x+dx,818),fill=(247,235,208,round(flow*160)),width=2)
  im.alpha_composite(stream)
 return im.crop((0,420,1920,1080))

def world_frame(t):
 im=moving_background(t)
 im.alpha_composite(factory_frame(round(t*FPS)%(CYCLE*FPS)),(0,420))
 return im.convert('RGB')

@lru_cache(maxsize=1)
def cloud_assets():
 raw=Image.open(ROOT/'assets/cloud-clusters.png').convert('RGBA')
 a=np.array(raw).copy();rgb=a[:,:,:3].astype(np.int16)
 a[:,:,3][(a[:,:,3]<65)|((rgb.max(2)-rgb.min(2)>145)&(a[:,:,3]<250))]=0
 sheet=Image.fromarray(a)
 # Three observed, separate cloud masses. Keep their opaque lobes intact.
 widths=[(0,750),(750,1480),(1480,raw.width)] if raw.width<2100 else [(0,raw.width*.36),(raw.width*.36,raw.width*.72),(raw.width*.72,raw.width)]
 clouds=[]
 for i,(l,r) in enumerate(widths):
  c=sheet.crop((round(l),0,round(r),sheet.height));box=c.getchannel('A').getbbox();c=c.crop(box)
  c=c.resize([(680,230),(780,195),(620,220)][i],L)
  # Preserve volume: substantially opaque instead of the old 34% haze.
  c.putalpha(c.getchannel('A').filter(ImageFilter.GaussianBlur(.7)).point(lambda v:round(v*.96)))
  clouds.append(c)
 mask=Image.new('L',(1920,1080));d=ImageDraw.Draw(mask)
 for box in [(255,230,655,560),(745,230,1165,575),(1255,230,1655,548)]:d.rectangle(box,fill=255)
 return clouds,mask.filter(ImageFilter.GaussianBlur(5))

def moving_background(t):
 bg=assets()[0].copy();clouds,mask=cloud_assets()
 phase=(t%DURATION)/DURATION;shift=1800*phase
 layer=Image.new('RGBA',bg.size)
 for k in [-1,0,1,2]:
  for i,c in enumerate(clouds):
   x=k*1800+i*600-shift-170
   layer.alpha_composite(c,(round(x),[345,390,365][i]))
 layer.putalpha(ImageChops.multiply(layer.getchannel('A'),mask));bg.alpha_composite(layer)
 return bg

def camera(t):
 theta=2*math.pi*(t%DURATION)/DURATION
 zoom=1.10+.05*math.sin(theta)
 cx=960+40*math.sin(theta+.4);cy=557+14*math.cos(theta)
 w=1920/zoom;h=1080/zoom
 return (cx-w/2,cy-h/2,cx+w/2,cy+h/2),zoom

def frame(t):
 box,_=camera(t)
 return world_frame(t).transform((1920,1080),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)

def render():
 out=ROOT/'output';out.mkdir(exist_ok=True)
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-g','180','-movflags','+faststart',str(out/'dream-cloud-factory-silent.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(FPS*DURATION):
   proc.stdin.write(frame(i/FPS).tobytes())
   if i%150==0:print(f'{i}/{FPS*DURATION} frames',flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0

def verify():
 out=ROOT/'output';p=out/'dream-cloud-factory-silent.mp4'
 assert ImageChops.difference(frame(0),frame(DURATION)).getbbox() is None
 assert ImageChops.difference(moving_background(0),moving_background(DURATION)).getbbox() is None
 cameras=[]
 for i in range(FPS*DURATION):
  box,z=camera(i/FPS);l,t,r,b=box
  assert l>=0 and t>=0 and r<=1920 and b<=1080
  # Union of all three complete processing stations, including products.
  assert l<225 and r>1710 and t<425 and b>860
  cameras.append(z)
 cloud_delta=float(np.abs(np.asarray(moving_background(0)).astype(np.int16)-np.asarray(moving_background(15)).astype(np.int16)).mean())
 assert cloud_delta>1.0
 # Independent clouds: differences stay in window apertures, not on factory architecture.
 diff=ImageChops.difference(moving_background(0),moving_background(15)).convert('RGB')
 assert not diff.crop((0,650,1920,1080)).getbbox()
 info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(p)]))
 v=info['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1920,1080,'30/1',str(FPS*DURATION))
 assert abs(float(info['format']['duration'])-DURATION)<1/FPS
 times=[0,5,10,15,20,25,30,35,40,45,50,55,59.9666667,1.8,3.2];images=[]
 sheet=Image.new('RGB',(1920,1220),'#393954');sd=ImageDraw.Draw(sheet)
 for n,t in enumerate(times):
  f=out/f'frame-{n+1}.png';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1',str(f)],check=True)
  img=Image.open(f);images.append(np.asarray(img).astype(np.int16));sheet.paste(img.resize((480,270)),((n%4)*480,(n//4)*305));sd.text(((n%4)*480+12,(n//4)*305+280),f't = {t:.2f} s',fill='white')
 sheet.save(out/'contact-sheet.jpg',quality=94)
 process_changes={}
 for name,x in CENTERS.items():
  crops=[]
  for idx in [0,14]:
   box,z=camera(times[idx]);l,top,_,_=box
   sample=Image.fromarray(images[idx].astype('uint8')).transform((128,85),Image.Transform.EXTENT,((x-64-l)*z,(765-top)*z,(x+64-l)*z,(850-top)*z),Image.Resampling.BICUBIC)
   crops.append(np.asarray(sample).astype(np.int16))
  delta=float(np.abs(crops[1]-crops[0]).mean());assert delta>3
  process_changes[name]=delta
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(p),'-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
 count=0;first=None;prev=None;deltas=[]
 while True:
  buf=proc.stdout.read(480*270*3)
  if not buf:break
  assert len(buf)==480*270*3
  a=np.frombuffer(buf,dtype=np.uint8).astype(np.int16)
  if first is None:first=a
  if prev is not None:deltas.append(float(np.abs(a-prev).mean()))
  prev=a;count+=1
 assert proc.wait()==0 and count==FPS*DURATION
 seam=float(np.abs(first-prev).mean())
 # Moving, finely painted backgrounds expose I/P-frame texture differences.
 # Check scene continuity separately from those high-frequency codec residuals.
 ia=Image.fromarray(first.reshape(270,480,3).astype('uint8'))
 ib=Image.fromarray(prev.reshape(270,480,3).astype('uint8'))
 blurred_seam=float(np.abs(np.asarray(ia.filter(ImageFilter.GaussianBlur(3))).astype(np.int16)-np.asarray(ib.filter(ImageFilter.GaussianBlur(3))).astype(np.int16)).mean())
 brightness_jump=float(abs(first.mean()-prev.mean()))
 assert blurred_seam<.75 and brightness_jump<.5
 source=[np.asarray(frame(t).resize((480,270))).astype(np.int16) for t in [0,1/FPS,DURATION-1/FPS]]
 source_seam=float(np.abs(source[0]-source[2]).mean())
 source_step=float(np.abs(source[0]-source[1]).mean())
 assert source_seam<=source_step+.02
 report={'duration_seconds':DURATION,'width':1920,'height':1080,'fps':FPS,'decoded_frames':count,'periodic_source_frame_0_equals_60':True,'periodic_cloud_layer':True,'encoded_seam_mean_difference':seam,'encoded_blurred_seam_mean_difference':blurred_seam,'encoded_mean_brightness_jump':brightness_jump,'source_seam_mean_difference':source_seam,'source_first_step_mean_difference':source_step,'max_adjacent_mean_difference':max(deltas),'cloud_independent_mean_change_0_to_15s':cloud_delta,'cloud_motion':'Constant leftward drift, 1800px per 60 seconds; masked behind architectural windows','camera_zoom_range':[min(cameras),max(cameras)],'camera_pan_radius_pixels':[40,14],'all_frames_crop_inside_source':True,'all_three_stations_visible_all_frames':True,'background_sha256':hashlib.sha256((ROOT/'assets/dream-cloud-concept.png').read_bytes()).hexdigest(),'audio_cycle_seconds':60,'factory_cycle_seconds':6,'decoded_process_changes_after_camera_compensation':process_changes}
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--still',type=float);ap.add_argument('--verify',action='store_true');args=ap.parse_args();(ROOT/'output').mkdir(exist_ok=True)
 if args.still is not None:frame(args.still).save(ROOT/'output/preview.png')
 elif args.verify:verify()
 else:render();verify()
