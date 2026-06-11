import { useState } from "react";
import { Sparkles, Paperclip, Wand2 } from "lucide-react";

function PromptCanvas({ setResult }) {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!idea.trim()) {
      alert("Please enter project idea");
      return;
    }

    try {
      setLoading(true);

     const response = await fetch("https://project-3e9l.onrender.com/generate-blueprint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_idea: idea,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Something went wrong");
        return;
      }

      setResult(data);
    } catch (error) {
      console.error("Backend error:", error);
      alert("Backend connect nahi ho raha. Check karo backend server running hai ya nahi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prompt-card">
      <div className="prompt-header">
        <div>
          <h2>Project Idea</h2>
          <p>Describe your idea and generate a structured project blueprint.</p>
        </div>

        <span className="ai-badge">
          <Sparkles size={14} />
          AI Powered
        </span>
      </div>

      <textarea
        placeholder="Example: Build an AI interview preparation platform..."
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
      />

      <div className="prompt-actions">
        <button className="secondary-btn" type="button">
          <Paperclip size={16} />
          Attach File
        </button>

        <button className="secondary-btn" type="button">
          <Wand2 size={16} />
          Enhance Prompt
        </button>

       <button
  className="primary-btn"
  type="button"
  onClick={() => {
    console.log("Generate clicked");
    handleGenerate();
  }}
  disabled={loading}
>
  {loading ? "Generating..." : "Generate Blueprint"}
</button>
      </div>
    </div>
  );
}

export default PromptCanvas;