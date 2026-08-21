import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [stats, setStats] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingIncident, setEditingIncident] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [sortOption, setSortOption] = useState("Newest");

  const emptyIncident = {
    title: "",
    description: "",
    severity: "Medium",
    category: "General",
    priority: "Medium",
    status: "Open",
    reported_by: 1,
    assigned_to: "",
  };

  const [newIncident, setNewIncident] = useState(emptyIncident);

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      // The dashboard needs both the summary counts and the incident list.
      const [statsResponse, incidentsResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/dashboard/stats"),
        fetch("http://127.0.0.1:8000/incidents/"),
      ]);

      if (!statsResponse.ok) {
        throw new Error("Failed to load dashboard data");
      }

      if (!incidentsResponse.ok) {
        throw new Error("Failed to load incidents");
      }

      const statsData = await statsResponse.json();
      const incidentsData = await incidentsResponse.json();

      setStats(statsData);
      setIncidents(incidentsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleIncidentChange = (event) => {
    const { name, value } = event.target;

    setNewIncident((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleCreateIncident = async (event) => {
    event.preventDefault();
    setError("");

    // Form fields are strings, but the API expects user IDs to be numbers.
    const payload = {
      ...newIncident,
      reported_by: Number(newIncident.reported_by),
      assigned_to:
        newIncident.assigned_to === ""
          ? null
          : Number(newIncident.assigned_to),
    };

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/incidents/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create incident");
      }

      setNewIncident(emptyIncident);
      setShowCreateForm(false);

      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const startEditing = (incident) => {
    setEditingIncident({
      ...incident,
      assigned_to: incident.assigned_to ?? "",
    });

    setShowCreateForm(false);
  };

  const handleEditChange = (event) => {
    const { name, value } = event.target;

    setEditingIncident((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleUpdateIncident = async (event) => {
    event.preventDefault();
    setError("");

    // Send only the editable incident fields back to the API.
    const payload = {
      title: editingIncident.title,
      description: editingIncident.description,
      severity: editingIncident.severity,
      category: editingIncident.category,
      priority: editingIncident.priority,
      status: editingIncident.status,
      reported_by: Number(editingIncident.reported_by),
      assigned_to:
        editingIncident.assigned_to === ""
          ? null
          : Number(editingIncident.assigned_to),
    };

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/incidents/${editingIncident.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update incident");
      }

      setEditingIncident(null);
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteIncident = async (incidentId) => {
    const confirmed = window.confirm(
      `Delete incident #${incidentId}? This action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    setError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/incidents/${incidentId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete incident");
      }

      if (editingIncident?.id === incidentId) {
        setEditingIncident(null);
      }

      await loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  // Apply every active filter before sorting the results shown in the table.
  const filteredIncidents = incidents.filter((incident) => {
    const title = incident.title ?? "";
    const description = incident.description ?? "";

    const matchesSearch =
      title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesSeverity =
      severityFilter === "All" ||
      incident.severity === severityFilter;

    const matchesStatus =
      statusFilter === "All" ||
      incident.status === statusFilter;

    const matchesPriority =
      priorityFilter === "All" ||
      incident.priority === priorityFilter;

    const matchesCategory =
      categoryFilter === "All" ||
      incident.category === categoryFilter;

    return (
      matchesSearch &&
      matchesSeverity &&
      matchesStatus &&
      matchesPriority &&
      matchesCategory
    );
  });

  const sortedIncidents = [...filteredIncidents].sort((a, b) => {
    if (sortOption === "Newest") {
      return new Date(b.created_at) - new Date(a.created_at);
    }

    if (sortOption === "Oldest") {
      return new Date(a.created_at) - new Date(b.created_at);
    }

    if (sortOption === "Severity") {
      const severityRank = {
        Critical: 4,
        High: 3,
        Medium: 2,
        Low: 1,
      };

      return (
        (severityRank[b.severity] ?? 0) -
        (severityRank[a.severity] ?? 0)
      );
    }

    if (sortOption === "Priority") {
      const priorityRank = {
        High: 3,
        Medium: 2,
        Low: 1,
      };

      return (
        (priorityRank[b.priority] ?? 0) -
        (priorityRank[a.priority] ?? 0)
      );
    }

    return 0;
  });

  const resetFilters = () => {
    // Summary cards call this to start each shortcut from a clean view.
    setSearchTerm("");
    setSeverityFilter("All");
    setStatusFilter("All");
    setPriorityFilter("All");
    setCategoryFilter("All");
    setSortOption("Newest");
  };

  const scrollToIncidents = () => {
    // Wait for the filter state update before moving the user to the list.
    setTimeout(() => {
      document
        .querySelector(".incidents-panel")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 0);
  };

  const showAllIncidents = () => {
    resetFilters();
    scrollToIncidents();
  };

  const showOpenIncidents = () => {
    setSearchTerm("");
    setSeverityFilter("All");
    setStatusFilter("Open");
    setPriorityFilter("All");
    setCategoryFilter("All");
    setSortOption("Newest");
    scrollToIncidents();
  };

  const showClosedIncidents = () => {
    setSearchTerm("");
    setSeverityFilter("All");
    setStatusFilter("Closed");
    setPriorityFilter("All");
    setCategoryFilter("All");
    setSortOption("Newest");
    scrollToIncidents();
  };

  const showCriticalIncidents = () => {
    setSearchTerm("");
    setSeverityFilter("Critical");
    setStatusFilter("All");
    setPriorityFilter("All");
    setCategoryFilter("All");
    setSortOption("Newest");
    scrollToIncidents();
  };

  const getBadgeClass = (value) => {
    return `badge badge-${String(value)
      .toLowerCase()
      .replaceAll(" ", "-")}`;
  };

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Cyber Defense Center</h1>
          <p>Security Incident Management Dashboard</p>
        </div>
      </header>

      <main className="dashboard">
        <section className="dashboard-heading">
          <h2>Security Overview</h2>
          <p>
            Monitor incident activity, severity, priority, and
            response status.
          </p>
        </section>

        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {loading && (
          <div className="loading-message">
            Refreshing data...
          </div>
        )}

        {stats && (
          <>
            <section className="stats-grid">
              <button
                type="button"
                className="stat-card stat-card-button"
                onClick={showAllIncidents}
              >
                <span>Total Incidents</span>
                <strong>{stats.total_incidents}</strong>
              </button>

              <button
                type="button"
                className="stat-card stat-card-button"
                onClick={showOpenIncidents}
              >
                <span>Open Incidents</span>
                <strong>{stats.open_incidents}</strong>
              </button>

              <button
                type="button"
                className="stat-card stat-card-button"
                onClick={showClosedIncidents}
              >
                <span>Closed Incidents</span>
                <strong>{stats.closed_incidents}</strong>
              </button>

              <button
                type="button"
                className="stat-card stat-card-button critical"
                onClick={showCriticalIncidents}
              >
                <span>Critical Incidents</span>
                <strong>{stats.critical_incidents}</strong>
              </button>
            </section>

            <section className="analytics-grid">
              <div className="panel">
                <h3>Priority Breakdown</h3>

                <div className="metric-row">
                  <span>High</span>
                  <strong>
                    {stats.priority?.high ?? 0}
                  </strong>
                </div>

                <div className="metric-row">
                  <span>Medium</span>
                  <strong>
                    {stats.priority?.medium ?? 0}
                  </strong>
                </div>

                <div className="metric-row">
                  <span>Low</span>
                  <strong>
                    {stats.priority?.low ?? 0}
                  </strong>
                </div>
              </div>

              <div className="panel">
                <h3>Incident Categories</h3>

                <div className="metric-row">
                  <span>Phishing</span>
                  <strong>
                    {stats.categories?.phishing ?? 0}
                  </strong>
                </div>

                <div className="metric-row">
                  <span>Malware</span>
                  <strong>
                    {stats.categories?.malware ?? 0}
                  </strong>
                </div>

                <div className="metric-row">
                  <span>Ransomware</span>
                  <strong>
                    {stats.categories?.ransomware ?? 0}
                  </strong>
                </div>
              </div>
            </section>

            <section className="incidents-panel">
              <div className="section-header">
                <div>
                  <h3>Recent Incidents</h3>
                  <p>
                    Latest security incidents recorded by the
                    system.
                  </p>
                </div>

                <div className="header-actions">
                  <button
                    type="button"
                    className="create-button"
                    onClick={() => {
                      setEditingIncident(null);
                      setShowCreateForm(
                        (current) => !current
                      );
                    }}
                  >
                    + Create Incident
                  </button>

                  <button
                    type="button"
                    className="refresh-button"
                    onClick={loadData}
                  >
                    Refresh Data
                  </button>
                </div>
              </div>

              {showCreateForm && (
                <form
                  className="create-incident-form"
                  onSubmit={handleCreateIncident}
                >
                  <h3 className="form-title">
                    Create Incident
                  </h3>

                  <label className="form-field full-width">
                    <span>Title</span>
                    <input
                      type="text"
                      name="title"
                      value={newIncident.title}
                      onChange={handleIncidentChange}
                      required
                    />
                  </label>

                  <label className="form-field full-width">
                    <span>Description</span>
                    <textarea
                      name="description"
                      value={newIncident.description}
                      onChange={handleIncidentChange}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>Category</span>
                    <select
                      name="category"
                      value={newIncident.category}
                      onChange={handleIncidentChange}
                    >
                      <option value="General">
                        General
                      </option>
                      <option value="Phishing">
                        Phishing
                      </option>
                      <option value="Malware">
                        Malware
                      </option>
                      <option value="Ransomware">
                        Ransomware
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Severity</span>
                    <select
                      name="severity"
                      value={newIncident.severity}
                      onChange={handleIncidentChange}
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">
                        Medium
                      </option>
                      <option value="High">High</option>
                      <option value="Critical">
                        Critical
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Priority</span>
                    <select
                      name="priority"
                      value={newIncident.priority}
                      onChange={handleIncidentChange}
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">
                        Medium
                      </option>
                      <option value="High">High</option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Status</span>
                    <select
                      name="status"
                      value={newIncident.status}
                      onChange={handleIncidentChange}
                    >
                      <option value="Open">Open</option>
                      <option value="In Progress">
                        In Progress
                      </option>
                      <option value="Closed">
                        Closed
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Reported By</span>
                    <input
                      type="number"
                      name="reported_by"
                      value={newIncident.reported_by}
                      onChange={handleIncidentChange}
                      min="1"
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>Assigned To</span>
                    <input
                      type="number"
                      name="assigned_to"
                      value={newIncident.assigned_to}
                      onChange={handleIncidentChange}
                      min="1"
                    />
                  </label>

                  <div className="form-actions">
                    <button
                      type="submit"
                      className="submit-button"
                    >
                      Create Incident
                    </button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() =>
                        setShowCreateForm(false)
                      }
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}

              {editingIncident && (
                <form
                  className="create-incident-form edit-form"
                  onSubmit={handleUpdateIncident}
                >
                  <h3 className="form-title">
                    Edit Incident #{editingIncident.id}
                  </h3>

                  <label className="form-field full-width">
                    <span>Title</span>
                    <input
                      type="text"
                      name="title"
                      value={editingIncident.title}
                      onChange={handleEditChange}
                      required
                    />
                  </label>

                  <label className="form-field full-width">
                    <span>Description</span>
                    <textarea
                      name="description"
                      value={editingIncident.description}
                      onChange={handleEditChange}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>Category</span>
                    <select
                      name="category"
                      value={editingIncident.category}
                      onChange={handleEditChange}
                    >
                      <option value="General">
                        General
                      </option>
                      <option value="Phishing">
                        Phishing
                      </option>
                      <option value="Malware">
                        Malware
                      </option>
                      <option value="Ransomware">
                        Ransomware
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Severity</span>
                    <select
                      name="severity"
                      value={editingIncident.severity}
                      onChange={handleEditChange}
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">
                        Medium
                      </option>
                      <option value="High">High</option>
                      <option value="Critical">
                        Critical
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Priority</span>
                    <select
                      name="priority"
                      value={editingIncident.priority}
                      onChange={handleEditChange}
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">
                        Medium
                      </option>
                      <option value="High">High</option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Status</span>
                    <select
                      name="status"
                      value={editingIncident.status}
                      onChange={handleEditChange}
                    >
                      <option value="Open">Open</option>
                      <option value="In Progress">
                        In Progress
                      </option>
                      <option value="Closed">
                        Closed
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Reported By</span>
                    <input
                      type="number"
                      name="reported_by"
                      value={editingIncident.reported_by}
                      onChange={handleEditChange}
                      min="1"
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>Assigned To</span>
                    <input
                      type="number"
                      name="assigned_to"
                      value={editingIncident.assigned_to}
                      onChange={handleEditChange}
                      min="1"
                    />
                  </label>

                  <div className="form-actions">
                    <button
                      type="submit"
                      className="submit-button"
                    >
                      Save Changes
                    </button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() =>
                        setEditingIncident(null)
                      }
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}

              <div className="filters">
                <input
                  type="text"
                  placeholder="Search incidents..."
                  value={searchTerm}
                  onChange={(e) =>
                    setSearchTerm(e.target.value)
                  }
                />

                <select
                  value={severityFilter}
                  onChange={(e) =>
                    setSeverityFilter(e.target.value)
                  }
                >
                  <option value="All">
                    All Severities
                  </option>
                  <option value="Low">Low</option>
                  <option value="Medium">
                    Medium
                  </option>
                  <option value="High">High</option>
                  <option value="Critical">
                    Critical
                  </option>
                </select>

                <select
                  value={statusFilter}
                  onChange={(e) =>
                    setStatusFilter(e.target.value)
                  }
                >
                  <option value="All">
                    All Statuses
                  </option>
                  <option value="Open">Open</option>
                  <option value="In Progress">
                    In Progress
                  </option>
                  <option value="Closed">
                    Closed
                  </option>
                </select>

                <select
                  value={priorityFilter}
                  onChange={(e) =>
                    setPriorityFilter(e.target.value)
                  }
                >
                  <option value="All">
                    All Priorities
                  </option>
                  <option value="Low">Low</option>
                  <option value="Medium">
                    Medium
                  </option>
                  <option value="High">High</option>
                </select>

                <select
                  value={categoryFilter}
                  onChange={(e) =>
                    setCategoryFilter(e.target.value)
                  }
                >
                  <option value="All">
                    All Categories
                  </option>
                  <option value="General">
                    General
                  </option>
                  <option value="Phishing">
                    Phishing
                  </option>
                  <option value="Malware">
                    Malware
                  </option>
                  <option value="Ransomware">
                    Ransomware
                  </option>
                </select>

                <select
                  value={sortOption}
                  onChange={(e) =>
                    setSortOption(e.target.value)
                  }
                >
                  <option value="Newest">
                    Newest First
                  </option>
                  <option value="Oldest">
                    Oldest First
                  </option>
                  <option value="Severity">
                    Severity
                  </option>
                  <option value="Priority">
                    Priority
                  </option>
                </select>

                <button
                  type="button"
                  className="reset-button"
                  onClick={resetFilters}
                >
                  Reset Filters
                </button>
              </div>

              <div className="table-wrapper">
                <table className="incidents-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Severity</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Assigned To</th>
                      <th>Actions</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedIncidents.length === 0 ? (
                      <tr>
                        <td colSpan="8">
                          No incidents found.
                        </td>
                      </tr>
                    ) : (
                      sortedIncidents.map((incident) => (
                        <tr key={incident.id}>
                          <td>{incident.id}</td>
                          <td>{incident.title}</td>
                          <td>{incident.category}</td>

                          <td>
                            <span
                              className={getBadgeClass(
                                incident.severity
                              )}
                            >
                              {incident.severity}
                            </span>
                          </td>

                          <td>
                            <span
                              className={getBadgeClass(
                                incident.priority
                              )}
                            >
                              {incident.priority}
                            </span>
                          </td>

                          <td>
                            <span
                              className={getBadgeClass(
                                incident.status
                              )}
                            >
                              {incident.status}
                            </span>
                          </td>

                          <td>
                            {incident.assigned_to ??
                              "Unassigned"}
                          </td>

                          <td>
                            <div className="row-actions">
                              <button
                                type="button"
                                className="edit-button"
                                onClick={() =>
                                  startEditing(incident)
                                }
                              >
                                Edit
                              </button>

                              <button
                                type="button"
                                className="delete-button"
                                onClick={() =>
                                  handleDeleteIncident(
                                    incident.id
                                  )
                                }
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;