const acronyms=new Set(['pd','lgd','ead','shap','emi','ebitda','raroc','inr','ml','api','id','csv','json','ocr','dti','dscr','roi','auc','kyc','app','cus','orion']);
export function displayLabel(value:string):string {
  return value.replaceAll('_',' ').replace(/\b[a-zA-Z]+\b/g,word=>acronyms.has(word.toLowerCase())?word.toUpperCase():word[0].toUpperCase()+word.slice(1).toLowerCase());
}
