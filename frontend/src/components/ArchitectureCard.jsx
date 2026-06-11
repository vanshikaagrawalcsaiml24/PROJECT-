function ArchitectureCard({ result }) {
  return (
    <div className="card">
      <h2>Architecture Studio</h2>

      <div className="architecture-flow">
        <div className="architecture-box">
          Frontend
          <span>
            {result?.tech_stack?.frontend || "React + Vite"}
          </span>
        </div>

        <div className="arrow">↓</div>

        <div className="architecture-box">
          Backend
          <span>
            {result?.tech_stack?.backend || "FastAPI"}
          </span>
        </div>

        <div className="arrow">↓</div>

        <div className="architecture-box">
          AI Layer
          <span>
            {result?.tech_stack?.ai || "Gemini API"}
          </span>
        </div>

        <div className="arrow">↓</div>

        <div className="architecture-box">
          Database
          <span>
            {result?.tech_stack?.database || "MongoDB"}
          </span>
        </div>
      </div>

      <div className="arrow">↓</div>

<div className="architecture-box">
  Deployment
  <span>
    {result?.tech_stack?.deployment || "Vercel + Render"}
  </span>
</div> 

      {result?.architecture && (
        <div className="mini-card">
          <h3>Architecture Details</h3>
          <p>{result.architecture}</p>
        </div>
      )}
    </div>
  );
}

export default ArchitectureCard;