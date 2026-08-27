const manifestPath = "data/digests/manifest.json";

const state = {
  manifest: null,
  selectedDate: null
};

const els = {
  year: document.querySelector("#yearSelect"),
  month: document.querySelector("#monthSelect"),
  day: document.querySelector("#daySelect"),
  dailyHeadline: document.querySelector("#dailyHeadline"),
  digestTitle: document.querySelector("#digestTitle"),
  digestSummary: document.querySelector("#digestSummary"),
  reportDate: document.querySelector("#reportDate"),
  coverageDate: document.querySelector("#coverageDate"),
  generatedAt: document.querySelector("#generatedAt"),
  collectionCount: document.querySelector("#collectionCount"),
  impactFrameworkList: document.querySelector("#impactFrameworkList"),
  priorityList: document.querySelector("#priorityList"),
  status: document.querySelector("#statusMessage"),
  content: document.querySelector("#digestContent"),
  sectionTemplate: document.querySelector("#sectionTemplate"),
  itemTemplate: document.querySelector("#itemTemplate"),
  scoreDialog: document.querySelector("#scoreDialog"),
  scoreDialogBody: document.querySelector("#scoreDialogBody"),
  scoreDialogClose: document.querySelector(".score-dialog__close")
};

init();

async function init() {
  setupScoreDialog();
  try {
    const response = await fetch(manifestPath);
    if (!response.ok) throw new Error("manifest not found");
    state.manifest = await response.json();
    buildDatePicker();
    const publishableEntries = getPublishableDigestEntries();
    const initialDate = publishableEntries.find((entry) => entry.reportDate === state.manifest.latest)?.reportDate || publishableEntries[0]?.reportDate;
    await selectDate(initialDate);
  } catch (error) {
    showStatus("資料讀取失敗。請確認 data/digests/manifest.json 是否存在，或使用本機伺服器開啟網站。");
  }
}

function buildDatePicker() {
  const dates = getDigestDates();
  const years = unique(dates.map((date) => date.getFullYear())).sort((a, b) => b - a);

  fillSelect(els.year, years, (year) => `${year}`);
  syncMonthOptions();
  syncDayOptions();

  els.year.addEventListener("change", () => {
    syncMonthOptions();
    syncDayOptions();
    selectDateFromControls();
  });

  els.month.addEventListener("change", () => {
    syncDayOptions();
    selectDateFromControls();
  });

  els.day.addEventListener("change", selectDateFromControls);
}

function syncMonthOptions() {
  const year = Number(els.year.value || getDigestDates()[0]?.getFullYear());
  const months = unique(getDigestDates()
    .filter((date) => date.getFullYear() === year)
    .map((date) => date.getMonth() + 1))
    .sort((a, b) => b - a);

  fillSelect(els.month, months, (month) => `${month} 月`);
}

function syncDayOptions() {
  const year = Number(els.year.value);
  const month = Number(els.month.value);
  const days = unique(getDigestDates()
    .filter((date) => date.getFullYear() === year && date.getMonth() + 1 === month)
    .map((date) => date.getDate()))
    .sort((a, b) => b - a);

  fillSelect(els.day, days, (day) => `${day} 日`);
}

function fillSelect(select, values, labeler) {
  const previousValue = select.value;
  select.replaceChildren(...values.map((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labeler(value);
    return option;
  }));

  if (values.map(String).includes(previousValue)) {
    select.value = previousValue;
  }
}

function selectDateFromControls() {
  const year = Number(els.year.value);
  const month = Number(els.month.value);
  const day = Number(els.day.value);
  selectDate(formatDate(year, month, day));
}

async function selectDate(reportDate) {
  if (!reportDate) {
    showStatus("目前還沒有任何 AI 日報。");
    return;
  }

  state.selectedDate = reportDate;
  updateControls(reportDate);

  const entry = state.manifest.digests.find((digest) => digest.reportDate === reportDate);
  if (!entry) {
    renderEmpty(reportDate);
    return;
  }

  try {
    showStatus("正在載入日報...");
    const response = await fetch(entry.path);
    if (!response.ok) throw new Error("digest not found");
    const digest = await response.json();
    renderDigest(digest);
    hideStatus();
  } catch (error) {
    renderEmpty(reportDate);
  }
}

