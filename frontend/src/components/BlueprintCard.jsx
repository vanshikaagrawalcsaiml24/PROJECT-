function BlueprintCard({ result }) {
  return (
    <div className="card">
      <h2>Generated Blueprint</h2>

      <div className="mini-card">
        <h3>Problem Statement</h3>
        <p>
          {result?.problem_statement ||
            "AI generated content will appear here."}
        </p>
      </div>

      <div className="mini-card">
        <h3>Objectives</h3>
        {result?.objectives ? (
          <ul>
            {result.objectives.map((obj, index) => (
              <li key={index}>{obj}</li>
            ))}
          </ul>
        ) : (
          <p>Project objectives will appear here.</p>
        )}
      </div>

      <div className="mini-card">
        <h3>Recommended Tech Stack</h3>
        {result?.tech_stack ? (
          <p>{result.tech_stack.join(" • ")}</p>
        ) : (
          <p>React • FastAPI • Gemini • MongoDB</p>
        )}
      </div>
    </div>
  );
}

export default BlueprintCard;