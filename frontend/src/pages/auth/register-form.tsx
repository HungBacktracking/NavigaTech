import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Form, Input, Button, message, Typography, Checkbox } from 'antd';
import { LockOutlined, MailOutlined } from '@ant-design/icons';
import { authApi } from '../../services/auth';

const { Link } = Typography;

interface RegisterFormInputs {
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

const RegisterForm = () => {
  const [loading, setLoading] = useState(false);
  const { control, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormInputs>({
    defaultValues: {
      agreeToTerms: false
    }
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormInputs) => {
    if (!data.agreeToTerms) {
      message.error('Please agree to the terms and conditions');
      return;
    }

    setLoading(true);
    try {
      await authApi.register({
        email: data.email,
        password: data.password
      });
      message.success('Registration successful! Please upload your CV to continue.');
      window.location.href = '/auth/upload-cv';
    } catch (error) {
      console.error('Registration failed:', error);
      message.error('Registration failed. Please try again.');
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
              prefix={<MailOutlined style={{ marginRight: 4 }} />}
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
            // pattern: {
            //   value: /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
            //   message: 'Password must contain uppercase, lowercase, number and special character',
            // }
          }}
          render={({ field }) => (
            <Input.Password
              {...field}
              prefix={<LockOutlined style={{ marginRight: 4 }} />}
              placeholder="Create a strong password"
              size="large"
              style={{ height: '50px', borderRadius: '8px' }}
            />
          )}
        />
      </Form.Item>

      <Form.Item
        label="Confirm Password"
        validateStatus={errors.confirmPassword ? 'error' : undefined}
        help={errors.confirmPassword?.message}
      >
        <Controller
          name="confirmPassword"
          control={control}
          rules={{
            required: 'Please confirm your password',
            validate: value => value === password || 'The passwords do not match'
          }}
          render={({ field }) => (
            <Input.Password
              {...field}
              prefix={<LockOutlined style={{ marginRight: 4 }} />}
              placeholder="Confirm your password"
              size="large"
              style={{ height: '50px', borderRadius: '8px' }}
            />
          )}
        />
      </Form.Item>

      <Form.Item style={{ marginBottom: '24px' }}>
        <Controller
          name="agreeToTerms"
          control={control}
          rules={{
            required: 'You must agree to the terms and conditions'
          }}
          render={({ field: { value, onChange } }) => (
            <Checkbox checked={value} onChange={onChange}>
              I agree to the <Link disabled href="/terms">Terms and Conditions</Link> and <Link disabled href="/privacy">Privacy Policy</Link>
            </Checkbox>
          )}
        />
        {errors.agreeToTerms && (
          <div style={{ color: '#ff4d4f' }}>{errors.agreeToTerms.message}</div>
        )}
      </Form.Item>

      <Button
        type="primary"
        htmlType="submit"
        size="large"
        shape="round"
        loading={loading}
        block
      >
        Create Account
      </Button>
    </Form>
  );
};

export default RegisterForm;