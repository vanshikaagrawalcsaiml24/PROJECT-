function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="sidebar">
      <h2>ProjectMentor AI</h2>

      <ul>
        <li
          className={activePage === "dashboard" ? "active-menu" : ""}
          onClick={() => setActivePage("dashboard")}
        >
          Dashboard
        </li>

        <li
          className={activePage === "architecture" ? "active-menu" : ""}
          onClick={() => setActivePage("architecture")}
        >
          Architecture Studio
        </li>

        <li
          className={activePage === "roadmap" ? "active-menu" : ""}
          onClick={() => setActivePage("roadmap")}
        >
          Roadmap Builder
        </li>

        <li
          className={activePage === "team" ? "active-menu" : ""}
          onClick={() => setActivePage("team")}
        >
          Team Planner
        </li>

        <li
          className={activePage === "risk" ? "active-menu" : ""}
          onClick={() => setActivePage("risk")}
        >
          Risk & Suggestions
        </li>
      </ul>
    </aside>
  );
}

export default Sidebar;