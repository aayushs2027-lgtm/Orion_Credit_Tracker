import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
const password=readFileSync('../.env','utf8').split('\n').find(x=>x.startsWith('ORION_ADMIN_PASSWORD='))!.split('=').slice(1).join('=').trim();

test('Address evidence escalation, verification and manager sign-off',async({page})=>{
 await page.goto('/');await page.getByLabel('Password',{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in securely'}).click();
 await expect(page.locator('main h1')).toBeVisible();
 const name='Synthetic Browser Address '+Date.now();
 const customer=await (await page.request.post('/api/customers',{data:{kind:'personal',name,identity:name,address:'10 Synthetic Master Road',financial:{income:150000,credit_score:780}}})).json();
 const application=await (await page.request.post('/api/applications',{data:{customer_id:customer.id,amount:500000,rate:12,months:60}})).json();
 await page.request.post(`/api/applications/${application.id}/documents`,{multipart:{file:{name:'synthetic-address-proof.txt',mimeType:'text/plain',buffer:Buffer.from('SYNTHETIC DEMONSTRATION\nAddress: 90 Synthetic Other Road')}}});
 const detail=await (await page.request.get(`/api/applications/${application.id}`)).json();const field=detail.documents[0].fields[0];
 await page.request.patch(`/api/fields/${field.id}`,{data:{value:field.value,status:'accepted'}});
 await page.reload();await page.getByLabel('Active application').selectOption(String(application.id));await page.locator('nav a').nth(13).click();
 const finding=page.locator('.investigation').filter({hasText:name});await expect(finding).toHaveCount(1);
 await finding.locator('select').first().selectOption('escalated');await finding.getByLabel(/Escalation team/i).selectOption('Identity Verification');await finding.locator('textarea').fill('Synthetic address evidence sent for a dated residence check');await finding.getByRole('button',{name:'Save Investigation'}).click();await expect(finding.locator('.badge')).toHaveText('Escalated');
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/consistency-workbench.png',fullPage:true});
 await finding.locator('select').first().selectOption('verified');await finding.locator('textarea').fill('Verified synthetic dated address proof and recorded residential move');await finding.getByRole('button',{name:'Save Investigation'}).click();await expect(finding.locator('.badge')).toHaveText('Verified');
 await finding.locator('select').first().selectOption('manager_approved');await finding.locator('textarea').fill('Manager accepts verified synthetic residence evidence');await finding.getByRole('button',{name:'Save Investigation'}).click();await expect(finding.locator('.badge')).toHaveText('Manager Approved');await expect(finding.locator('textarea')).toHaveCount(0);
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/consistency-mobile.png',fullPage:true});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});

test('Business annual revenue comparison creates a visible review finding',async({page})=>{
 await page.goto('/');await page.getByLabel('Password',{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in securely'}).click();await expect(page.locator('main h1')).toBeVisible();
 const name='Synthetic Browser Revenue '+Date.now();
 const customer=await (await page.request.post('/api/customers',{data:{kind:'business',name,identity:name,address:'20 Synthetic Business Park',financial:{revenue:50000000,cash_flow:6000000,ebitda:8000000,credit_score:760}}})).json();
 const application=await (await page.request.post('/api/applications',{data:{customer_id:customer.id,amount:5000000,rate:12,months:60}})).json();
 await page.reload();await page.getByLabel('Active application').selectOption(String(application.id));await page.locator('nav a').nth(5).click();
 await page.getByLabel('Previous Year Revenue (INR)',{exact:true}).fill('10000000');await page.getByLabel('Previous Reporting Year',{exact:true}).fill('2024');await page.getByLabel('Current Reporting Year',{exact:true}).fill('2025');await page.getByRole('button',{name:'Save financial snapshot'}).click();
 await expect(page.getByRole('status')).toContainText('Financial snapshot saved');await expect(page.locator('.flag-row').filter({hasText:'400.0% growth'})).toBeVisible();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/revenue-verification.png',fullPage:true});await page.getByRole('button',{name:'Review Findings'}).click();await expect(page.locator('.investigation').filter({hasText:name})).toContainText('400.0% growth');
});
test('Executive navigation, intake, inference, review and exports',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.getByLabel(new RegExp('Password','i'),{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in securely'}).click();
 await expect(page.getByRole('heading',{name:new RegExp('Institutional\\ Command\\ Center','i')})).toBeVisible();
 await expect(page.getByText('Assessed Exposure',{exact:true})).toBeVisible();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/command-center.png',fullPage:true});
 const links=page.locator('nav a');await expect(links).toHaveCount(16);
 for(let i=0;i<16;i++){await links.nth(i).click();await expect(page.locator('main h1')).toBeVisible();await expect(page.locator('main')).not.toContainText('Select a case and run underwriting');}
 await links.nth(14).click();await expect(page.getByRole('heading',{name:new RegExp('Held\\-out\\ candidate\\ benchmark','i')})).toBeVisible();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/governance.png',fullPage:true});
 await links.nth(1).click();const id=Date.now();
 await page.getByLabel(new RegExp('Legal\\ full\\ name','i'),{exact:true}).fill('Browser Demo '+id);
 await page.getByLabel(new RegExp('Identity\\ /\\ registration\\ ID','i')).fill('E2E-'+id);
 await page.getByLabel(new RegExp('Registered\\ address','i'),{exact:true}).fill('42 Fictional Browser Road');
 await page.getByRole('button',{name:'Save & continue'}).click();
 await expect(page.getByRole('heading',{name:/Step 2: Upload/i})).toBeVisible();
 await page.getByLabel(new RegExp('Upload\\ document','i')).setInputFiles({name:'browser-report.txt',mimeType:'text/plain',buffer:Buffer.from('Monthly income: INR 150,000\nCredit score: 780\n')});
 await expect(page.getByText('browser-report.txt',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Review extracted fields'}).click();
 await page.getByRole('button',{name:'Accept',exact:true}).first().click();await expect(page.getByRole('status')).toContainText('Field reviewed');
 await page.getByRole('button',{name:'Apply accepted fields'}).click();await expect(page.getByRole('status')).toContainText('Reviewed fields applied');
 await page.getByRole('button',{name:'Run entity resolution'}).click();await page.getByRole('button',{name:'Continue to underwriting'}).click();
 await page.getByRole('button',{name:'Launch case & begin underwriting'}).click();
 await expect(page.getByRole('heading',{name:new RegExp('Personal\\ Credit\\ Underwriting\\ \\&\\ ML\\ Risk\\ Intelligence','i')})).toBeVisible();
 await expect(page.getByText('Model PD',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Human review',exact:true}).click();
 await page.getByLabel(new RegExp('Reason\\ \\(minimum\\ 10\\ characters\\)','i')).fill('Browser test verified fictional capacity and supporting evidence');
 await page.getByLabel(new RegExp('Credit\\ override\\ \\(administrator\\ only\\)','i')).check();await page.getByRole('button',{name:'Record decision'}).click();
 await expect(page.getByRole('status')).toContainText('Human decision and audit record saved');
 await links.nth(15).click();await expect(page.getByText('Integrity Verified',{exact:true})).toBeVisible();
 const download=page.waitForEvent('download');await page.getByRole('link',{name:'Export audit log JSON'}).click();expect((await download).suggestedFilename()).toBe('orion-audit.json');
 await links.nth(2).click();await page.getByLabel(new RegExp('Search\\ customers','i')).fill('Browser Demo '+id);await expect(page.locator('tbody tr')).toHaveCount(1);
 expect(errors).toEqual([]);
});
test('Mobile navigation and actual scenario calculation',async({page})=>{
 await page.goto('/');await page.getByLabel(new RegExp('Password','i'),{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in securely'}).click();
 await page.getByLabel(new RegExp('Active\\ application','i')).selectOption('8');await page.locator('nav a').nth(9).click();
 await page.getByLabel(new RegExp('Revenue\\ change\\ \\(%\\)','i'),{exact:true}).fill('-20');await page.getByRole('button',{name:'Run stress & Monte Carlo'}).click();
 await expect(page.getByText('Stressed Expected Loss',{exact:true})).toBeVisible();
 await page.setViewportSize({width:780,height:1000});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/screenshots/scenario-mobile.png',fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});
test('Business intake, collateral, tree inference and report import',async({page})=>{
 await page.goto('/');await page.getByLabel(new RegExp('Password','i'),{exact:true}).fill(password);await page.getByRole('button',{name:'Sign in securely'}).click();
 await page.locator('nav a').nth(1).click();await page.getByRole('button',{name:'Business / commercial',exact:true}).click();
 const id=Date.now();await page.getByLabel(new RegExp('Registered\\ business\\ name','i')).fill('Browser Business '+id);await page.getByLabel(new RegExp('Identity\\ /\\ registration\\ ID','i')).fill('BIZ-'+id);await page.getByLabel(new RegExp('Registered\\ address','i'),{exact:true}).fill('10 Fictional Industrial Estate');
 await page.getByLabel(new RegExp('Annual\\ revenue\\ \\(INR\\)','i'),{exact:true}).fill('24000000');await page.getByLabel(new RegExp('Annual\\ EBITDA\\ \\(INR\\)','i'),{exact:true}).fill('4000000');await page.getByLabel(new RegExp('Annual\\ cash\\ flow\\ for\\ debt\\ service\\ \\(INR\\)','i'),{exact:true}).fill('3200000');await page.getByLabel(new RegExp('Secured\\ facility\\ \\(register\\ collateral\\ in\\ Collateral\\ Lab\\)','i')).check();
 await page.getByRole('button',{name:'Save & continue'}).click();await expect(page.getByRole('heading',{name:/Step 2: Upload/i})).toBeVisible();
 await page.getByLabel(new RegExp('Upload\\ document','i')).setInputFiles({name:'business-bureau.txt',mimeType:'text/plain',buffer:Buffer.from('Credit score: 740\nInquiries: 1\nAccount: Demo Business Bank | Term loan | 100000 | 200000 | 5000 | 0 | 000000\n')});await expect(page.getByText('business-bureau.txt',{exact:true})).toBeVisible();
 await page.locator('nav a').nth(7).click();await page.getByLabel(new RegExp('Market\\ value\\ \\(INR\\)','i')).fill('2000000');await page.getByLabel(new RegExp('Valuation\\ date','i')).fill('2026-10-01');await page.getByRole('button',{name:'Add asset',exact:true}).click();await expect(page.getByRole('status')).toContainText('Collateral saved');
 await page.locator('nav a').nth(5).click();await page.getByLabel(new RegExp('Assessment\\ algorithm','i')).selectOption('XGBoost');await page.getByRole('button',{name:'Run assessment',exact:true}).click();await expect(page.getByRole('status')).toContainText('Assessment saved');
 await expect(page.getByText('Debt Service Coverage',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Import reviewed credit accounts'}).click();await expect(page.getByRole('status')).toContainText('Reviewed credit accounts imported');await expect(page.getByRole('cell',{name:'Demo Business Bank',exact:true})).toBeVisible();
 await page.locator('nav a').nth(12).click();await expect(page.getByRole('heading',{name:/SHAP attribution/i})).toBeVisible();
 await page.locator('nav a').nth(5).click();await page.reload();await expect(page.getByRole('heading',{name:new RegExp('Business\\ Credit\\ Underwriting\\ \\&\\ Financial\\ Analysis','i')})).toBeVisible();
});
