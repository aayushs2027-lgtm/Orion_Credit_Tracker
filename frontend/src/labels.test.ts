import {describe,it,expect} from 'vitest';
import {displayLabel} from './labels';
describe('Consistent interface labels',()=>{
 it('humanizes stored workflow and finding names',()=>{expect(displayLabel('pending_review')).toBe('Pending Review');expect(displayLabel('address_conflict')).toBe('Address Conflict');expect(displayLabel('manager_approved')).toBe('Manager Approved')});
 it('preserves finance acronyms',()=>{expect(displayLabel('annual EBITDA (INR)')).toBe('Annual EBITDA (INR)');expect(displayLabel('PD × LGD × EAD')).toBe('PD × LGD × EAD')});
});
