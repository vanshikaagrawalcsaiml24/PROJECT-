function RoadmapCard({ result }) {
  const roadmap = result?.roadmap || [
    "Idea Analysis",
    "Architecture Design",
    "Frontend Development",
    "Backend Integration",
    "Testing & Deployment",
  ];

  return (
    <div className="card">
      <h2>Timeline Roadmap</h2>

      <div className="timeline">
        {roadmap.map((item, index) => (
          <div className="timeline-item" key={index}>
            <div className="timeline-dot"></div>
            <div>
              <h3>Week {index + 1}</h3>
              <p>{item}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RoadmapCard;