/**
 * Wartungsplaner - Lovelace Dashboard Card for Home Assistant
 * Compact card with 3 modes: standard, compact, stats
 */

const CARD_STRINGS = {
  de: {
    title: "Wartungsplaner",
    overdue: "Überfällig",
    dueSoon: "Bald fällig",
    done: "Erledigt",
    neverDone: "Nie erledigt",
    open: "offen",
    never: "Nie",
    daysShort: "T.",
    noUrgent: "Keine dringenden Aufgaben",
    allTasks: "Alle {n} Aufgaben anzeigen",
    allTasksLink: "Alle Aufgaben",
    complete: "Erledigen",
    mode: "Modus",
    modeStandard: "Standard",
    modeCompact: "Kompakt",
    modeStats: "Nur Statistik",
    titleLabel: "Titel (leer = Standard)",
    maxTasks: "Max. angezeigte Aufgaben",
    showComplete: "Erledigen-Button anzeigen",
    priorities: {
      low: "Niedrig",
      medium: "Mittel",
      high: "Hoch",
      critical: "Kritisch",
    },
  },
  en: {
    title: "Maintenance Planner",
    overdue: "Overdue",
    dueSoon: "Due Soon",
    done: "Done",
    neverDone: "Never Done",
    open: "open",
    never: "Never",
    daysShort: "d.",
    noUrgent: "No urgent tasks",
    allTasks: "Show all {n} tasks",
    allTasksLink: "All tasks",
    complete: "Complete",
    mode: "Mode",
    modeStandard: "Standard",
    modeCompact: "Compact",
    modeStats: "Stats only",
    titleLabel: "Title (empty = default)",
    maxTasks: "Max. displayed tasks",
    showComplete: "Show complete button",
    priorities: {
      low: "Low",
      medium: "Medium",
      high: "High",
      critical: "Critical",
    },
  },
};

const STATUS_COLORS = {
  overdue: "#f44336",
  due: "#ff9800",
  due_soon: "#ff9800",
  never_done: "#9e9e9e",
  done: "#4caf50",
  snoozed: "#9e9e9e",
};

const STATUS_DOT_COLORS = {
  overdue: "#b71c1c",
  due: "#ff9800",
  due_soon: "#ff9800",
  never_done: "#9e9e9e",
  done: "#4caf50",
  snoozed: "#9e9e9e",
};

class WartungsplanerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._data = null;
    this._categories = null;
    this._lang = "de";
    this._lastLoad = 0;
    this._loading = false;
  }

  static getConfigElement() {
    return document.createElement("wartungsplaner-card-editor");
  }

  static getStubConfig() {
    return {
      mode: "standard",
      title: "",
      max_tasks: 5,
      show_complete: true,
    };
  }

  setConfig(config) {
    this._config = {
      mode: config.mode || "standard",
      title: config.title || "",
      max_tasks: config.max_tasks != null ? config.max_tasks : 5,
      show_complete: config.show_complete !== false,
    };
  }

  getCardSize() {
    if (this._config.mode === "stats") return 3;
    if (this._config.mode === "compact") return 2 + (this._config.max_tasks || 5);
    return 3 + (this._config.max_tasks || 5);
  }

  set hass(hass) {
    this._hass = hass;
    this._lang = (hass.language || "de").startsWith("en") ? "en" : "de";

    const now = Date.now();
    if (now - this._lastLoad > 30000 && !this._loading) {
      this._loadData();
    }
  }

  get _t() {
    return CARD_STRINGS[this._lang] || CARD_STRINGS.de;
  }

  async _loadData() {
    if (!this._hass) return;
    this._loading = true;
    this._lastLoad = Date.now();

    try {
      const [taskResult, catResult] = await Promise.all([
        this._hass.callWS({ type: "wartungsplaner/get_tasks" }),
        this._hass.callWS({ type: "wartungsplaner/get_categories" }),
      ]);
      this._data = taskResult;
      this._categories = catResult.categories;
      this._render();
    } catch (e) {
      // Integration may not be loaded yet
    } finally {
      this._loading = false;
    }
  }

  _getCategoryLabel(categoryId) {
    if (!this._categories) return categoryId;
    const cat = this._categories.find((c) => c.id === categoryId);
    if (!cat) return categoryId;
    return this._lang === "en" ? cat.name_en : cat.name_de;
  }

  _getUrgentTasks() {
    if (!this._data || !this._data.tasks) return [];
    const today = new Date().toISOString().split("T")[0];
    return Object.entries(this._data.tasks)
      .filter(([, task]) => {
        if (task.snoozed_until && task.snoozed_until > today) return false;
        if (task.status === "snoozed" && task.snoozed_until && task.snoozed_until <= today) return true;
        return ["overdue", "due", "due_soon", "never_done"].includes(task.status);
      })
      .sort(([, a], [, b]) => {
        const order = { overdue: 0, due: 1, never_done: 2, due_soon: 3 };
        return (order[a.status] ?? 4) - (order[b.status] ?? 4);
      })
      .slice(0, this._config.max_tasks);
  }

  async _completeTask(taskId) {
    if (!this._hass) return;
    try {
      await this._hass.callWS({
        type: "wartungsplaner/complete_task",
        task_id: taskId,
      });
      this._lastLoad = 0;
      await this._loadData();
    } catch (e) {
      // Ignore
    }
  }

  _navigateToPanel() {
    history.pushState(null, "", "/wartungsplaner");
    const event = new Event("location-changed", { bubbles: true, composed: true });
    this.dispatchEvent(event);
  }

  _formatDays(task) {
    const t = this._t;
    if (task.days_until_due == null) return { text: t.never, cls: "grey" };
    const d = task.days_until_due;
    if (d < 0) return { text: `${d} ${t.daysShort}`, cls: "red" };
    if (d === 0) return { text: `0 ${t.daysShort}`, cls: "red" };
    return { text: `${d} ${t.daysShort}`, cls: "orange" };
  }

  _render() {
    const t = this._t;
    const mode = this._config.mode;
    const title = this._config.title || t.title;

    const urgentTasks = mode !== "stats" ? this._getUrgentTasks() : [];
    const stats = this._data ? this._data.stats : null;
    const total = stats ? stats.total : 0;
    const urgentCount = stats ? stats.overdue + stats.due_soon + stats.due + stats.never_done : 0;

    let content = "";

    if (mode === "stats") {
      content = this._renderStats(title, stats);
    } else if (urgentTasks.length === 0 && stats) {
      content = this._renderEmpty(title, urgentCount);
    } else if (mode === "compact") {
      content = this._renderCompact(title, urgentCount, urgentTasks, stats, total);
    } else {
      content = this._renderStandard(title, urgentCount, urgentTasks, stats, total);
    }

    this.shadowRoot.innerHTML = `
      <style>${this._getStyles()}</style>
      <ha-card>${content}</ha-card>
    `;

    // Bind events
    this.shadowRoot.querySelectorAll(".task-action").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        this._completeTask(btn.dataset.taskId);
      });
    });

    const footerLink = this.shadowRoot.querySelector(".footer-link");
    if (footerLink) {
      footerLink.addEventListener("click", (e) => {
        e.preventDefault();
        this._navigateToPanel();
      });
    }
  }

  _renderHeader(title, urgentCount) {
    const t = this._t;
    const badge =
      urgentCount > 0
        ? `<span class="header-badge">${urgentCount} ${t.open}</span>`
        : "";
    return `
      <div class="card-header">
        <div class="card-title">
          <ha-icon icon="mdi:wrench-clock" class="header-icon"></ha-icon>
          ${this._esc(title)}
        </div>
        ${badge}
      </div>`;
  }

  _renderStatsRow(stats) {
    if (!stats) return "";
    const t = this._t;
    return `
      <div class="stats-row">
        <div class="stat">
          <div class="stat-num red">${stats.overdue}</div>
          <div class="stat-label">${t.overdue}</div>
        </div>
        <div class="stat">
          <div class="stat-num orange">${stats.due_soon + stats.due}</div>
          <div class="stat-label">${t.dueSoon}</div>
        </div>
        <div class="stat">
          <div class="stat-num green">${stats.done}</div>
          <div class="stat-label">${t.done}</div>
        </div>
        <div class="stat">
          <div class="stat-num grey">${stats.never_done}</div>
          <div class="stat-label">${t.neverDone}</div>
        </div>
      </div>`;
  }

  _renderProgressBar(stats) {
    if (!stats || stats.total === 0) return "";
    const total = stats.total;
    const pct = (n) => ((n / total) * 100).toFixed(1);
    return `
      <div class="progress-bar">
        <div class="progress-segment" style="width:${pct(stats.overdue)}%;background:#f44336"></div>
        <div class="progress-segment" style="width:${pct(stats.due_soon + stats.due)}%;background:#ff9800"></div>
        <div class="progress-segment" style="width:${pct(stats.done)}%;background:#4caf50"></div>
        <div class="progress-segment" style="width:${pct(stats.never_done)}%;background:#9e9e9e"></div>
      </div>`;
  }

  _renderTaskItem(taskId, task, compact) {
    const t = this._t;
    const days = this._formatDays(task);
    const dotColor = STATUS_DOT_COLORS[task.status] || "#9e9e9e";
    const showComplete = this._config.show_complete;

    let meta = "";
    if (!compact) {
      const catLabel = this._getCategoryLabel(task.category);
      const priLabel = t.priorities[task.priority] || task.priority;
      meta = `<div class="task-meta"><span>${this._esc(catLabel)}</span><span>&middot;</span><span>${this._esc(priLabel)}</span></div>`;
    }

    const actionBtn = showComplete
      ? `<button class="task-action" data-task-id="${this._esc(taskId)}" title="${t.complete}">
           <svg viewBox="0 0 24 24"><path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>
         </button>`
      : "";

    return `
      <div class="task-item">
        <div class="task-status-dot" style="background:${dotColor}"></div>
        <div class="task-info">
          <div class="task-name">${this._esc(task.name)}</div>
          ${meta}
        </div>
        <div class="task-days ${days.cls}">${days.text}</div>
        ${actionBtn}
      </div>`;
  }

  _renderFooter(total) {
    const t = this._t;
    const text = total > 0 ? t.allTasks.replace("{n}", total) : t.allTasksLink;
    return `
      <div class="card-footer">
        <a href="/wartungsplaner" class="footer-link">${text} &rarr;</a>
      </div>`;
  }

  _renderStandard(title, urgentCount, tasks, stats, total) {
    const items = tasks.map(([id, task]) => this._renderTaskItem(id, task, false)).join("");
    return `
      ${this._renderHeader(title, urgentCount)}
      ${this._renderStatsRow(stats)}
      <div class="task-list">${items}</div>
      ${this._renderFooter(total)}`;
  }

  _renderCompact(title, urgentCount, tasks, stats, total) {
    const items = tasks.map(([id, task]) => this._renderTaskItem(id, task, true)).join("");
    return `
      ${this._renderHeader(title, urgentCount)}
      ${this._renderProgressBar(stats)}
      <div class="task-list">${items}</div>
      ${this._renderFooter(total)}`;
  }

  _renderStats(title, stats) {
    return `
      ${this._renderHeader(title, 0)}
      ${this._renderStatsRow(stats)}
      ${this._renderProgressBar(stats)}`;
  }

  _renderEmpty(title, urgentCount) {
    const t = this._t;
    return `
      ${this._renderHeader(title, urgentCount)}
      <div class="empty-state">
        <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"/></svg>
        <p>${t.noUrgent}</p>
      </div>`;
  }

  _esc(str) {
    if (!str) return "";
    const el = document.createElement("span");
    el.textContent = str;
    return el.innerHTML;
  }

  _getStyles() {
    return `
      :host {
        display: block;
      }
      ha-card {
        overflow: hidden;
      }
      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 16px 12px;
      }
      .card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .header-icon {
        --mdc-icon-size: 24px;
        color: var(--primary-color);
      }
      .header-badge {
        background: #b71c1c;
        color: white;
        font-size: 12px;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
      }

      /* Stats row */
      .stats-row {
        display: flex;
        gap: 1px;
        background: var(--divider-color, #2a2a2a);
        margin: 0 16px 12px;
        border-radius: 8px;
        overflow: hidden;
      }
      .stat {
        flex: 1;
        text-align: center;
        padding: 8px 4px;
        background: var(--card-background-color, var(--ha-card-background, #252525));
      }
      .stat-num {
        font-size: 20px;
        font-weight: 500;
        line-height: 1.2;
      }
      .stat-label {
        font-size: 10px;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.3px;
      }
      .stat-num.red { color: #f44336; }
      .stat-num.orange { color: #ff9800; }
      .stat-num.green { color: #4caf50; }
      .stat-num.grey { color: #9e9e9e; }

      /* Progress bar */
      .progress-bar {
        height: 3px;
        background: var(--divider-color, #2a2a2a);
        margin: 0 16px 12px;
        border-radius: 2px;
        overflow: hidden;
        display: flex;
      }
      .progress-segment {
        height: 100%;
        transition: width 0.3s;
      }

      /* Task list */
      .task-list {
        padding: 0 12px 8px;
      }
      .task-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 4px;
        border-bottom: 1px solid var(--divider-color, #2a2a2a);
      }
      .task-item:last-child {
        border-bottom: none;
      }
      .task-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
      }
      .task-info {
        flex: 1;
        min-width: 0;
      }
      .task-name {
        font-size: 14px;
        font-weight: 400;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--primary-text-color);
      }
      .task-meta {
        font-size: 11px;
        color: var(--secondary-text-color);
        display: flex;
        gap: 8px;
        margin-top: 1px;
      }
      .task-days {
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
      }
      .task-days.red { color: #f44336; }
      .task-days.orange { color: #ff9800; }
      .task-days.grey { color: #9e9e9e; }

      /* Complete button */
      .task-action {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 1.5px solid var(--divider-color, #444);
        background: transparent;
        color: var(--secondary-text-color);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        flex-shrink: 0;
        transition: all 0.15s;
        padding: 0;
      }
      .task-action:hover {
        border-color: #4caf50;
        color: #4caf50;
        background: rgba(76,175,80,0.1);
      }
      .task-action svg {
        width: 16px;
        height: 16px;
      }

      /* Footer */
      .card-footer {
        text-align: center;
        padding: 8px 16px 14px;
      }
      .card-footer a {
        font-size: 12px;
        color: var(--primary-color);
        text-decoration: none;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
        cursor: pointer;
      }

      /* Empty state */
      .empty-state {
        text-align: center;
        padding: 24px 16px;
        color: var(--secondary-text-color);
      }
      .empty-state svg {
        width: 36px;
        height: 36px;
        margin-bottom: 8px;
        opacity: 0.4;
        fill: currentColor;
      }
      .empty-state p {
        font-size: 13px;
      }
    `;
  }
}

class WartungsplanerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._lang = "de";
  }

  set hass(hass) {
    this._hass = hass;
    this._lang = (hass.language || "de").startsWith("en") ? "en" : "de";
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  get _t() {
    return CARD_STRINGS[this._lang] || CARD_STRINGS.de;
  }

  _render() {
    const t = this._t;
    const mode = this._config.mode || "standard";
    const title = this._config.title || "";
    const maxTasks = this._config.max_tasks != null ? this._config.max_tasks : 5;
    const showComplete = this._config.show_complete !== false;

    this.shadowRoot.innerHTML = `
      <style>
        .editor {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 16px 0;
        }
        .row {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        label {
          font-size: 12px;
          font-weight: 500;
          color: var(--secondary-text-color);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        select, input[type="text"], input[type="number"] {
          padding: 8px;
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 4px;
          background: var(--card-background-color, var(--ha-card-background, #fff));
          color: var(--primary-text-color);
          font-size: 14px;
        }
        .checkbox-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .checkbox-row label {
          text-transform: none;
          font-size: 14px;
          color: var(--primary-text-color);
        }
      </style>
      <div class="editor">
        <div class="row">
          <label>${t.mode}</label>
          <select id="mode">
            <option value="standard" ${mode === "standard" ? "selected" : ""}>${t.modeStandard}</option>
            <option value="compact" ${mode === "compact" ? "selected" : ""}>${t.modeCompact}</option>
            <option value="stats" ${mode === "stats" ? "selected" : ""}>${t.modeStats}</option>
          </select>
        </div>
        <div class="row">
          <label>${t.titleLabel}</label>
          <input type="text" id="title" value="${this._esc(title)}">
        </div>
        <div class="row">
          <label>${t.maxTasks}</label>
          <input type="number" id="max_tasks" min="1" max="20" value="${maxTasks}">
        </div>
        <div class="checkbox-row">
          <input type="checkbox" id="show_complete" ${showComplete ? "checked" : ""}>
          <label for="show_complete">${t.showComplete}</label>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById("mode").addEventListener("change", (e) => {
      this._config = { ...this._config, mode: e.target.value };
      this._fireConfigChanged();
    });

    this.shadowRoot.getElementById("title").addEventListener("input", (e) => {
      this._config = { ...this._config, title: e.target.value };
      this._fireConfigChanged();
    });

    this.shadowRoot.getElementById("max_tasks").addEventListener("change", (e) => {
      this._config = { ...this._config, max_tasks: parseInt(e.target.value, 10) || 5 };
      this._fireConfigChanged();
    });

    this.shadowRoot.getElementById("show_complete").addEventListener("change", (e) => {
      this._config = { ...this._config, show_complete: e.target.checked };
      this._fireConfigChanged();
    });
  }

  _fireConfigChanged() {
    const event = new CustomEvent("config-changed", {
      detail: { config: { ...this._config } },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  _esc(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

customElements.define("wartungsplaner-card", WartungsplanerCard);
customElements.define("wartungsplaner-card-editor", WartungsplanerCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "wartungsplaner-card",
  name: "Wartungsplaner",
  description: "Compact maintenance task overview card",
  preview: true,
  documentationURL: "https://github.com/philippauer/ha-wartungsplaner",
});
