import React from "react";
import Register from "./pages/Register"; // ✅ Make sure path is correct
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ChatbotUI from "./components/ChatbotUI"; 

function App() {
  return (
    <Router>
      <Routes>
        {/* Default route for Register */}
        <Route path="/register" element={<Register />} />

        {/* Chatbot route */}
        <Route path="/chatbot" element={<ChatbotUI />} />
        <Route path="*" element={<Register />} /> 
      </Routes>
    </Router>
  );
}

export default App;
