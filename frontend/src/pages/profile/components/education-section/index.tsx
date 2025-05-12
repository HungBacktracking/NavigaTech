import React from 'react';
import { Typography, Flex, Button, Card, Divider, Popconfirm, theme, Tooltip } from 'antd';
import { EditOutlined, PlusOutlined, DeleteOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { Education } from '../../../../lib/types/user';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

interface EducationSectionProps {
  educationsList: Education[];
  openEducationModal: (education?: Education) => void;
  handleDeleteEducation: (id: string) => void;
  isDeletingEducation: boolean;
  deletingIds: string[];
}

const EducationSection: React.FC<EducationSectionProps> = ({
  educationsList,
  openEducationModal,
  handleDeleteEducation,
  isDeletingEducation,
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
          <Title level={4} style={{ margin: 0 }}>Education</Title>
          <Button
            type="primary"
            icon={<PlusCircleOutlined />}
            onClick={() => openEducationModal()}
          >
            New
          </Button>
        </Flex>
      }
      style={{ marginBottom: 24, borderRadius: 8 }}
    >
      {educationsList && educationsList.length > 0 ? (
        <Flex vertical gap={16}>
          {educationsList.map((education, index) => (
            <div key={education.id}>
              {index > 0 && <Divider style={{ margin: '8px 0' }} />}
              <Flex justify="space-between" align="flex-start">
                <div style={{ flex: 1 }}>
                  <Title level={4} style={{ marginTop: 0, marginBottom: 4 }}>{education.school_name}</Title>
                  <Text strong>{education.major} - {education.degree_type}</Text>
                  <div>
                    <Text type="secondary">
                      {formatDate(education.start_date)} - {education.is_current ? 'Present' : formatDate(education.end_date)}
                    </Text>
                  </div>
                  {education.description && (
                    <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                      {education.description}
                    </Paragraph>
                  )}
                </div>
                <Flex gap={8}>
                  <Tooltip title="Edit">
                    <Button
                      type="text"
                      icon={<EditOutlined style={{ color: token.colorPrimary }} />}
                      onClick={() => openEducationModal(education)}
                    />
                  </Tooltip>
                  <Popconfirm
                    title="Are you sure you want to delete this education?"
                    onConfirm={() => handleDeleteEducation(education.id)}
                    okText="Yes"
                    cancelText="No"
                  >
                    <Tooltip title="Delete">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        loading={isDeletingEducation && deletingIds.includes(education.id)}
                      />
                    </Tooltip>
                  </Popconfirm>
                </Flex>
              </Flex>
            </div>
          ))}
        </Flex>
      ) : (
        <Text type="secondary">Add your educational background</Text>
      )}
    </Card>
  );
};

export default EducationSection;