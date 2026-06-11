function RiskAnalysisCard() {
  return (
    <div className="card">
      <h2>Risk Analysis</h2>

      <div className="team-grid">
        <div className="team-member">
          <h3>API Cost</h3>
          <p>Medium</p>
        </div>

        <div className="team-member">
          <h3>Security</h3>
          <p>Low</p>
        </div>

        <div className="team-member">
          <h3>Scalability</h3>
          <p>Medium</p>
        </div>

        <div className="team-member">
          <h3>Deployment</h3>
          <p>Low</p>
        </div>
      </div>

      <div className="mini-card">
        <h3>Overall Risk Score</h3>
        <p>6.5 / 10</p>
      </div>
    </div>
  );
}

export default RiskAnalysisCard;