function updateControls(reportDate) {
  const [year, month, day] = reportDate.split("-").map(Number);
  els.year.value = year;
  syncMonthOptions();
  els.month.value = month;
  syncDayOptions();
  els.day.value = day;
}

function renderDigest(digest) {
  if (els.dailyHeadline) {
    els.dailyHeadline.textContent = digest.headline || `Bella's AI 趨勢日報｜${formatDisplayDate(digest.reportDate)}`;
  }
  if (els.digestTitle) {
    els.digestTitle.textContent = digest.headline || `Bella's AI 趨勢日報｜${formatDisplayDate(digest.reportDate)}`;
  }
  if (els.digestSummary) {
    els.digestSummary.textContent = digest.summary || "";
  }
  els.reportDate.textContent = formatDisplayDate(digest.reportDate);
  els.coverageDate.textContent = formatDisplayDate(digest.coverageDate);
  els.generatedAt.textContent = formatGeneratedAt(digest.generatedAt);
  if (els.collectionCount) {
    els.collectionCount.textContent = collectionCountText(digest);
  }
  renderImpactFramework(digest.scoringPolicy?.impactFramework || []);
  renderPriority(digest.scoringPolicy?.priority || []);

  const sections = digest.sections || [];
  els.content.replaceChildren(renderStrategyBrief(digest), ...sections.map(renderSection));
}

function renderStrategyBrief(digest) {
  const takeaways = strategyTakeaways(digest);
  if (!takeaways.length) return document.createDocumentFragment();

  const section = document.createElement("section");
  section.className = "strategy-brief";
  section.setAttribute("aria-label", "今日策略判讀");

  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Decision Lens";

  const title = document.createElement("h2");
  title.textContent = "今日策略判讀";

  const list = document.createElement("ul");
  list.replaceChildren(...takeaways.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));

  section.replaceChildren(eyebrow, title, list);
  return section;
}

function strategyTakeaways(digest) {
  if (Array.isArray(digest.strategyTakeaways) && digest.strategyTakeaways.length) {
    return digest.strategyTakeaways.map(String).filter(Boolean).slice(0, 4);
  }
  const summary = digest.summary || "";
  return summary
    .replaceAll("；", "。")
    .replaceAll("，並", "。並")
    .split("。")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 3)
    .map((item) => `${item}。`);
}

function collectionCountText(digest) {
  const sections = digest.sections || [];
  const newsCount = sections
    .filter((section) => section.id !== "applications")
    .reduce((sum, section) => sum + (section.items?.length || 0), 0);
  const applicationCount = sections
    .filter((section) => section.id === "applications")
    .reduce((sum, section) => sum + (section.items?.length || 0), 0);
  return `新聞判讀 ${newsCount} 則｜應用切角 ${applicationCount} 則`;
}

