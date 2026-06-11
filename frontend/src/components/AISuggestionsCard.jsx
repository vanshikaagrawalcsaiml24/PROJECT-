function AISuggestionsCard() {
  return (
    <div className="card">
      <h2>AI Recommendations</h2>

      <ul className="roadmap-list">
        <li>Use JWT Authentication</li>
        <li>Use Redis for Caching</li>
        <li>Deploy Frontend on Vercel</li>
        <li>Deploy Backend on Render</li>
        <li>Add Rate Limiting</li>
      </ul>
    </div>
  );
}

export default AISuggestionsCard;