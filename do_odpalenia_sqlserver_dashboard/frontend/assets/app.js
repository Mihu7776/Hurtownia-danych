const filterIds = ["year", "city", "manufacturer", "drug", "type", "refunded"];

const money = new Intl.NumberFormat("pl-PL", {
  style: "currency",
  currency: "PLN",
  maximumFractionDigits: 0,
});
const number = new Intl.NumberFormat("pl-PL");
const decimal = new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 2 });

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function queryString() {
  const params = new URLSearchParams();
  for (const id of filterIds) {
    const value = document.getElementById(id).value;
    if (value) params.set(id, value);
  }
  return params.toString();
}

async function api(path, includeFilters = true) {
  const qs = includeFilters ? queryString() : "";
  const response = await fetch(qs ? `${path}?${qs}` : path);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}

function fillSelect(id, values, label = "Wszystkie") {
  const select = document.getElementById(id);
  const current = select.value;
  select.innerHTML = `<option value="">${label}</option>`;
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
  select.value = values.includes(current) ? current : "";
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function renderKpis(summary) {
  setText("kpiSales", money.format(summary.total_sales || 0));
  setText("kpiTransactions", number.format(summary.transactions || 0));
  setText("kpiAverage", money.format(summary.avg_price || 0));
  setText("kpiRefunds", `${decimal.format(summary.refund_rate || 0)}%`);
  const range = summary.date_from && summary.date_to ? `${summary.date_from} - ${summary.date_to}` : "";
  setText("dateRange", range);
  setText("dateRangeHero", range || "-");
  setText("kpiDrugs", number.format(summary.drug_count || 0));
  setText("kpiManufacturers", number.format(summary.manufacturer_count || 0));
  setText("kpiCities", number.format(summary.city_count || 0));
}

function renderLineChart(id, data) {
  const root = document.getElementById(id);
  if (!data.length) {
    root.innerHTML = '<p class="empty">Brak danych dla wybranych filtrow.</p>';
    return;
  }
  const width = 920;
  const height = 320;
  const pad = { top: 18, right: 18, bottom: 40, left: 58 };
  const values = data.map((item) => Number(item.total_sales || 0));
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const step = data.length > 1 ? (width - pad.left - pad.right) / (data.length - 1) : 0;
  const points = data.map((item, index) => {
    const x = pad.left + index * step;
    const y = height - pad.bottom - ((Number(item.total_sales || 0) - min) / range) * (height - pad.top - pad.bottom);
    return { x, y, label: item.label, value: item.total_sales };
  });
  const line = points.map((point, index) => `${index ? "L" : "M"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
  const area = `${line} L ${points.at(-1).x.toFixed(2)} ${height - pad.bottom} L ${points[0].x.toFixed(2)} ${height - pad.bottom} Z`;
  const tickEvery = Math.max(1, Math.ceil(data.length / 6));
  const ticks = points
    .filter((_, index) => index % tickEvery === 0 || index === points.length - 1)
    .map((point) => `<text class="axis-label" x="${point.x}" y="${height - 12}" text-anchor="middle">${escapeHtml(point.label)}</text>`)
    .join("");
  const yTicks = [0, 0.5, 1]
    .map((part) => {
      const y = height - pad.bottom - part * (height - pad.top - pad.bottom);
      const value = min + part * range;
      return `
        <line x1="${pad.left}" x2="${width - pad.right}" y1="${y}" y2="${y}" stroke="#ddd8cf" stroke-width="1" />
        <text class="axis-label" x="8" y="${y + 4}">${money.format(value)}</text>
      `;
    })
    .join("");
  const circles = points
    .map((point) => `<circle cx="${point.x}" cy="${point.y}" r="3.5"><title>${escapeHtml(point.label)}: ${money.format(point.value)}</title></circle>`)
    .join("");

  root.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Sprzedaz miesieczna" class="h-[320px] w-full">
      ${yTicks}
      <path d="${area}" fill="rgba(15, 139, 125, 0.14)"></path>
      <path d="${line}" fill="none" stroke="#0f8b7d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
      <g fill="#0f8b7d">${circles}</g>
      ${ticks}
    </svg>
  `;
}

function renderBars(id, data, valueKey, formatter) {
  const root = document.getElementById(id);
  if (!data.length) {
    root.innerHTML = '<p class="empty">Brak danych.</p>';
    return;
  }
  const max = Math.max(...data.map((item) => Number(item[valueKey] || 0)), 1);
  root.innerHTML = data
    .map((item) => {
      const value = Number(item[valueKey] || 0);
      const width = Math.max(2, (value / max) * 100);
      return `
        <div class="bar-row">
          <div class="bar-meta">
            <span class="bar-label" title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</span>
            <span class="bar-value">${formatter(value)}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="width: ${width}%"></div></div>
        </div>
      `;
    })
    .join("");
}

function renderRefundDonut(data) {
  const root = document.getElementById("refundDonut");
  const refunded = data.find((item) => item.label === "Refundowane") || { transactions: 0, total_sales: 0 };
  const notRefunded = data.find((item) => item.label === "Bez refundacji") || { transactions: 0, total_sales: 0 };
  const total = Number(refunded.transactions || 0) + Number(notRefunded.transactions || 0);
  const rate = total ? (Number(refunded.transactions || 0) / total) * 100 : 0;
  root.innerHTML = `
    <div class="donut-card">
      <div class="donut" style="--value: ${rate.toFixed(2)}">
        <div>
          <strong>${decimal.format(rate)}%</strong>
          <span>refundowane</span>
        </div>
      </div>
      <div class="donut-legend">
        <div><span>Refundowane</span><strong>${number.format(refunded.transactions || 0)}</strong></div>
        <div><span>Bez refundacji</span><strong>${number.format(notRefunded.transactions || 0)}</strong></div>
        <div><span>Wartosc refundowanych</span><strong>${money.format(refunded.total_sales || 0)}</strong></div>
      </div>
    </div>
  `;
}

function renderTypes(data) {
  const root = document.getElementById("drugTypes");
  if (!data.length) {
    root.innerHTML = '<p class="empty">Brak danych.</p>';
    return;
  }
  root.innerHTML = data
    .map(
      (item) => `
      <div class="type-card">
        <span>${escapeHtml(item.label)}</span>
        <strong>${money.format(item.total_sales || 0)}</strong>
        <small>${number.format(item.transactions || 0)} transakcji · srednio ${money.format(item.avg_price || 0)}</small>
      </div>
    `,
    )
    .join("");
}

function renderSources(summary) {
  const root = document.getElementById("sourceSummary");
  const items = summary.metadata || [];
  if (!items.length) {
    root.innerHTML = '<p class="empty">Brak metadanych zrodel.</p>';
    return;
  }
  root.innerHTML = items
    .map((item) => {
      const total = item.total_available ? ` / ${number.format(item.total_available)} total` : "";
      return `
        <div class="source-item">
          <strong>${escapeHtml(item.source_name)}</strong>
          <div>${number.format(item.records_loaded || 0)} loaded${total}</div>
          <a href="${escapeHtml(item.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source_url)}</a>
        </div>
      `;
    })
    .join("");
}

function renderRecords(data) {
  const body = document.getElementById("recordsBody");
  if (!data.length) {
    body.innerHTML = '<tr><td colspan="8" class="p-3 empty">Brak rekordow.</td></tr>';
    return;
  }
  body.innerHTML = data
    .map(
      (row) => `
      <tr class="hover:bg-stone-50">
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.sale_date)}</td>
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.city)}</td>
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.drug)}</td>
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.manufacturer)}</td>
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.drug_type)}</td>
        <td class="border-b border-stone-200 p-3">${escapeHtml(row.condition)}</td>
        <td class="border-b border-stone-200 p-3">${number.format(row.cntDrug || 0)}</td>
        <td class="border-b border-stone-200 p-3">${money.format(row.total_sales || 0)}</td>
      </tr>
    `,
    )
    .join("");
}

function renderProjectInfo(info) {
  document.getElementById("etlSteps").innerHTML = info.etl
    .map(
      (step, index) => `
      <div class="etl-step">
        <div class="text-xs font-black uppercase text-teal">Step ${index + 1}</div>
        <div class="mt-1 text-sm">${escapeHtml(step)}</div>
      </div>
    `,
    )
    .join("");
  document.getElementById("sqlFiles").innerHTML = info.sql_files
    .map(
      (file) => `
      <a class="sql-link" href="${escapeHtml(file.url)}" target="_blank" rel="noreferrer">
        <span>${escapeHtml(file.name)}</span>
        <i data-lucide="external-link" class="h-4 w-4"></i>
      </a>
    `,
    )
    .join("");
}

async function refreshDashboard() {
  const [summary, timeseries, drugs, manufacturers, cities, conditions, refunds, drugTypes, records, sourceSummary, labelers, reactions] =
    await Promise.all([
      api("/api/summary"),
      api("/api/timeseries"),
      api("/api/top-drugs"),
      api("/api/manufacturers"),
      api("/api/cities"),
      api("/api/conditions"),
      api("/api/refunds"),
      api("/api/drug-types"),
      api("/api/records"),
      api("/api/source-summary"),
      api("/api/source-labelers"),
      api("/api/source-reactions"),
    ]);
  renderKpis(summary);
  renderLineChart("lineChart", timeseries);
  renderBars("topDrugs", drugs, "total_sales", money.format);
  renderBars("manufacturers", manufacturers, "total_sales", money.format);
  renderBars("cities", cities, "total_sales", money.format);
  renderBars("conditions", conditions, "total_sales", money.format);
  renderRefundDonut(refunds);
  renderTypes(drugTypes);
  renderSources(sourceSummary);
  renderBars("labelers", labelers, "products", number.format);
  renderBars("reactions", reactions, "reports", number.format);
  renderRecords(records);
  if (window.lucide) window.lucide.createIcons();
}

async function init() {
  const [filters, projectInfo] = await Promise.all([api("/api/filters", false), api("/api/project-info", false)]);
  fillSelect("year", filters.years);
  fillSelect("city", filters.cities);
  fillSelect("manufacturer", filters.manufacturers);
  fillSelect("drug", filters.drugs);
  fillSelect("type", filters.types);
  renderProjectInfo(projectInfo);
  for (const id of filterIds) {
    document.getElementById(id).addEventListener("change", refreshDashboard);
  }
  document.getElementById("resetFilters").addEventListener("click", () => {
    for (const id of filterIds) document.getElementById(id).value = "";
    refreshDashboard();
  });
  await refreshDashboard();
}

init().catch((error) => {
  document.body.insertAdjacentHTML("afterbegin", `<div class="m-3 rounded-lg border border-red-300 bg-red-50 p-3 text-red-900">${escapeHtml(error.message)}</div>`);
});
