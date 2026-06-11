function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="sidebar">
      <h2>ProjectMentor AI</h2>

      <ul>
        <li onClick={() => setActivePage("dashboard")}>
          Dashboard
        </li>

        <li onClick={() => setActivePage("architecture")}>
          Architecture Studio
        </li>

        <li onClick={() => setActivePage("roadmap")}>
          Roadmap Builder
        </li>

        <li onClick={() => setActivePage("team")}>
          Team Planner
        </li>

        <li onClick={() => setActivePage("score")}>
          Project Score
        </li>

        <li onClick={() => setActivePage("health")}>
          Project Health
        </li>

        <li onClick={() => setActivePage("risk")}>
          Risk Analysis
        </li>

        <li onClick={() => setActivePage("suggestions")}>
          AI Suggestions
        </li>
      </ul>
    </aside>
  );
}

export default Sidebar;