import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import AppLayout from './components/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Usuarios from './pages/Usuarios';
import Clientes from './pages/Clientes';
import Propriedades from './pages/Propriedades';
import Talhoes from './pages/Talhoes';
import Culturas from './pages/Culturas';
import TiposOcorrencia from './pages/TiposOcorrencia';
import Drones from './pages/Drones';
import Baterias from './pages/Baterias';
import Insumos from './pages/Insumos';
import OrdensServico from './pages/OrdensServico';
import Missoes from './pages/Missoes';
import Checklists from './pages/Checklists';
import Manutencoes from './pages/Manutencoes';
import Documentos from './pages/Documentos';
import Financeiro from './pages/Financeiro';
import Relatorios from './pages/Relatorios';
import Auditoria from './pages/Auditoria';
import Ocorrencias from './pages/Ocorrencias';
import Evidencias from './pages/Evidencias';

export default function App() {
  return (
    <ConfigProvider locale={ptBR}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<Login />} />

            {/* Authenticated — wrapped in AppLayout */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />

                {/* Cadastros */}
                <Route path="/clientes" element={<Clientes />} />
                <Route path="/propriedades" element={<Propriedades />} />
                <Route path="/talhoes" element={<Talhoes />} />
                <Route path="/culturas" element={<Culturas />} />
                <Route path="/insumos" element={<Insumos />} />
                <Route path="/tipos-ocorrencia" element={<TiposOcorrencia />} />

                {/* Frota — Administrador only */}
                <Route path="/drones" element={<Drones />} />
                <Route path="/baterias" element={<Baterias />} />

                {/* Operações */}
                <Route path="/ordens-servico" element={<OrdensServico />} />
                <Route path="/missoes" element={<Missoes />} />
                <Route path="/checklists" element={<Checklists />} />
                <Route path="/ocorrencias" element={<Ocorrencias />} />
                <Route path="/evidencias" element={<Evidencias />} />
                <Route path="/manutencoes" element={<Manutencoes />} />

                {/* Documentos */}
                <Route path="/documentos" element={<Documentos />} />

                {/* Financeiro */}
                <Route path="/financeiro" element={<Financeiro />} />
                <Route path="/relatorios" element={<Relatorios />} />

                {/* Sistema — Administrador only */}
                <Route path="/usuarios" element={<Usuarios />} />
                <Route path="/auditoria" element={<Auditoria />} />
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ConfigProvider>
  );
}
