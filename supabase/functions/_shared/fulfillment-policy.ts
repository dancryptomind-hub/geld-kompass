type Session = {mode: string | null; payment_status: string; metadata?: Record<string,string | undefined> | null};
export function purchaseProduct(s: Session): string | null {
  if (s.mode !== "payment" || !["paid", "no_payment_required"].includes(s.payment_status)) return null;
  if (s.metadata?.gk_item === "workbook") return "gk_workbook_de";
  if (s.metadata?.gk_item === "report") return "gk_freedom_report";
  return null;
}
