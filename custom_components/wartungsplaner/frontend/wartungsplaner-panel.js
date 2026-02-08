/**
 * Wartungsplaner - Sidebar Panel for Home Assistant
 * Vanilla Web Component with Shadow DOM
 */

const STRINGS = {
  de: {
    overview: "Übersicht",
    tasks: "Aufgaben",
    templates: "Vorlagen",
    total: "Gesamt",
    overdue: "Überfällig",
    dueSoon: "Bald fällig",
    due: "Fällig",
    done: "Erledigt",
    neverDone: "Nie erledigt",
    addTask: "Aufgabe hinzufügen",
    editTask: "Aufgabe bearbeiten",
    deleteTask: "Aufgabe löschen",
    completeTask: "Als erledigt markieren",
    save: "Speichern",
    cancel: "Abbrechen",
    delete: "Löschen",
    close: "Schließen",
    add: "Hinzufügen",
    name: "Name",
    description: "Beschreibung",
    category: "Kategorie",
    priority: "Priorität",
    interval: "Intervall",
    intervalUnit: "Einheit",
    notes: "Notizen",
    search: "Suchen...",
    filterAll: "Alle",
    noTasks: "Keine Aufgaben vorhanden",
    noUrgent: "Keine dringenden Aufgaben",
    urgentTasks: "Dringende Aufgaben",
    lastCompleted: "Zuletzt erledigt",
    nextDue: "Nächste Fälligkeit",
    days: "Tage",
    weeks: "Wochen",
    months: "Monate",
    years: "Jahre",
    daysUntilDue: "Tage bis fällig",
    addFromTemplate: "Aus Vorlage hinzufügen",
    confirmDelete: "Möchten Sie diese Aufgabe wirklich löschen?",
    completionNotes: "Erledigungs-Notizen (optional)",
    never: "Nie",
    categories: {
      heating: "Heizung",
      safety: "Sicherheit",
      plumbing: "Sanitär",
      appliances: "Geräte",
      exterior: "Außen",
      interior: "Innen",
      electrical: "Elektrik",
      garden: "Garten",
      cleaning: "Reinigung",
      other: "Sonstiges",
    },
    priorities: {
      low: "Niedrig",
      medium: "Mittel",
      high: "Hoch",
      critical: "Kritisch",
    },
    statuses: {
      done: "Erledigt",
      due_soon: "Bald fällig",
      due: "Fällig",
      overdue: "Überfällig",
      never_done: "Nie erledigt",
    },
  },
  en: {
    overview: "Overview",
    tasks: "Tasks",
    templates: "Templates",
    total: "Total",
    overdue: "Overdue",
    dueSoon: "Due Soon",
    due: "Due",
    done: "Done",
    neverDone: "Never Done",
    addTask: "Add Task",
    editTask: "Edit Task",
    deleteTask: "Delete Task",
    completeTask: "Mark as completed",
    save: "Save",
    cancel: "Cancel",
    delete: "Delete",
    close: "Close",
    add: "Add",
    name: "Name",
    description: "Description",
    category: "Category",
    priority: "Priority",
    interval: "Interval",
    intervalUnit: "Unit",
    notes: "Notes",
    search: "Search...",
    filterAll: "All",
    noTasks: "No tasks available",
    noUrgent: "No urgent tasks",
    urgentTasks: "Urgent Tasks",
    lastCompleted: "Last completed",
    nextDue: "Next due",
    days: "Days",
    weeks: "Weeks",
    months: "Months",
    years: "Years",
    daysUntilDue: "Days until due",
    addFromTemplate: "Add from template",
    confirmDelete: "Are you sure you want to delete this task?",
    completionNotes: "Completion notes (optional)",
    never: "Never",
    categories: {
      heating: "Heating",
      safety: "Safety",
      plumbing: "Plumbing",
      appliances: "Appliances",
      exterior: "Exterior",
      interior: "Interior",
      electrical: "Electrical",
      garden: "Garden",
      cleaning: "Cleaning",
      other: "Other",
    },
    priorities: {
      low: "Low",
      medium: "Medium",
      high: "High",
      critical: "Critical",
    },
    statuses: {
      done: "Done",
      due_soon: "Due Soon",
      due: "Due",
      overdue: "Overdue",
      never_done: "Never Done",
    },
  },
};

