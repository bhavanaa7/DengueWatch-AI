import { fmt, toCsv } from './format';

describe('format utils', () => {
  it('formats missing values with a dash', () => { expect(fmt(null)).toBe('—'); expect(fmt(2.345, 2)).toBe('2.35'); });
  it('builds csv with header', () => { expect(toCsv([{ a: 1, b: 'x' }])).toBe('a,b\n1,"x"'); expect(toCsv([])).toBe(''); });
});
