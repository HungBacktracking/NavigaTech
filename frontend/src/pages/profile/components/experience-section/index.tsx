import React from 'react';
import { Typography, Flex, Button, Card, Divider, Popconfirm, Tooltip, theme } from 'antd';
import { EditOutlined, DeleteOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { Experience } from '../../../../lib/types/user';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

interface ExperienceSectionProps {
  experiencesList: Experience[];
  openExperienceModal: (experience?: Experience) => void;
  handleDeleteExperience: (id: string) => void;
  isDeletingExperience: boolean;
  deletingIds: string[];
}

const ExperienceSection: React.FC<ExperienceSectionProps> = ({
  experiencesList,
  openExperienceModal,
  handleDeleteExperience,
  isDeletingExperience,
  deletingIds
}) => {
  const { token } = theme.useToken();
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Present';
    return dayjs(dateString).format('MMM YYYY');
  };

  return (
    <Card
      variant="borderless"
      title={
        <Flex justify="space-between" align="center">
          <Title level={4} style={{ margin: 0 }}>Experience</Title>
          <Button
            type="primary"
            icon={<PlusCircleOutlined />}
            onClick={() => openExperienceModal()}
          >
            New
          </Button>
        </Flex>
      }
      style={{ marginBottom: 24, borderRadius: 8 }}
      styles={{
        header: {
          marginBottom: 0,
        }
      }}
    >
      {experiencesList && experiencesList.length > 0 ? (
        <Flex vertical gap={16} >
          {experiencesList.map((experience, index) => (
            <div key={experience.id}>
              {index > 0 && <Divider style={{ margin: '8px 0' }} />}
              <Flex justify="space-between" align="flex-start">
                <div style={{ flex: 1 }}>
                  <Title level={4} style={{ marginTop: 0, marginBottom: 4 }}>{experience.position}</Title>
                  <Text strong>{experience.company}</Text>
                  <div>
                    <Text type="secondary">
                      {formatDate(experience.start_date)} - {formatDate(experience.end_date)}
                    </Text>
                  </div>
                  {experience.description && (
                    <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                      {experience.description}
                    </Paragraph>
                  )}
                </div>
                <Flex gap={8}>
                  <Tooltip title="Edit">
                    <Button
                      type="text"
                      icon={<EditOutlined style={{ color: token.colorPrimary }}/>}
                      onClick={() => openExperienceModal(experience)}
                    />
                  </Tooltip>
                  <Popconfirm
                    title="Are you sure you want to delete this experience?"
                    onConfirm={() => handleDeleteExperience(experience.id)}
                    okText="Yes"
                    cancelText="No"
                  >
                    <Tooltip title="Delete">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        loading={isDeletingExperience && deletingIds.includes(experience.id)}
                      />
                    </Tooltip>
                  </Popconfirm>
                </Flex>
              </Flex>
            </div>
          ))}
        </Flex>
      ) : (
        <Text type="secondary">Add your work experience to showcase your professional journey</Text>
      )}
    </Card>
  );
};

export default ExperienceSection;