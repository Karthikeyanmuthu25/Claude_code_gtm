/**
 * ChartRenderer
 * Parses ```chart blocks from the Markdown report and generates a
 * standalone HTML file with inline Chart.js visualisations.
 *
 * Usage:
 *   node utils/chart-renderer.js reports/my-report.md
 *   → outputs reports/my-report.html
 */

import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ── Parse chart blocks from Markdown ─────────────────────────────────────────
function parseChartBlocks(markdown) {
  const blocks = [];
  const regex = /```chart\n([\s\S]*?)```/g;
  let match;
  let idx = 0;
  while ((match = regex.exec(markdown)) !== null) {
    try {
      const config = JSON.parse(match[1]);
      blocks.push({ id: `chart-${idx++}`, config, raw: match[0] });
    } catch (e) {
      console.warn(`⚠️  Failed to parse chart block ${idx}: ${e.message}`);
    }
  }
  return blocks;
}

// ── Replace chart blocks with HTML placeholder divs ──────────────────────────
function injectChartDivs(markdown, blocks) {
  let result = markdown;
  for (const block of blocks) {
    result = result.replace(
      block.raw,
      `<div class="chart-container" id="${block.id}-wrap"><canvas id="${block.id}"></canvas></div>`
    );
  }
  return result;
}

// ── Convert Markdown to basic HTML (lightweight, no deps) ────────────────────
function mdToHtml(md) {
  return md
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^---$/gm, "<hr>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
    .replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
    .replace(/\|(.+)\|/g, (row) => {
      const cells = row.split("|").filter(Boolean).map((c) => `<td>${c.trim()}</td>`).join("");
      return `<tr>${cells}</tr>`;
    })
    .replace(/(<tr>.*<\/tr>\n?)+/g, (m) => `<table>${m}</table>`)
    .replace(/\n{2,}/g, "</p><p>")
    .replace(/^(?!<[hupbtc])/gm, "");
}

// ── Generate Chart.js init script ────────────────────────────────────────────
function generateChartScripts(blocks) {
  return blocks
    .map(({ id, config }) => {
      const { type, title, xLabel, yLabel, data } = config;

      if (type === "scatter") {
        const datasets = data.datasets.map((d) => ({
          label: d.label,
          data: [{ x: d.x, y: d.y }],
          backgroundColor: d.color || "#6366f1",
          pointRadius: 10,
          pointHoverRadius: 14,
        }));
        return `
new Chart(document.getElementById('${id}'), {
  type: 'scatter',
  data: { datasets: ${JSON.stringify(datasets)} },
  options: {
    responsive: true,
    plugins: {
      title: { display: true, text: ${JSON.stringify(title)}, font: { size: 15, weight: '500' } },
      legend: { position: 'right' }
    },
    scales: {
      x: { title: { display: true, text: ${JSON.stringify(xLabel || "")} }, min: 0, max: 11 },
      y: { title: { display: true, text: ${JSON.stringify(yLabel || "")} }, min: 0, max: 11 }
    }
  }
});`;
      }

      if (type === "radar") {
        const datasets = data.datasets.map((d) => ({
          label: d.label,
          data: d.data,
          borderColor: d.color || "#6366f1",
          backgroundColor: (d.color || "#6366f1") + "33",
          pointBackgroundColor: d.color || "#6366f1",
        }));
        return `
new Chart(document.getElementById('${id}'), {
  type: 'radar',
  data: { labels: ${JSON.stringify(data.labels)}, datasets: ${JSON.stringify(datasets)} },
  options: {
    responsive: true,
    plugins: {
      title: { display: true, text: ${JSON.stringify(title)}, font: { size: 15, weight: '500' } }
    },
    scales: {
      r: { min: 0, max: 10, ticks: { stepSize: 2 }, grid: { color: '#e5e7eb' } }
    }
  }
});`;
      }

      // Line / bar
      const colors = data.datasets[0].colors || [data.datasets[0].color || "#6366f1"];
      const bgColors =
        type === "line"
          ? (data.datasets[0].color || "#6366f1") + "22"
          : data.labels.map((_, i) => colors[i % colors.length]);

      const datasets = data.datasets.map((d) => ({
        label: d.label,
        data: d.data,
        backgroundColor: bgColors,
        borderColor: d.color || colors[0] || "#6366f1",
        borderWidth: type === "line" ? 2.5 : 0,
        fill: type === "line",
        tension: 0.4,
        pointRadius: type === "line" ? 4 : 0,
      }));

      return `
new Chart(document.getElementById('${id}'), {
  type: '${type === "line" ? "line" : "bar"}',
  data: { labels: ${JSON.stringify(data.labels)}, datasets: ${JSON.stringify(datasets)} },
  options: {
    responsive: true,
    plugins: {
      title: { display: true, text: ${JSON.stringify(title)}, font: { size: 15, weight: '500' } },
      legend: { display: false }
    },
    scales: {
      x: { title: { display: true, text: ${JSON.stringify(xLabel || "")} }, grid: { display: false } },
      y: { title: { display: true, text: ${JSON.stringify(yLabel || "")} }, grid: { color: '#f3f4f6' } }
    }
  }
});`;
    })
    .join("\n");
}

