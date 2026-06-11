function ProjectScoreCard({ result }) {
  return (
    <div className="card">
      <h2>Project Evaluation</h2>

      <div className="team-grid">
        <div className="team-member">
          <h3>Innovation</h3>
          <p>8/10</p>
        </div>

        <div className="team-member">
          <h3>Complexity</h3>
          <p>7/10</p>
        </div>

        <div className="team-member">
          <h3>Scalability</h3>
          <p>9/10</p>
        </div>

        <div className="team-member">
          <h3>Overall Score</h3>
          <p>8.0/10</p>
        </div>
      </div>
    </div>
  );
}

export default ProjectScoreCard;