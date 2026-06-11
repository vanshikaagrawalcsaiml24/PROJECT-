function ProjectScoreCard({ result }) {
  const score = result?.project_score || {
    innovation: 8,
    complexity: 7,
    scalability: 9,
    overall: 8,
  };

  return (
    <div className="card">
      <h2>Project Evaluation</h2>

      <div className="team-grid">
        <div className="team-member">
          <h3>Innovation</h3>
          <p>{score.innovation}/10</p>
        </div>

        <div className="team-member">
          <h3>Complexity</h3>
          <p>{score.complexity}/10</p>
        </div>

        <div className="team-member">
          <h3>Scalability</h3>
          <p>{score.scalability}/10</p>
        </div>

        <div className="team-member">
          <h3>Overall Score</h3>
          <p>{score.overall}/10</p>
        </div>
      </div>
    </div>
  );
}

export default ProjectScoreCard;