// ── Build full HTML document ──────────────────────────────────────────────────
function buildHtml(bodyMd, blocks, title = "Market Sizing Report") {
  const bodyHtml = mdToHtml(bodyMd);
  const chartScripts = generateChartScripts(blocks);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 16px; line-height: 1.7; color: #1f2937; background: #f9fafb; }
    .wrapper { max-width: 860px; margin: 0 auto; padding: 40px 24px 80px; background: #fff; min-height: 100vh; }
    h1 { font-size: 2rem; font-weight: 700; color: #111827; margin: 32px 0 8px; border-bottom: 3px solid #6366f1; padding-bottom: 12px; }
    h2 { font-size: 1.4rem; font-weight: 600; color: #1f2937; margin: 40px 0 12px; }
    h3 { font-size: 1.1rem; font-weight: 600; color: #374151; margin: 24px 0 8px; }
    p { margin: 12px 0; color: #374151; }
    em { color: #6b7280; font-style: normal; display: block; margin: 4px 0 20px; }
    strong { color: #111827; }
    ul, ol { padding-left: 24px; margin: 12px 0; }
    li { margin: 6px 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
    th { background: #f3f4f6; text-align: left; padding: 10px 14px; font-weight: 600; border-bottom: 2px solid #e5e7eb; }
    td { padding: 10px 14px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }
    tr:hover td { background: #f9fafb; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 32px 0; }
    blockquote { border-left: 4px solid #6366f1; padding: 12px 20px; background: #f5f3ff; color: #4b5563; margin: 20px 0; border-radius: 0 8px 8px 0; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 14px; }
    a { color: #6366f1; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .chart-container { margin: 28px 0; padding: 24px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; }
    .chart-container canvas { max-height: 320px; }
    .footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 13px; color: #9ca3af; }
  </style>
</head>
<body>
<div class="wrapper">
${bodyHtml}
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
${chartScripts}
</script>
</body>
</html>`;
}

// ── Main export + CLI ─────────────────────────────────────────────────────────
export async function renderMarkdownToHtml(mdPath) {
  const markdown = await fs.readFile(mdPath, "utf8");
  const blocks = parseChartBlocks(markdown);
  const mdWithDivs = injectChartDivs(markdown, blocks);
  const title = markdown.match(/^# (.+)$/m)?.[1] || "Market Sizing Report";
  const html = buildHtml(mdWithDivs, blocks, title);

  const htmlPath = mdPath.replace(/\.md$/, ".html");
  await fs.writeFile(htmlPath, html, "utf8");
  console.log(`✅  HTML report with charts → ${htmlPath}`);
  return htmlPath;
}

// CLI usage
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const mdPath = process.argv[2];
  if (!mdPath) {
    console.error("Usage: node utils/chart-renderer.js <report.md>");
    process.exit(1);
  }
  await renderMarkdownToHtml(path.resolve(mdPath));
}
