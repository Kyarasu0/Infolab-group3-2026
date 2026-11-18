import React from "react";
import ReactDOM from "react-dom/client";

import { Dashboard } from "./components/5-Pages/01-Dashboard/Dashboard";
import "./global.css";
import { applyTheme } from "./theme/applyTheme";

applyTheme();
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Dashboard />
  </React.StrictMode>,
);
