import { Card, Typography, Button, Flex } from 'antd';
import { StarFilled, BarChartOutlined } from '@ant-design/icons';
import { MouseEvent } from 'react';
import { orange } from '@ant-design/colors';
import AIButton from '../../../../components/ai-button';

const { Text, Title } = Typography;

interface MiniFavoriteJobCardProps {
  jobName: string;
  companyName: string;
  isAnalyzing: boolean;
  handleAnalyze: () => void;
  handleToggleFavorite: (e: MouseEvent) => void;
}

const MiniFavoriteJobCard = ({ jobName, companyName, isAnalyzing, handleAnalyze, handleToggleFavorite }: MiniFavoriteJobCardProps) => {
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
            {jobName}
          </Title>
          <Button
            type="text"
            icon={<StarFilled style={{ color: orange.primary }} />}
            onClick={handleToggleFavorite}
            size="small"
          />
        </Flex>
        <Text type="secondary">{companyName}</Text>
        <AIButton
          type="primary"
          loading={isAnalyzing}
          icon={<BarChartOutlined />}
          style={{
            marginTop: 8,
            width: '100%',
            textAlign: 'center',
          }}
          onClick={handleAnalyze}
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Job'}
        </AIButton>
      </Flex>
    </Card>
  );
};

export default MiniFavoriteJobCard;