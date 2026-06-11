import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import PromptCanvas from "../components/PromptCanvas";
import BlueprintCard from "../components/BlueprintCard";
import ArchitectureCard from "../components/ArchitectureCard";
import RoadmapCard from "../components/RoadmapCard";
import TeamPlannerCard from "../components/TeamPlannerCard";
import ProjectScoreCard from "../components/ProjectScorecard";
import RiskAnalysisCard from "../components/RiskAnalysisCard";
import AISuggestionsCard from "../components/AISuggestionsCard";
import ProjectHealthCard from "../components/ProjectHealthCard";

function Dashboard() {
  const [result, setResult] = useState(null);
  const [activePage, setActivePage] = useState("dashboard");

  return (
    <div className="dashboard">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <main className="content">
        <Topbar result={result} />

        <div className="welcome-section">
          <h1 className="hero-title">
            Project Architecture <span>Studio</span>
          </h1>
          <p>
            Generate complete AI-powered project blueprints, architecture,
            roadmap, and technology recommendations.
          </p>
        </div>

        <div className="stats">
          <div className="stat-card">
            <h3>50+</h3>
            <p>Blueprints Generated</p>
          </div>

          <div className="stat-card">
            <h3>20+</h3>
            <p>Tech Stacks</p>
          </div>

          <div className="stat-card">
            <h3>15+</h3>
            <p>Architecture Templates</p>
          </div>
        </div>

        <div className="cards-grid">
          {activePage === "dashboard" && (
            <>
              <PromptCanvas setResult={setResult} />
              <BlueprintCard result={result} />
              <ProjectScoreCard result={result} />
            </>
          )}

          {activePage === "architecture" && (
            <ArchitectureCard result={result} />
          )}

          {activePage === "roadmap" && (
            <RoadmapCard result={result} />
          )}

          {activePage === "team" && (
            <TeamPlannerCard result={result} />
          )}

          {activePage === "risk" && (
            <>
              <RiskAnalysisCard result={result} />
              <AISuggestionsCard result={result} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;