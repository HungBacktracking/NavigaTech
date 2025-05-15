import { Card, Typography, Button, Flex } from 'antd';
import { StarFilled, BarChartOutlined, EyeOutlined } from '@ant-design/icons';
import { MouseEvent } from 'react';
import { orange } from '@ant-design/colors';
import AIButton from '../../../../components/ai-button';
import { JobAnalytic, JobFavoriteResponse } from '../../../../lib/types/job';

const { Text, Title } = Typography;

interface MiniFavoriteJobCardProps {
  job: JobFavoriteResponse
  isAnalyzing: boolean;
  handleAnalyze: () => void;
  handleToggleFavorite: (e: MouseEvent) => void;
  handleViewDetail: () => void;
}

const MiniFavoriteJobCard = ({ job, isAnalyzing, handleAnalyze, handleToggleFavorite, handleViewDetail }: MiniFavoriteJobCardProps) => {
  return (
    <Card
      size="small"
      style={{
        borderRadius: 8,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Flex vertical>
        <Flex justify="space-between" align="center">
          <Title level={5} style={{ margin: 0 }}>
            {job.job_name}
          </Title>
          <Button
            type="text"
            icon={<StarFilled style={{ color: orange.primary }} />}
            onClick={handleToggleFavorite}
            size="small"
          />
        </Flex>
        <Text type="secondary">{job.company_name}</Text>
        {job.is_analyze && (
          <Button
            type="primary"
            shape="round"
            icon={<EyeOutlined />}
            onClick={(e: MouseEvent) => {
              e.stopPropagation();
              handleViewDetail();
            }}
            style={{ marginTop: 16 }}
          >
            View Analysis
          </Button>
        )}
        {!job.is_analyze && (
          <AIButton
            icon={<BarChartOutlined />}
            loading={isAnalyzing}
            onClick={(e: MouseEvent) => {
              e.stopPropagation();
              handleAnalyze();
            }}
            disabled={isAnalyzing}
            style={{ marginTop: 16, width: '100%' }}
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Job"}
          </AIButton>
        )}
      </Flex>
    </Card>
  );
};

export default MiniFavoriteJobCard;