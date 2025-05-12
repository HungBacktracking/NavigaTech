import React from 'react';
import { Typography, Flex, Button, Card, Divider, Popconfirm, theme, Tooltip } from 'antd';
import { EditOutlined, DeleteOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { Project } from '../../../../lib/types/user';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

interface ProjectsSectionProps {
  projectsList: Project[];
  openProjectModal: (project?: Project) => void;
  handleDeleteProject: (id: string) => void;
  isDeletingProject: boolean;
  deletingIds: string[];
}

const ProjectsSection: React.FC<ProjectsSectionProps> = ({
  projectsList,
  openProjectModal,
  handleDeleteProject,
  isDeletingProject,
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
          <Title level={4} style={{ margin: 0 }}>Projects</Title>
          <Button
            type="primary"
            icon={<PlusCircleOutlined />}
            onClick={() => openProjectModal()}
          >
            New
          </Button>
        </Flex>
      }
      style={{ marginBottom: 24, borderRadius: 8 }}
    >
      {projectsList && projectsList.length > 0 ? (
        <Flex vertical gap={16}>
          {projectsList.map((project, index) => (
            <div key={project.id}>
              {index > 0 && <Divider style={{ margin: '8px 0' }} />}
              <Flex justify="space-between" align="flex-start">
                <div style={{ flex: 1 }}>
                  <Title level={4} style={{ marginTop: 0, marginBottom: 4 }}>{project.project_name}</Title>
                  {project.role && (
                    <Text strong style={{ display: 'block' }}>{project.role}</Text>
                  )}
                  <div>
                    <Text type="secondary">
                      {project.start_date && formatDate(project.start_date)}
                      {project.start_date && project.end_date && ' - '}
                      {project.end_date && formatDate(project.end_date)}
                    </Text>
                  </div>
                  {project.description && (
                    <Paragraph style={{ marginBottom: 8 }}>
                      {project.description}
                    </Paragraph>
                  )}
                  {project.achievement && (
                    <Paragraph style={{ marginBottom: 8 }}>
                      <strong>Achievement: </strong>{project.achievement}
                    </Paragraph>
                  )}
                </div>
                <Flex gap={8}>
                  <Tooltip title="Edit">
                    <Button
                      type="text"
                      icon={<EditOutlined style={{ color: token.colorPrimary }}/>}
                      onClick={() => openProjectModal(project)}
                      loading={isDeletingProject && deletingIds.includes(project.id)}
                    />
                  </Tooltip>
                  <Popconfirm
                    title="Are you sure you want to delete this project?"
                    onConfirm={() => handleDeleteProject(project.id)}
                    okText="Yes"
                    cancelText="No"
                  >
                    <Tooltip title="Delete">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        loading={isDeletingProject && deletingIds.includes(project.id)}
                      />
                    </Tooltip>
                  </Popconfirm>
                </Flex>
              </Flex>
            </div>
          ))}
        </Flex>
      ) : (
        <Text type="secondary">Showcase your projects to highlight your skills and achievements</Text>
      )}
    </Card>
  );
};

export default ProjectsSection;