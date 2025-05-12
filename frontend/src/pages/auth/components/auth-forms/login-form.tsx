import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Form, Input, Button, message, Checkbox, Flex, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { authApi } from '../../../../services/auth';
import { setToken } from '../../../../lib/helpers/auth-tokens';

const { Link } = Typography;

interface LoginFormInputs {
  email: string;
  password: string;
  remember: boolean;
}

const LoginForm = () => {
  const [loading, setLoading] = useState(false);
  const { control, handleSubmit, formState: { errors } } = useForm<LoginFormInputs>({
    defaultValues: {
      remember: true
    }
  });

  const onSubmit = async (data: LoginFormInputs) => {
    setLoading(true);
    try {
      const response = await authApi.login({
        email: data.email,
        password: data.password
      });
      setToken(response.access_token);
      // setRefreshToken(response.refresh_token);
      message.success('Login successful!');
      window.location.href = '/home';
    } catch (error) {
      console.error('Login failed:', error);
      message.error('Login failed. Please check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form layout="vertical" onFinish={handleSubmit(onSubmit)} style={{ width: '100%' }}>
      <Form.Item
        label="Email"
        validateStatus={errors.email ? 'error' : undefined}
        help={errors.email?.message}
      >
        <Controller
          name="email"
          control={control}
          rules={{
            required: 'Please input your email',
            pattern: {
              value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Please enter a valid email address',
            },
          }}
          render={({ field }) => (
            <Input
              {...field}
              prefix={<UserOutlined style={{ marginRight: 4 }} />}
              placeholder="Enter your email"
              size="large"
              style={{ height: '50px', borderRadius: '8px' }}
            />
          )}
        />
      </Form.Item>

      <Form.Item
        label="Password"
        validateStatus={errors.password ? 'error' : undefined}
        help={errors.password?.message}
      >
        <Controller
          name="password"
          control={control}
          rules={{
            required: 'Please input your password',
            minLength: {
              value: 6,
              message: 'Password must be at least 6 characters',
            },
          }}
          render={({ field }) => (
            <Input.Password
              {...field}
              prefix={<LockOutlined style={{ marginRight: 4 }} />}
              placeholder="Enter your password"
              size="large"
              style={{ height: '50px', borderRadius: '8px' }}
            />
          )}
        />
      </Form.Item>

      <Flex justify="space-between" align="center" style={{ marginBottom: '20px' }}>
        <Controller
          name="remember"
          control={control}
          render={({ field: { value, onChange } }) => (
            <Checkbox disabled checked={value} onChange={onChange}>
              Remember me
            </Checkbox>
          )}
        />
        <Link disabled href="/auth/forgot-password">Forgot password?</Link>
      </Flex>

      <Button
        type="primary"
        htmlType="submit"
        size="large"
        shape="round"
        loading={loading}
        block
      >
        Log In
      </Button>
    </Form>
  );
};

export default LoginForm;