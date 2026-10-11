export async function api(path:string,method='GET',body?:unknown){
 const response=await fetch('/api'+path,{method,credentials:'include',headers:body instanceof FormData?{}:{'Content-Type':'application/json'},body:body instanceof FormData?body:body===undefined?undefined:JSON.stringify(body)});
 if(!response.ok){let error;try{error=await response.json()}catch{error={detail:response.statusText}}throw new Error(typeof error.detail==='string'?error.detail:JSON.stringify(error.detail))}
 return response.json();
}
export const money=(v:number|null|undefined)=>v==null?'N/A':new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(v);
export const percent=(v:number|null|undefined)=>v==null?'N/A':(v*100).toFixed(2)+'%';
export const decimal=(v:number|null|undefined)=>v==null?'N/A':v.toFixed(2)+'x';
