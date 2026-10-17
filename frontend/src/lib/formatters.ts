/**
 * frontend/src/lib/formatters.ts
 * Number and string formatting helpers following AGENTS.md conventions.
 */

export function formatLpa(val: number | null | undefined): string {
  if (val === null || val === undefined) return 'N/A'
  return `${val.toFixed(1)} LPA`
}

export function formatInr(val: number | null | undefined): string {
  if (val === null || val === undefined) return 'N/A'
  return `₹${val.toLocaleString('en-IN')}`
}

export function formatSampleSize(n: number | null | undefined): string {
  if (n === null || n === undefined) return 'n = 0'
  return `n = ${n.toLocaleString('en-IN')}`
}

export function formatPercentage(val: number | null | undefined): string {
  if (val === null || val === undefined) return '0.0%'
  return `${val.toFixed(1)}%`
}

export function formatExpRange(minExp: number, maxExp: number): string {
  if (minExp === 0 && maxExp <= 1) return '0-1 yrs (Fresher)'
  return `${minExp}-${maxExp} yrs`
}
