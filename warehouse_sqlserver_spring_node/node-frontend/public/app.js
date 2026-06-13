const API = "http://127.0.0.1:8080/api";

function money(value) {
  return Number(value || 0).toLocaleString("pl-PL", { maximumFractionDigits: 2 });
}

async function get(path) {
  const response = await fetch(API + path);
  if (!response.ok) {
    throw new Error("API error");
  }
  return response.json();
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function bars(id, rows, labelField, valueField) {
  const box = document.getElementById(id);
  const max = Math.max(...rows.map(row => Number(row[valueField] || 0)), 1);
  box.innerHTML = rows.map(row => {
    const value = Number(row[valueField] || 0);
    const width = Math.max((value / max) * 100, 4);
    return `
      <div class="bar-row">
        <div class="bar-label">
          <span>${row[labelField]}</span>
          <strong>${money(value)}</strong>
        </div>
        <div class="bar"><div style="width:${width}%"></div></div>
      </div>
    `;
  }).join("");
}

function sourceRows(rows) {
  document.getElementById("sources").innerHTML = rows.map(row => `
    <tr>
      <td>${row.source_name}</td>
      <td>${money(row.records_loaded)}</td>
    </tr>
  `).join("");
}

async function start() {
  const summary = await get("/summary");
  const topDrugs = await get("/top-drugs");
  const manufacturers = await get("/manufacturers");
  const cities = await get("/cities");
  const sources = await get("/sources");

  setText("factRows", money(summary.fact_rows));
  setText("soldCount", money(summary.sold_count));
  setText("salesValue", money(summary.sales_value));
  setText("drugCount", money(summary.drug_count));

  bars("topDrugs", topDrugs, "drug_name", "sold_count");
  bars("manufacturers", manufacturers, "manufacturer_name", "sales_value");
  bars("cities", cities, "city_name", "sales_value");
  sourceRows(sources);
}

start().catch(error => {
  document.body.insertAdjacentHTML("beforeend", `<div class="error">Nie udalo sie pobrac danych: ${error.message}</div>`);
});
