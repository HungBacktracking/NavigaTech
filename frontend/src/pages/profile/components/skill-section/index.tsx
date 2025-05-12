import { ChangeEvent } from 'react';
import { Typography, Flex, Button, Card, Tag, Input, Tooltip, theme } from 'antd';
import { EditOutlined, PlusOutlined, CloseOutlined, SaveFilled } from '@ant-design/icons';

const { Title, Text } = Typography;

interface SkillsSectionProps {
  editingSections: boolean;
  skillsList: string[];
  editingSkills: boolean;
  setEditingSkills: (value: boolean) => void;
  newSkill: string;
  setNewSkill: (value: string) => void;
  handleAddSkill: () => void;
  handleRemoveSkill: (skill: string) => void;
  onSubmitSkills: () => void;
  isUpdatingSkills: boolean;
  onCancelEdit?: () => void;
}

const SkillsSection = ({
  editingSections,
  skillsList,
  editingSkills,
  setEditingSkills,
  newSkill,
  setNewSkill,
  handleAddSkill,
  handleRemoveSkill,
  onSubmitSkills,
  isUpdatingSkills,
  onCancelEdit
}: SkillsSectionProps) => {
  const { token } = theme.useToken();

  const handleCancel = () => {
    if (onCancelEdit) {
      onCancelEdit();
    }
    setEditingSkills(false);
  };

  return (
    <Card
      variant='borderless'
      title={
        <Flex justify="space-between" align="center">
          <Title level={4} style={{ margin: 0 }}>Skills</Title>
          {!editingSections && (
            <Button
              type="text"
              icon={
                editingSkills ?
                  <Tooltip title="Close">
                    <CloseOutlined style={{ fontSize: 16 }} />
                  </Tooltip> :
                  <Tooltip title="Edit">
                    <EditOutlined style={{ fontSize: 16, color: token.colorPrimary }} />
                  </Tooltip>
              }
              onClick={() => setEditingSkills(!editingSkills)}
            />
          )}
        </Flex>
      }
      style={{ marginBottom: 24, borderRadius: 8 }}
    >
      {editingSkills ? (
        <div>
          <Flex wrap="wrap" gap={8} style={{ marginBottom: 16 }}>
            {skillsList?.map((skill, index) => (
              <Tag
                key={index}
                closable
                closeIcon={<CloseOutlined style={{ color: token.colorPrimary, fontSize: 12, marginLeft: 8 }} />}
                onClose={() => handleRemoveSkill(skill)}
                color={token.colorPrimary}
                style={{
                  borderRadius: '32px',
                  padding: '4px 16px',
                  backgroundColor: token.colorPrimaryBg,
                  color: token.colorPrimary,
                  borderColor: token.colorPrimary,
                }}
              >
                {skill}
              </Tag>
            ))}
          </Flex>
          <Flex>
            <Tooltip title="Add Skill">
              <Button shape="circle" type="primary" onClick={handleAddSkill} icon={<PlusOutlined />}></Button>
            </Tooltip>
            <Input
              placeholder="Add a skill"
              value={newSkill}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setNewSkill(e.target.value)}
              onPressEnter={handleAddSkill}
              style={{ marginLeft: 16, flex: 1 }}
            />
          </Flex>
          <Flex gap={16} style={{ marginTop: 32 }}>
            <Button
              type="primary"
              icon={<SaveFilled />}
              onClick={onSubmitSkills}
              loading={isUpdatingSkills}
            >
              Save
            </Button>
            <Button
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </Flex>
        </div>
      ) : (
        <Flex wrap="wrap" gap={8}>
          {skillsList && skillsList.length > 0 ? (
            skillsList.map((skill, index) => (
              <Tag
                key={index}
                color={token.colorPrimary}
                style={{
                  borderRadius: '32px',
                  padding: '4px 16px',
                  backgroundColor: token.colorPrimaryBg,
                  color: token.colorPrimary,
                  borderColor: token.colorPrimary,
                  margin: '0 8px 8px 0'
                }}
              >
                {skill}
              </Tag>
            ))
          ) : (
            <Text type="secondary">Add skills to highlight your expertise</Text>
          )}
        </Flex>
      )}
    </Card>
  );
};

export default SkillsSection;
