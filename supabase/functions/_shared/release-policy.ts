// Freigaben werden ausschließlich am Server gesetzt. Das Arbeitsbuch startet vor Plus/Report.
export function releaseError(item: string, env: Record<string, string | undefined>): string | null {
  const flag = item === 'workbook' ? 'WORKBOOK_ENABLED' : item === 'report' ? 'REPORT_ENABLED' : 'PLUS_ENABLED';
  if (env[flag] !== '1') return 'not_available';
  if (item === 'workbook' && (env.MANAGED_PAYMENTS !== '1' || env.TOS_CONSENT !== '1')) return 'workbook_setup_incomplete';
  return null;
}
