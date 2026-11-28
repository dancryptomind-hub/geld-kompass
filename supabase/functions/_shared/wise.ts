// Geld-Kompass Pro · Wise Business Helfer (zusätzliche Zahlungsalternative neben Stripe).
// Alle Zugangsdaten (WISE_ENABLED, WISE_PAYMENT_LINKS_JSON, WISE_ACCOUNT_IBAN, WISE_ACCOUNT_HOLDER, WISE_ACCOUNT_BIC, WISE_WEBHOOK_PUBLIC_KEY)
// kommen ausschließlich aus Supabase-Secrets — niemals aus dem Repository.

export interface WiseCatalogItem {
  code: string;
  amountCents: number;
  currency: "EUR";
  needsUser: boolean;
  labelDe: string;
  labelEn: string;
}

export const WISE_CATALOG: Record<string, WiseCatalogItem> = {
  workbook: {
    code: "WB",
    amountCents: 999,
    currency: "EUR",
    needsUser: false,
    labelDe: "Arbeitsbuch (PDF)",
    labelEn: "Workbook (PDF)",
  },
  report: {
    code: "FR",
    amountCents: 1499,
    currency: "EUR",
    needsUser: false,
    labelDe: "Freiheits-Report (PDF)",
    labelEn: "Freedom Report (PDF)",
  },
  plus_yearly: {
    code: "P1Y",
    amountCents: 3900,
    currency: "EUR",
    needsUser: true,
    labelDe: "Geld-Kompass Plus (1 Jahr)",
    labelEn: "Money Compass Plus (1 year)",
  },
  plus_5y: {
    code: "P5Y",
    amountCents: 14900,
    currency: "EUR",
    needsUser: true,
    labelDe: "Geld-Kompass Plus (5-Jahres-Pass)",
    labelEn: "Money Compass Plus (5-year pass)",
  },
  plus_10y: {
    code: "P10Y",
    amountCents: 24900,
    currency: "EUR",
    needsUser: true,
    labelDe: "Geld-Kompass Plus (10-Jahres-Pass)",
    labelEn: "Money Compass Plus (10-year pass)",
  },
  whitelabel_pro_yearly: {
    code: "WLPY",
    amountCents: 46800,
    currency: "EUR",
    needsUser: false,
    labelDe: "White-Label Pro (jährlich)",
    labelEn: "White-Label Pro (annual)",
  },
  whitelabel_pro_monthly: {
    code: "WLPM",
    amountCents: 4900,
    currency: "EUR",
    needsUser: false,
    labelDe: "White-Label Pro (monatlich)",
    labelEn: "White-Label Pro (monthly)",
  },
  whitelabel_team_yearly: {
    code: "WLTY",
    amountCents: 142800,
    currency: "EUR",
    needsUser: false,
    labelDe: "White-Label Kanzlei & Teams (jährlich)",
    labelEn: "White-Label Teams (annual)",
  },
  whitelabel_team_monthly: {
    code: "WLTM",
    amountCents: 14900,
    currency: "EUR",
    needsUser: false,
    labelDe: "White-Label Kanzlei & Teams (monatlich)",
    labelEn: "White-Label Teams (monthly)",
  },
};

export type WiseEnv = Record<string, string | undefined>;

export function wiseCatalogItem(name: unknown): { key: string; item: WiseCatalogItem } | null {
  const k = typeof name === "string" ? name : "";
  return Object.prototype.hasOwnProperty.call(WISE_CATALOG, k)
    ? { key: k, item: WISE_CATALOG[k] }
    : null;
}

export function wiseEnabledError(env: WiseEnv): string | null {
  if (env.WISE_ENABLED !== "1") return "wise_not_enabled";
  const hasLinks = Boolean(env.WISE_PAYMENT_LINKS_JSON && env.WISE_PAYMENT_LINKS_JSON.trim().startsWith("{"));
  const hasIban = Boolean(env.WISE_ACCOUNT_IBAN && env.WISE_ACCOUNT_HOLDER);
  if (!hasLinks && !hasIban) return "wise_not_configured";
  return null;
}

