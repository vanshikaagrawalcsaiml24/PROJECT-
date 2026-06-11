function TeamPlannerCard({ result }) {
  const roles = result?.team_roles || [
    "Frontend Developer",
    "Backend Developer",
    "AI Engineer",
    "Tester",
    "Project Manager",
    "Documentation Lead",
  ];

  return (
    <div className="card">
      <h2>Team Planner</h2>

      <div className="team-grid">
        {roles.map((role, index) => (
          <div className="team-role" key={index}>
            <h3>{role}</h3>
            <p>
              {role === "Frontend Developer" && "React UI, dashboard, API integration"}
              {role === "Backend Developer" && "FastAPI, routes, database and API logic"}
              {role === "AI/ML Engineer" && "Prompt design, AI response formatting and model testing"}
              {role === "Database Engineer" && "Database schema, storage and data handling"}
              {role === "UI/UX Designer" && "User interface design and user experience flow"}
              {![
                "Frontend Developer",
                "Backend Developer",
                "AI/ML Engineer",
                "Database Engineer",
                "UI/UX Designer",
              ].includes(role) && "Project task contribution and implementation"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TeamPlannerCard;