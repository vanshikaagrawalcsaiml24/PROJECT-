function BlueprintCard({ result }) {
  if (!result) {
    return (
      <div className="card">
        <h2>Generated Blueprint</h2>

        <div className="mini-card">
          <h3>Problem Statement</h3>
          <p>AI generated content will appear here.</p>
        </div>

        <div className="mini-card">
          <h3>Objectives</h3>
          <p>Project objectives will appear here.</p>
        </div>

        <div className="mini-card">
          <h3>Recommended Tech Stack</h3>
          <p>React • FastAPI • Gemini • MongoDB</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Generated Blueprint</h2>

      <div className="mini-card">
        <h3>Problem Statement</h3>
        <p>{result.problem_statement}</p>
      </div>

      <div className="mini-card">
        <h3>Objectives</h3>

        <ul>
          {result.objectives?.map((obj, index) => (
            <li key={index}>{obj}</li>
          ))}
        </ul>
      </div>

      <div className="mini-card">
        <h3>Target Users</h3>

        <ul>
          {result.target_users?.map((user, index) => (
            <li key={index}>{user}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default BlueprintCard;