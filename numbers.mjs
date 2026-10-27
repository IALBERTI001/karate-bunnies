// Player-facing number display: no commas; large values compact (1K, 1.04K, 12.5K, 3.2M).
// Shared by every screen so counts look the same everywhere.
const UNITS = ['', 'K', 'M', 'B', 'T'];

export function formatCount(value) {
  const n = Math.floor(Number(value));
  if (!Number.isFinite(n)) return '0';
  if (n < 0) return '-' + formatCount(-n);
  if (n < 1000) return String(n);
  let unit = 0;
  let scaled = n;
  while (scaled >= 1000 && unit < UNITS.length - 1) { scaled /= 1000; unit++; }
  // Three significant digits, rounded down so a player never sees more than they have.
  const decimals = scaled >= 100 ? 0 : scaled >= 10 ? 1 : 2;
  const factor = 10 ** decimals;
  let shown = Math.floor(scaled * factor) / factor;
  if (shown >= 1000 && unit < UNITS.length - 1) { shown = 1; unit++; }
  return shown.toFixed(decimals).replace(/\.?0+$/, '') + UNITS[unit];
}
