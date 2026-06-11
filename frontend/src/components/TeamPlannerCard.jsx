function TeamPlannerCard() {
  return (
    <div className="card">
      <h2>👥 Team Planner</h2>

      <div className="team-grid">
        <div className="team-role">
          <h3>Frontend Developer (2)</h3>
          <p>React UI, dashboard, API integration</p>
        </div>

        <div className="team-role">
          <h3>Backend Developer</h3>
          <p>FastAPI, routes, Gemini connection</p>
        </div>

        <div className="team-role">
          <h3>AI Engineer</h3>
          <p>Prompt design and AI response formatting</p>
        </div>

        <div className="team-role">
          <h3>Tester</h3>
          <p>Bug testing and validation</p>
        </div>
        <div className="team-role">
  <h3>Project Manager</h3>
  <p>Task planning and team coordination</p>
</div>

<div className="team-role">
  <h3>Documentation Lead</h3>
  <p>Reports, PPT and project documentation</p>
</div>
      </div>
    </div>
  );
}

export default TeamPlannerCard;
