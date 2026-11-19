// Freigaben werden am Server geprüft: Plus & Report übernehmen nach Freigabe die produktive Arbeitsbuch-Anbindung,
// sofern sie nicht per PLUS_ENABLED=0 / REPORT_ENABLED=0 ausdrücklich deaktiviert wurden.
export function releaseError(item: string, env: Record<string, string | undefined>): string | null {
  const flag = item === 'workbook' ? 'WORKBOOK_ENABLED' : item === 'report' ? 'REPORT_ENABLED' : 'PLUS_ENABLED';
  const liveReady = env.WORKBOOK_ENABLED === '1' && env.MANAGED_PAYMENTS === '1' && env.TOS_CONSENT === '1';
  if (env[flag] === '0') return 'not_available';
  if (item === 'workbook') {
    if (env.WORKBOOK_ENABLED !== '1') return 'not_available';
    if (!liveReady) return 'workbook_setup_incomplete';
    return null;
  }
  if (env[flag] === '1' || liveReady) return null;
  return 'not_available';
}