export function buildWiseReference(itemCode: string, randomBytes?: Uint8Array): string {
  const bytes = randomBytes ?? crypto.getRandomValues(new Uint8Array(4));
  const hex = Array.from(bytes.slice(0, 4), (b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  return `GK-WISE-${itemCode}-${hex}`;
}

export function extractWiseReference(text: unknown): string | null {
  if (typeof text !== "string") return null;
  const m = text.toUpperCase().match(/\bGK-WISE-[A-Z0-9]{2,6}-[0-9A-F]{8}\b/);
  return m ? m[0] : null;
}

export interface WiseCheckoutInstruction {
  provider: "wise";
  mode: "payment_link" | "bank_transfer";
  item: string;
  reference: string;
  amount_eur: number;
  amount_cents: number;
  currency: "EUR";
  url?: string;
  beneficiary?: string;
  iban?: string;
  bic?: string;
}

export function resolveWiseInstruction(
  itemKey: string,
  item: WiseCatalogItem,
  reference: string,
  env: WiseEnv,
): WiseCheckoutInstruction | null {
  if (env.WISE_PAYMENT_LINKS_JSON) {
    try {
      const links = JSON.parse(env.WISE_PAYMENT_LINKS_JSON) as Record<string, unknown>;
      const rawUrl = links[itemKey];
      if (typeof rawUrl === "string" && /^https:\/\/(wise\.com|pay\.wise\.com)\//.test(rawUrl)) {
        return {
          provider: "wise",
          mode: "payment_link",
          item: itemKey,
          reference,
          amount_eur: Number((item.amountCents / 100).toFixed(2)),
          amount_cents: item.amountCents,
          currency: item.currency,
          url: rawUrl,
        };
      }
    } catch {
      // Ungültiges JSON fällt sicher auf Banküberweisung zurück (falls konfiguriert).
    }
  }
  const iban = (env.WISE_ACCOUNT_IBAN || "").replace(/\s+/g, "").toUpperCase();
  const holder = (env.WISE_ACCOUNT_HOLDER || "").trim();
  const bic = (env.WISE_ACCOUNT_BIC || "").replace(/\s+/g, "").toUpperCase();
  if (iban && holder) {
    return {
      provider: "wise",
      mode: "bank_transfer",
      item: itemKey,
      reference,
      amount_eur: Number((item.amountCents / 100).toFixed(2)),
      amount_cents: item.amountCents,
      currency: item.currency,
      beneficiary: holder,
      iban,
      ...(bic ? { bic } : {}),
    };
  }
  return null;
}

function pemToDer(pem: string): ArrayBuffer {
  const b64 = pem
    .replace(/-----BEGIN PUBLIC KEY-----/g, "")
    .replace(/-----END PUBLIC KEY-----/g, "")
    .replace(/\s+/g, "");
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

function base64ToBytes(b64: string): Uint8Array<ArrayBuffer> {
  const bin = atob(b64.trim());
  const buf = new ArrayBuffer(bin.length);
  const out = new Uint8Array(buf);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

/** Verifiziert Wise Business Webhook-Signatur (X-Signature-SHA256, RSA-PKCS1-v1_5 + SHA-256). */
export async function verifyWiseSignature(
  rawBody: string,
  signatureBase64: string,
  publicKeyPem: string,
): Promise<boolean> {
  if (!signatureBase64 || !publicKeyPem) return false;
  try {
    const key = await crypto.subtle.importKey(
      "spki",
      pemToDer(publicKeyPem),
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false,
      ["verify"],
    );
    return await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5",
      key,
      base64ToBytes(signatureBase64),
      new TextEncoder().encode(rawBody),
    );
  } catch {
    return false;
  }
}
