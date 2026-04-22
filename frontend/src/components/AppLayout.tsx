import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Typography, Dropdown, theme } from 'antd';
import {
  DashboardOutlined,
  UserOutlined,
  TeamOutlined,
  HomeOutlined,
  AppstoreOutlined,
  ExperimentOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  MedicineBoxOutlined,
  FileTextOutlined,
  AimOutlined,
  CheckSquareOutlined,
  ToolOutlined,
  SafetyCertificateOutlined,
  DollarOutlined,
  BarChartOutlined,
  AuditOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
  WarningOutlined,
  CameraOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAuth } from '../auth/useAuth';
import type { Perfil } from '../types/auth';

const { Header, Sider, Content } = Layout;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
  allowedPerfis: Perfil[] | 'ALL';
}

interface MenuGroup {
  key: string;
  label: string;
  icon: React.ReactNode;
  children: MenuItem[];
}

const menuGroups: MenuGroup[] = [
  {
    key: 'geral',
    label: 'Geral',
    icon: <DashboardOutlined />,
    children: [
      {
        key: 'dashboard',
        icon: <DashboardOutlined />,
        label: 'Dashboard',
        path: '/dashboard',
        allowedPerfis: 'ALL',
      },
    ],
  },
  {
    key: 'cadastros',
    label: 'Cadastros',
    icon: <AppstoreOutlined />,
    children: [
      {
        key: 'usuarios',
        icon: <UserOutlined />,
        label: 'Usuários',
        path: '/usuarios',
        allowedPerfis: ['ADMINISTRADOR'],
      },
      {
        key: 'clientes',
        icon: <TeamOutlined />,
        label: 'Clientes',
        path: '/clientes',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
      {
        key: 'propriedades',
        icon: <HomeOutlined />,
        label: 'Propriedades',
        path: '/propriedades',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
      {
        key: 'talhoes',
        icon: <AppstoreOutlined />,
        label: 'Talhões',
        path: '/talhoes',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
      {
        key: 'culturas',
        icon: <ExperimentOutlined />,
        label: 'Culturas',
        path: '/culturas',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
      {
        key: 'tipos-ocorrencia',
        icon: <ExclamationCircleOutlined />,
        label: 'Tipos de Ocorrência',
        path: '/tipos-ocorrencia',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
    ],
  },
  {
    key: 'frota',
    label: 'Frota',
    icon: <RocketOutlined />,
    children: [
      {
        key: 'drones',
        icon: <RocketOutlined />,
        label: 'Drones',
        path: '/drones',
        allowedPerfis: ['ADMINISTRADOR'],
      },
      {
        key: 'baterias',
        icon: <ThunderboltOutlined />,
        label: 'Baterias',
        path: '/baterias',
        allowedPerfis: ['ADMINISTRADOR'],
      },
      {
        key: 'insumos',
        icon: <MedicineBoxOutlined />,
        label: 'Insumos',
        path: '/insumos',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
    ],
  },
  {
    key: 'operacoes',
    label: 'Operações',
    icon: <AimOutlined />,
    children: [
      {
        key: 'ordens-servico',
        icon: <FileTextOutlined />,
        label: 'Ordens de Serviço',
        path: '/ordens-servico',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL'],
      },
      {
        key: 'missoes',
        icon: <AimOutlined />,
        label: 'Missões',
        path: '/missoes',
        allowedPerfis: ['ADMINISTRADOR', 'COORDENADOR_OPERACIONAL', 'PILOTO', 'TECNICO'],
      },
      {
        key: 'checklists',
        icon: <CheckSquareOutlined />,
        label: 'Checklists',
        path: '/checklists',
        allowedPerfis: ['ADMINISTRADOR', 'PILOTO', 'TECNICO'],
      },
      {
        key: 'ocorrencias',
        icon: <WarningOutlined />,
        label: 'Ocorrências',
        path: '/ocorrencias',
        allowedPerfis: ['ADMINISTRADOR', 'PILOTO'],
      },
      {
        key: 'evidencias',
        icon: <CameraOutlined />,
        label: 'Evidências',
        path: '/evidencias',
        allowedPerfis: ['ADMINISTRADOR', 'PILOTO'],
      },
      {
        key: 'manutencoes',
        icon: <ToolOutlined />,
        label: 'Manutenções',
        path: '/manutencoes',
        allowedPerfis: ['ADMINISTRADOR', 'TECNICO'],
      },
    ],
  },
  {
    key: 'documentos',
    label: 'Documentos',
    icon: <SafetyCertificateOutlined />,
    children: [
      {
        key: 'documentos-oficiais',
        icon: <SafetyCertificateOutlined />,
        label: 'Documentos Oficiais',
        path: '/documentos',
        allowedPerfis: ['ADMINISTRADOR'],
      },
    ],
  },
  {
    key: 'financeiro-grupo',
    label: 'Financeiro',
    icon: <DollarOutlined />,
    children: [
      {
        key: 'financeiro',
        icon: <DollarOutlined />,
        label: 'Financeiro',
        path: '/financeiro',
        allowedPerfis: ['ADMINISTRADOR', 'FINANCEIRO'],
      },
      {
        key: 'relatorios',
        icon: <BarChartOutlined />,
        label: 'Relatórios',
        path: '/relatorios',
        allowedPerfis: ['ADMINISTRADOR', 'FINANCEIRO'],
      },
    ],
  },
  {
    key: 'sistema',
    label: 'Sistema',
    icon: <AuditOutlined />,
    children: [
      {
        key: 'auditoria',
        icon: <AuditOutlined />,
        label: 'Auditoria',
        path: '/auditoria',
        allowedPerfis: ['ADMINISTRADOR'],
      },
    ],
  },
];

function filterMenuByPerfil(perfil: Perfil): MenuProps['items'] {
  const result: MenuProps['items'] = [];

  for (const group of menuGroups) {
    const visibleChildren = group.children.filter(
      (item) => item.allowedPerfis === 'ALL' || item.allowedPerfis.includes(perfil),
    );

    if (visibleChildren.length === 0) continue;

    // If the group has only one child, show it as a top-level item
    if (visibleChildren.length === 1) {
      const child = visibleChildren[0];
      result.push({
        key: child.key,
        icon: child.icon,
        label: child.label,
      });
    } else {
      result.push({
        key: group.key,
        icon: group.icon,
        label: group.label,
        children: visibleChildren.map((child) => ({
          key: child.key,
          icon: child.icon,
          label: child.label,
        })),
      });
    }
  }

  return result;
}

function findPathByKey(key: string): string | undefined {
  for (const group of menuGroups) {
    for (const item of group.children) {
      if (item.key === key) return item.path;
    }
  }
  return undefined;
}

function findKeyByPath(pathname: string): string | undefined {
  for (const group of menuGroups) {
    for (const item of group.children) {
      if (item.path === pathname) return item.key;
    }
  }
  return undefined;
}

function findOpenGroupByPath(pathname: string): string[] {
  for (const group of menuGroups) {
    for (const item of group.children) {
      if (item.path === pathname) {
        // Only return group key if the group has multiple visible items
        // (single-item groups are rendered as top-level)
        return [group.key];
      }
    }
  }
  return [];
}

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { token: themeToken } = theme.useToken();

  const perfil = user?.perfil ?? 'PILOTO';
  const menuItems = filterMenuByPerfil(perfil);
  const selectedKey = findKeyByPath(location.pathname);
  const defaultOpenKeys = findOpenGroupByPath(location.pathname);

  const onMenuClick: MenuProps['onClick'] = ({ key }) => {
    const path = findPathByKey(key);
    if (path) navigate(path);
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sair',
      danger: true,
    },
  ];

  const onUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      logout();
      navigate('/login', { replace: true });
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        breakpoint="lg"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 48,
            margin: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 700,
            fontSize: collapsed ? 14 : 16,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
          }}
        >
          <RocketOutlined style={{ fontSize: 20, marginRight: collapsed ? 0 : 8 }} />
          {!collapsed && 'AgroFlightOps'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKey ? [selectedKey] : []}
          defaultOpenKeys={defaultOpenKeys}
          items={menuItems}
          onClick={onMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: themeToken.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={{ items: userMenuItems, onClick: onUserMenuClick }} placement="bottomRight">
            <Button type="text" icon={<UserOutlined />}>
              {user?.nome || user?.email || 'Usuário'}
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <div
            style={{
              padding: 24,
              background: themeToken.colorBgContainer,
              borderRadius: themeToken.borderRadiusLG,
              minHeight: 360,
            }}
          >
            <Outlet />
          </div>
        </Content>
        <Layout.Footer style={{ textAlign: 'center' }}>
          <Typography.Text type="secondary">
            AgroFlightOps ©{new Date().getFullYear()} — Gestão de Pulverização com Drones
          </Typography.Text>
        </Layout.Footer>
      </Layout>
    </Layout>
  );
}
