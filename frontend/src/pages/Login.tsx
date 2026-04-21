import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { Button, Card, Form, Input, message, Typography } from 'antd';
import { LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../auth/useAuth';
import type { LoginRequest } from '../types/auth';

const { Title } = Typography;

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // Already logged in — go straight to dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const onFinish = async (values: LoginRequest) => {
    setLoading(true);
    try {
      await login(values.email, values.senha);
      navigate('/dashboard', { replace: true });
    } catch {
      message.error('Credenciais inválidas. Verifique email e senha.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f0f2f5',
      }}
    >
      <Card style={{ width: 380, boxShadow: '0 2px 8px rgba(0,0,0,0.09)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3} style={{ marginBottom: 4 }}>
            AgroFlightOps
          </Title>
          <Typography.Text type="secondary">
            Gestão de Pulverização com Drones
          </Typography.Text>
        </div>

        <Form<LoginRequest>
          name="login"
          onFinish={onFinish}
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Informe seu email' },
              { type: 'email', message: 'Email inválido' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Email"
              size="large"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="senha"
            rules={[{ required: true, message: 'Informe sua senha' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Senha"
              size="large"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              Entrar
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
