// Optional visual verification: requires Playwright and an installed Chromium.
const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");

(async () => {
  const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:8080";
  const output = process.env.QA_OUTPUT || ".qa";
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROMIUM_PATH
      ? { executablePath: process.env.CHROMIUM_PATH }
      : {}),
  });
  const routes = [
    "",
    "products/ledglet/",
    "support/",
    "privacy/",
    "products/ledglet/privacy/",
    "products/ledglet/terms/",
    "products/ledglet/legal-history/",
    "products/ledglet/legal-history/2026-11-08/privacy/",
  ];
  const results = [];
  try {
    for (const [label, width, height, scheme] of [
      ["desktop", 1440, 1100, "light"],
      ["mobile", 390, 844, "light"],
      ["compact-dark", 320, 740, "dark"],
    ]) {
      const context = await browser.newContext({
        viewport: { width, height },
        colorScheme: scheme,
      });
      const page = await context.newPage();
      const failures = [];
      page.on("pageerror", (error) => failures.push(error.message));
      page.on("request", (request) => {
        if (!request.url().startsWith(origin))
          failures.push(`Unexpected network request: ${request.url()}`);
      });
      for (const lang of ["en", "uk", "ru"]) {
        const prefix = lang === "en" ? "/" : `/${lang}/`;
        for (const route of routes) {
          const url = prefix + route;
          const response = await page.goto(origin + url, { waitUntil: "load" });
          if (response.status() !== 200)
            throw new Error(`HTTP ${response.status()} at ${url}`);
          if ((await page.locator("h1").count()) !== 1)
            throw new Error(`Missing unique h1: ${url}`);
          if ((await page.locator("html").getAttribute("lang")) !== lang)
            throw new Error(`Wrong language: ${url}`);
          const overflow = await page.evaluate(
            () => document.documentElement.scrollWidth > innerWidth + 1,
          );
          if (overflow)
            throw new Error(`Horizontal overflow at ${width}px: ${url}`);
          const links = page.locator(".languages a");
          for (let i = 0; i < 3; i++) {
            const expectedPrefix = i === 0 ? "/" : `/${["en", "uk", "ru"][i]}/`;
            if (
              (await links.nth(i).getAttribute("href")) !==
              expectedPrefix + route
            )
              throw new Error(`Language loses document: ${url}`);
          }
          results.push({ url, width, scheme, status: response.status() });
        }
      }
      await page.goto(origin + "/", { waitUntil: "load" });
      await page.keyboard.press("Tab");
      if ((await page.locator(":focus").getAttribute("href")) !== "#main")
        throw new Error("Keyboard skip link unavailable");
      const screenshotRoute =
        label === "desktop"
          ? "/"
          : label === "mobile"
            ? "/uk/products/ledglet/"
            : "/ru/products/ledglet/terms/";
      await page.goto(origin + screenshotRoute, { waitUntil: "load" });
      await page.screenshot({
        path: path.join(output, `${label}.png`),
        fullPage: true,
      });
      if (failures.length) throw new Error(failures.join("\n"));
      await context.close();
    }
    fs.writeFileSync(
      path.join(output, "browser-results.json"),
      JSON.stringify({ pages: results.length, results }, null, 2) + "\n",
    );
    console.log(
      `PASS: ${results.length} page/viewport/theme checks; language destinations, keyboard skip link, no overflow, no third-party requests.`,
    );
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
