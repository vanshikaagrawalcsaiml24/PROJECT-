import { Search, Bell } from "lucide-react";
import jsPDF from "jspdf";

function Topbar({ result }) {
  const handleExportPDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("ProjectMentor AI - Project Blueprint Report", 15, 20);

    doc.setFontSize(12);

    let y = 35;

    doc.text("1. Project Blueprint", 15, y);
    y += 10;
    doc.text(result?.blueprint || "No blueprint generated yet.", 15, y, {
      maxWidth: 180,
    });

    y += 30;
    doc.text("2. Architecture", 15, y);
    y += 10;
    doc.text(result?.architecture || "No architecture generated yet.", 15, y, {
      maxWidth: 180,
    });

    y += 30;
    doc.text("3. Tech Stack", 15, y);
    y += 10;
    doc.text(
      `Frontend: ${result?.tech_stack?.frontend || "React + Vite"}`,
      15,
      y
    );
    y += 8;
    doc.text(`Backend: ${result?.tech_stack?.backend || "FastAPI"}`, 15, y);
    y += 8;
    doc.text(`AI Layer: ${result?.tech_stack?.ai || "Gemini API"}`, 15, y);
    y += 8;
    doc.text(`Database: ${result?.tech_stack?.database || "MongoDB"}`, 15, y);

    y += 20;
    doc.text("4. Risk Analysis", 15, y);
    y += 10;
    doc.text("API Cost Risk: Medium", 15, y);
    y += 8;
    doc.text("Security Risk: Low", 15, y);
    y += 8;
    doc.text("Scalability Risk: Medium", 15, y);
    y += 8;
    doc.text("Deployment Risk: Low", 15, y);

    doc.save("ProjectMentor-Blueprint.pdf");
  };

  return (
    <div className="topbar">
      <div className="search-box">
        <Search size={18} />
        <input placeholder="Search projects, blueprints, tech stacks..." />
      </div>

      <div className="topbar-actions">
        <Bell size={20} />
        <button className="export-btn" onClick={handleExportPDF}>
          Export PDF
        </button>
      </div>
    </div>
  );
}

export default Topbar;