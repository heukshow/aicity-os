// Isolated sandbox PNG validation. No network, filesystem or production bindings.
// Uses bounded Node zlib; a Worker port must separately verify nodejs_compat support.
import { inflateSync } from 'node:zlib';
import { AD_ASSET_SPECS } from './ad-asset-specs.js';
export const AD_ASSET_MIME_TYPES = Object.freeze(['image/png']);
const PNG_SIGNATURE = [137,80,78,71,13,10,26,10];
const CRC_TABLE = Uint32Array.from({length:256}, (_, value) => {
  for (let bit=0;bit<8;bit++) value=value&1 ? 0xedb88320^(value>>>1) : value>>>1;
  return value>>>0;
});
function crc32(bytes,start,end) { let crc=0xffffffff;for(let i=start;i<end;i++)crc=CRC_TABLE[(crc^bytes[i])&255]^(crc>>>8);return (crc^0xffffffff)>>>0; }
function reject(message) { throw new Error('Invalid advertisement asset: '+message); }
function scanlines(chunks,rowBytes,height) {
  const size=(rowBytes+1)*height, compressed=new Uint8Array(chunks.reduce((n,c)=>n+c.length,0));
  let at=0;for(const chunk of chunks){compressed.set(chunk,at);at+=chunk.length;}
  let result;
  try { result=inflateSync(compressed,{info:true,maxOutputLength:size+1}); }
  catch { reject('PNG image data rejected or decoded size limit exceeded'); }
  // A valid first zlib stream followed by junk or another stream is not a valid IDAT payload.
  if(result.engine.bytesWritten!==compressed.length)reject('trailing PNG compressed image data');
  const decoded=result.buffer;
  if(decoded.length!==size)reject('decoded PNG scanline size mismatch');
  for(let i=0;i<size;i+=rowBytes+1)if(decoded[i]>4)reject('unsupported PNG scanline filter');
  return decoded;
}
function hasTransparency(decoded,width,height,channels) {
  const stride=width*channels;let previous=new Uint8Array(stride),transparent=false;
  const paeth=(a,b,c)=>{const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c;};
  for(let y=0;y<height;y++){
    const row=new Uint8Array(stride),at=y*(stride+1),filter=decoded[at];
    for(let x=0;x<stride;x++){
      const a=x>=channels?row[x-channels]:0,b=previous[x],c=x>=channels?previous[x-channels]:0;
      const predict=filter===0?0:filter===1?a:filter===2?b:filter===3?Math.floor((a+b)/2):paeth(a,b,c);
      row[x]=(decoded[at+1+x]+predict)&255;
      if(x%channels===channels-1&&row[x]<255)transparent=true;
    }
    previous=row;
  }
  return transparent;
}
export async function validateAdAsset(role,declaredMime,bytes) {
  if(!Object.hasOwn(AD_ASSET_SPECS,role))reject('unsupported role');
  if(declaredMime!=='image/png')reject('unsupported MIME type; sandbox accepts PNG only');
  const source=bytes instanceof Uint8Array?bytes:bytes instanceof ArrayBuffer?new Uint8Array(bytes):null,spec=AD_ASSET_SPECS[role];
  if(!source||source.length<57)reject('truncated PNG or unsupported byte input');
  if(source.length>spec.maxBytes)reject('file exceeds role size limit');
  const data=new Uint8Array(source);
  if(!PNG_SIGNATURE.every((b,i)=>data[i]===b))reject('MIME and PNG signature mismatch');
  const view=new DataView(data.buffer);let offset=8,width,height,channels,color,sawHeader=false,sawImage=false,imageEnded=false,sawEnd=false;const compressed=[];
  while(offset<data.length){
    if(data.length-offset<12)reject('truncated PNG chunk');
    const length=view.getUint32(offset);if(length>data.length-offset-12)reject('PNG chunk exceeds file bounds');
    const type=String.fromCharCode(...data.subarray(offset+4,offset+8));
    if(!/^[A-Za-z]{2}[A-Z][A-Za-z]$/.test(type))reject('invalid PNG chunk type');
    const start=offset+8,end=start+length;
    if(crc32(data,offset+4,end)!==view.getUint32(end))reject('PNG chunk CRC mismatch');
    if(!sawHeader&&type!=='IHDR')reject('PNG must start with IHDR');
    if(sawImage&&type!=='IDAT')imageEnded=true;
    if(type==='IHDR'){
      if(sawHeader||length!==13)reject('invalid or duplicate PNG header');sawHeader=true;
      width=view.getUint32(start);height=view.getUint32(start+4);color=data[start+9];channels={0:1,2:3,4:2,6:4}[color];
      if(width!==spec.width||height!==spec.height)reject('PNG dimensions must match role');
      if(data[start+8]!==8||!channels||data[start+10]!==0||data[start+11]!==0||data[start+12]!==0)reject('sandbox supports non-interlaced 8-bit grayscale/RGB/alpha PNG only');
    }else if(type==='IDAT'){
      if(imageEnded)reject('PNG image chunks must be consecutive');sawImage=true;compressed.push(data.subarray(start,end));
    }else if(type==='IEND'){
      if(!sawImage||length!==0||end+4!==data.length)reject('invalid PNG end or trailing bytes');sawEnd=true;
    }else{
      if(['acTL','fcTL','fdAT'].includes(type))reject('animated PNG is unsupported');
      if(type[0]===type[0].toUpperCase())reject('unsupported critical PNG chunk');
      if(type==='tRNS'&&([4,6].includes(color)||sawImage||length!==(color===0?2:6)))reject('invalid PNG transparency chunk');
    }
    offset=end+4;
  }
  if(!sawEnd)reject('missing PNG end');
  const decoded=scanlines(compressed,width*channels,height);
  if(role==='logo'&&(![4,6].includes(color)||!hasTransparency(decoded,width,height,channels)))reject('logo requires an alpha-channel PNG with actual transparency');
  const hash=new Uint8Array(await crypto.subtle.digest('SHA-256',data));
  return {mime:'image/png',width,height,byte_size:data.length,sha256:Array.from(hash,b=>b.toString(16).padStart(2,'0')).join(''),data};
}
