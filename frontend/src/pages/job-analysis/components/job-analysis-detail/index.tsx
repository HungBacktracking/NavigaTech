import { Typography, Flex, Space, Button, Tag, Tabs, Progress, List, Anchor, theme } from 'antd';
import {
  EnvironmentOutlined,
  LinkOutlined,
  CheckCircleFilled,
  AuditOutlined,
  DollarCircleOutlined,
  SettingOutlined,
  CloseCircleFilled
} from '@ant-design/icons';
import { useEffect, useState, useRef, useCallback } from 'react';
import { JobAnalysisDetail as JobAnalysisDetailType } from '../../../../lib/types/job';
import { blue, green, red, yellow } from '@ant-design/colors';
import ReactMarkdown from 'react-markdown';

const { Title, Text, Paragraph } = Typography;
const { useToken } = theme;

interface JobAnalysisDetailProps {
  job: JobAnalysisDetailType;
}

const JobAnalysisDetail = ({ job }: JobAnalysisDetailProps) => {
  const { token } = useToken();
  const [activeTab, setActiveTab] = useState('1');
  const [activeAnchor, setActiveAnchor] = useState('general');
  const [progressAnimation, setProgressAnimation] = useState(0);
  const [containerReady, setContainerReady] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const isManualScrollRef = useRef(false);
  const sectionRefs = useRef<Record<string, HTMLDivElement | null>>({});

  const feedbackSections = [
    {
      key: 'general',
      title: 'General Overview',
      content: job.generalFeedback
    },
    {
      key: 'role',
      title: 'Role Fit',
      content: job.roleFeedback
    },
    {
      key: 'skills',
      title: 'Technical Skills',
      content: job.skillsFeedback
    },
    {
      key: 'experience',
      title: 'Work Experience',
      content: job.workExperienceFeedback
    },
    {
      key: 'education',
      title: 'Education',
      content: job.educationFeedback
    },
    {
      key: 'language',
      title: 'Language Skills',
      content: job.languageFeedback
    }
  ];

  useEffect(() => {
    if (activeTab === '1') {
      const timer = setTimeout(() => {
        setProgressAnimation(job.matchScore);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [activeTab, job.matchScore]);

  useEffect(() => {
    if (!containerReady) return;

    const container = contentRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isManualScrollRef.current) return;

      const sections = feedbackSections.map(section => ({
        id: section.key,
        element: document.getElementById(section.key)
      })).filter(section => section.element) as { id: string, element: HTMLElement }[];

      const scrollPosition = container.scrollTop;

      const activeSection = sections.find(section => {
        const { offsetTop, offsetHeight } = section.element;
        return scrollPosition >= offsetTop &&
          scrollPosition < offsetTop + offsetHeight;
      });

      if (activeSection) {
        setActiveAnchor(activeSection.id);
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [containerReady]);

  const setContentRef = useCallback((node: HTMLDivElement) => {
    contentRef.current = node;
    if (node) {
      setContainerReady(true);
    }
  }, []);
  
  const getMatchScoreColor = (score: number) => {
    if (score >= 75) return green.primary;
    if (score >= 50) return blue.primary;
    if (score >= 25) return yellow[5];
    return red.primary;
  };

  const handleAnchorClick = (link: { href: string }) => {
    const anchorKey = link.href.replace('#', '');
    isManualScrollRef.current = true;

    setActiveAnchor(anchorKey);
    document.getElementById(anchorKey)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });

    setTimeout(() => {
      isManualScrollRef.current = false;
    }, 500);
  };

  const items = [
    {
      key: '1',
      label: 'Matching Analysis',
      children: (
        <Flex vertical style={{ padding: '0 16px' }}>
          <Flex vertical>
            <Title level={5}>Overall</Title>
            <Progress
              percent={progressAnimation}
              strokeColor={getMatchScoreColor(job.matchScore)}
              status="active"
            />
            <Text>
              {job.matchScore > 75 ? 'Excellent match for your profile!' :
                job.matchScore > 50 ? 'Good match for your profile' :
                  job.matchScore > 25 ? 'Moderate match for your profile' :
                    'Consider improving your skills or looking for better matches'}
            </Text>
          </Flex>

          <Flex justify="space-between" style={{ marginTop: 16 }}>
            <Flex vertical style={{ flex: 1 }}>
              <Title level={4} style={{ color: token.colorSuccessActive, margin: 0 }}>Strengths</Title>
              <List
                dataSource={job.strengths}
                split={false}
                renderItem={(item) => (
                  <Space size="small" style={{ width: '100%', marginBottom: 8 }}>
                    <CheckCircleFilled style={{ color: green.primary, fontSize: 16 }} />
                    <Text>{item}</Text>
                  </Space>
                )}
                style={{
                  padding: '8px 0',
                }}
              />
            </Flex>

            <Flex vertical style={{ flex: 1 }}>
              <Title level={4} style={{ color: red.primary, margin: 0 }}>Weaknesses</Title>
              <List
                itemLayout="horizontal"
                dataSource={job.weaknesses}
                split={false}
                renderItem={(item) => (
                  <Space size="small" style={{ width: '100%', marginBottom: 8 }}>
                    <CloseCircleFilled style={{ color: red.primary, fontSize: 16 }} />
                    <Text>{item}</Text>
                  </Space>
                )}
                style={{
                  padding: '8px 0',
                }}
              />
            </Flex>
          </Flex>
        </Flex>
      ),
    },
    {
      key: '2',
      label: 'AI Report',
      children: (
        <Flex style={{ height: '60vh' }} className="scrollbar-custom container">
          <Flex
            style={{
              width: 180,
              borderRight: `1px solid ${token.colorBorderSecondary}`,
              overflowY: 'auto'
            }}
          >
            <Anchor
              affix={false}
              direction="vertical"
              items={feedbackSections.map(section => ({
                key: section.key,
                href: `#${section.key}`,
                title: section.title,
              }))}
              onClick={(e, link) => {
                e.preventDefault();
                handleAnchorClick({ href: link.href });
              }}
              getCurrentAnchor={() => {
                return `#${activeAnchor}`;
              }}
              getContainer={() => contentRef.current as HTMLElement}
            />
          </Flex>

          <Flex
            vertical
            style={{
              flex: 1,
              padding: '0 16px',
              overflowY: 'auto'
            }}
            ref={setContentRef}
            className="content"
          >
            {feedbackSections.map((section) => (
              <div
                key={section.key}
                id={section.key}
                style={{ scrollMarginTop: 16 }}
                ref={(el) => {
                  sectionRefs.current[section.key] = el;
                }}
                data-section
              >
                <ReactMarkdown
                  components={{
                    h1: ({ ...props }) => <Title level={2} {...props} />,
                    h2: ({ ...props }) => <Title level={3} {...props} style={{ marginTop: 0 }} />,
                    h3: ({ ...props }) => <Title level={4} {...props} />,
                    p: ({ ...props }) => <Paragraph {...props} />,
                    ul: ({ ...props }) => <ul style={{ paddingLeft: 16 }} {...props} />,
                    li: ({ ...props }) => <li style={{ marginBottom: 4 }} {...props} />
                  }}
                >
                  {section.content}
                </ReactMarkdown>
              </div>
            ))}
          </Flex>
        </Flex>
      )
    }
  ];

  return (
    <Flex vertical>
      <Flex vertical>
        <Title level={3} style={{ margin: 0 }}>{job.title}</Title>
        <Space>
          <Text type="secondary" style={{ fontSize: 16, fontWeight: 600 }}>{job.companyName}</Text>
          <Button
            type="text"
            icon={<LinkOutlined />}
            href={job.originalUrl}
            target="_blank"
            style={{
              color: token.colorPrimary,
            }}
          >
            Apply
          </Button>
        </Space>
      </Flex>


      <Flex gap="middle" wrap="wrap" style={{ marginTop: 8 }}>
        <Space size="small">
          <Space>
            <EnvironmentOutlined />
            {job.location}
          </Space>
          {job.type && (
            <Space>
              <AuditOutlined />
              {job.type}
            </Space>
          )}
          {job.salary && (
            <Space>
              <DollarCircleOutlined />
              {job.salary}
            </Space>
          )}
        </Space>
        <Space>
          <SettingOutlined />
          <span>Analyzed on {job.analyzedAt.toLocaleString()}</span>
        </Space>
        <Space wrap>
          {job.skills.map((skill, index) => (
            <Tag key={index} color={blue[0]} style={{ padding: '2px 8px', fontSize: 12, borderRadius: 8, borderColor: blue[2] }}>
              <Text style={{ color: blue[6] }}>{skill}</Text>
            </Tag>
          ))}
        </Space>
      </Flex>

      <Tabs
        defaultActiveKey="1"
        items={items}
        onChange={setActiveTab}
        tabBarStyle={{ marginTop: 16 }}
        style={{
          alignItems: 'center',
        }}
      />
    </Flex>
  );
};

export default JobAnalysisDetail;