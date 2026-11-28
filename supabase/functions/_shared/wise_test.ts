import { assertEquals, assertMatch } from "jsr:@std/assert@1";
import {
  buildWiseReference,
  extractWiseReference,
  resolveWiseInstruction,
  verifyWiseSignature,
  wiseCatalogItem,
  wiseEnabledError,
} from "./wise.ts";

Deno.test("wise gating blocks when WISE_ENABLED != 1 or unconfigured", () => {
  assertEquals(wiseEnabledError({}), "wise_not_enabled");
  assertEquals(wiseEnabledError({ WISE_ENABLED: "0" }), "wise_not_enabled");
  assertEquals(wiseEnabledError({ WISE_ENABLED: "1" }), "wise_not_configured");
  assertEquals(
    wiseEnabledError({ WISE_ENABLED: "1", WISE_ACCOUNT_IBAN: "BE00123456789012", WISE_ACCOUNT_HOLDER: "FreedomByDan LLC" }),
    null,
  );
});

Deno.test("wise catalog & reference formatting", () => {
  const wb = wiseCatalogItem("workbook");
  assertEquals(wb?.item.amountCents, 999);
  assertEquals(wb?.item.needsUser, false);
  const wl = wiseCatalogItem("whitelabel_pro_yearly");
  assertEquals(wl?.item.amountCents, 46800);
  assertEquals(wiseCatalogItem("unknown_xyz"), null);

  const ref = buildWiseReference("WB", new Uint8Array([0xab, 0xcd, 0x12, 0x34]));
  assertEquals(ref, "GK-WISE-WB-ABCD1234");
  assertMatch(buildWiseReference("WLPY"), /^GK-WISE-WLPY-[0-9A-F]{8}$/);
  assertEquals(extractWiseReference("Payment for GK-WISE-WB-ABCD1234 thanks"), "GK-WISE-WB-ABCD1234");
  assertEquals(extractWiseReference("No ref here"), null);
});

Deno.test("wise instruction prefers verified wise.com payment link, falls back to IBAN", () => {
  const wb = wiseCatalogItem("workbook")!;
  const linkRes = resolveWiseInstruction("workbook", wb.item, "GK-WISE-WB-11223344", {
    WISE_PAYMENT_LINKS_JSON: JSON.stringify({ workbook: "https://wise.com/pay/business/freedombydan" }),
  });
  assertEquals(linkRes?.mode, "payment_link");
  assertEquals(linkRes?.url, "https://wise.com/pay/business/freedombydan");

  // Reject non-wise.com URLs and fall back to IBAN
  const bankRes = resolveWiseInstruction("workbook", wb.item, "GK-WISE-WB-11223344", {
    WISE_PAYMENT_LINKS_JSON: JSON.stringify({ workbook: "https://evil.example/pay" }),
    WISE_ACCOUNT_IBAN: "BE68 5390 0754 7034",
    WISE_ACCOUNT_HOLDER: "FreedomByDan LLC",
    WISE_ACCOUNT_BIC: "TRWIBEB1XXX",
  });
  assertEquals(bankRes?.mode, "bank_transfer");
  assertEquals(bankRes?.iban, "BE68539007547034");
  assertEquals(bankRes?.bic, "TRWIBEB1XXX");
});

Deno.test("wise webhook RSA-SHA256 signature verification accepts valid and rejects tampered payloads", async () => {
  const kp = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true,
    ["sign", "verify"],
  );
  const spki = await crypto.subtle.exportKey("spki", kp.publicKey);
  const b64Key = btoa(String.fromCharCode(...new Uint8Array(spki)));
  const pem = `-----BEGIN PUBLIC KEY-----\n${b64Key}\n-----END PUBLIC KEY-----`;

  const payload = JSON.stringify({ event_type: "balances#credit", data: { amount: 9.99, currency: "EUR", reference: "GK-WISE-WB-ABCD1234" } });
  const sigBuf = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", kp.privateKey, new TextEncoder().encode(payload));
  const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sigBuf)));

  assertEquals(await verifyWiseSignature(payload, sigB64, pem), true);
  assertEquals(await verifyWiseSignature(payload + " ", sigB64, pem), false);
  assertEquals(await verifyWiseSignature(payload, "", pem), false);
});
