import { describe, it, expect } from 'vitest'
import {
  formatLpa,
  formatInr,
  formatSampleSize,
  formatPercentage,
  formatExpRange,
} from './formatters'

describe('formatters', () => {
  it('formats LPA numbers accurately', () => {
    expect(formatLpa(8.54)).toBe('8.5 LPA')
    expect(formatLpa(14)).toBe('14.0 LPA')
    expect(formatLpa(null)).toBe('N/A')
    expect(formatLpa(undefined)).toBe('N/A')
  })

  it('formats INR currency values', () => {
    expect(formatInr(1200000)).toContain('12,00,000')
    expect(formatInr(null)).toBe('N/A')
  })

  it('formats sample sizes', () => {
    expect(formatSampleSize(412)).toBe('n = 412')
    expect(formatSampleSize(0)).toBe('n = 0')
    expect(formatSampleSize(null)).toBe('n = 0')
  })

  it('formats percentages to 1 decimal place', () => {
    expect(formatPercentage(52.74)).toBe('52.7%')
    expect(formatPercentage(0)).toBe('0.0%')
    expect(formatPercentage(null)).toBe('0.0%')
  })

  it('formats experience ranges', () => {
    expect(formatExpRange(0, 1)).toBe('0-1 yrs (Fresher)')
    expect(formatExpRange(3, 6)).toBe('3-6 yrs')
  })
})
