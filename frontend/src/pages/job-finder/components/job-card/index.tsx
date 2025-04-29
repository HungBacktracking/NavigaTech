import { Button, Card, Flex, Image, Space, Tag, Tooltip, Typography } from "antd";
import { EnvironmentOutlined, ClockCircleOutlined, StarFilled, StarOutlined, AuditOutlined, BookOutlined, BarChartOutlined } from "@ant-design/icons";
import { Job } from "../../../../lib/types/job";
import styles from "./styles.module.css";
import { blue, blueDark, gray, orange } from "@ant-design/colors";
import { extractDomainFromUrl } from "../../../../lib/helpers/string";
import AIButton from "../../../../components/ai-button";

const { Text, Title } = Typography;

interface JobCardProps {
  job: Job;
  isFavorite: boolean;
  handleSelectJob: (job: Job) => void;
  isSelected: boolean;
}

const JobCard = ({ job, isFavorite, handleSelectJob, isSelected }: JobCardProps) => {
  const formatDate = (date: Date) => {
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  const handleFavoriteToggle = (e: MouseEvent) => {
    e.stopPropagation();
    // TODO: Handle favorite toggle logic here
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
            style={{ padding: "8px 0" }}>
            <div className={styles.logoContainer}>
              <Image
                src={job.company.logo}
                alt={`${job.company.name} logo`}
                style={{
                  width: 40,
                  height: 40,
                }}
              />
            </div>
            <Flex vertical>
              <Title level={4} style={{ color: blue.primary, margin: 0, fontWeight: 500 }}>
                {job.title}
              </Title>
              <Text type="secondary">
                {job.company.name}
              </Text>
            </Flex>
          </Flex>
          <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"} color={blueDark[1]}>
            <Button
              type="text"
              shape="circle"
              icon={isFavorite ? <StarFilled style={{ color: orange.primary, fontSize: 20 }} /> : <StarOutlined style={{ color: gray[3], fontSize: 20 }} />}
              onClick={handleFavoriteToggle}
              style={{ marginLeft: "auto" }}
            />
          </Tooltip>
        </Flex>
      }
      onClick={() => handleSelectJob(job)}
      style={{
        width: 500,
        borderRadius: 16,
      }}
      styles={{
        body: {
          padding: '16px 24px'
        }
      }}
    >
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
              {formatDate(job.datePosted)}
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
        <Flex horizontal justify="space-between" align="center" style={{ margin: "8px 0 0 0" }}>
          <a
            href={job.originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className={styles.sourceLink}
          >
            {extractDomainFromUrl(job.originalUrl)}
          </a>

          <Space>
            <AIButton
              icon={<BarChartOutlined />}
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                // Job Analysis logic here
              }}
            >
              Analysis
            </AIButton>

            <AIButton
              icon={<BookOutlined />}
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                // Save job logic
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