const STATUS_COLORS = {
  done: "#4caf50",
  due_soon: "#ff9800",
  due: "#f44336",
  overdue: "#b71c1c",
  never_done: "#9e9e9e",
};

const PRIORITY_COLORS = {
  low: "#8bc34a",
  medium: "#2196f3",
  high: "#ff9800",
  critical: "#f44336",
};

const CATEGORY_ICONS = {
  heating: "mdi:radiator",
  safety: "mdi:shield-check",
  plumbing: "mdi:water-pump",
  appliances: "mdi:washing-machine",
  exterior: "mdi:home-roof",
  interior: "mdi:sofa",
  electrical: "mdi:flash",
  garden: "mdi:flower",
  cleaning: "mdi:broom",
  other: "mdi:dots-horizontal",
};

class WartungsplanerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._tasks = {};
    this._stats = {};
    this._templates = [];
    this._activeTab = "overview";
    this._filterCategory = "all";
    this._filterStatus = "all";
    this._searchQuery = "";
    this._lang = "de";
  }

  set hass(hass) {
    this._hass = hass;
    if (hass && hass.language) {
      this._lang = hass.language.startsWith("de") ? "de" : "en";
    }
    if (!this._initialized) {
      this._initialized = true;
      this._loadData();
    }
  }

  get hass() {
    return this._hass;
  }

  get t() {
    return STRINGS[this._lang] || STRINGS.de;
  }

  connectedCallback() {
    this._render();
  }

  async _loadData() {
    if (!this._hass) return;
    try {
      const result = await this._hass.callWS({ type: "wartungsplaner/get_tasks" });
      this._tasks = result.tasks || {};
      this._stats = result.stats || {};
      this._render();
    } catch (e) {
      console.error("Wartungsplaner: Failed to load tasks", e);
    }
  }

  async _loadTemplates() {
    if (!this._hass) return;
    try {
      const result = await this._hass.callWS({ type: "wartungsplaner/get_templates" });
      this._templates = result.templates || [];
    } catch (e) {
      console.error("Wartungsplaner: Failed to load templates", e);
    }
  }

  _render() {
    const t = this.t;
    this.shadowRoot.innerHTML = `
      <style>${this._getStyles()}</style>
      <div class="container">
        <div class="header">
          <h1>
            <ha-icon icon="mdi:wrench-clock"></ha-icon>
            Wartungsplaner
          </h1>
        </div>
        <div class="tabs">
          <button class="tab ${this._activeTab === "overview" ? "active" : ""}" data-tab="overview">
            <ha-icon icon="mdi:view-dashboard"></ha-icon> ${t.overview}
          </button>
          <button class="tab ${this._activeTab === "tasks" ? "active" : ""}" data-tab="tasks">
            <ha-icon icon="mdi:format-list-checks"></ha-icon> ${t.tasks}
          </button>
          <button class="tab ${this._activeTab === "templates" ? "active" : ""}" data-tab="templates">
            <ha-icon icon="mdi:file-document-multiple"></ha-icon> ${t.templates}
          </button>
        </div>
        <div class="tab-content">
          ${this._renderActiveTab()}
        </div>
      </div>
    `;
    this._attachEventListeners();
  }

  _renderActiveTab() {
    switch (this._activeTab) {
      case "overview":
        return this._renderOverview();
      case "tasks":
        return this._renderTasks();
      case "templates":
        return this._renderTemplates();
      default:
        return "";
    }
  }

  _renderOverview() {
    const t = this.t;
    const stats = this._stats;
    const tasks = Object.values(this._tasks);
    const urgent = tasks
      .filter((task) => ["overdue", "due", "due_soon", "never_done"].includes(task.status))
      .sort((a, b) => {
        const order = { overdue: 0, due: 1, never_done: 2, due_soon: 3 };
        return (order[a.status] ?? 4) - (order[b.status] ?? 4);
      });

    return `
      <div class="overview">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">${stats.total || 0}</div>
            <div class="stat-label">${t.total}</div>
          </div>
          <div class="stat-card stat-overdue">
            <div class="stat-number">${stats.overdue || 0}</div>
            <div class="stat-label">${t.overdue}</div>
          </div>
          <div class="stat-card stat-due-soon">
            <div class="stat-number">${(stats.due_soon || 0) + (stats.due || 0)}</div>
            <div class="stat-label">${t.dueSoon}</div>
          </div>
          <div class="stat-card stat-done">
            <div class="stat-number">${stats.done || 0}</div>
            <div class="stat-label">${t.done}</div>
          </div>
        </div>

        <h2>${t.urgentTasks}</h2>
        ${
          urgent.length === 0
            ? `<div class="empty-state"><ha-icon icon="mdi:check-all"></ha-icon><p>${t.noUrgent}</p></div>`
            : `<div class="task-list">${urgent.map((task) => this._renderTaskCard(task)).join("")}</div>`
        }
      </div>
    `;
  }

  _renderTasks() {
    const t = this.t;
    let tasks = Object.values(this._tasks);

    if (this._filterCategory !== "all") {
      tasks = tasks.filter((task) => task.category === this._filterCategory);
    }
    if (this._filterStatus !== "all") {
      tasks = tasks.filter((task) => task.status === this._filterStatus);
    }
    if (this._searchQuery) {
      const q = this._searchQuery.toLowerCase();
      tasks = tasks.filter(
        (task) =>
          task.name.toLowerCase().includes(q) ||
          (task.description && task.description.toLowerCase().includes(q))
      );
    }

    tasks.sort((a, b) => {
      const order = { overdue: 0, due: 1, never_done: 2, due_soon: 3, done: 4 };
      const diff = (order[a.status] ?? 5) - (order[b.status] ?? 5);
      if (diff !== 0) return diff;
      if (a.days_until_due == null && b.days_until_due == null) return 0;
      if (a.days_until_due == null) return 1;
      if (b.days_until_due == null) return -1;
      return a.days_until_due - b.days_until_due;
    });

    const categories = ["all", ...Object.keys(t.categories)];
    const statuses = ["all", ...Object.keys(t.statuses)];

    return `
      <div class="tasks-view">
        <div class="toolbar">
          <div class="filters">
            <select class="filter-select" id="filterCategory">
              ${categories
                .map(
                  (c) =>
                    `<option value="${c}" ${this._filterCategory === c ? "selected" : ""}>${
                      c === "all" ? t.filterAll : t.categories[c]
                    }</option>`
                )
                .join("")}
            </select>
            <select class="filter-select" id="filterStatus">
              ${statuses
                .map(
                  (s) =>
                    `<option value="${s}" ${this._filterStatus === s ? "selected" : ""}>${
                      s === "all" ? t.filterAll : t.statuses[s]
                    }</option>`
                )
                .join("")}
            </select>
            <input type="text" class="search-input" id="searchInput" placeholder="${t.search}" value="${this._searchQuery}" />
          </div>
          <button class="btn btn-primary" id="addTaskBtn">
            <ha-icon icon="mdi:plus"></ha-icon> ${t.addTask}
          </button>
        </div>

        ${
          tasks.length === 0
            ? `<div class="empty-state"><ha-icon icon="mdi:clipboard-text-off"></ha-icon><p>${t.noTasks}</p></div>`
            : `<div class="task-list">${tasks.map((task) => this._renderTaskCard(task)).join("")}</div>`
        }
      </div>
    `;
  }

  _renderTaskCard(task) {
    const t = this.t;
    const statusColor = STATUS_COLORS[task.status] || "#9e9e9e";
    const priorityColor = PRIORITY_COLORS[task.priority] || "#2196f3";
    const categoryIcon = CATEGORY_ICONS[task.category] || "mdi:dots-horizontal";
    const statusLabel = t.statuses[task.status] || task.status;
    const categoryLabel = t.categories[task.category] || task.category;
    const priorityLabel = t.priorities[task.priority] || task.priority;
    const daysText =
      task.days_until_due != null
        ? task.days_until_due < 0
          ? `${Math.abs(task.days_until_due)} ${t.days} ${t.overdue.toLowerCase()}`
          : task.days_until_due === 0
            ? t.due
            : `${task.days_until_due} ${t.days}`
        : t.neverDone;

    return `
      <div class="task-card" data-task-id="${task.id}">
        <div class="task-status-bar" style="background-color: ${statusColor}"></div>
        <div class="task-content">
          <div class="task-header">
            <div class="task-title-row">
              <ha-icon icon="${categoryIcon}" style="color: var(--secondary-text-color);"></ha-icon>
              <span class="task-name">${this._escapeHtml(task.name)}</span>
            </div>
            <div class="task-badges">
              <span class="badge" style="background-color: ${statusColor}; color: white;">${statusLabel}</span>
              <span class="badge" style="background-color: ${priorityColor}; color: white;">${priorityLabel}</span>
            </div>
          </div>
          ${task.description ? `<div class="task-description">${this._escapeHtml(task.description)}</div>` : ""}
          <div class="task-meta">
            <span><ha-icon icon="mdi:clock-outline"></ha-icon> ${daysText}</span>
            <span><ha-icon icon="mdi:tag"></ha-icon> ${categoryLabel}</span>
            <span><ha-icon icon="mdi:refresh"></ha-icon> ${task.interval_value} ${t[task.interval_unit] || task.interval_unit}</span>
          </div>
          <div class="task-actions">
            <button class="btn btn-small btn-success complete-btn" data-task-id="${task.id}" title="${t.completeTask}">
              <ha-icon icon="mdi:check"></ha-icon>
            </button>
            <button class="btn btn-small edit-btn" data-task-id="${task.id}" title="${t.editTask}">
              <ha-icon icon="mdi:pencil"></ha-icon>
            </button>
            <button class="btn btn-small btn-danger delete-btn" data-task-id="${task.id}" title="${t.deleteTask}">
              <ha-icon icon="mdi:delete"></ha-icon>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  _renderTemplates() {
    const t = this.t;
    const categories = {};
    for (const tmpl of this._templates) {
      const cat = tmpl.category;
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(tmpl);
    }

    if (this._templates.length === 0) {
      return `<div class="empty-state"><p>Laden...</p></div>`;
    }

    return `
      <div class="templates-view">
        <p class="templates-intro">${t.addFromTemplate}</p>
        ${Object.entries(categories)
          .map(
            ([cat, tmpls]) => `
          <div class="template-category">
            <h3>
              <ha-icon icon="${CATEGORY_ICONS[cat] || "mdi:dots-horizontal"}"></ha-icon>
              ${t.categories[cat] || cat}
            </h3>
            <div class="template-list">
              ${tmpls
                .map(
                  (tmpl) => `
                <div class="template-card">
                  <div class="template-info">
                    <div class="template-name">${this._escapeHtml(tmpl.name)}</div>
                    <div class="template-desc">${this._escapeHtml(tmpl.description)}</div>
                    <div class="template-meta">
                      <span class="badge" style="background-color: ${PRIORITY_COLORS[tmpl.priority]}; color: white;">
                        ${t.priorities[tmpl.priority]}
                      </span>
                      <span>${tmpl.interval_value} ${t[tmpl.interval_unit] || tmpl.interval_unit}</span>
                    </div>
                  </div>
                  <button class="btn btn-primary btn-small add-template-btn" data-template-id="${tmpl.id}">
                    <ha-icon icon="mdi:plus"></ha-icon>
                  </button>
                </div>
              `
                )
                .join("")}
            </div>
          </div>
        `
          )
          .join("")}
      </div>
    `;
  }

  _attachEventListeners() {
    const root = this.shadowRoot;

    // Tab navigation
    root.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", (e) => {
        this._activeTab = tab.dataset.tab;
        if (this._activeTab === "templates" && this._templates.length === 0) {
          this._loadTemplates().then(() => this._render());
        } else {
          this._render();
        }
      });
    });

    // Filters
    const filterCat = root.getElementById("filterCategory");
    if (filterCat) {
      filterCat.addEventListener("change", (e) => {
        this._filterCategory = e.target.value;
        this._render();
      });
    }

    const filterStatus = root.getElementById("filterStatus");
    if (filterStatus) {
      filterStatus.addEventListener("change", (e) => {
        this._filterStatus = e.target.value;
        this._render();
      });
    }

    const searchInput = root.getElementById("searchInput");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this._searchQuery = e.target.value;
        this._render();
      });
    }

    // Add task button
    const addBtn = root.getElementById("addTaskBtn");
    if (addBtn) {
      addBtn.addEventListener("click", () => this._showTaskDialog());
    }

    // Task card actions
    root.querySelectorAll(".complete-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        this._showCompleteDialog(btn.dataset.taskId);
      });
    });

    root.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const task = this._tasks[btn.dataset.taskId];
        if (task) this._showTaskDialog(task);
      });
    });

    root.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        this._showDeleteConfirm(btn.dataset.taskId);
      });
    });

    // Template add buttons
    root.querySelectorAll(".add-template-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        this._addFromTemplate(btn.dataset.templateId);
      });
    });
  }

  _showTaskDialog(task = null) {
    const t = this.t;
    const isEdit = task !== null;
    const dialog = document.createElement("div");
    dialog.innerHTML = `
      <div class="dialog-overlay">
        <div class="dialog">
          <h2>${isEdit ? t.editTask : t.addTask}</h2>
          <div class="form-group">
            <label>${t.name}</label>
            <input type="text" id="taskName" value="${isEdit ? this._escapeHtml(task.name) : ""}" />
          </div>
          <div class="form-group">
            <label>${t.description}</label>
            <textarea id="taskDesc" rows="3">${isEdit ? this._escapeHtml(task.description || "") : ""}</textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>${t.category}</label>
              <select id="taskCategory">
                ${Object.entries(t.categories)
                  .map(
                    ([val, label]) =>
                      `<option value="${val}" ${isEdit && task.category === val ? "selected" : ""}>${label}</option>`
                  )
                  .join("")}
              </select>
            </div>
            <div class="form-group">
              <label>${t.priority}</label>
              <select id="taskPriority">
                ${Object.entries(t.priorities)
                  .map(
                    ([val, label]) =>
                      `<option value="${val}" ${isEdit && task.priority === val ? "selected" : ""}>${label}</option>`
                  )
                  .join("")}
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>${t.interval}</label>
              <input type="number" id="taskIntervalValue" min="1" value="${isEdit ? task.interval_value : 1}" />
            </div>
            <div class="form-group">
              <label>${t.intervalUnit}</label>
              <select id="taskIntervalUnit">
                <option value="days" ${isEdit && task.interval_unit === "days" ? "selected" : ""}>${t.days}</option>
                <option value="weeks" ${isEdit && task.interval_unit === "weeks" ? "selected" : ""}>${t.weeks}</option>
                <option value="months" ${isEdit && task.interval_unit === "months" ? "selected" : "" || !isEdit ? "selected" : ""}>${t.months}</option>
                <option value="years" ${isEdit && task.interval_unit === "years" ? "selected" : ""}>${t.years}</option>
              </select>
            </div>
          </div>
          <div class="dialog-actions">
            <button class="btn" id="dialogCancel">${t.cancel}</button>
            <button class="btn btn-primary" id="dialogSave">${t.save}</button>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.appendChild(dialog);

    dialog.querySelector("#dialogCancel").addEventListener("click", () => dialog.remove());
    dialog.querySelector(".dialog-overlay").addEventListener("click", (e) => {
      if (e.target.classList.contains("dialog-overlay")) dialog.remove();
    });

    dialog.querySelector("#dialogSave").addEventListener("click", async () => {
      const name = dialog.querySelector("#taskName").value.trim();
      if (!name) return;

      const data = {
        name,
        description: dialog.querySelector("#taskDesc").value.trim(),
        category: dialog.querySelector("#taskCategory").value,
        priority: dialog.querySelector("#taskPriority").value,
        interval_value: parseInt(dialog.querySelector("#taskIntervalValue").value, 10),
        interval_unit: dialog.querySelector("#taskIntervalUnit").value,
      };

      try {
        if (isEdit) {
          await this._hass.callWS({
            type: "wartungsplaner/update_task",
            task_id: task.id,
            ...data,
          });
        } else {
          await this._hass.callWS({
            type: "wartungsplaner/add_task",
            ...data,
          });
        }
        dialog.remove();
        await this._loadData();
      } catch (e) {
        console.error("Wartungsplaner: Failed to save task", e);
      }
    });
  }

  _showCompleteDialog(taskId) {
    const t = this.t;
    const dialog = document.createElement("div");
    dialog.innerHTML = `
      <div class="dialog-overlay">
        <div class="dialog dialog-small">
          <h2>${t.completeTask}</h2>
          <div class="form-group">
            <label>${t.completionNotes}</label>
            <textarea id="completionNotes" rows="3"></textarea>
          </div>
          <div class="dialog-actions">
            <button class="btn" id="dialogCancel">${t.cancel}</button>
            <button class="btn btn-success" id="dialogComplete">
              <ha-icon icon="mdi:check"></ha-icon> ${t.completeTask}
            </button>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.appendChild(dialog);

    dialog.querySelector("#dialogCancel").addEventListener("click", () => dialog.remove());
    dialog.querySelector(".dialog-overlay").addEventListener("click", (e) => {
      if (e.target.classList.contains("dialog-overlay")) dialog.remove();
    });

    dialog.querySelector("#dialogComplete").addEventListener("click", async () => {
      const notes = dialog.querySelector("#completionNotes").value.trim();
      try {
        await this._hass.callWS({
          type: "wartungsplaner/complete_task",
          task_id: taskId,
          notes,
        });
        dialog.remove();
        await this._loadData();
      } catch (e) {
        console.error("Wartungsplaner: Failed to complete task", e);
      }
    });
  }

  _showDeleteConfirm(taskId) {
    const t = this.t;
    const dialog = document.createElement("div");
    dialog.innerHTML = `
      <div class="dialog-overlay">
        <div class="dialog dialog-small">
          <h2>${t.deleteTask}</h2>
          <p>${t.confirmDelete}</p>
          <div class="dialog-actions">
            <button class="btn" id="dialogCancel">${t.cancel}</button>
            <button class="btn btn-danger" id="dialogDelete">
              <ha-icon icon="mdi:delete"></ha-icon> ${t.delete}
            </button>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.appendChild(dialog);

    dialog.querySelector("#dialogCancel").addEventListener("click", () => dialog.remove());
    dialog.querySelector(".dialog-overlay").addEventListener("click", (e) => {
      if (e.target.classList.contains("dialog-overlay")) dialog.remove();
    });

    dialog.querySelector("#dialogDelete").addEventListener("click", async () => {
      try {
        await this._hass.callWS({
          type: "wartungsplaner/delete_task",
          task_id: taskId,
        });
        dialog.remove();
        await this._loadData();
      } catch (e) {
        console.error("Wartungsplaner: Failed to delete task", e);
      }
    });
  }

  async _addFromTemplate(templateId) {
    try {
      await this._hass.callWS({
        type: "wartungsplaner/add_from_template",
        template_id: templateId,
      });
      await this._loadData();
      this._activeTab = "tasks";
      this._render();
    } catch (e) {
      console.error("Wartungsplaner: Failed to add from template", e);
    }
  }

  _escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  _getStyles() {
    return `
      :host {
        display: block;
        --wp-primary: var(--primary-color, #03a9f4);
        --wp-bg: var(--primary-background-color, #fafafa);
        --wp-card-bg: var(--card-background-color, #ffffff);
        --wp-text: var(--primary-text-color, #212121);
        --wp-text-secondary: var(--secondary-text-color, #727272);
        --wp-divider: var(--divider-color, #e0e0e0);
        --wp-radius: 12px;
        --wp-shadow: var(--ha-card-box-shadow, 0 2px 6px rgba(0,0,0,0.1));
        font-family: var(--paper-font-body1_-_font-family, "Roboto", sans-serif);
      }

      .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 16px;
        color: var(--wp-text);
      }

      .header {
        margin-bottom: 16px;
      }

      .header h1 {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
        font-size: 24px;
        font-weight: 400;
        color: var(--wp-text);
      }

      .header h1 ha-icon {
        color: var(--wp-primary);
        --mdc-icon-size: 28px;
      }

      /* Tabs */
      .tabs {
        display: flex;
        gap: 4px;
        margin-bottom: 16px;
        border-bottom: 1px solid var(--wp-divider);
        padding-bottom: 0;
      }

      .tab {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 10px 20px;
        border: none;
        background: none;
        color: var(--wp-text-secondary);
        font-size: 14px;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
        font-family: inherit;
      }

      .tab:hover {
        color: var(--wp-text);
        background: var(--wp-divider);
        border-radius: 8px 8px 0 0;
      }

      .tab.active {
        color: var(--wp-primary);
        border-bottom-color: var(--wp-primary);
        font-weight: 500;
      }

      .tab ha-icon {
        --mdc-icon-size: 18px;
      }

      /* Stats */
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
      }

      .stat-card {
        background: var(--wp-card-bg);
        border-radius: var(--wp-radius);
        padding: 20px;
        text-align: center;
        box-shadow: var(--wp-shadow);
      }

      .stat-number {
        font-size: 36px;
        font-weight: 500;
        line-height: 1;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 13px;
        color: var(--wp-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .stat-overdue .stat-number { color: #b71c1c; }
      .stat-due-soon .stat-number { color: #ff9800; }
      .stat-done .stat-number { color: #4caf50; }

      /* Task List */
      h2 {
        font-size: 18px;
        font-weight: 500;
        margin: 0 0 12px;
        color: var(--wp-text);
      }

      .task-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .task-card {
        display: flex;
        background: var(--wp-card-bg);
        border-radius: var(--wp-radius);
        box-shadow: var(--wp-shadow);
        overflow: hidden;
        transition: transform 0.15s;
      }

      .task-card:hover {
        transform: translateY(-1px);
      }

      .task-status-bar {
        width: 5px;
        flex-shrink: 0;
      }

      .task-content {
        flex: 1;
        padding: 14px 16px;
        min-width: 0;
      }

      .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 6px;
        flex-wrap: wrap;
      }

      .task-title-row {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
      }

      .task-title-row ha-icon {
        --mdc-icon-size: 20px;
        flex-shrink: 0;
      }

      .task-name {
        font-weight: 500;
        font-size: 15px;
      }

      .task-badges {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
      }

      .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
      }

      .task-description {
        font-size: 13px;
        color: var(--wp-text-secondary);
        margin-bottom: 8px;
        line-height: 1.4;
      }

      .task-meta {
        display: flex;
        gap: 16px;
        font-size: 12px;
        color: var(--wp-text-secondary);
        flex-wrap: wrap;
      }

      .task-meta span {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .task-meta ha-icon {
        --mdc-icon-size: 14px;
      }

      .task-actions {
        display: flex;
        gap: 6px;
        margin-top: 10px;
        justify-content: flex-end;
      }

      /* Buttons */
      .btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        border: 1px solid var(--wp-divider);
        border-radius: 8px;
        background: var(--wp-card-bg);
        color: var(--wp-text);
        font-size: 14px;
        cursor: pointer;
        transition: all 0.15s;
        font-family: inherit;
      }

      .btn:hover {
        background: var(--wp-divider);
      }

      .btn ha-icon {
        --mdc-icon-size: 18px;
      }

      .btn-primary {
        background: var(--wp-primary);
        color: white;
        border-color: var(--wp-primary);
      }

      .btn-primary:hover {
        opacity: 0.9;
        background: var(--wp-primary);
      }

      .btn-success {
        background: #4caf50;
        color: white;
        border-color: #4caf50;
      }

      .btn-success:hover {
        opacity: 0.9;
        background: #4caf50;
      }

      .btn-danger {
        background: #f44336;
        color: white;
        border-color: #f44336;
      }

      .btn-danger:hover {
        opacity: 0.9;
        background: #f44336;
      }

      .btn-small {
        padding: 4px 10px;
        font-size: 12px;
      }

      .btn-small ha-icon {
        --mdc-icon-size: 16px;
      }

      /* Toolbar */
      .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      .filters {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        flex: 1;
      }

      .filter-select, .search-input {
        padding: 8px 12px;
        border: 1px solid var(--wp-divider);
        border-radius: 8px;
        background: var(--wp-card-bg);
        color: var(--wp-text);
        font-size: 14px;
        font-family: inherit;
      }

      .search-input {
        min-width: 180px;
        flex: 1;
      }

      /* Templates */
      .templates-view {
        padding-bottom: 16px;
      }

      .templates-intro {
        font-size: 14px;
        color: var(--wp-text-secondary);
        margin: 0 0 16px;
      }

      .template-category {
        margin-bottom: 20px;
      }

      .template-category h3 {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 10px;
        color: var(--wp-text);
      }

      .template-category h3 ha-icon {
        --mdc-icon-size: 20px;
        color: var(--wp-primary);
      }

      .template-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .template-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        background: var(--wp-card-bg);
        border-radius: var(--wp-radius);
        padding: 12px 16px;
        box-shadow: var(--wp-shadow);
      }

      .template-info {
        flex: 1;
        min-width: 0;
      }

      .template-name {
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 2px;
      }

      .template-desc {
        font-size: 12px;
        color: var(--wp-text-secondary);
        line-height: 1.4;
        margin-bottom: 6px;
      }

      .template-meta {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 12px;
        color: var(--wp-text-secondary);
      }

      /* Empty state */
      .empty-state {
        text-align: center;
        padding: 48px 16px;
        color: var(--wp-text-secondary);
      }

      .empty-state ha-icon {
        --mdc-icon-size: 48px;
        margin-bottom: 12px;
        opacity: 0.5;
      }

      .empty-state p {
        margin: 0;
        font-size: 15px;
      }

      /* Dialog */
      .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
        padding: 16px;
      }

      .dialog {
        background: var(--wp-card-bg);
        border-radius: var(--wp-radius);
        padding: 24px;
        width: 100%;
        max-width: 500px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      }

      .dialog-small {
        max-width: 400px;
      }

      .dialog h2 {
        margin: 0 0 16px;
        font-size: 20px;
      }

      .form-group {
        margin-bottom: 14px;
      }

      .form-group label {
        display: block;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 4px;
        color: var(--wp-text-secondary);
      }

      .form-group input,
      .form-group textarea,
      .form-group select {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid var(--wp-divider);
        border-radius: 8px;
        background: var(--wp-bg);
        color: var(--wp-text);
        font-size: 14px;
        font-family: inherit;
        box-sizing: border-box;
      }

      .form-group textarea {
        resize: vertical;
      }

      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }

      .dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 20px;
      }

      .dialog p {
        margin: 0 0 16px;
        color: var(--wp-text-secondary);
        line-height: 1.5;
      }

      /* Responsive */
      @media (max-width: 600px) {
        .container {
          padding: 8px;
        }

        .header h1 {
          font-size: 20px;
        }

        .stats-grid {
          grid-template-columns: repeat(2, 1fr);
        }

        .toolbar {
          flex-direction: column;
          align-items: stretch;
        }

        .filters {
          flex-direction: column;
        }

        .task-header {
          flex-direction: column;
        }

        .form-row {
          grid-template-columns: 1fr;
        }

        .tab {
          padding: 8px 12px;
          font-size: 13px;
        }
      }
    `;
  }
}

customElements.define("wartungsplaner-panel", WartungsplanerPanel);
