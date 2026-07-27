const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");
const fs = require("fs");

(async () => {
  const base = __dirname;
  const chromeCandidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ];
  const executablePath = chromeCandidates.find((candidate) => fs.existsSync(candidate));
  const browser = await chromium.launch({ headless: true, executablePath });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1.5,
  });

  await page.goto(pathToFileURL(path.join(base, "chart-source.html")).href);
  await page.evaluate(() => document.fonts.ready);

  for (const figure of await page.locator(".page").all()) {
    const name = await figure.getAttribute("data-name");
    await figure.screenshot({
      path: path.join(base, `${name}.png`),
      type: "png",
    });
  }

  await browser.close();
})();
