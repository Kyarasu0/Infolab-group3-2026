import React from "react";
import ReactDOM from "react-dom/client";

import { Dashboard } from "./components/5-Pages/01-Dashboard/Dashboard";
import "./theme/tokens.css";
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Dashboard />
  </React.StrictMode>,
);