function renderImpactFramework(framework) {
  if (!els.impactFrameworkList) return;
  const items = framework.length ? framework : ["國際事件與產業格局", "品牌端", "使用者端 / 深度工作者", "一般社會大眾"];
  els.impactFrameworkList.replaceChildren(...items.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderPriority(priorityItems) {
  els.priorityList.replaceChildren(...priorityItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderSection(section) {
  const node = els.sectionTemplate.content.cloneNode(true);
  const wrapper = node.querySelector(".digest-section");
  wrapper.id = section.id;
  node.querySelector(".section-heading__count").textContent = `${section.items?.length || 0} 則資訊`;
  node.querySelector("h2").textContent = section.title;
  node.querySelector(".section-heading p:not(.section-heading__count)").textContent = section.description;

  const list = node.querySelector(".item-list");
  if (!section.items?.length) {
    const empty = document.createElement("div");
    empty.className = "empty-section";
    empty.textContent = "這個區塊目前沒有收錄內容。";
    list.append(empty);
    return node;
  }

  if (section.id === "applications") {
    list.classList.add("application-list");
    list.replaceChildren(renderApplications(section.items));
    return node;
  }

  list.replaceChildren(...section.items.map(renderItem));
  return node;
}

function renderItem(item) {
  const node = els.itemTemplate.content.cloneNode(true);
  renderSources(node.querySelector(".source-line"), item);
  node.querySelector("h3").textContent = item.title;
  renderScoreBadge(node.querySelector(".score-badge"), item);
  node.querySelector(".summary").textContent = item.summary;
  renderParagraphs(node.querySelector(".analysis"), item.analysis || []);
  renderImpactAngles(node.querySelector(".analysis"), item);
  node.querySelector(".what").textContent = item.what;
  node.querySelector(".so-what").textContent = item.soWhat;
  node.querySelector(".now-what").textContent = item.nowWhat;

  const tagRow = node.querySelector(".tag-row");
  tagRow.replaceChildren(...(item.tags || []).map((tag) => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = tag;
    return span;
  }));

  return node;
}

function renderImpactAngles(anchor, item) {
  if (!Array.isArray(item.impactAngles) || !item.impactAngles.length || !anchor) return;
  const row = document.createElement("div");
  row.className = "impact-angle-row";
  const label = document.createElement("span");
  label.textContent = "判讀角度";
  const pills = item.impactAngles.slice(0, 4).map((angle) => {
    const pill = document.createElement("span");
    pill.className = "angle-pill";
    pill.textContent = angle;
    return pill;
  });
  row.replaceChildren(label, ...pills);
  anchor.after(row);
}

function renderScoreBadge(container, item) {
  const score = normalizeScore(item.score || {});
  const total = Object.values(score).reduce((sum, value) => sum + value, 0);
  const scoreText = document.createElement("span");
  scoreText.textContent = `${total} 分`;

  const infoButton = document.createElement("button");
  infoButton.type = "button";
  infoButton.className = "score-info";
  infoButton.textContent = "i";
  infoButton.setAttribute("aria-label", `查看「${item.title}」分數說明`);
  infoButton.addEventListener("click", () => openScoreDialog(item));

  container.replaceChildren(scoreText, infoButton);
}

function setupScoreDialog() {
  els.scoreDialogClose?.addEventListener("click", () => els.scoreDialog?.close());
  els.scoreDialog?.addEventListener("click", (event) => {
    if (event.target === els.scoreDialog) {
      els.scoreDialog.close();
    }
  });
}

function openScoreDialog(item) {
  if (!els.scoreDialog || !els.scoreDialogBody) return;

  const score = normalizeScore(item.score || {});
  const fields = [
    ["產業重大性", score.industryImpact ?? 0, "0-5"],
    ["數位行銷影響", score.digitalMarketingImpact ?? 0, "0-5"],
    ["內容 / 搜尋 / 社群 / 媒體廣告影響", score.contentSearchSocialAdsImpact ?? 0, "0-5"],
    ["工具可用性", score.toolUsability ?? 0, "0-5"],
    ["指定追蹤公司 / 工具相關性", score.trackedEntityRelevance ?? 0, "0-3"]
  ];
  const calculatedTotal = fields.reduce((sum, [, value]) => sum + Number(value || 0), 0);
  const total = calculatedTotal;

  const title = document.createElement("p");
  title.className = "score-dialog__item";
  title.textContent = item.title;

  const intro = document.createElement("p");
  intro.textContent = "每則資訊依 5 個面向評分，排序優先看產業重大性，再看數位行銷影響。";

  const list = document.createElement("dl");
  list.className = "score-breakdown";
  fields.forEach(([label, value, range]) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = `${label}（${range}）`;
    dd.textContent = `${value} 分`;
    row.append(dt, dd);
    list.append(row);
  });

  const formula = document.createElement("p");
  formula.className = "score-formula";
  formula.textContent = `${fields.map(([, value]) => value).join(" + ")} = ${total} 分`;

  els.scoreDialogBody.replaceChildren(title, intro, list, formula);
  els.scoreDialog.showModal();
}

function normalizeScore(score) {
  const fields = {
    industryImpact: 5,
    digitalMarketingImpact: 5,
    contentSearchSocialAdsImpact: 5,
    toolUsability: 5,
    trackedEntityRelevance: 3
  };
  return Object.fromEntries(
    Object.entries(fields).map(([key, max]) => [key, normalizeScoreValue(score[key], max)])
  );
}

function normalizeScoreValue(value, max) {
  const number = Math.round(Number(value) || 0);
  if (number < 0) return 0;
  if (number <= max) return number;
  if (max === 3) {
    return Math.min(max, Math.round(number <= 5 ? (number * 3) / 5 : (number * 3) / 10));
  }
  return Math.min(max, Math.round(number / 2));
}

function renderSources(container, item) {
  const label = document.createElement("span");
  label.textContent = "來源：";

  const sources = normalizeSources(item);
  const sourceNodes = sources.flatMap((source, index) => {
    const node = source.url ? document.createElement("a") : document.createElement("span");
    node.textContent = source.name || "未標示媒體";
    if (source.url) {
      node.href = source.url;
      node.target = "_blank";
      node.rel = "noopener";
    }

    const nodes = [node];
    if (index < sources.length - 1) {
      const separator = document.createElement("span");
      separator.textContent = "、";
      nodes.push(separator);
    }
    return nodes;
  });

  const date = document.createElement("span");
  date.className = "source-date";
  date.textContent = ` · ${formatDisplayDate(getPublishedDate(item))}`;
  container.replaceChildren(label, ...sourceNodes, date);
}

function renderApplications(items) {
  const list = document.createElement("ul");
  list.className = "application-bullets";

  list.replaceChildren(...items.map((item) => {
    const li = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    title.textContent = item.title;
    body.textContent = item.summary || item.nowWhat || "";
    li.append(title, body);
    return li;
  }));

  return list;
}

function renderParagraphs(container, paragraphs) {
  container.replaceChildren(...paragraphs.map((paragraph) => {
    const p = document.createElement("p");
    p.textContent = paragraph;
    return p;
  }));
}

function normalizeSources(item) {
  if (Array.isArray(item.sources) && item.sources.length) {
    return item.sources;
  }
  return [{
    name: item.source || "未標示媒體",
    publishedDate: item.publishedDate,
    url: item.url || ""
  }];
}

function getSourceNames(item) {
  if (Array.isArray(item.sources) && item.sources.length) {
    return item.sources.map((source) => source.name).filter(Boolean).join("、") || "未標示媒體";
  }
  return item.source || "未標示媒體";
}

function getPublishedDate(item) {
  if (Array.isArray(item.sources) && item.sources.length) {
    return item.sources[0].publishedDate || item.publishedDate;
  }
  return item.publishedDate;
}

function getPrimaryUrl(item) {
  if (Array.isArray(item.sources) && item.sources.length) {
    return item.sources.find((source) => source.url)?.url || "";
  }
  return item.url || "";
}

function renderEmpty(reportDate) {
  if (els.digestTitle) {
    els.digestTitle.textContent = `沒有 ${formatDisplayDate(reportDate)} 的日報`;
  }
  if (els.dailyHeadline) {
    els.dailyHeadline.textContent = `沒有 ${formatDisplayDate(reportDate)} 的日報`;
  }
  if (els.digestSummary) {
    els.digestSummary.textContent = "這天還沒有 AI 日報。未來自動更新後，這裡會顯示對應日期內容。";
  }
  els.reportDate.textContent = formatDisplayDate(reportDate);
  els.coverageDate.textContent = "--";
  els.generatedAt.textContent = "--";
  if (els.collectionCount) {
    els.collectionCount.textContent = "--";
  }
  renderImpactFramework([]);
  els.priorityList.replaceChildren();
  els.content.replaceChildren();
  showStatus("這天還沒有 AI 日報。");
}

function showStatus(message) {
  els.status.textContent = message;
  els.status.hidden = false;
}

function hideStatus() {
  els.status.hidden = true;
}

function getDigestDates() {
  return getPublishableDigestEntries()
    .map((digest) => parseDate(digest.reportDate))
    .filter(Boolean)
    .sort((a, b) => b - a);
}

function getPublishableDigestEntries() {
  return (state.manifest?.digests || []).filter((digest) => !digest.isDemo && !digest.noindex);
}

function unique(values) {
  return [...new Set(values)];
}

function parseDate(value) {
  if (!value) return null;
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatDate(year, month, day) {
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function formatDisplayDate(value) {
  if (!value) return "--";
  const [year, month, day] = value.split("-").map(Number);
  return `${year}/${String(month).padStart(2, "0")}/${String(day).padStart(2, "0")}`;
}

function formatGeneratedAt(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-TW", {
    timeZone: "Asia/Taipei",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(date);
}
