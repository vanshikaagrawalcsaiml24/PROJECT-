function ProjectHealthCard() {
  const items = [
    { name: "Feasibility", value: "92%" },
    { name: "Innovation", value: "84%" },
    { name: "Scalability", value: "88%" },
    { name: "Risk Control", value: "76%" },
  ];

  return (
    <div className="card">
      <h2>Project Health</h2>

      <div className="health-list">
        {items.map((item) => (
          <div className="health-item" key={item.name}>
            <div className="health-top">
              <span>{item.name}</span>
              <span>{item.value}</span>
            </div>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{ width: item.value }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProjectHealthCard;