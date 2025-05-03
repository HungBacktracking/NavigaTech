import { Button, Card, Flex, Image, Space, Tag, Tooltip, Typography } from "antd";
import { EnvironmentOutlined, ClockCircleOutlined, StarFilled, StarOutlined, AuditOutlined, BookOutlined, BarChartOutlined } from "@ant-design/icons";
import { Job } from "../../../../lib/types/job";
import { blue, blueDark, gray, orange } from "@ant-design/colors";
import { extractDomainFromUrl, formatDateToEngPeriodString } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";
import { useMobile } from "../../../../hooks/use-mobile";
import { MouseEvent } from "react";

const { Text, Title } = Typography;

interface JobCardProps {
  job: Job;
  isFavorite: boolean;
  handleToggleFavorite: (e: MouseEvent) => void;
  handleSelectJob: (job: Job) => void;
  isSelected: boolean;
}

const JobCard = ({ job, isFavorite, handleSelectJob, handleToggleFavorite, isSelected = false }: JobCardProps) => {
  const { isMobile: isTablet } = useMobile(1024);

  const handleJobAnalysisClick = (id: string) => {
    console.log(`Job Analysis for job ID: ${id}`);
    // TODO: Implement job analysis logic here
  }

  const handleCreateCVClick = (id: string) => {
    console.log(`Create CV for job ID: ${id}`);
    // TODO: Implement create CV logic here
  }

  return (
    <Card
      hoverable
      title={
        <Flex
          horizontal
          justify="space-between"
          align="center"
        >
          <Flex
            horizontal
            gap="middle"
            align="center"
            justify="start"
            style={{ padding: 0 }}>
            <div style={{ padding: 2, borderRadius: 4, backgroundColor: '#fafafa' }}>
              <Image
                src={job.companyLogo}
                alt={`${job.companyName} logo`}
                fallback={`https://placehold.co/100x100?text=${job.companyName[0]}`}
                style={{
                  width: 40,
                  height: 40,
                }}
                preview={false}
              />
            </div>
            <Flex vertical>
              <Title level={4} style={{ color: blue.primary, margin: 0, fontWeight: 500, textWrap: "wrap" }}>
                {job.title}
              </Title>
              <Text type="secondary">
                {job.companyName}
              </Text>
            </Flex>
          </Flex>
          <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"} color={blueDark[1]}>
            <Button
              type="text"
              shape="circle"
              icon={isFavorite ? <StarFilled style={{ color: orange.primary, fontSize: 20 }} /> : <StarOutlined style={{ color: gray[3], fontSize: 20 }} />}
              onClick={handleToggleFavorite}
              style={{ marginLeft: "auto" }}
            />
          </Tooltip>
        </Flex>
      }
      onClick={() => handleSelectJob(job)}
      style={{
        borderRadius: 16,
        border: isSelected ? `0.5px solid ${blue[3]}` : undefined,
        boxShadow: isSelected ? `0 0 12px ${blue[2]}` : undefined,
        position: isSelected ? 'relative' : undefined,
      }}
      styles={{
        header: {
          padding: '8px 12px'
        },
        body: {
          padding: '12px 16px'
        },
      }}
    >
      {isSelected && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 10,
            bottom: 10,
            width: 4,
            backgroundColor: blue[3],
            borderRadius: 24,
            transition: 'all 0.3s ease-in-out',
          }}
        />
      )}
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Flex vertical gap="small">
          <Space>
            <EnvironmentOutlined />
            {job.location}
          </Space>
          <Flex horizontal gap="large" wrap="wrap">
            {job.type && (
              <Space>
                <AuditOutlined />
                {job.type}
              </Space>
            )}
            {job.salary && <span>{job.salary}</span>}
          </Flex>
          {job.datePosted && (
            <Space>
              <ClockCircleOutlined />
              {formatDateToEngPeriodString(job.datePosted)}
            </Space>
          )}
        </Flex>
        <Space wrap>
          {job.skills.map((skill, index) => (
            <Tag key={index} color={blue[0]} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 8 }}>
              <Text>{skill}</Text>
            </Tag>
          ))}
        </Space>
        <Flex 
          horizontal={!isTablet}
          vertical={isTablet}
          gap="small"
          justify="space-between"
          align="center"
          style={{ margin: "4px 0 0 0" }}>
          <a
            href={job.originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
          >
            {extractDomainFromUrl(job.originalUrl)}
          </a>

          <Space>
            <AIButton
              icon={<BarChartOutlined />}
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                handleJobAnalysisClick(job.id);
              }}
            >
              Analysis
            </AIButton>

            <AIButton
              icon={<BookOutlined />}
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                handleCreateCVClick(job.id);
              }}
            >
              Create CV
            </AIButton>
          </Space>
        </Flex>
      </Space>

    </Card>
  );
};

export default JobCard;