import { Typography, Flex, Form, Input, Button, Card, Avatar, theme } from 'antd';
import { Controller } from 'react-hook-form';
import { EditOutlined, UserOutlined, EnvironmentOutlined, SaveOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface ProfileHeaderProps {
  editingSections: boolean;
  name: string;
  headline: string;
  location: string;
  introduction: string;
  handleEditProfile: () => void;
  handleCancelEdit: () => void;
  handleBasicInfoSubmit: any;
  basicInfoControl: any;
  isUpdatingBasicInfo: boolean;
}

const ProfileHeader = ({
  editingSections,
  name,
  headline,
  location,
  introduction,
  handleEditProfile,
  handleCancelEdit,
  handleBasicInfoSubmit,
  basicInfoControl,
  isUpdatingBasicInfo,
}: ProfileHeaderProps) => {
  const { token } = theme.useToken();

  return (
    <Card
      variant="borderless"
      style={{ marginBottom: 24, borderRadius: 8 }}
      cover={
        <div
          style={{
            height: '150px',
            background: `linear-gradient(135deg, ${token.colorPrimaryBg}, ${token.colorPrimary}, ${token.colorPrimaryBg})`,
            borderTopLeftRadius: 8,
            borderTopRightRadius: 8
          }}
        />
      }
    >
      <Flex vertical align="center" style={{ marginTop: -100 }}>
        <Avatar
          size={200}
          icon={<UserOutlined />}
          style={{
            border: '4px solid white',
            backgroundColor: token.colorPrimaryBg,
            color: token.colorPrimary
          }}
        />

        {!editingSections ? (
          <>
            <Title level={1} style={{ marginBottom: 0, marginTop: 16, textAlign: 'center' }}>
              {name || 'Your Name'}
            </Title>
            <Text style={{ fontSize: '16px', marginBottom: 12, display: 'block', textAlign: 'center' }}>
              {headline || 'Add your professional headline'}
            </Text>

            <Flex align="center" style={{ marginBottom: 8 }}>
              <EnvironmentOutlined style={{ marginRight: 8, color: token.colorTextSecondary }} />
              <Text>{location || 'Add your location'}</Text>
            </Flex>

            {introduction && (
              <Paragraph style={{ marginTop: 16, textAlign: 'center', maxWidth: '80%' }}>
                {introduction}
              </Paragraph>
            )}

            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={handleEditProfile}
              style={{ marginTop: 16 }}
            >
              Edit Profile
            </Button>
          </>
        ) : (
          <Form
            layout="vertical"
            style={{ width: '100%', marginTop: 16 }}
            onFinish={handleBasicInfoSubmit}
          >
            <Card variant="borderless" title="Basic Information" style={{ boxShadow: '1px 2px 8px rgba(0, 0, 0, 0.1)' }}>
              <Form.Item label="Full Name">
                <Controller
                  name="name"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="Your full name" />}
                />
              </Form.Item>

              <Form.Item label="Professional Headline">
                <Controller
                  name="headline"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="e.g. Senior Software Developer" />}
                />
              </Form.Item>

              <Form.Item label="Location">
                <Controller
                  name="location"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="Your location" />}
                />
              </Form.Item>

              <Form.Item label="Introduction">
                <Controller
                  name="introduction"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => (
                    <Input.TextArea
                      {...field}
                      placeholder="A brief introduction about yourself"
                      rows={4}
                    />
                  )}
                />
              </Form.Item>
            </Card>

            <Card variant="borderless"  title="Contact Information" style={{ marginTop: 16, boxShadow: '1px 2px 8px rgba(0, 0, 0, 0.1)' }}>
              <Form.Item label="Email Address">
                <Controller
                  name="email"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input disabled {...field} placeholder="Your email address" />}
                />
              </Form.Item>

              <Form.Item label="Phone Number">
                <Controller
                  name="phone_number"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="Your phone number" />}
                />
              </Form.Item>

              <Form.Item label="LinkedIn URL">
                <Controller
                  name="linkedin_url"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="Your LinkedIn profile URL" />}
                />
              </Form.Item>

              <Form.Item label="GitHub URL">
                <Controller
                  name="github_url"
                  control={basicInfoControl}
                  defaultValue=""
                  render={({ field }) => <Input {...field} placeholder="Your GitHub profile URL" />}
                />
              </Form.Item>
            </Card>

            <Flex justify="center" gap={16} style={{ marginTop: 24 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={isUpdatingBasicInfo}
                size="large"
                icon={<SaveOutlined />}
              >
                Save Profile
              </Button>
              <Button onClick={handleCancelEdit} size="large">
                Cancel
              </Button>
            </Flex>
          </Form>
        )}
      </Flex>
    </Card>
  );
};

export default ProfileHeader;