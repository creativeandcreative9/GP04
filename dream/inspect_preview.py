import numpy as np
from PIL import Image
import render

def match(im,template,x,y,dx,dy):
 h,w=template.shape;left=max(0,int(x-w/2-dx));top=max(0,int(y-h/2-dy));right=min(im.shape[1],int(x+w/2+dx));bottom=min(im.shape[0],int(y+h/2+dy));a=im[top:bottom,left:right]
 t=template-template.mean();H,W=a.shape;shape=(H+h-1,W+w-1)
 corr=np.fft.irfft2(np.fft.rfft2(a,shape)*np.fft.rfft2(t[::-1,::-1],shape),shape)[h-1:H,w-1:W]
 def sums(a):
  s=np.pad(a,((1,0),(1,0))).cumsum(0).cumsum(1);return s[h:,w:]-s[:-h,w:]-s[h:,:-w]+s[:-h,:-w]
 var=np.maximum(sums(a*a)-sums(a)**2/(h*w),1e-9)
 ncc=corr/np.sqrt(var*np.sum(t*t));yy,xx=np.unravel_index(ncc.argmax(),ncc.shape)
 return [left+xx+w/2,top+yy+h/2,float(ncc[yy,xx])]


if __name__=='__main__':
 import subprocess,json
 from pathlib import Path
 from PIL import ImageDraw
 root=Path(__file__).resolve().parent
 path=root/'output/dream-cloud-factory-preview-1080p.mp4'
 frames=[]
 for t in [0,5,10,15]:
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
  frames.append(Image.frombytes('RGB',(1920,1080),data))
 a=np.asarray(frames[0].convert('L')).astype(float);b=np.asarray(frames[1].convert('L')).astype(float)
 box,z=render.camera(0);observed=[]
 for wx,wy,n,search in [(460,520,70,90),(1460,520,70,90),(1030,425,26,230)]:
  x=round((wx-box[0])*z);y=round((wy-box[1])*z)
  template=a[y-n//2:y+n//2,x-n//2:x+n//2]
  found=match(b,template,x,y,search,50)
  observed.append({'source_landmark':[wx,wy],'start_pixel':[x,y],'after_5_seconds':[float(v) for v in found[:2]],'correlation':found[2]})
 assert all(v['correlation']>.75 for v in observed)
 r=(observed[1]['after_5_seconds'][0]-observed[0]['after_5_seconds'][0])/(observed[1]['start_pixel'][0]-observed[0]['start_pixel'][0])
 b5,z5=render.camera(5);cx0=(box[0]+box[2])/2;cx5=(b5[0]+b5[2])/2
 pan=(r*(observed[0]['start_pixel'][0]-960)+960-observed[0]['after_5_seconds'][0])/z5
 cloud=observed[2];before=(cloud['start_pixel'][0]-960)/z+cx0;after=(cloud['after_5_seconds'][0]-960)/z5+cx5
 assert 1.015<r<1.035 and 10<pan<25 and -165<after-before<-135
 report={'measurement_source':path.name,'interval_seconds':5,'measured_zoom_ratio':r,'measured_camera_pan_world_pixels':pan,'measured_independent_cloud_world_shift_pixels':after-before,'landmarks':observed,'normal_speed_visual_review':'No playback capability in executor. The user approved the completed version; these decoded-frame measurements complement user review.'}
 (root/'output/preview-motion-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
 canvas=Image.new('RGB',(1920,1120),'#28253a');draw=ImageDraw.Draw(canvas)
 for i,img in enumerate(frames):
  canvas.paste(img.resize((960,540)),((i%2)*960,(i//2)*560));draw.text(((i%2)*960+12,(i//2)*560+542),str(i*5)+' seconds / delivered preview',fill='white')
 canvas.save(root/'output/motion-check-5s.jpg',quality=95)
 print(json.dumps(report,indent=2))
