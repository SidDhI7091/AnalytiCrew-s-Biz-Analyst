import React, { useState } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

const ChatbotUI = () => {
  const projectId = "1019"; // 🔥 Hardcoded for now
  const [messages, setMessages] = useState([
    { text: "Hello! I can help you fill missing requirements. 🚀", sender: "bot" }
  ]);
  const [input, setInput] = useState("");
  const [missingRequirements, setMissingRequirements] = useState([]);
  const [step, setStep] = useState(0); // 0 - Initial, 1 - User selection, 2 - Done

  const fetchMissingRequirements = async () => {
    try {
      const response = await fetch(`http://localhost:8000/gap-analysis/${projectId}`, {
        method: "POST",
      });
      const data = await response.json();
      if (data && data.missing && data.missing.length > 0) {
        setMissingRequirements(data.missing);

        // Format missing requirements list
        const formattedList = data.missing.map((item, idx) => `${idx + 1}. ${item}`).join("\n");

        // 🧠 Push messages to chat
        setMessages((prev) => [
          ...prev,
          { text: `🔎 Missing Requirements Detected:\n\n${formattedList}`, sender: "bot" },
          { text: "Please enter numbers (comma separated) to add, or type 'no' to skip.", sender: "bot" }
        ]);

        setStep(1);
      } else {
        setMessages((prev) => [...prev, { text: "No missing requirements found. ✅", sender: "bot" }]);
        setStep(2);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { text: "❌ Error fetching gap analysis!", sender: "bot" }]);
    }
  };

  const sendSelectedRequirements = async (selectedRequirements) => {
    try {
      const response = await fetch(`http://localhost:8000/gap-analysis/confirm-add/${projectId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requirements: selectedRequirements }),
      });

      if (!response.ok) {
        throw new Error("Failed to confirm add");
      }

      const result = await response.json();
      console.log("Server response after adding:", result);

      setMessages((prev) => [...prev, { text: "✅ Selected requirements have been added to Firestore!", sender: "bot" }]);
    } catch (error) {
      console.error("Error confirming additions:", error);
      setMessages((prev) => [...prev, { text: "❌ Failed to add requirements", sender: "bot" }]);
    }
  };

  const handleUserSubmit = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    // First, echo user's message
    setMessages((prev) => [...prev, { text: trimmedInput, sender: "user" }]);
    setInput("");

    if (step === 0) {
      // No gap triggered yet
      await fetchMissingRequirements();
      return;
    }

    if (step === 1) {
      if (trimmedInput.toLowerCase() === "no") {
        setMessages((prev) => [...prev, { text: "👍 Okay, no requirements will be added.", sender: "bot" }]);
        setStep(2);
        return;
      }

      const selectedIndexes = trimmedInput.split(",").map((num) => parseInt(num.trim()) - 1);
      const selectedReqs = selectedIndexes.map((idx) => missingRequirements[idx]).filter(Boolean);

      if (selectedReqs.length > 0) {
        await sendSelectedRequirements(selectedReqs);
      } else {
        setMessages((prev) => [...prev, { text: "⚡ Invalid input, please try again.", sender: "bot" }]);
      }

      setStep(2);
    }
  };

  return (
    <div className="flex flex-col h-[90vh] max-w-md mx-auto border p-4 rounded-lg shadow-md bg-white">
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={clsx(
              "p-2 rounded-lg max-w-xs whitespace-pre-line",
              msg.sender === "bot" ? "bg-gray-200 self-start" : "bg-blue-500 text-white self-end"
            )}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="flex mt-4">
        <input
          type="text"
          placeholder="Type here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleUserSubmit()}
          className="flex-1 border rounded-l-lg p-2 focus:outline-none"
        />
        <button onClick={handleUserSubmit} className="bg-blue-500 p-2 rounded-r-lg">
          <PaperAirplaneIcon className="h-5 w-5 text-white" />
        </button>
      </div>
    </div>
  );
};

export default ChatbotUI;
