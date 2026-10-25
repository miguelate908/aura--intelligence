import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Landing from "./landing/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Resource from "./pages/Resource";
import Assistant from "./pages/Assistant";
import Graph from "./pages/Graph";

function Layout() {
  const { authed, logout } = useAuth();
  if (!authed) return <Navigate to="/login" replace />;
  return (
    <div className="app">
      <nav aria-label="Panel">
        <b>AURA</b>
        <NavLink to="/app" end>Resumen</NavLink>
        <NavLink to="/app/customers">Clientes</NavLink>
        <NavLink to="/app/products">Productos</NavLink>
        <NavLink to="/app/warehouses">Bodegas</NavLink>
        <NavLink to="/app/graph">Grafo</NavLink>
        <NavLink to="/app/assistant">Asistente IA</NavLink>
        <span className="sp" />
        <button className="ghost" onClick={logout}>Cerrar sesión</button>
      </nav>
      <main><Outlet /></main>
    </div>
  );
}

const F = (name: string, label: string, type = "text", required = false) => ({ name, label, type, required });

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/app" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="customers" element={<Resource path="/customers" title="Clientes" fields={[F("name", "Nombre", "text", true), F("email", "Correo", "email"), F("phone", "Teléfono")]} />} />
        <Route path="products" element={<Resource path="/products" title="Productos" fields={[F("sku", "SKU", "text", true), F("name", "Nombre", "text", true), F("price", "Precio", "number")]} />} />
        <Route path="warehouses" element={<Resource path="/warehouses" title="Bodegas" fields={[F("name", "Nombre", "text", true), F("location", "Ubicación")]} />} />
        <Route path="graph" element={<Graph />} />
        <Route path="assistant" element={<Assistant />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
