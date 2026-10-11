import re, shutil, subprocess, tempfile
from pathlib import Path
import pymupdf

PATTERNS={
    'income':r'(?:monthly\s+(?:net\s+)?(?:income|salary)|net\s+salary)\s*[:=]\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)',
    'obligations':r'(?:monthly\s+obligations|existing\s+emi)\s*[:=]\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)',
    'credit_score':r'(?:credit|bureau|cibil)\s+score\s*[:=]\s*(\d{3})',
    'revenue':r'(?:annual\s+)?revenue\s*[:=]\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)',
    'ebitda':r'ebitda\s*[:=]\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)',
    'employer':r'employer\s*[:=]\s*([^\r\n]+)',
    'address':r'address\s*[:=]\s*([^\r\n]+)',
    'delinquencies':r'delinquencies\s*[:=]\s*(\d+)',
    'utilization':r'utilization\s*[:=]\s*(0(?:\.\d+)?|1(?:\.0+)?)',
    'inquiries':r'inquiries\s*[:=]\s*(\d+)',
    'outstanding':r'outstanding\s*[:=]\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)',
}
def extract(path:Path):
    pages=[]; method='text'; notices=[]
    if path.suffix=='.txt': pages=[path.read_text(encoding='utf-8')]
    elif path.suffix=='.pdf':
        with pymupdf.open(path) as doc:
            if doc.is_encrypted: raise ValueError('Encrypted PDFs are not supported')
            if len(doc)>50: raise ValueError('Maximum 50 PDF pages')
            for page in doc:
                text=page.get_text()
                if not text.strip():
                    if shutil.which('tesseract'):
                        with tempfile.TemporaryDirectory(dir=path.parent) as folder:
                            image=Path(folder)/'page.png'; page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(image)
                            text=subprocess.run(['tesseract',str(image),'stdout'],capture_output=True,text=True,timeout=30,check=True).stdout
                            method='ocr'
                    else: notices.append(f'Page {page.number+1}: image-only; Tesseract not installed, manual review required')
                pages.append(text)
    else:
        if not shutil.which('tesseract'): raise ValueError('Image OCR requires Tesseract; upload a text PDF or TXT instead')
        pages=[subprocess.run(['tesseract',str(path),'stdout'],capture_output=True,text=True,timeout=30,check=True).stdout];method='ocr'
    fields=[]
    for i,text in enumerate(pages):
        for key,pattern in PATTERNS.items():
            for match in re.finditer(pattern,text,re.I):
                fields.append(dict(key=key,value=match.group(1).strip().replace(',',''),page=i+1,evidence=match.group(0),confidence=.7 if method=='ocr' else .9))
    return '\n'.join(pages),fields,method,notices

def credit_accounts(text):
    """Supported explicit format, no inferred bureau fields or accounts."""
    accounts=[]
    for line in text.splitlines():
        if not line.strip().lower().startswith('account:'):continue
        values=[v.strip() for v in line.split(':',1)[1].split('|')]
        if len(values)!=7:raise ValueError('Account rows need 7 pipe-separated values: creditor | type | outstanding | limit | monthly payment | days past due | history')
        creditor,kind,outstanding,limit,payment,dpd,history=values
        numbers=[float(v.replace(',','')) for v in (outstanding,limit,payment)]
        if any(not __import__('math').isfinite(v) or v<0 for v in numbers) or not 0<=int(dpd)<=1000:raise ValueError('Invalid credit account amounts or days past due')
        accounts.append(dict(creditor=creditor,account_type=kind,outstanding=numbers[0],credit_limit=numbers[1],monthly_payment=numbers[2],days_past_due=int(dpd),history=history,source_line=line))
    return accounts
