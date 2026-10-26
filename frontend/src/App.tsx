import { useEffect, useState } from "react";
import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { api } from "./api";
import { useAuth } from "./auth";
import Landing from "./pages/Landing";
import Privacy from "./pages/Privacy";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Resource from "./pages/Resource";
import Graph from "./pages/Graph";
import Assistant from "./pages/Assistant";
import Requests from "./pages/Requests";
import "./panel.css";

function Layout() {
  const { authed, logout } = useAuth();
  const [admin, setAdmin] = useState(false);
  useEffect(() => {
    if (authed) api<{ admin: boolean }>("/demo-requests/is-admin").then((d) => setAdmin(d.admin)).catch(() => setAdmin(false));
  }, [authed]);
  if (!authed) return <Navigate to="/login" replace />;
  return (
    <div className="panel">
      <div className="app">
        <nav aria-label="Panel">
          <b>AURA</b>
          <NavLink to="/app" end>Resumen</NavLink>
          <NavLink to="/app/customers">Clientes</NavLink>
          <NavLink to="/app/products">Productos</NavLink>
          <NavLink to="/app/warehouses">Bodegas</NavLink>
          <NavLink to="/app/graph">Grafo</NavLink>
          <NavLink to="/app/assistant">Asistente</NavLink>
          {admin && <NavLink to="/app/requests">Solicitudes</NavLink>}
          <span className="sp" />
          <a href="/">Ver sitio</a>
          <button className="ghost" onClick={logout}>Cerrar sesión</button>
        </nav>
        <main><Outlet /></main>
      </div>
    </div>
  );
}

const F = (name: string, label: string, type = "text", required = false) => ({ name, label, type, required });

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/privacidad" element={<Privacy />} />
      <Route path="/login" element={<Login />} />
      <Route path="/app" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="customers" element={<Resource path="/customers" title="Clientes" fields={[F("name", "Nombre", "text", true), F("email", "Correo", "email"), F("phone", "Teléfono")]} />} />
        <Route path="products" element={<Resource path="/products" title="Productos" fields={[F("sku", "SKU", "text", true), F("name", "Nombre", "text", true), F("price", "Precio", "number")]} />} />
        <Route path="warehouses" element={<Resource path="/warehouses" title="Bodegas" fields={[F("name", "Nombre", "text", true), F("location", "Ubicación")]} />} />
        <Route path="graph" element={<Graph />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="requests" element={<Requests />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
