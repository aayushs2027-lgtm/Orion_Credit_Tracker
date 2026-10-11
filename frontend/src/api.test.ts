import {describe,it,expect} from 'vitest';
import {money,percent,decimal} from './api';
describe('Financial display conventions',()=>{it('distinguishes missing denominators from zero',()=>{expect(percent(null)).toBe('N/A');expect(percent(0)).toBe('0.00%');expect(decimal(undefined)).toBe('N/A')});it('uses Indian rupees and accurate percentages',()=>{expect(money(100000)).toContain('1,00,000');expect(percent(.12345)).toBe('12.35%')})});
